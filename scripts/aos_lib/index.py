from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from .cadence import due_date, index_dates
from .config import (
    BUCKET_ORDER,
    CLASS_RANK,
    HEADING_AFTER,
    HEADING_UNPLACED,
    PROJECT_STATUSES,
    RECURRING_TYPES,
    SECTION_UNDEFINED,
    UNIQUE_TYPES,
    projects_dir,
    tasks_dir,
)
from .taskio import TaskFile, atomic_write, iter_task_files, load_by_slug
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
    return bucket_for((when - today).days, overdue=False, undefined=False)


def infinitive_of(task: TaskFile) -> str:
    text = task.data.get("infinitive")
    if isinstance(text, str) and text.strip():
        return text.strip()
    raise ValueError(f"{task.path}: missing infinitive")


def clock_of(data: dict) -> tuple[int, int] | None:
    raw = data.get("do_in")
    if raw in (None, "", False):
        return None
    m = CLOCK_RE.match(str(raw).strip())
    if not m:
        raise ValueError(f"invalid do_in {raw!r}")
    return int(m.group(1)), int(m.group(2))


def after_slug(data: dict) -> str | None:
    raw = data.get("do_after")
    if raw in (None, "", False):
        return None
    return str(raw).strip()


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
    def __init__(self, task: TaskFile, href: str, *, present: bool) -> None:
        self.task = task
        self.href = href
        self.present = present
        self.slug = task.slug
        self.infinitive = infinitive_of(task)
        self.clock = clock_of(task.data)
        self.after = after_slug(task.data)
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


def _sorted_nodes(
    nodes: list[_Node], order: dict[str, tuple[str, int, int]]
) -> list[_Node]:
    bands = _project_bands(nodes, order)
    return sorted(nodes, key=lambda n: _sort_key(n, order, bands))


def _line(node: _Node) -> str:
    return f"- [ ] [{node.infinitive}]({node.href})"


def _check_cycles(nodes: dict[str, _Node]) -> None:
    color: dict[str, int] = {}

    def walk(slug: str) -> None:
        state = color.get(slug, 0)
        if state == 1:
            raise ValueError(f"do_after cycle at {slug}")
        if state == 2:
            return
        color[slug] = 1
        node = nodes.get(slug)
        if node and node.after:
            if node.after not in nodes:
                raise ValueError(f"do_after missing slug {node.after!r}")
            walk(node.after)
        color[slug] = 2

    for slug in list(nodes):
        walk(slug)


def _render_children(
    parent: _Node,
    kids: dict[str, list[_Node]],
    order: dict[str, tuple[str, int, int]],
    *,
    depth: int,
    lines: list[str],
) -> None:
    children = _sorted_nodes(kids.get(parent.slug) or [], order)
    visible = [c for c in children if c.present or kids.get(c.slug)]
    if not visible:
        return
    if parent.clock is not None and depth == 0:
        lines.append("")
        lines.append(f"### {HEADING_AFTER} {parent.infinitive}")
        lines.append("")
    for child in visible:
        if child.present:
            lines.append(_line(child))
        _render_children(child, kids, order, depth=depth + 1, lines=lines)


def render_placed(
    present: list[_Node],
    catalog: dict[str, _Node],
    order: dict[str, tuple[str, int, int]],
    *,
    headings: bool,
) -> list[str]:
    if not headings:
        return [_line(n) for n in _sorted_nodes(present, order)]

    kids: dict[str, list[_Node]] = defaultdict(list)
    for node in present:
        if node.after and node.after in catalog:
            kids[node.after].append(node)

    def ensure_ancestor(slug: str, seen: set[str]) -> None:
        if slug in seen:
            return
        seen.add(slug)
        node = catalog.get(slug)
        if node is None or not node.after or node.after not in catalog:
            return
        parent = catalog[node.after]
        if not any(existing.slug == node.slug for existing in kids[parent.slug]):
            kids[parent.slug].append(node)
        ensure_ancestor(parent.slug, seen)

    walked: set[str] = set()
    for slug in list(kids):
        ensure_ancestor(slug, walked)

    present_slugs = {n.slug for n in present}
    referenced = {n.slug for group in kids.values() for n in group}
    roots: list[_Node] = []
    for node in present:
        if node.slug not in referenced:
            roots.append(node)
    for slug in kids:
        parent = catalog.get(slug)
        if parent is None or parent.slug in referenced or parent.slug in present_slugs:
            continue
        roots.append(parent)

    fence_nodes = [n for n in roots if n.clock is not None]
    fence_bands = _project_bands(fence_nodes, order)

    def fence_key(node: _Node) -> tuple:
        return ((node.clock or (99, 99)),) + _sort_key(node, order, fence_bands)

    fences = sorted(fence_nodes, key=fence_key)
    lines: list[str] = []
    for fence in fences:
        if fence.present:
            lines.append(_line(fence))
        _render_children(fence, kids, order, depth=0, lines=lines)

    unplaced = [n for n in roots if n.clock is None]
    shells = [n for n in unplaced if not n.present]
    loose = [n for n in unplaced if n.present]
    for shell in _sorted_nodes(shells, order):
        _render_children(shell, kids, order, depth=0, lines=lines)
    if loose:
        if lines:
            lines.append("")
        lines.append(f"### {HEADING_UNPLACED}")
        lines.append("")
        for node in _sorted_nodes(loose, order):
            lines.append(_line(node))
            _render_children(node, kids, order, depth=1, lines=lines)
    return lines


def render_index(days_by_bucket: dict[str, list[tuple[date | None, list[str]]]]) -> str:
    lines = ["# Tasks"]
    any_items = False
    for heading in BUCKET_ORDER:
        chunks = days_by_bucket.get(heading) or []
        if not chunks:
            continue
        any_items = True
        lines.append("")
        lines.append(f"## {heading}")
        lines.append("")
        for i, chunk in enumerate(chunks):
            if i and chunk:
                lines.append("")
            lines.extend(chunk)
    if not any_items:
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    lines.append("")
    return "\n".join(lines)


def _href(folder: str, slug: str) -> str:
    return f"{folder}/{slug}.md"


def collect_index(root: Path, today: date) -> dict[str, list[list[str]]]:
    order = project_order(root)
    catalog: dict[str, _Node] = {}
    for task in iter_task_files(root):
        catalog[task.slug] = _Node(task, _href(task.folder, task.slug), present=False)
    _check_cycles(catalog)

    placed: dict[str, dict[date | None, list[_Node]]] = defaultdict(lambda: defaultdict(list))
    for task in iter_task_files(root):
        t = task.type
        node = catalog.get(task.slug)
        if node is None:
            continue
        if t in UNIQUE_TYPES:
            if task.folder != "pending":
                continue
            due = due_date(task.data)
            heading = unique_bucket(due, today)
            when = None if due is None else due
            present = _Node(task, node.href, present=True)
            placed[heading][when].append(present)
            continue
        if t in RECURRING_TYPES and task.status == "pending":
            if task.folder != "pending":
                continue
            due = due_date(task.data)
            heading = unique_bucket(due, today)
            when = None if due is None else due
            present = _Node(task, node.href, present=True)
            placed[heading][when].append(present)
            continue
        if t in RECURRING_TYPES:
            if task.folder != "ongoing":
                continue
        elif t == "maintenance":
            if task.folder != "ongoing":
                continue
        else:
            continue
        for when in index_dates(task.data, today):
            heading = recurring_bucket(when, today)
            present = _Node(task, node.href, present=True)
            placed[heading][when].append(present)

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
            nodes = by_day[day]
            text = render_placed(
                nodes,
                catalog,
                order,
                headings=day is not None,
            )
            if text:
                chunks.append(text)
        out[heading] = chunks
    return out


def reindex(root: Path, today: date | None = None) -> Path:
    from .config import today as today_fn

    if today is None:
        today = today_fn(root)
    items = collect_index(root, today)
    lines = ["# Tasks"]
    any_items = False
    for heading in BUCKET_ORDER:
        chunks = items.get(heading) or []
        if not chunks:
            continue
        any_items = True
        lines.append("")
        lines.append(f"## {heading}")
        lines.append("")
        first = True
        for chunk in chunks:
            if not first:
                lines.append("")
            first = False
            lines.extend(chunk)
    if not any_items:
        lines.append("")
        text = "\n".join(lines).rstrip() + "\n"
    else:
        lines.append("")
        text = "\n".join(lines)
    path = tasks_dir(root) / "tasks.md"
    atomic_write(path, text)
    return path
