from __future__ import annotations

from pathlib import Path

from .config import TASK_FOLDERS, schedule_dir, user_dir


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


def drop_from_schedule(root: Path, slug: str) -> None:
    """Remove the unique from every schedule day. Delete the day file if empty of links."""
    base = schedule_dir(root)
    if not base.is_dir():
        return
    needle = f"/{slug}.md"
    for path in list(base.rglob("*.md")):
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        kept: list[str] = []
        removed = False
        has_link = False
        for line in lines:
            stripped = line.strip().replace("\\", "/")
            is_item = stripped.startswith("- ") and "](" in stripped
            if is_item and needle in stripped:
                removed = True
                continue
            if is_item:
                has_link = True
            kept.append(line)
        if not removed:
            continue
        if not has_link:
            path.unlink()
            _prune_empty_parents(path.parent, base)
            continue
        text = "".join(kept)
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")


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
