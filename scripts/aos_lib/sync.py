from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from .cadence import until_date
from .config import RECURRING_TYPES, SECTION_TODAY, today as today_fn
from .gitutil import commit_user, push_if_origin
from .index import reindex
from .links import folder_from_href, rewrite_task_links
from .taskio import TaskFile, load_by_slug, move_task
from .yamlfm import as_date_list

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
ITEM_RE = re.compile(
    r"^(\s*-\s*\[)([xX ])(\]\s+\[[^\]]*\]\s*\()([^\)]+)(\)\s*)$"
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


def _append_done_on(task: TaskFile, day: date) -> None:
    existing = as_date_list(task.data.get("done_on") or [])
    if day not in existing:
        existing.append(day)
        existing.sort()
    task.data["done_on"] = existing


def complete_unique(root: Path, task: TaskFile, day: date) -> None:
    old = task.folder
    task.data["status"] = "completed"
    task.data["completed_on"] = day
    task.save()
    if old != "completed":
        move_task(task, "completed", root)
        rewrite_task_links(root, task.slug, old, "completed")


def mark_recurring_today(root: Path, task: TaskFile, day: date) -> None:
    _append_done_on(task, day)
    until = until_date(task.data)
    if until == day:
        task.data["status"] = "completed"
        task.save()
        old = task.folder
        if old != "completed":
            move_task(task, "completed", root)
            rewrite_task_links(root, task.slug, old, "completed")
    else:
        task.save()


def finish_recurring_until(root: Path, task: TaskFile) -> None:
    old = task.folder
    task.data["status"] = "completed"
    task.save()
    if old != "completed":
        move_task(task, "completed", root)
        rewrite_task_links(root, task.slug, old, "completed")


def collect_checked(root: Path) -> dict[str, list[str]]:
    """Slugs that sync() would apply, without mutating files.

    Catch-up snapshots this before daily-close rewrites tasks.md.
    """
    report: dict[str, list[str]] = {
        "reverted": [],
        "unique": [],
        "recurring": [],
    }
    tasks_md = root / "user" / "tasks" / "tasks.md"
    if not tasks_md.is_file():
        return report
    text = tasks_md.read_text(encoding="utf-8")
    for section, href, _line in parse_checked(text):
        folder, slug = folder_from_href(href)
        if not folder or not slug:
            continue
        if folder == "recurring" and section != SECTION_TODAY:
            report["reverted"].append(slug)
            continue
        task = load_by_slug(root, slug)
        if task is None:
            continue
        if folder == "recurring" and section == SECTION_TODAY:
            if task.type not in RECURRING_TYPES and task.folder != "recurring":
                continue
            report["recurring"].append(slug)
            continue
        if folder == "pending":
            report["unique"].append(slug)
    return report


def apply_collected(
    root: Path,
    report: dict[str, list[str]],
    today: date,
    *,
    commit: bool = True,
) -> dict[str, list[str]]:
    for slug in report["unique"]:
        task = load_by_slug(root, slug)
        if task is None:
            continue
        complete_unique(root, task, today)
    for slug in report["recurring"]:
        task = load_by_slug(root, slug)
        if task is None:
            continue
        mark_recurring_today(root, task, today)
    reindex(root, today)
    if commit and any(report.values()):
        if commit_user(root, "aos: sync tasks"):
            push_if_origin(root)
    return report


def sync(root: Path, today: date | None = None, *, commit: bool = True) -> dict[str, list[str]]:
    if today is None:
        today = today_fn(root)
    report = collect_checked(root)
    return apply_collected(root, report, today, commit=commit)
