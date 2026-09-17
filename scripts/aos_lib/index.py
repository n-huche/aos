from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

from .cadence import index_dates
from .config import (
    BUCKET_ORDER,
    SECTION_1_DAY,
    SECTION_2_3_DAYS,
    SECTION_4_7_DAYS,
    SECTION_8_30_DAYS,
    SECTION_OVERDUE,
    SECTION_PLUS_30,
    SECTION_TODAY,
    SECTION_UNDEFINED,
    UNIQUE_TYPES,
    tasks_dir,
)
from .taskio import atomic_write, iter_task_files
from .yamlfm import as_date


def bucket_for(delta_or_none: int | None, *, overdue: bool, undefined: bool) -> str:
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


def render_index(items_by_bucket: dict[str, list[tuple[str, str]]]) -> str:
    lines = ["# Tasks"]
    any_items = False
    for heading in BUCKET_ORDER:
        items = items_by_bucket.get(heading) or []
        if not items:
            continue
        any_items = True
        lines.append("")
        lines.append(f"## {heading}")
        lines.append("")
        for title, href in items:
            lines.append(f"- [ ] [{title}]({href})")
    if not any_items:
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    lines.append("")
    return "\n".join(lines)


def collect_index(root: Path, today: date) -> dict[str, list[tuple[str, str]]]:
    buckets: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for task in iter_task_files(root):
        t = task.type
        if t in UNIQUE_TYPES:
            if task.folder != "pending":
                continue
            due = as_date(task.data.get("due"))
            heading = unique_bucket(due, today)
            href = f"pending/{task.slug}.md"
            sort_key = due.isoformat() if due else "9999-99-99"
            buckets[heading].append((sort_key + task.title.lower(), task.title, href))
        else:
            if task.folder != "recurring":
                continue
            dates = index_dates(task.data, today)
            href = f"recurring/{task.slug}.md"
            for when in dates:
                heading = recurring_bucket(when, today)
                sort_key = when.isoformat() + task.title.lower()
                buckets[heading].append((sort_key, task.title, href))
    out: dict[str, list[tuple[str, str]]] = {}
    for heading, rows in buckets.items():
        rows.sort()
        out[heading] = [(title, href) for _k, title, href in rows]
    return out


def reindex(root: Path, today: date | None = None) -> Path:
    from .config import today as today_fn

    if today is None:
        today = today_fn(root)
    items = collect_index(root, today)
    text = render_index(items)
    path = tasks_dir(root) / "tasks.md"
    atomic_write(path, text)
    return path
