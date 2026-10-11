"""Migrate one vault from due/do_in/do_after onto do_on, do_at, and paused.

Generic: it reads whatever is in the vault at run time. A second run does
not change file bytes. `--dry-run` prints the path diff and writes nothing.

Pending unique and recurring tasks lose their date and clock and move to
`tasks/paused/`. Maintenance stays where it is. Completed and canceled
tasks stay; `due` is renamed to `do_on`. A `do_in` or `do_after` that is
a clock becomes `do_at`. A `do_after` that names another task is removed.
Project and phase `due` is renamed to `do_on` and kept as history. Their
status is derived from the tasks. Then the YYYY-MM schedule and daily
layout is applied.
"""

from __future__ import annotations

import filecmp
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path

from .config import (
    RECURRING_TYPES,
    UNIQUE_TYPES,
    projects_dir,
    tasks_dir,
    user_dir,
)
from .layout import migrate_layout
from .reconcile import derived_status
from .yamlfm import split_frontmatter

_CLOCK = re.compile(r"^(\d{1,2}):(\d{2})$")
_DROP_KEYS = frozenset({"do_in", "do_after", "do_between"})


def migrate_vault(
    root: Path,
    today: date | None = None,
    *,
    dry_run: bool = False,
) -> list[str]:
    from .config import today as today_fn

    if today is None:
        today = today_fn(root)
    if dry_run:
        return _dry_run(root, today)
    notes = _apply(root, today)
    return notes


def _dry_run(root: Path, today: date) -> list[str]:
    base = user_dir(root)
    if not base.is_dir():
        return ["dry-run: no user/"]
    with tempfile.TemporaryDirectory() as tmp:
        copy_root = Path(tmp) / "root"
        shutil.copytree(base, copy_root / "user")
        _apply(copy_root, today)
        lines = ["dry-run:"]
        lines.extend(_path_diff(base, copy_root / "user"))
        if len(lines) == 1:
            lines.append("unchanged")
        return lines


def _apply(root: Path, today: date) -> list[str]:
    from .index import reindex

    notes: list[str] = []
    notes.extend(_migrate_tasks(root))
    notes.extend(_migrate_projects(root))
    reindex(root, today)
    notes.append("reindex")
    notes.extend(migrate_layout(root, today))
    return notes


def _migrate_tasks(root: Path) -> list[str]:
    notes: list[str] = []
    base = tasks_dir(root)
    if not base.is_dir():
        return notes
    moves: list[tuple[Path, str]] = []
    for folder in ("pending", "ongoing", "paused", "completed", "obsolete", "canceled"):
        directory = base / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            data, _body = split_frontmatter(text)
            kind = str(data.get("type") or "").strip()
            status = str(data.get("status") or "").strip()
            drop_dates = kind in UNIQUE_TYPES | RECURRING_TYPES and (
                status == "pending" or folder == "pending"
            )
            updated = _rewrite_task_frontmatter(text, drop_dates=drop_dates)
            if updated != text:
                path.write_text(updated, encoding="utf-8")
                notes.append(f"task: {_rel(root, path)}")
            if drop_dates and folder != "paused":
                moves.append((path, path.stem))
    paused = base / "paused"
    for path, slug in moves:
        paused.mkdir(parents=True, exist_ok=True)
        dest = paused / path.name
        if dest.exists():
            notes.append(f"kept: {_rel(root, path)}")
            continue
        path.rename(dest)
        _replace_in_user(root, f"pending/{slug}.md", f"paused/{slug}.md")
        notes.append(f"pause: tasks/paused/{slug}.md")
    pending = base / "pending"
    if pending.is_dir() and not any(pending.iterdir()):
        pending.rmdir()
    return notes


def _migrate_projects(root: Path) -> list[str]:
    notes: list[str] = []
    base = projects_dir(root)
    if not base.is_dir():
        return notes
    hubs: list[tuple[str, Path]] = []
    for status_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        for proj in sorted(p for p in status_dir.iterdir() if p.is_dir()):
            hubs.append((status_dir.name, proj))
    hubs.sort(key=lambda item: len(item[1].name), reverse=True)
    for status, proj in hubs:
        _rename_due_tree(proj)
        _derive_phases(root, proj)
        if status in {"completed", "canceled"}:
            continue
        slug = proj.name
        statuses = _task_statuses(root, slug)
        new = derived_status(statuses)
        hub = proj / f"{slug}.md"
        if hub.is_file():
            _set_status_line(hub, new)
        if new == status:
            continue
        dest = base / new / slug
        if dest.exists():
            notes.append(f"kept: {_rel(root, proj)}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        proj.rename(dest)
        _replace_in_user(root, f"projects/{status}/{slug}", f"projects/{new}/{slug}")
        notes.append(f"project: projects/{new}/{slug}")
        if status_dir_empty(base / status):
            (base / status).rmdir()
    return notes


def status_dir_empty(path: Path) -> bool:
    return path.is_dir() and not any(path.iterdir())


def _derive_phases(root: Path, proj: Path) -> None:
    phases = proj / "phases"
    if not phases.is_dir():
        return
    slug = proj.name
    for phase_path in sorted(phases.glob("*.md")):
        data, _body = split_frontmatter(phase_path.read_text(encoding="utf-8"))
        current = str(data.get("status") or "").strip()
        if current in {"completed", "obsolete"}:
            continue
        statuses = _task_statuses(root, slug, phase_path.stem)
        new = derived_status(statuses)
        if new == "canceled":
            new = "obsolete"
        if new != current:
            _set_status_line(phase_path, new)


def _task_statuses(root: Path, project: str, phase: str | None = None) -> list[str]:
    from .taskio import iter_task_files

    found: list[str] = []
    for task in iter_task_files(root):
        if str(task.data.get("project") or "").strip() != project:
            continue
        if phase is not None and str(task.data.get("phase") or "").strip() != phase:
            continue
        found.append(task.status)
    return found


def _rename_due_tree(proj: Path) -> None:
    for path in sorted(proj.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        updated = _rename_due(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def _rename_due(text: str) -> str:
    split = _split_raw(text)
    if split is None:
        return text
    fm, body = split
    lines = []
    for line in fm.split("\n"):
        if line.startswith("due:"):
            line = "do_on:" + line[len("due:") :]
        lines.append(line)
    return _join_raw("\n".join(lines), body)


def _rewrite_task_frontmatter(text: str, *, drop_dates: bool) -> str:
    split = _split_raw(text)
    if split is None:
        return text
    fm, body = split
    clocks: list[str] = []
    out: list[str] = []
    for line in fm.split("\n"):
        if line.startswith((" ", "\t")) or ":" not in line:
            out.append(line)
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if key in _DROP_KEYS:
            found = _clocks(raw)
            if found:
                clocks.extend(found)
            continue
        if key in {"due", "do_on", "do_at"} and drop_dates:
            continue
        if key == "status" and drop_dates:
            out.append("status: paused")
            continue
        if key == "due" and not drop_dates:
            out.append("do_on:" + line[len("due:") :])
            continue
        if key == "do_at" and not drop_dates:
            clocks = _clocks(raw) + [c for c in clocks if c not in _clocks(raw)]
            continue
        out.append(line)
    if clocks and not drop_dates:
        rendered = ", ".join(f'"{clock}"' for clock in _unique(clocks))
        out.append(f"do_at: [{rendered}]")
    return _join_raw("\n".join(out), body)


def _clocks(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        parts = [part.strip() for part in inner.split(",")]
    else:
        parts = [raw]
    found: list[str] = []
    for part in parts:
        token = part.strip().strip("\"'")
        match = _CLOCK.match(token)
        if not match:
            return []
        found.append(f"{int(match.group(1)):02d}:{match.group(2)}")
    return found


def _unique(items: list[str]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def _set_status_line(path: Path, status: str) -> None:
    text = path.read_text(encoding="utf-8")
    split = _split_raw(text)
    if split is None:
        return
    fm, body = split
    lines = []
    replaced = False
    for line in fm.split("\n"):
        if line.startswith("status:") and not line.startswith((" ", "\t")):
            lines.append(f"status: {status}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.insert(0, f"status: {status}")
    updated = _join_raw("\n".join(lines), body)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def _replace_in_user(root: Path, old: str, new: str) -> None:
    base = user_dir(root)
    if not base.is_dir() or old == new:
        return
    for path in base.rglob("*.md"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if old not in text:
            continue
        path.write_text(text.replace(old, new), encoding="utf-8")


def _split_raw(text: str) -> tuple[str, str] | None:
    if not text.startswith("---\n"):
        return None
    lines = text.split("\n")
    for index in range(1, len(lines)):
        if lines[index] == "---":
            fm = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return fm, body
    return None


def _join_raw(fm: str, body: str) -> str:
    return f"---\n{fm}\n---\n{body}"


def _path_diff(before: Path, after: Path) -> list[str]:
    old = _files(before)
    new = _files(after)
    lines: list[str] = []
    for rel in sorted(set(old) | set(new)):
        if rel not in old:
            lines.append(f"A {rel}")
        elif rel not in new:
            lines.append(f"D {rel}")
        elif not filecmp.cmp(before / rel, after / rel, shallow=False):
            lines.append(f"M {rel}")
    return lines


def _files(base: Path) -> set[str]:
    if not base.is_dir():
        return set()
    return {
        path.relative_to(base).as_posix()
        for path in base.rglob("*")
        if path.is_file()
    }


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
