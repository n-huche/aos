from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from .cadence import do_on_date, index_dates, stacked_dates
from .config import (
    BAND_AFTERNOON,
    BAND_EVENING,
    BAND_MORNING,
    BAND_ORDER,
    BAND_OVERNIGHT,
    BUCKET_ORDER,
    CLASS_RANK,
    HEADING_UNTIMED,
    PROJECT_STATUSES,
    RECURRING_TYPES,
    UNIQUE_TYPES,
    projects_dir,
    tasks_dir,
)
from .taskio import TaskFile, atomic_write, iter_task_files
from .yamlfm import split_frontmatter

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CLOCK_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def bucket_for(delta_or_none: int | None, *, overdue: bool, undefined: bool) -> str:
    from .config import (
        SECTION_1_DAY,
        SECTION_2_3_DAYS,
        SECTION_4_7_DAYS,
        SECTION_8_30_DAYS,
        SECTION_OVERDUE,
        SECTION_PLUS_30,
        SECTION_TODAY,
        SECTION_UNDEFINED,
    )

    if undefined:
        return SECTION_UNDEFINED
    if overdue:
        return SECTION_OVERDUE
    assert delta_or_none is not None
    delta = delta_or_none
    if delta <= 0:
        return SECTION_TODAY
    if delta == 1:
        return SECTION_1_DAY
    if delta in (2, 3):
        return SECTION_2_3_DAYS
    if 4 <= delta <= 7:
        return SECTION_4_7_DAYS
    if 8 <= delta <= 30:
        return SECTION_8_30_DAYS
    return SECTION_PLUS_30


def unique_bucket(due: date | None, today: date) -> str:
    if due is None:
        return bucket_for(None, overdue=False, undefined=True)
    if due < today:
        return bucket_for(None, overdue=True, undefined=False)
    return bucket_for((due - today).days, overdue=False, undefined=False)


def recurring_bucket(when: date, today: date) -> str:
    if when < today:
        return bucket_for(None, overdue=True, undefined=False)
    return bucket_for((when - today).days, overdue=False, undefined=False)


def infinitive_of(task: TaskFile) -> str:
    text = task.data.get("infinitive")
    if isinstance(text, str) and text.strip():
        return text.strip()
    raise ValueError(f"{task.path}: missing infinitive")


def clocks_of(data: dict) -> list[tuple[int, int]]:
    """do_at as a list of HH:MM. A comma-separated string is the same list."""
    raw = data.get("do_at")
    if raw in (None, "", False, []):
        return []
    if isinstance(raw, str):
        parts = [part.strip() for part in raw.split(",") if part.strip()]
    elif isinstance(raw, list):
        parts = []
        for item in raw:
            if item in (None, "", False):
                continue
            parts.append(str(item).strip())
    else:
        raise ValueError(f"invalid do_at {raw!r}")
    found: list[tuple[int, int]] = []
    for part in parts:
        match = CLOCK_RE.match(part)
        if not match:
            raise ValueError(f"invalid do_at {part!r}")
        clock = (int(match.group(1)), int(match.group(2)))
        if clock in found:
            raise ValueError(f"duplicate do_at {part}")
        found.append(clock)
    return found


def band_of(clock: tuple[int, int]) -> str:
    minutes = clock[0] * 60 + clock[1]
    if minutes < 6 * 60:
        return BAND_OVERNIGHT
    if minutes < 12 * 60:
        return BAND_MORNING
    if minutes < 18 * 60:
        return BAND_AFTERNOON
    return BAND_EVENING


def _h1(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _slugs_in_order(text: str) -> list[str]:
    out: list[str] = []
    for href in LINK_RE.findall(text):
        name = href.split("#", 1)[0].split("?", 1)[0].rstrip("/").split("/")[-1]
        if name.endswith(".md"):
            out.append(name[:-3])
    return out


def project_order(root: Path) -> dict[str, tuple[str, int, int]]:
    """slug -> (project title, phase index, task index)."""
    found: dict[str, tuple[str, int, int]] = {}
    base = projects_dir(root)
    if not base.is_dir():
        return found
    for status in PROJECT_STATUSES:
        d = base / status
        if not d.is_dir():
            continue
        for proj in sorted(p for p in d.iterdir() if p.is_dir()):
            hub = proj / f"{proj.name}.md"
            if not hub.is_file():
                continue
            _data, body = split_frontmatter(hub.read_text(encoding="utf-8"))
            title = _h1(body) or proj.name
            in_phases = False
            phase_slugs: list[str] = []
            for line in body.splitlines():
                if line.startswith("## "):
                    in_phases = line[3:].strip() == "Phases"
                    continue
                if in_phases:
                    phase_slugs.extend(_slugs_in_order(line))
            for pi, phase_slug in enumerate(phase_slugs):
                phase = proj / "phases" / f"{phase_slug}.md"
                if not phase.is_file():
                    continue
                _pdata, pbody = split_frontmatter(phase.read_text(encoding="utf-8"))
                in_tasks = False
                ti = 0
                for line in pbody.splitlines():
                    if line.startswith("## "):
                        in_tasks = line[3:].strip() == "Tasks"
                        continue
                    if not in_tasks:
                        continue
                    for slug in _slugs_in_order(line):
                        found.setdefault(slug, (title, pi, ti))
                        ti += 1
    return found


class _Node:
    def __init__(
        self,
        task: TaskFile,
        href: str,
        *,
        clock: tuple[int, int] | None,
    ) -> None:
        self.task = task
        self.href = href
        self.slug = task.slug
        self.infinitive = infinitive_of(task)
        self.clock = clock
        self.rank = CLASS_RANK.get(task.type, 9)


def _project_bands(
    nodes: list[_Node], order: dict[str, tuple[str, int, int]]
) -> dict[str, int]:
    """One type-band per project, so the same project stays in presentation order."""
    bands: dict[str, int] = {}
    for node in nodes:
        placed = order.get(node.slug)
        if placed is None:
            continue
        title = placed[0]
        bands[title] = min(node.rank, bands.get(title, node.rank))
    return bands


def _sort_key(
    node: _Node,
    order: dict[str, tuple[str, int, int]],
    bands: dict[str, int],
) -> tuple:
    placed = order.get(node.slug)
    if placed is None:
        return (node.rank, 0, node.infinitive.casefold(), 0, 0, "")
    title, phase_i, task_i = placed
    return (
        bands.get(title, node.rank),
        1,
        title.casefold(),
        phase_i,
        task_i,
        node.infinitive.casefold(),
    )


def _line(node: _Node) -> str:
    return f"- [ ] [{node.infinitive}]({node.href})"


def _separate(lines: list[str]) -> None:
    """One blank line before the next block. Never two in a row, never a leading one."""
    if lines and lines[-1] != "":
        lines.append("")


def _append_tasks(lines: list[str], rows: list[str]) -> None:
    """Task lines stay one list. A blank line is only for a heading block."""
    if lines and lines[-1].startswith("- [ ]"):
        lines.extend(rows)
        return
    _separate(lines)
    lines.extend(rows)


def render_placed(
    present: list[_Node],
    order: dict[str, tuple[str, int, int]],
    *,
    headings: bool,
) -> list[str]:
    if not present:
        return []
    if not headings:
        bands = _project_bands(present, order)
        return [_line(node) for node in sorted(present, key=lambda n: _sort_key(n, order, bands))]

    grouped: dict[str, list[_Node]] = defaultdict(list)
    untimed: list[_Node] = []
    for node in present:
        if node.clock is None:
            untimed.append(node)
        else:
            grouped[band_of(node.clock)].append(node)

    lines: list[str] = []
    for name in BAND_ORDER:
        nodes = grouped.get(name) or []
        if not nodes:
            continue
        bands = _project_bands(nodes, order)
        nodes.sort(key=lambda n: ((n.clock or (99, 99)),) + _sort_key(n, order, bands))
        _separate(lines)
        lines.append(f"### {name}")
        lines.append("")
        for node in nodes:
            lines.append(_line(node))
    if untimed:
        bands = _project_bands(untimed, order)
        untimed.sort(key=lambda n: _sort_key(n, order, bands))
        _separate(lines)
        lines.append(f"### {HEADING_UNTIMED}")
        lines.append("")
        for node in untimed:
            lines.append(_line(node))
    return lines


def _extend(lines: list[str], chunk: list[str]) -> None:
    body = list(chunk)
    while body and body[0] == "":
        body.pop(0)
    while body and body[-1] == "":
        body.pop()
    if not body:
        return
    _separate(lines)
    lines.extend(body)


def _merge_section(chunks: list[list[str]]) -> list[str]:
    """One `###` heading per section. Later days append under the first use.

    A task line stays in the heading that already opened. A later heading
    does not pull the previous task out of that list.
    """
    groups: dict[str, list[str]] = {}
    blocks: list[tuple[str, object]] = []

    def flush_loose(loose: list[str]) -> None:
        if loose:
            blocks.append(("loose", list(loose)))
            loose.clear()

    for chunk in chunks:
        loose: list[str] = []
        current: list[str] | None = None
        body = [line for line in chunk if line != ""]
        for line in body:
            if line.startswith("### "):
                flush_loose(loose)
                bucket = groups.get(line)
                if bucket is None:
                    bucket = []
                    groups[line] = bucket
                    blocks.append(("group", (line, bucket)))
                current = bucket
                continue
            if current is None:
                loose.append(line)
            else:
                current.append(line)
        flush_loose(loose)

    lines: list[str] = []
    for kind, payload in blocks:
        if kind == "loose":
            rows = payload if isinstance(payload, list) else []
            if not rows:
                continue
            _append_tasks(lines, rows)
            continue
        heading, rows = payload  # type: ignore[misc]
        if not isinstance(rows, list) or not rows:
            continue
        _separate(lines)
        lines.append(heading)
        lines.append("")
        lines.extend(rows)
    return lines


def assemble_index(chunks_by_heading: dict[str, list[list[str]]]) -> str:
    lines = ["# Tasks"]
    any_items = False
    for heading in BUCKET_ORDER:
        chunks = chunks_by_heading.get(heading) or []
        if not any(any(line.strip() for line in chunk) for chunk in chunks):
            continue
        any_items = True
        _separate(lines)
        lines.append(f"## {heading}")
        _extend(lines, _merge_section(chunks))
    if not any_items:
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    lines.append("")
    return "\n".join(lines)


def render_index(days_by_bucket: dict[str, list[tuple[date | None, list[str]]]]) -> str:
    chunks_by_heading = {
        heading: [list(chunk) for _day, chunk in pairs]
        for heading, pairs in days_by_bucket.items()
    }
    return assemble_index(chunks_by_heading)


def _href(folder: str, slug: str) -> str:
    return f"{folder}/{slug}.md"


def _occurrences(task: TaskFile, today: date) -> list[date | None]:
    """Dates that put this task in the index. None means Undefined."""
    if task.type in UNIQUE_TYPES:
        if task.folder != "pending":
            return []
        when = do_on_date(task.data)
        return [when]
    if task.type in RECURRING_TYPES and task.status == "pending":
        if task.folder != "pending":
            return []
        return [do_on_date(task.data)]
    if task.type in RECURRING_TYPES and task.status == "ongoing":
        if task.folder != "ongoing":
            return []
        when = do_on_date(task.data)
        if when is not None:
            return stacked_dates(task.data, today)
        return list(index_dates(task.data, today))
    if task.type == "maintenance" and task.status == "ongoing" and task.folder == "ongoing":
        return list(index_dates(task.data, today))
    return []


def collect_index(root: Path, today: date) -> dict[str, list[list[str]]]:
    order = project_order(root)
    placed: dict[str, dict[date | None, list[_Node]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for task in iter_task_files(root):
        href = _href(task.folder, task.slug)
        try:
            clocks = clocks_of(task.data)
        except ValueError:
            clocks = []
        # The index shows the task once, at the first clock as written.
        # The month grid keeps every clock.
        appearances = clocks[:1] or [None]
        for when in _occurrences(task, today):
            if when is None:
                heading = unique_bucket(None, today)
            elif task.type == "maintenance" or (
                task.type in RECURRING_TYPES
                and task.status == "ongoing"
                and do_on_date(task.data) is None
            ):
                heading = recurring_bucket(when, today)
            else:
                heading = unique_bucket(when, today)
            for clock in appearances:
                placed[heading][when].append(_Node(task, href, clock=clock))

    out: dict[str, list[list[str]]] = {}
    for heading, by_day in placed.items():
        chunks: list[list[str]] = []
        days = sorted((d for d in by_day if d is not None), key=lambda d: d.toordinal())
        if None in by_day:
            days_seq: list[date | None] = list(days)
            days_seq.append(None)
        else:
            days_seq = list(days)
        for day in days_seq:
            text = render_placed(by_day[day], order, headings=day is not None)
            if text:
                chunks.append(text)
        out[heading] = chunks
    return out


def reindex(
    root: Path,
    today: date | None = None,
    *,
    apply_checks: bool = True,
    note_completed: bool | None = None,
    commit: bool = True,
) -> Path:
    """Rebuild the index and the open schedule.

    By default, read `[x]` in tasks.md first and apply it: complete a unique,
    start a recurring, advance `do_on`, or drop a forbidden check. Then
    reconcile folders, rebuild the schedule, and rewrite tasks.md. When a
    check was applied, write `## Completed tasks` on today's open daily.
    Then commit and push the vault when files changed. `commit=False`
    skips that. `daily-close` passes apply_checks=False so a midnight
    rebuild does not consume a checkbox.
    """
    from .config import today as today_fn

    if today is None:
        today = today_fn(root)
    if apply_checks:
        from .gitutil import git_lock, user_git_root

        # Same lock as sync_vault, acquired first. The pass re-reads tasks.md
        # under it, so a checkbox watch already cleared is not applied again.
        with git_lock(user_git_root(root)):
            return _reindex_work(
                root,
                today,
                apply_checks=True,
                note_completed=note_completed,
                commit=commit,
            )
    return _reindex_work(
        root,
        today,
        apply_checks=False,
        note_completed=note_completed,
        commit=commit,
    )


def _reindex_work(
    root: Path,
    today: date,
    *,
    apply_checks: bool,
    note_completed: bool | None,
    commit: bool,
) -> Path:
    from .reconcile import reconcile_all
    from .schedule import regenerate_schedule
    from .sync import apply_report, collect_checked

    report = {"reverted": [], "unique": [], "recurring": [], "start": []}
    if apply_checks:
        report = collect_checked(root)
        apply_report(root, report, today)
    applied = any(report.values())
    if note_completed is None:
        note_completed = applied
    reconcile_all(root)
    regenerate_schedule(root, today)
    if note_completed:
        from .daily import write_open_completed

        write_open_completed(root, today)
    items = collect_index(root, today)
    text = assemble_index(items)
    path = tasks_dir(root) / "tasks.md"
    atomic_write(path, text)
    if commit:
        from .gitutil import sync_vault

        sync_vault(root, "aos reindex")
    return path
