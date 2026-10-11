"""Move one vault onto the YYYY-MM schedule and daily paths.

Idempotent: a second run leaves every file byte the same. A paused task
does not gain `do_on`. A date that lived only on a schedule day file is
appended under that task's `## When` when the file does not already name
the day.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from .config import daily_dir, schedule_dir, tasks_dir
from .daily import (
    closed_daily_dates,
    daily_path,
    ensure_placeholder,
    month_rollup_path,
    render_daily,
    tasks_score,
    write_month_rollup,
)
from .links import rewrite_layout_links
from .schedule import month_path
from .taskio import atomic_write

_YEAR = re.compile(r"^\d{4}$")
_MM = re.compile(r"^\d{2}$")
_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_RESULT = re.compile(r"\*\*Result:\*\*")
_BULLET = re.compile(r"^- \[(.*?)\]\((.*?)\)\s*$")


def migrate_layout(root: Path, today: date | None = None) -> list[str]:
    from .config import today as today_fn

    if today is None:
        today = today_fn(root)
    notes: list[str] = []
    targets, futures = _layout_maps(root)
    changed = rewrite_layout_links(root, targets, futures)
    notes.extend(f"link: {_rel(root, path)}" for path in changed)
    notes.extend(_migrate_dailies(root))
    notes.extend(_rename_grids(root))
    notes.extend(_consume_schedule_days(root))
    notes.extend(_remove_old_daily_rollups(root))
    placeholder = ensure_placeholder(root, today)
    notes.append(f"daily: {_rel(root, placeholder)}")
    months = {(when.year, when.month) for when in closed_daily_dates(root)}
    months.add((today.year, today.month))
    for year, month in sorted(months):
        path = write_month_rollup(root, date(year, month, 1))
        notes.append(f"month: {_rel(root, path)}")
    return notes


def _layout_maps(root: Path) -> tuple[dict[Path, Path], dict[Path, Path]]:
    """Link targets, and the post-move path of files that themselves move."""
    targets: dict[Path, Path] = {}
    futures: dict[Path, Path] = {}
    base = daily_dir(root)
    if base.is_dir():
        for year_dir in _year_dirs(base):
            year = int(year_dir.name)
            for path in year_dir.glob("*.md"):
                if not _MM.match(path.stem):
                    continue
                month = int(path.stem)
                if not 1 <= month <= 12:
                    continue
                dest = month_rollup_path(root, date(year, month, 1)).resolve()
                targets[path.resolve()] = dest
                futures[path.resolve()] = dest
            for month_dir in _month_dirs(year_dir):
                month = int(month_dir.name)
                for src in month_dir.glob("*.md"):
                    if not _MM.match(src.stem):
                        continue
                    try:
                        when = date(year, month, int(src.stem))
                    except ValueError:
                        continue
                    dest = daily_path(root, when).resolve()
                    targets[src.resolve()] = dest
                    futures[src.resolve()] = dest
    sched = schedule_dir(root)
    if sched.is_dir():
        for year_dir in _year_dirs(sched):
            year = int(year_dir.name)
            for path in year_dir.glob("*.md"):
                if not _MM.match(path.stem):
                    continue
                month = int(path.stem)
                if not 1 <= month <= 12:
                    continue
                dest = month_path(root, year, month).resolve()
                targets[path.resolve()] = dest
                futures[path.resolve()] = dest
            for month_dir in _month_dirs(year_dir):
                month = int(month_dir.name)
                dest = month_path(root, year, month).resolve()
                for src in month_dir.glob("*.md"):
                    if not _MM.match(src.stem):
                        continue
                    try:
                        date(year, month, int(src.stem))
                    except ValueError:
                        continue
                    targets[src.resolve()] = dest
    return targets, futures


def _migrate_dailies(root: Path) -> list[str]:
    notes: list[str] = []
    base = daily_dir(root)
    if not base.is_dir():
        return notes
    sources: list[tuple[Path, date]] = []
    for year_dir in _year_dirs(base):
        year = int(year_dir.name)
        for month_dir in _month_dirs(year_dir):
            month = int(month_dir.name)
            for src in sorted(month_dir.glob("*.md")):
                if not _MM.match(src.stem):
                    notes.append(f"kept: {_rel(root, src)}")
                    continue
                try:
                    when = date(year, month, int(src.stem))
                except ValueError:
                    notes.append(f"kept: {_rel(root, src)}")
                    continue
                sources.append((src, when))
    for src, when in sources:
        dest = daily_path(root, when)
        original = src.read_text(encoding="utf-8")
        converted = _convert_daily(original, when)
        if not dest.exists():
            atomic_write(dest, converted)
            src.unlink()
            notes.append(f"daily-move: {_rel(root, dest)}")
            continue
        current = dest.read_text(encoding="utf-8")
        both_new = "| hour | did |" in current and "| hour | did |" in original
        if current == converted or both_new:
            src.unlink()
            notes.append(f"daily-drop: {_rel(root, src)}")
        else:
            notes.append(f"kept: {_rel(root, src)}")
    for year_dir in _year_dirs(base):
        for month_dir in _month_dirs(year_dir):
            _rmdir_if_empty(month_dir)
    return notes


def _convert_daily(text: str, when: date) -> str:
    if "| hour | did |" in text:
        return text if text.endswith("\n") else text + "\n"
    completed, failed = _task_lists(text)
    planned = [(href, True) for _title, href in completed]
    planned += [(href, False) for _title, href in failed]
    notes = _legacy_notes(text)
    return render_daily(when, {}, "null", tasks_score(planned), completed, failed, notes)


def _task_lists(text: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    completed: list[tuple[str, str]] = []
    failed: list[tuple[str, str]] = []
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        match = _BULLET.match(line.strip())
        if not match:
            continue
        row = (match.group(1), match.group(2))
        if current == "Completed tasks":
            completed.append(row)
        elif current == "Failed tasks":
            failed.append(row)
    return completed, failed


def _legacy_notes(text: str) -> str | None:
    results: list[str] = []
    other: list[str] = []
    current: str | None = None
    skipping = False
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            skipping = current in {"Completed tasks", "Failed tasks"}
            if not skipping:
                other.append(line)
            continue
        if skipping:
            if line.strip() and _BULLET.match(line.strip()) is None:
                other.append(line)
            continue
        if current is None and line.startswith("# "):
            continue
        if current is None and _RESULT.search(line):
            results.append(line.strip())
            continue
        if current is None and not line.strip():
            continue
        other.append(line)
    chunks: list[str] = []
    if results:
        chunks.append("\n".join(results))
    extra = "\n".join(other).strip()
    if extra:
        chunks.append(extra)
    if not chunks:
        return None
    return "\n\n".join(chunks) + "\n"


def _rename_grids(root: Path) -> list[str]:
    notes: list[str] = []
    base = schedule_dir(root)
    if not base.is_dir():
        return notes
    for year_dir in _year_dirs(base):
        for src in sorted(year_dir.glob("*.md")):
            if not _MM.match(src.stem):
                continue
            month = int(src.stem)
            if not 1 <= month <= 12:
                notes.append(f"kept: {_rel(root, src)}")
                continue
            dest = month_path(root, int(year_dir.name), month)
            if not dest.exists():
                src.rename(dest)
                notes.append(f"schedule: {_rel(root, dest)}")
            elif dest.read_bytes() == src.read_bytes():
                src.unlink()
                notes.append(f"schedule-drop: {_rel(root, src)}")
            else:
                notes.append(f"kept: {_rel(root, src)}")
    return notes


def _consume_schedule_days(root: Path) -> list[str]:
    notes: list[str] = []
    base = schedule_dir(root)
    if not base.is_dir():
        return notes
    for year_dir in _year_dirs(base):
        year = int(year_dir.name)
        for month_dir in _month_dirs(year_dir):
            month = int(month_dir.name)
            for src in sorted(month_dir.glob("*.md")):
                if not _MM.match(src.stem):
                    notes.append(f"kept: {_rel(root, src)}")
                    continue
                try:
                    when = date(year, month, int(src.stem))
                except ValueError:
                    notes.append(f"kept: {_rel(root, src)}")
                    continue
                if _preserve_day(src, when, root):
                    src.unlink()
                    notes.append(f"schedule-day: {when.isoformat()}")
                else:
                    notes.append(f"kept: {_rel(root, src)}")
            _rmdir_if_empty(month_dir)
        _rmdir_if_empty(year_dir)
    return notes


def _preserve_day(path: Path, when: date, root: Path) -> bool:
    """Record `when` on each linked task. False when a line would be lost."""
    text = path.read_text(encoding="utf-8")
    targets: list[Path] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("# "):
            continue
        hrefs = _LINK.findall(line)
        if not hrefs:
            return False
        for href in hrefs:
            target = _resolve_task(path, href, root)
            if target is None:
                return False
            targets.append(target)
    seen: set[Path] = set()
    for target in targets:
        if target in seen:
            continue
        seen.add(target)
        body = target.read_text(encoding="utf-8")
        updated = _append_when(body, when)
        if updated != body:
            target.write_text(updated, encoding="utf-8")
    return True


def _resolve_task(day_file: Path, href: str, root: Path) -> Path | None:
    raw = href.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    raw = raw.split("#", 1)[0].split("?", 1)[0].strip()
    if not raw or "://" in raw:
        return None
    candidate = (day_file.parent / raw).resolve()
    tasks = tasks_dir(root).resolve()
    try:
        rel = candidate.relative_to(tasks)
    except ValueError:
        return None
    if len(rel.parts) != 2 or not candidate.is_file():
        return None
    return candidate


def _mentions_date(text: str, when: date) -> bool:
    if when.isoformat() in text:
        return True
    patterns = (
        rf"(?<!\d){when.day}/{when.month}/{when.year}(?!\d)",
        rf"(?<!\d){when.day:02d}/{when.month:02d}/{when.year}(?!\d)",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _append_when(text: str, when: date) -> str:
    if _mentions_date(text, when):
        return text
    line = when.isoformat()
    lines = text.splitlines()
    start = next((i for i, row in enumerate(lines) if row.strip() == "## When"), None)
    if start is None:
        return text.rstrip() + "\n\n## When\n\n" + line + "\n"
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    insert_at = end
    while insert_at > start + 1 and lines[insert_at - 1].strip() == "":
        insert_at -= 1
    lines.insert(insert_at, line)
    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    return out


def _remove_old_daily_rollups(root: Path) -> list[str]:
    notes: list[str] = []
    base = daily_dir(root)
    if not base.is_dir():
        return notes
    for year_dir in _year_dirs(base):
        for path in sorted(year_dir.glob("*.md")):
            if not _MM.match(path.stem):
                continue
            month = int(path.stem)
            if not 1 <= month <= 12:
                continue
            path.unlink()
            notes.append(f"daily-rollup-drop: {_rel(root, path)}")
    return notes


def _year_dirs(base: Path) -> list[Path]:
    return sorted(path for path in base.iterdir() if path.is_dir() and _YEAR.match(path.name))


def _month_dirs(year_dir: Path) -> list[Path]:
    return sorted(
        path for path in year_dir.iterdir() if path.is_dir() and _MM.match(path.name)
    )


def _rmdir_if_empty(path: Path) -> None:
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
