from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

from .cadence import day_complete, do_on_date, occurs_on, until_date
from .config import (
    RECURRING_TYPES,
    SERIES_TYPES,
    UNIQUE_TYPES,
    WEEKDAYS,
    daily_dir,
)
from .gitutil import commit_user, push_or_warn
from .index import reindex
from .sync import finish_recurring_until
from .taskio import atomic_write, iter_task_files
from .yamlfm import as_date

NOTES_RE = re.compile(r"^##\s+Notes.*$", re.M)
HOUR_ROW_RE = re.compile(r"^\|\s*(\d{2}:00)\s*\|\s*(.*?)\s*\|$")
METRICS_MARK = "| routine | tasks |"


def ymd_date_from_path(path: Path, root: Path) -> date | None:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) != 3:
        return None
    y, m, name = parts
    if not name.endswith(".md"):
        return None
    day = name[:-3]
    try:
        return date(int(y), int(m), int(day))
    except ValueError:
        return None


def daily_path(root: Path, d: date) -> Path:
    return daily_dir(root) / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.day:02d}.md"


def month_rollup_path(root: Path, d: date) -> Path:
    return daily_dir(root) / f"{d.year:04d}" / f"{d.month:02d}.md"


def extract_notes(text: str) -> str | None:
    match = NOTES_RE.search(text)
    if not match:
        return None
    return text[match.start() :].rstrip() + "\n"


def extract_hours(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in text.splitlines():
        match = HOUR_ROW_RE.match(line.strip())
        if match:
            found[match.group(1)] = match.group(2).strip()
    return found


def daily_is_closed(text: str) -> bool:
    """A placeholder has the hour table and no metrics. Anything else counts."""
    if METRICS_MARK in text or "**Result:**" in text:
        return True
    if "| hour | did |" in text:
        return False
    return True


def _href_for(task_folder: str, slug: str) -> str:
    return f"../../../tasks/{task_folder}/{slug}.md"


def collect_daily(
    root: Path, d: date
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, bool]]]:
    """Completed, failed, and planned rows.

    Planned row is (href, done). Paused tasks are absent.
    """
    completed: list[tuple[str, str]] = []
    failed: list[tuple[str, str]] = []
    planned: list[tuple[str, bool]] = []
    for task in list(iter_task_files(root)):
        if task.folder in {"paused", "canceled", "obsolete"}:
            continue
        if task.status in {"paused", "canceled", "obsolete"}:
            continue
        t = task.type
        if t in UNIQUE_TYPES:
            completed_on = as_date(task.data.get("completed_on"))
            when = do_on_date(task.data)
            href = _href_for(task.folder, task.slug)
            if completed_on == d:
                completed.append((task.title, href))
                planned.append((href, True))
            elif task.folder == "pending" and when is not None and when <= d:
                failed.append((task.title, _href_for("pending", task.slug)))
                planned.append((_href_for("pending", task.slug), False))
            continue
        if t not in SERIES_TYPES:
            continue
        if t in RECURRING_TYPES and task.status == "pending":
            when = do_on_date(task.data)
            if when is not None and when <= d:
                href = _href_for("pending", task.slug)
                failed.append((task.title, href))
                planned.append((href, False))
            continue
        until = until_date(task.data)
        if t in RECURRING_TYPES and until == d and task.folder == "ongoing":
            done = day_complete(task.data, d) or (
                do_on_date(task.data) is not None and do_on_date(task.data) > d
            )
            finish_recurring_until(root, task)
            href = _href_for("completed", task.slug)
            planned.append((href, done))
            if done:
                completed.append((task.title, href))
            else:
                failed.append((task.title, href))
            continue
        when = do_on_date(task.data)
        if t in RECURRING_TYPES and task.status == "ongoing" and when is not None:
            href = _href_for(task.folder, task.slug)
            checked = day_complete(task.data, d)
            if checked:
                completed.append((task.title, href))
                planned.append((href, True))
            elif when <= d:
                failed.append((task.title, href))
                planned.append((href, False))
            continue
        if not occurs_on(task.data, d):
            continue
        href = _href_for(task.folder, task.slug)
        done = day_complete(task.data, d)
        planned.append((href, done))
        if done:
            completed.append((task.title, href))
        else:
            failed.append((task.title, href))
    completed.sort(key=lambda item: item[0].lower())
    failed.sort(key=lambda item: item[0].lower())
    return completed, failed, planned


def _percent(done: int, total: int) -> str:
    if total <= 0:
        return "null"
    return f"{round(100 * done / total)}%"


def routine_score(root: Path, d: date, hours: dict[str, str]) -> tuple[str, list[tuple[str, str, list[str]]]]:
    """routine percent, and deviations as (hour, category, planned tokens)."""
    from .schedule import plan_cell

    comparable = 0
    matched = 0
    deviations: list[tuple[str, str, list[str]]] = []
    for hour in range(24):
        label = f"{hour:02d}:00"
        report = hours.get(label, "null").strip()
        plan = plan_cell(root, d, hour)
        report_empty = report == "" or report.lower() == "null"
        if plan is None or report_empty:
            continue
        tokens = [part.strip() for part in plan.split(",") if part.strip()]
        comparable += 1
        if report in tokens:
            matched += 1
            continue
        deviations.append((label, report, tokens))
    return _percent(matched, comparable), deviations


def tasks_score(planned: list[tuple[str, bool]]) -> str:
    if not planned:
        return "null"
    done = sum(1 for _href, ok in planned if ok)
    return _percent(done, len(planned))


def _parse_percent(cell: str) -> float | None:
    cell = cell.strip()
    if not cell.endswith("%"):
        return None
    try:
        return float(cell[:-1])
    except ValueError:
        return None


def render_daily(
    d: date,
    hours: dict[str, str],
    routine: str,
    tasks: str,
    completed: list[tuple[str, str]],
    failed: list[tuple[str, str]],
    notes: str | None = None,
) -> str:
    lines = [f"# {d.isoformat()}", "", "| hour | did |", "| --- | --- |"]
    for hour in range(24):
        label = f"{hour:02d}:00"
        did = hours.get(label, "null") or "null"
        lines.append(f"| {label} | {did} |")
    lines.extend(
        [
            "",
            METRICS_MARK,
            "| --- | --- |",
            f"| {routine} | {tasks} |",
            "",
            "## Completed tasks",
            "",
        ]
    )
    if completed:
        for title, href in completed:
            lines.append(f"- [{title}]({href})")
        lines.append("")
    else:
        lines.append("")
    if failed:
        lines.append("## Failed tasks")
        lines.append("")
        for title, href in failed:
            lines.append(f"- [{title}]({href})")
        lines.append("")
    if notes:
        notes = notes.rstrip() + "\n"
        if not notes.startswith("## "):
            lines.append("## Notes, optional")
            lines.append("")
        lines.append(notes.rstrip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_placeholder(d: date) -> str:
    """Tomorrow's file from midnight: the hour table only, no metrics yet."""
    lines = [f"# {d.isoformat()}", "", "| hour | did |", "| --- | --- |"]
    for hour in range(24):
        lines.append(f"| {hour:02d}:00 | null |")
    lines.append("")
    return "\n".join(lines)


def write_daily(
    root: Path,
    d: date,
    completed: list[tuple[str, str]],
    failed: list[tuple[str, str]],
    planned: list[tuple[str, bool]],
) -> Path:
    path = daily_path(root, d)
    hours: dict[str, str] = {}
    notes = None
    if path.is_file():
        old = path.read_text(encoding="utf-8")
        hours = extract_hours(old)
        notes = extract_notes(old)
    routine, _deviations = routine_score(root, d, hours)
    tasks = tasks_score(planned)
    text = render_daily(d, hours, routine, tasks, completed, failed, notes)
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return path
    atomic_write(path, text)
    return path


def ensure_placeholder(root: Path, d: date) -> Path:
    path = daily_path(root, d)
    if path.is_file():
        return path
    atomic_write(path, render_placeholder(d))
    return path


def _clear_done_on(root: Path, d: date) -> None:
    """Drop D from done_on. A later date stays (the return-day check)."""
    from .yamlfm import as_date_list

    for task in list(iter_task_files(root)):
        if task.type not in SERIES_TYPES:
            continue
        dates = as_date_list(task.data.get("done_on") or [])
        kept = [item for item in dates if item != d]
        if kept == dates:
            continue
        task.data["done_on"] = kept
        task.save()


def list_daily_dates(root: Path) -> list[date]:
    base = daily_dir(root)
    found: list[date] = []
    if not base.is_dir():
        return found
    for path in base.rglob("*.md"):
        when = ymd_date_from_path(path, base)
        if when is not None:
            found.append(when)
    found.sort()
    return found


def closed_daily_dates(root: Path) -> list[date]:
    base = daily_dir(root)
    found: list[date] = []
    if not base.is_dir():
        return found
    for path in base.rglob("*.md"):
        when = ymd_date_from_path(path, base)
        if when is None:
            continue
        text = path.read_text(encoding="utf-8")
        if daily_is_closed(text):
            found.append(when)
    found.sort()
    return found


def last_closed_day(root: Path) -> date | None:
    dates = closed_daily_dates(root)
    if not dates:
        return None
    return dates[-1]


def missing_close_dates(root: Path, today: date) -> list[date]:
    """Days that still need daily-close: after the last closed daily, through yesterday.

    With no closed daily yet, only yesterday — not the whole calendar.
    A placeholder for tomorrow does not count as closed.
    """
    yesterday = today - timedelta(days=1)
    existing = closed_daily_dates(root)
    if not existing:
        return [yesterday]
    last = existing[-1]
    if last >= yesterday:
        return []
    missed: list[date] = []
    d = last + timedelta(days=1)
    while d <= yesterday:
        missed.append(d)
        d += timedelta(days=1)
    return missed


def _deviation_rows(root: Path, d: date) -> list[tuple[str, str, list[str]]]:
    path = daily_path(root, d)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    if not daily_is_closed(text):
        return []
    _routine, deviations = routine_score(root, d, extract_hours(text))
    return deviations


def _day_percents(root: Path, d: date) -> tuple[float | None, float | None]:
    path = daily_path(root, d)
    if not path.is_file():
        return None, None
    text = path.read_text(encoding="utf-8")
    routine = None
    tasks = None
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| routine") or line.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 2 and cells[0].endswith("%") or (
            len(cells) == 2 and (cells[0] == "null" or cells[0].endswith("%"))
            and ":" not in cells[0]
        ):
            routine = _parse_percent(cells[0])
            tasks = _parse_percent(cells[1])
    return routine, tasks


def render_month_rollup(root: Path, year: int, month: int) -> str:
    import calendar

    last = calendar.monthrange(year, month)[1]
    day_rows: list[tuple[date, float | None, float | None]] = []
    hour_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    task_counts: dict[str, int] = {}
    for day_num in range(1, last + 1):
        when = date(year, month, day_num)
        path = daily_path(root, when)
        if not path.is_file() or not daily_is_closed(path.read_text(encoding="utf-8")):
            continue
        routine, tasks = _day_percents(root, when)
        day_rows.append((when, routine, tasks))
        for hour, category, tokens in _deviation_rows(root, when):
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            for token in tokens:
                task_counts[token] = task_counts.get(token, 0) + 1

    def avg(values: list[float]) -> str:
        if not values:
            return "null"
        return f"{round(sum(values) / len(values))}%"

    lines = [f"# {year:04d}-{month:02d}", "", "## Days", "", "| day | weekday | routine | tasks |", "| --- | --- | --- | --- |"]
    for when, routine, tasks in day_rows:
        lines.append(
            "| {day} | {weekday} | {routine} | {tasks} |".format(
                day=f"{when.day:02d}",
                weekday=WEEKDAYS[when.weekday()],
                routine="null" if routine is None else f"{round(routine)}%",
                tasks="null" if tasks is None else f"{round(tasks)}%",
            )
        )
    lines.extend(["", "## Weekdays", "", "| weekday | routine | tasks |", "| --- | --- | --- |"])
    for name in WEEKDAYS:
        routines = [routine for when, routine, _tasks in day_rows if WEEKDAYS[when.weekday()] == name and routine is not None]
        tasks = [tasks for when, _routine, tasks in day_rows if WEEKDAYS[when.weekday()] == name and tasks is not None]
        if not routines and not tasks:
            continue
        lines.append(f"| {name} | {avg(routines)} | {avg(tasks)} |")
    routines = [routine for _when, routine, _tasks in day_rows if routine is not None]
    tasks = [tasks for _when, _routine, tasks in day_rows if tasks is not None]
    lines.extend(
        [
            "",
            "## Month",
            "",
            METRICS_MARK,
            "| --- | --- |",
            f"| {avg(routines)} | {avg(tasks)} |",
            "",
            "## Hours with the most deviations",
            "",
            "| hour | deviations |",
            "| --- | --- |",
        ]
    )
    for hour, count in sorted(hour_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {hour} | {count} |")
    lines.extend(
        [
            "",
            "## Deviations by category",
            "",
            "| category | count |",
            "| --- | --- |",
        ]
    )
    for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0].casefold())):
        lines.append(f"| {category} | {count} |")
    lines.extend(
        [
            "",
            "## Tasks most deviated",
            "",
            "| task | count |",
            "| --- | --- |",
        ]
    )
    for task, count in sorted(task_counts.items(), key=lambda item: (-item[1], item[0].casefold())):
        lines.append(f"| {task} | {count} |")
    lines.append("")
    return "\n".join(lines)


def write_month_rollup(root: Path, d: date) -> Path:
    path = month_rollup_path(root, d)
    atomic_write(path, render_month_rollup(root, d.year, d.month))
    return path


def daily_close(
    root: Path,
    d: date | None = None,
    *,
    today: date | None = None,
    commit: bool = True,
) -> Path:
    from .config import today as today_fn
    from .reconcile import reconcile_all
    from .schedule import regenerate_schedule

    if today is None:
        today = today_fn(root)
    if d is None:
        d = today - timedelta(days=1)
    reconcile_all(root)
    completed, failed, planned = collect_daily(root, d)
    regenerate_schedule(root, today)
    path = write_daily(root, d, completed, failed, planned)
    _clear_done_on(root, d)
    ensure_placeholder(root, d + timedelta(days=1))
    write_month_rollup(root, d)
    reindex(root, d + timedelta(days=1))
    if commit:
        commit_user(root, f"aos: daily-close {d.isoformat()}")
        push_or_warn(root)
    return path


def catch_up(
    root: Path,
    today: date | None = None,
    *,
    commit: bool = True,
) -> list[str]:
    """Close missed days first. Leftover `[x]` count as the recovery day.

    Snapshot checks before daily-close, because reindex rewrites tasks.md.
    Offline days get no credit; work lands on today, when AOS is up.
    """
    from .config import today as today_fn
    from .sync import apply_collected, collect_checked

    if today is None:
        today = today_fn(root)
    missed = missing_close_dates(root, today)
    if not missed:
        return ["catch-up-none"]
    leftover = collect_checked(root)
    actions: list[str] = []
    for d in missed:
        daily_close(root, d, today=today, commit=commit)
        actions.append(f"catch-up-close:{d.isoformat()}")
    applied = (
        len(leftover["unique"])
        + len(leftover["recurring"])
        + len(leftover.get("start") or [])
    )
    if applied:
        apply_collected(root, leftover, today, commit=commit)
        actions.append(f"catch-up-sync:{today.isoformat()}:{applied}")
    else:
        actions.append("catch-up-sync:none")
    return actions
