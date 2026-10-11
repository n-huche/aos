from __future__ import annotations

import os
import re
from pathlib import Path

from .config import TASK_FOLDERS, schedule_dir, user_dir

_DAILY_DAY = re.compile(r"daily/(\d{4})/(\d{2})/(\d{2})\.md")
_SCHED_DAY = re.compile(r"schedule/(\d{4})/(\d{2})/(\d{2})\.md")
_DAILY_MONTH = re.compile(r"daily/(\d{4})/(\d{2})\.md")
_SCHED_MONTH = re.compile(r"schedule/(\d{4})/(\d{2})\.md")
_MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def rewrite_task_links(root: Path, slug: str, old_folder: str, new_folder: str) -> None:
    if old_folder == new_folder:
        return
    old = f"{old_folder}/{slug}.md"
    new = f"{new_folder}/{slug}.md"
    base = user_dir(root)
    if not base.is_dir():
        return
    sched = schedule_dir(root)
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".md":
            continue
        if sched.is_dir():
            try:
                path.resolve().relative_to(sched.resolve())
                continue
            except ValueError:
                pass
        text = path.read_text(encoding="utf-8")
        if old not in text:
            continue
        path.write_text(text.replace(old, new), encoding="utf-8")


def rewrite_layout_links(
    root: Path,
    targets: dict[Path, Path] | None = None,
    futures: dict[Path, Path] | None = None,
) -> list[Path]:
    """Point vault links at the YYYY-MM layout.

    `targets` maps a file that still exists at the old path to the path it
    will have (a schedule day file maps to the month grid). `futures` maps
    a file that itself moves, so relative links are written from there.
    """
    targets = targets or {}
    futures = futures or {}
    base = user_dir(root)
    changed: list[Path] = []
    if not base.is_dir():
        return changed
    for path in sorted(base.rglob("*.md")):
        if not path.is_file():
            continue
        resolved = path.resolve()
        future = futures.get(resolved, resolved)
        text = path.read_text(encoding="utf-8")
        updated = _rewrite_layout_text(text, resolved, future, targets)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
    return changed


def _rewrite_layout_text(
    text: str,
    source: Path,
    future: Path,
    targets: dict[Path, Path],
) -> str:
    def repl_link(match: re.Match[str]) -> str:
        label, href = match.group(1), match.group(2)
        updated = _map_href(href, source, future, targets)
        if updated is None or updated == href:
            return match.group(0)
        return f"[{label}]({updated})"

    text = _MD_LINK.sub(repl_link, text)
    text = _DAILY_DAY.sub(_daily_day, text)
    text = _SCHED_DAY.sub(_sched_day, text)
    text = _DAILY_MONTH.sub(_daily_month, text)
    text = _SCHED_MONTH.sub(_sched_month, text)
    return text


def _map_href(
    href: str,
    source: Path,
    future: Path,
    targets: dict[Path, Path],
) -> str | None:
    raw = href.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    suffix = ""
    base = raw
    for mark in ("#", "?"):
        if mark in base:
            base, extra = base.split(mark, 1)
            suffix = mark + extra + suffix
    if not base or "://" in base or base.startswith("mailto:"):
        return None
    resolved = (source.parent / base).resolve()
    target = targets.get(resolved)
    if target is None:
        return None
    return Path(os.path.relpath(target, start=future.parent)).as_posix() + suffix


def _daily_day(match: re.Match[str]) -> str:
    year, month, day = match.group(1), match.group(2), match.group(3)
    return f"daily/{year}/{year}-{month}/{year}-{month}-{day}.md"


def _sched_day(match: re.Match[str]) -> str:
    year, month, _day = match.group(1), match.group(2), match.group(3)
    return f"schedule/{year}/{year}-{month}.md"


def _daily_month(match: re.Match[str]) -> str:
    year, month = match.group(1), match.group(2)
    return f"daily/{year}/{year}-{month}/{year}-{month}.md"


def _sched_month(match: re.Match[str]) -> str:
    year, month = match.group(1), match.group(2)
    return f"schedule/{year}/{year}-{month}.md"


def folder_from_href(href: str) -> tuple[str | None, str | None]:
    href = href.strip()
    if href.startswith("<") and href.endswith(">"):
        href = href[1:-1]
    href = href.split("#", 1)[0].split("?", 1)[0]
    parts = Path(href).parts
    if not parts:
        return None, None
    name = parts[-1]
    if not name.endswith(".md"):
        return None, None
    slug = name[:-3]
    folder = None
    if len(parts) >= 2 and parts[-2] in TASK_FOLDERS:
        folder = parts[-2]
    return folder, slug
