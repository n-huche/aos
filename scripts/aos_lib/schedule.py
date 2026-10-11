"""Month grid derived from do_on and do_at.

Closed days are frozen: a column whose date already has a closed daily
is never rewritten. The first time a month file is created, every column
is written once, including days that are already closed.
"""

from __future__ import annotations

import calendar
import re
from datetime import date
from pathlib import Path

from .cadence import do_on_date, occurs_on, until_date
from .config import RECURRING_TYPES, SERIES_TYPES, UNIQUE_TYPES, WEEKDAYS, schedule_dir
from .taskio import iter_task_files

_HEADER_DAY = re.compile(r"^(\d{1,2})\s*-\s*[a-z]{3}$")


def month_path(root: Path, year: int, month: int) -> Path:
    return schedule_dir(root) / f"{year:04d}" / f"{year:04d}-{month:02d}.md"


def _on_grid(task) -> bool:
    if task.folder in {"paused", "completed", "canceled", "obsolete"}:
        return False
    if task.status in {"paused", "completed", "canceled", "obsolete"}:
        return False
    return True


def _months_for(root: Path, today: date) -> set[tuple[int, int]]:
    from .index import clocks_of

    months: set[tuple[int, int]] = set()
    for task in iter_task_files(root):
        if not _on_grid(task):
            continue
        try:
            clocks = clocks_of(task.data)
        except ValueError:
            continue
        if not clocks:
            continue
        if task.type in UNIQUE_TYPES or (
            task.type in RECURRING_TYPES and task.status == "pending"
        ):
            when = do_on_date(task.data)
            if when is not None:
                months.add((when.year, when.month))
            continue
        if task.type in SERIES_TYPES or task.type in RECURRING_TYPES:
            months.add((today.year, today.month))
            when = do_on_date(task.data)
            if when is not None:
                months.add((when.year, when.month))
            until = until_date(task.data)
            if until is not None:
                months.add((until.year, until.month))
    return months


def _labels_for_day(root: Path, day: date) -> dict[int, list[str]]:
    """hour -> labels, for one unfrozen day."""
    from .index import CLASS_RANK, clocks_of, infinitive_of, project_order

    order = project_order(root)
    buckets: dict[int, list[tuple[tuple, str]]] = {}
    for task in iter_task_files(root):
        if not _on_grid(task):
            continue
        try:
            clocks = clocks_of(task.data)
        except ValueError:
            continue
        if not clocks:
            continue
        if not _planned_on(task, day):
            continue
        label = _label(task, order, infinitive_of)
        rank = CLASS_RANK.get(task.type, 9)
        seen_hours: set[int] = set()
        for hour, _minute in clocks:
            if hour in seen_hours:
                continue
            seen_hours.add(hour)
            buckets.setdefault(hour, []).append(((rank, label.casefold(), task.slug), label))
    out: dict[int, list[str]] = {}
    for hour, rows in buckets.items():
        rows.sort(key=lambda item: item[0])
        out[hour] = [label for _key, label in rows]
    return out


def _label(task, order: dict, infinitive_of) -> str:
    if task.type in {"unique-project", "recurring-project"}:
        placed = order.get(task.slug)
        if placed is not None:
            text = placed[0]
        else:
            text = str(task.data.get("project") or "").strip() or infinitive_of(task)
    else:
        text = infinitive_of(task)
    return text.replace("|", "/")


def _planned_on(task, day: date) -> bool:
    when = do_on_date(task.data)
    if task.type in UNIQUE_TYPES:
        return when == day
    if task.type in RECURRING_TYPES and task.status == "pending":
        return when == day
    if task.type in RECURRING_TYPES and task.status == "ongoing":
        if when is not None and day < when:
            return False
        until = until_date(task.data)
        if until is not None and day > until:
            return False
        return occurs_on(task.data, day)
    if task.type == "maintenance":
        return occurs_on(task.data, day)
    return False


def parse_month(text: str) -> dict[int, dict[int, str]]:
    """day -> hour -> cell text, from an existing month file."""
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return {}
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    days: list[int | None] = []
    for cell in header[1:]:
        match = _HEADER_DAY.match(cell.strip())
        days.append(int(match.group(1)) if match else None)
    found: dict[int, dict[int, str]] = {}
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells:
            continue
        hour_text = cells[0]
        if len(hour_text) < 2 or not hour_text[:2].isdigit():
            continue
        hour = int(hour_text[:2])
        for index, day in enumerate(days):
            if day is None:
                continue
            value = cells[index + 1].strip() if index + 1 < len(cells) else "null"
            found.setdefault(day, {})[hour] = value or "null"
    return found


def render_month(year: int, month: int, cells: dict[int, dict[int, str]]) -> str:
    last = calendar.monthrange(year, month)[1]
    headers = ["hour"]
    for day_num in range(1, last + 1):
        when = date(year, month, day_num)
        headers.append(f"{day_num} - {WEEKDAYS[when.weekday()]}")
    lines = [
        f"# {year:04d}-{month:02d}",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for hour in range(24):
        row = [f"{hour:02d}:00"]
        for day_num in range(1, last + 1):
            row.append(cells.get(day_num, {}).get(hour, "null"))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


_MONTH_STEM = re.compile(r"^(\d{4})-(\d{2})$")


def _existing_months(root: Path) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()
    base = schedule_dir(root)
    if not base.is_dir():
        return found
    for path in base.glob("*/*.md"):
        match = _MONTH_STEM.match(path.stem)
        if not match or match.group(1) != path.parent.name:
            continue
        year, month = int(match.group(1)), int(match.group(2))
        if 1 <= month <= 12:
            found.add((year, month))
    return found


def regenerate_schedule(root: Path, today: date, *, frozen_through: date | None = None) -> None:
    """Rewrite open columns. Leave columns on or before frozen_through.

    Months that already have a file are refreshed too, so a completed task
    leaves the open cells.
    """
    from .daily import last_closed_day
    from .taskio import atomic_write

    if frozen_through is None:
        frozen_through = last_closed_day(root)
    months = _months_for(root, today) | _existing_months(root)
    for year, month in sorted(months):
        path = month_path(root, year, month)
        previous: dict[int, dict[int, str]] = {}
        existed = path.is_file()
        if existed:
            previous = parse_month(path.read_text(encoding="utf-8"))
        last = calendar.monthrange(year, month)[1]
        cells: dict[int, dict[int, str]] = {}
        for day_num in range(1, last + 1):
            when = date(year, month, day_num)
            frozen = existed and frozen_through is not None and when <= frozen_through
            if frozen and day_num in previous:
                cells[day_num] = dict(previous[day_num])
                for hour in range(24):
                    cells[day_num].setdefault(hour, "null")
                continue
            labels = _labels_for_day(root, when)
            cells[day_num] = {}
            for hour in range(24):
                row = labels.get(hour) or []
                cells[day_num][hour] = ", ".join(row) if row else "null"
        atomic_write(path, render_month(year, month, cells))


def plan_cell(root: Path, when: date, hour: int) -> str | None:
    """Plan text for one hour, or None when the cell is empty or missing."""
    path = month_path(root, when.year, when.month)
    if not path.is_file():
        return None
    parsed = parse_month(path.read_text(encoding="utf-8"))
    raw = parsed.get(when.day, {}).get(hour, "null")
    if raw is None or raw.strip().lower() == "null" or not raw.strip():
        return None
    return raw.strip()

