from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

from .cadence import done_on_set, occurs_on, until_date
from .config import RECURRING_TYPES, UNIQUE_TYPES, daily_dir, schedule_dir
from .gitutil import commit_user, push_if_origin
from .index import reindex
from .sync import finish_recurring_until
from .taskio import atomic_write, iter_task_files
from .yamlfm import as_date

NOTES_RE = re.compile(r"^##\s+Notes.*$", re.M)


def schedule_date_from_path(path: Path, schedule_root: Path) -> date | None:
    try:
        rel = path.relative_to(schedule_root)
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


def delete_past_schedule(root: Path, d: date) -> list[Path]:
    base = schedule_dir(root)
    removed: list[Path] = []
    if not base.is_dir():
        return removed
    for path in list(base.rglob("*.md")):
        if path.name == "constraints.md":
            continue
        when = schedule_date_from_path(path, base)
        if when is None:
            continue
        if when <= d:
            path.unlink()
            removed.append(path)
            _prune_empty_parents(path.parent, base)
    return removed


def _prune_empty_parents(start: Path, stop: Path) -> None:
    cur = start
    while cur != stop and cur.is_dir():
        try:
            next(cur.iterdir())
            break
        except StopIteration:
            parent = cur.parent
            cur.rmdir()
            cur = parent


def extract_notes(text: str) -> str | None:
    m = NOTES_RE.search(text)
    if not m:
        return None
    return text[m.start():].rstrip() + "\n"


def daily_sets(text: str) -> tuple[set[str], set[str], str | None]:
    """Parse completed and failed hrefs from an existing daily file."""
    completed: set[str] = set()
    failed: set[str] = set()
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if line.startswith("- ["):
            href = ""
            if "](" in line and line.endswith(")"):
                href = line.rsplit("](", 1)[-1][:-1]
            if section.startswith("Completed tasks"):
                completed.add(href)
            elif section.startswith("Failed tasks"):
                failed.add(href)
    result = None
    for line in text.splitlines():
        if line.startswith("**Result:**"):
            result = line.split(":", 1)[-1].strip()
            break
    return completed, failed, result


def _href_for(task_folder: str, slug: str) -> str:
    return f"../tasks/{task_folder}/{slug}.md"


def collect_daily(root: Path, d: date) -> tuple[list[tuple[str, str]], list[tuple[str, str]], bool]:
    """Returns (completed items, failed items, had_early_unique).

    Item is (title, href). had_early_unique: unique completed_on==D with due date != D.
    """
    completed: list[tuple[str, str]] = []
    failed: list[tuple[str, str]] = []
    early = False
    for task in list(iter_task_files(root)):
        t = task.type
        if t in UNIQUE_TYPES:
            completed_on = as_date(task.data.get("completed_on"))
            due = as_date(task.data.get("due"))
            if completed_on == d:
                href = _href_for(task.folder, task.slug)
                completed.append((task.title, href))
                if due is not None and due != d:
                    early = True
            elif task.folder == "pending" and due is not None and due <= d:
                failed.append((task.title, _href_for("pending", task.slug)))
            continue
        if t not in RECURRING_TYPES:
            continue
        if task.folder in {"canceled", "obsolete"}:
            continue
        until = until_date(task.data)
        done = d in done_on_set(task.data)
        if until == d:
            if task.folder == "recurring":
                finish_recurring_until(root, task)
                folder = "completed"
            else:
                folder = task.folder
            if done:
                completed.append((task.title, _href_for(folder, task.slug)))
            else:
                failed.append((task.title, _href_for(folder, task.slug)))
            continue
        if not occurs_on(task.data, d):
            continue
        if done:
            completed.append((task.title, _href_for(task.folder, task.slug)))
        else:
            failed.append((task.title, _href_for(task.folder, task.slug)))
    completed.sort(key=lambda x: x[0].lower())
    failed.sort(key=lambda x: x[0].lower())
    return completed, failed, early


def result_of(completed: list[tuple[str, str]], failed: list[tuple[str, str]], early: bool) -> str:
    if failed:
        return "failure"
    if early:
        return "success"
    return "satisfactory"


def render_daily(
    d: date,
    result: str,
    completed: list[tuple[str, str]],
    failed: list[tuple[str, str]],
    notes: str | None = None,
) -> str:
    lines = [
        f"# {d.isoformat()}",
        "",
        f"**Result:** {result}",
        "",
        "## Completed tasks",
        "",
    ]
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
    text = "\n".join(lines).rstrip() + "\n"
    return text


def write_daily(
    root: Path,
    d: date,
    completed: list[tuple[str, str]],
    failed: list[tuple[str, str]],
    early: bool,
) -> Path:
    result = result_of(completed, failed, early)
    path = daily_dir(root) / f"{d.isoformat()}.md"
    notes = None
    if path.is_file():
        old = path.read_text(encoding="utf-8")
        old_c, old_f, old_r = daily_sets(old)
        new_c = {href for _t, href in completed}
        new_f = {href for _t, href in failed}
        if old_c == new_c and old_f == new_f and old_r == result:
            return path
        notes = extract_notes(old)
    text = render_daily(d, result, completed, failed, notes)
    atomic_write(path, text)
    return path


def daily_close(
    root: Path,
    d: date | None = None,
    *,
    today: date | None = None,
    commit: bool = True,
) -> Path:
    from .config import today as today_fn

    if today is None:
        today = today_fn(root)
    if d is None:
        d = today - timedelta(days=1)
    completed, failed, early = collect_daily(root, d)
    path = write_daily(root, d, completed, failed, early)
    delete_past_schedule(root, d)
    reindex(root, d + timedelta(days=1))
    if commit:
        if commit_user(root, f"aos: daily-close {d.isoformat()}"):
            push_if_origin(root)
    return path


def list_daily_dates(root: Path) -> list[date]:
    base = daily_dir(root)
    found: list[date] = []
    if not base.is_dir():
        return found
    for path in base.glob("*.md"):
        try:
            found.append(date.fromisoformat(path.stem))
        except ValueError:
            continue
    found.sort()
    return found


def missing_close_dates(root: Path, today: date) -> list[date]:
    """Days that still need daily-close: after the last daily, through yesterday.

    With no daily yet, only yesterday — not the whole calendar.
    """
    yesterday = today - timedelta(days=1)
    existing = list_daily_dates(root)
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
    applied = len(leftover["unique"]) + len(leftover["recurring"])
    if applied:
        apply_collected(root, leftover, today, commit=commit)
        actions.append(f"catch-up-sync:{today.isoformat()}:{applied}")
    else:
        actions.append("catch-up-sync:none")
    return actions
