from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from .config import TASK_FOLDERS, tasks_dir
from .yamlfm import join_frontmatter, split_frontmatter


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


@dataclass
class TaskFile:
    path: Path
    folder: str
    data: dict[str, Any]
    body: str

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def type(self) -> str:
        return str(self.data.get("type") or "").strip()

    @property
    def status(self) -> str:
        return str(self.data.get("status") or "").strip()

    @property
    def title(self) -> str:
        for line in self.body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
        return self.slug

    def save(self) -> None:
        atomic_write(self.path, join_frontmatter(self.data, self.body))


def load_task(path: Path, folder: str) -> TaskFile:
    text = path.read_text(encoding="utf-8")
    data, body = split_frontmatter(text)
    return TaskFile(path=path, folder=folder, data=data, body=body)


def iter_task_files(root: Path) -> Iterator[TaskFile]:
    base = tasks_dir(root)
    for folder in TASK_FOLDERS:
        d = base / folder
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            yield load_task(path, folder)


def load_by_slug(root: Path, slug: str) -> TaskFile | None:
    base = tasks_dir(root)
    for folder in TASK_FOLDERS:
        path = base / folder / f"{slug}.md"
        if path.is_file():
            return load_task(path, folder)
    return None


def task_path(root: Path, folder: str, slug: str) -> Path:
    return tasks_dir(root) / folder / f"{slug}.md"


def move_task(task: TaskFile, new_folder: str, root: Path) -> TaskFile:
    dest = task_path(root, new_folder, task.slug)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if task.path.resolve() != dest.resolve():
        task.path.replace(dest)
    task.path = dest
    task.folder = new_folder
    return task
