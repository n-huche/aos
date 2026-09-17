from __future__ import annotations

from pathlib import Path

from .config import TASK_FOLDERS, user_dir


def rewrite_task_links(root: Path, slug: str, old_folder: str, new_folder: str) -> None:
    if old_folder == new_folder:
        return
    old = f"{old_folder}/{slug}.md"
    new = f"{new_folder}/{slug}.md"
    base = user_dir(root)
    if not base.is_dir():
        return
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if old not in text:
            continue
        path.write_text(text.replace(old, new), encoding="utf-8")


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
