"""Move tasks and hubs to the folder their dates and children require.

Runs from reindex and daily-close so a date edit is
visible without a separate checkbox pass.
"""

from __future__ import annotations

from pathlib import Path

from .cadence import do_on_date
from .config import (
    PROJECT_STATUSES,
    RECURRING_TYPES,
    UNIQUE_TYPES,
    projects_dir,
)
from .links import rewrite_task_links
from .taskio import TaskFile, iter_task_files, move_task
from .yamlfm import join_frontmatter, split_frontmatter


def derived_status(statuses: list[str]) -> str:
    """Project/phase status from the statuses of its tasks.

    `canceled` here is the project outcome. Callers map that to `obsolete`
    for a phase. `completed` and `canceled` hubs are sticky and are not
    passed through this function.
    """
    live = [status for status in statuses if status not in {"canceled", "obsolete"}]
    if not statuses or not live:
        return "canceled"
    if "ongoing" in live:
        return "ongoing"
    if set(live) == {"paused"}:
        return "paused"
    if "completed" not in live:
        return "pending"
    if "pending" not in live and "paused" not in live:
        return "completed"
    return "ongoing"


def reconcile_all(root: Path) -> None:
    _reconcile_tasks(root)
    _reconcile_projects(root)


def _place(root: Path, task: TaskFile, folder: str) -> None:
    if task.status != folder:
        task.data["status"] = folder
        task.save()
    if task.folder != folder:
        old = task.folder
        move_task(task, folder, root)
        rewrite_task_links(root, task.slug, old, folder)


def _reconcile_tasks(root: Path) -> None:
    for task in list(iter_task_files(root)):
        if task.type in UNIQUE_TYPES:
            if task.status in {"completed", "obsolete", "canceled"}:
                continue
            _place(root, task, "pending" if do_on_date(task.data) else "paused")
            continue
        if task.type in RECURRING_TYPES:
            if task.status in {"ongoing", "completed", "obsolete", "canceled"}:
                continue
            _place(root, task, "pending" if do_on_date(task.data) else "paused")
            continue
        if task.type == "maintenance":
            if task.status == "paused":
                _place(root, task, "paused")
            elif task.status == "canceled":
                _place(root, task, "canceled")
            elif task.status == "ongoing":
                _place(root, task, "ongoing")


def _tasks_for(root: Path, project: str, phase: str | None = None) -> list[TaskFile]:
    found: list[TaskFile] = []
    for task in iter_task_files(root):
        if str(task.data.get("project") or "").strip() != project:
            continue
        if phase is not None and str(task.data.get("phase") or "").strip() != phase:
            continue
        found.append(task)
    return found


def _write_status(path: Path, status: str) -> None:
    data, body = split_frontmatter(path.read_text(encoding="utf-8"))
    if str(data.get("status") or "").strip() == status:
        return
    data["status"] = status
    path.write_text(join_frontmatter(data, body), encoding="utf-8")


def _rewrite_project_links(root: Path, slug: str, old: str, new: str) -> None:
    if old == new:
        return
    old_s = f"projects/{old}/{slug}"
    new_s = f"projects/{new}/{slug}"
    base = root / "user"
    if not base.is_dir():
        return
    for path in base.rglob("*.md"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if old_s not in text:
            continue
        path.write_text(text.replace(old_s, new_s), encoding="utf-8")


def _reconcile_projects(root: Path) -> None:
    base = projects_dir(root)
    if not base.is_dir():
        return
    found: list[tuple[str, Path]] = []
    for status in PROJECT_STATUSES:
        directory = base / status
        if not directory.is_dir():
            continue
        for proj in sorted(p for p in directory.iterdir() if p.is_dir()):
            found.append((status, proj))
    for status, proj in found:
        slug = proj.name
        hub = proj / f"{slug}.md"
        if not hub.is_file():
            continue
        _reconcile_phases(root, slug, proj)
        if status in {"completed", "canceled"}:
            continue
        statuses = [task.status for task in _tasks_for(root, slug)]
        new = derived_status(statuses)
        if new == status:
            _write_status(hub, new)
            continue
        _write_status(hub, new)
        dest_dir = base / new / slug
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        if dest_dir.exists():
            continue
        proj.rename(dest_dir)
        _rewrite_project_links(root, slug, status, new)


def _reconcile_phases(root: Path, project: str, proj: Path) -> None:
    phases = proj / "phases"
    if not phases.is_dir():
        return
    for phase_path in sorted(phases.glob("*.md")):
        data, _body = split_frontmatter(phase_path.read_text(encoding="utf-8"))
        current = str(data.get("status") or "").strip()
        if current in {"completed", "obsolete"}:
            continue
        statuses = [
            task.status for task in _tasks_for(root, project, phase_path.stem)
        ]
        new = derived_status(statuses)
        if new == "canceled":
            new = "obsolete"
        if new != current:
            _write_status(phase_path, new)
