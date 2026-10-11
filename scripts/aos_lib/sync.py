from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from datetime import timedelta

from .cadence import day_complete, do_on_date, next_cadence_date, until_date
from .config import (
    RECURRING_TYPES,
    SECTION_TODAY,
    SERIES_TYPES,
    UNIQUE_TYPES,
)
from .links import folder_from_href, rewrite_task_links
from .taskio import TaskFile, load_by_slug, move_task
from .yamlfm import as_date_list

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
ITEM_RE = re.compile(
    r"^(\s*-\s*\[)([xX ])(\]\s+\[[^\]]*\]\s*\()([^\)]+)(\).*$)"
)


def parse_checked(text: str) -> list[tuple[str, str, str]]:
    """Return (section, href, raw_line) for checked items, top to bottom."""
    section = ""
    found: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        hm = HEADING_RE.match(line.strip())
        if hm:
            section = hm.group(1).strip()
            continue
        im = ITEM_RE.match(line)
        if not im:
            continue
        mark = im.group(2)
        if mark not in ("x", "X"):
            continue
        href = im.group(4).strip()
        found.append((section, href, line))
    return found


def _mark_done_on(task: TaskFile, day: date) -> None:
    """Keep today and any later date. Drop earlier dates."""
    kept = [d for d in as_date_list(task.data.get("done_on") or []) if d > day]
    kept.append(day)
    kept.sort()
    task.data["done_on"] = kept


def complete_unique(root: Path, task: TaskFile, day: date) -> None:
    old = task.folder
    task.data["status"] = "completed"
    task.data["completed_on"] = day
    task.save()
    if old != "completed":
        move_task(task, "completed", root)
        rewrite_task_links(root, task.slug, old, "completed")


def _move_status(root: Path, task: TaskFile, folder: str) -> None:
    task.data["status"] = folder if folder != "ongoing" else "ongoing"
    if folder == "completed":
        task.data["status"] = "completed"
    task.save()
    old = task.folder
    if old != folder:
        move_task(task, folder, root)
        rewrite_task_links(root, task.slug, old, folder)


def _advance_do_on(task: TaskFile, day: date) -> bool:
    """Record the check. Move do_on to the next cadence day after the scheduled one.

    Returns True when the series is finished (the next day would pass until).
    A series with no do_on keeps the cadence clock and finishes only on until == day.
    """
    _mark_done_on(task, day)
    scheduled = do_on_date(task.data)
    until = until_date(task.data)
    if scheduled is None:
        return bool(task.type in RECURRING_TYPES and until == day and day_complete(task.data, day))
    if until is not None and scheduled >= until:
        return True
    nxt = next_cadence_date(task.data, scheduled + timedelta(days=1))
    if nxt is None or (until is not None and nxt > until):
        if until is not None:
            return True
        return False
    task.data["do_on"] = nxt
    return False


def mark_series_today(root: Path, task: TaskFile, day: date) -> None:
    if task.type in RECURRING_TYPES and do_on_date(task.data) is not None:
        finished = _advance_do_on(task, day)
        if finished:
            _move_status(root, task, "completed")
        else:
            task.save()
        return
    _mark_done_on(task, day)
    until = until_date(task.data)
    if task.type in RECURRING_TYPES and until == day and day_complete(task.data, day):
        _move_status(root, task, "completed")
    else:
        task.save()


def start_recurring(root: Path, task: TaskFile, day: date) -> None:
    """First check begins the series, in any section, and advances do_on."""
    finished = _advance_do_on(task, day)
    if finished:
        _move_status(root, task, "completed")
        return
    task.data["status"] = "ongoing"
    task.save()
    old = task.folder
    if old != "ongoing":
        move_task(task, "ongoing", root)
        rewrite_task_links(root, task.slug, old, "ongoing")


def finish_recurring_until(root: Path, task: TaskFile) -> None:
    old = task.folder
    task.data["status"] = "completed"
    task.save()
    if old != "completed":
        move_task(task, "completed", root)
        rewrite_task_links(root, task.slug, old, "completed")


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _ongoing_check_allowed(task: TaskFile, section: str) -> bool:
    """Maintenance and a dateless live series count only in Today.

    A live recurring with do_on counts in any section: Today when the day
    is here, Overdue while catching up, and a later bucket when he does it
    early. Each check advances one scheduled occurrence.
    """
    if task.type not in SERIES_TYPES:
        return False
    if task.type in RECURRING_TYPES and do_on_date(task.data) is not None:
        return True
    return section == SECTION_TODAY


def collect_checked(root: Path) -> dict[str, list[str]]:
    """Slugs that a check pass would apply, without mutating files.

    Catch-up snapshots this before daily-close rewrites tasks.md.
    """
    report: dict[str, list[str]] = {
        "reverted": [],
        "unique": [],
        "recurring": [],
        "start": [],
    }
    tasks_md = root / "user" / "tasks" / "tasks.md"
    if not tasks_md.is_file():
        return report
    text = tasks_md.read_text(encoding="utf-8")
    for section, href, _line in parse_checked(text):
        folder, slug = folder_from_href(href)
        if not folder or not slug:
            continue
        task = load_by_slug(root, slug)
        if task is None:
            continue
        if folder == "ongoing":
            if _ongoing_check_allowed(task, section):
                report["recurring"].append(slug)
            else:
                report["reverted"].append(slug)
            continue
        if folder == "pending":
            if task.type in RECURRING_TYPES:
                report["start"].append(slug)
                continue
            if task.type in UNIQUE_TYPES:
                report["unique"].append(slug)
    for key in report:
        # Each stacked Overdue line is one occurrence. Do not collapse them.
        if key == "recurring":
            continue
        report[key] = _dedupe(report[key])
    return report


def apply_report(root: Path, report: dict[str, list[str]], today: date) -> None:
    """Apply a snapshotted check list. Does not rebuild the index."""
    for slug in report["unique"]:
        task = load_by_slug(root, slug)
        if task is None:
            continue
        complete_unique(root, task, today)
    for slug in report.get("start") or []:
        task = load_by_slug(root, slug)
        if task is None or task.type not in RECURRING_TYPES:
            continue
        start_recurring(root, task, today)
    for slug in report["recurring"]:
        task = load_by_slug(root, slug)
        if task is None:
            continue
        if task.status == "completed":
            continue
        mark_series_today(root, task, today)


def apply_collected(
    root: Path,
    report: dict[str, list[str]],
    today: date,
    *,
    commit: bool = True,
) -> dict[str, list[str]]:
    """Apply checks that were snapshotted before a rebuild wiped tasks.md.

    Catch-up uses this so the return day gets the credit, not the missed days.
    The rebuild does not read tasks.md again.
    """
    from .index import reindex

    apply_report(root, report, today)
    reindex(root, today, apply_checks=False, note_completed=True, commit=commit)
    return report
