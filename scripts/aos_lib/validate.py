from __future__ import annotations

import re
from pathlib import Path

from .cadence import cadence_of, due_date, until_date, weekday_names
from .index import after_slug, clock_of
from .config import (
    ALL_TYPES,
    CADENCE_KINDS,
    INTERVAL_UNITS,
    MAINTENANCE_STATUSES,
    PHASE_STATUSES,
    PROJECT_STATUSES,
    RECURRING_STATUSES,
    RECURRING_TYPES,
    STATUS_FOLDER,
    UNIQUE_STATUSES,
    UNIQUE_TYPES,
    WEEKDAYS,
    projects_dir,
    user_dir,
)
from .taskio import iter_task_files
from .yamlfm import as_date, split_frontmatter

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_tasks(root))
    errors.extend(_validate_projects(root))
    errors.extend(_validate_links(root))
    return errors


def _validate_common(task) -> list[str]:
    errors: list[str] = []
    inf = task.data.get("infinitive")
    if not isinstance(inf, str) or not inf.strip():
        errors.append(f"{task.path}: missing infinitive")
    if task.data.get("times") is not None:
        errors.append(f"{task.path}: times is not a field")
    has_in = task.data.get("do_in") not in (None, "", False)
    has_after = task.data.get("do_after") not in (None, "", False)
    if has_in and has_after:
        errors.append(f"{task.path}: do_in and do_after are exclusive")
    if has_in:
        try:
            clock_of(task.data)
        except ValueError:
            errors.append(f"{task.path}: invalid do_in")
    return errors


def _forbid_placement(task) -> list[str]:
    if task.data.get("do_in") not in (None, "", False) or task.data.get("do_after") not in (
        None,
        "",
        False,
    ):
        return [f"{task.path}: undefined due has no do_in or do_after"]
    return []


def _validate_after_graph(tasks) -> list[str]:
    errors: list[str] = []
    by_slug = {task.slug: task for task in tasks}
    color: dict[str, int] = {}

    def walk(slug: str) -> None:
        state = color.get(slug, 0)
        if state == 1:
            errors.append(f"do_after cycle at {slug}")
            return
        if state == 2:
            return
        color[slug] = 1
        task = by_slug.get(slug)
        parent = after_slug(task.data) if task else None
        if parent:
            if parent not in by_slug:
                errors.append(f"{task.path}: do_after missing slug {parent!r}")
            else:
                walk(parent)
        color[slug] = 2

    for slug in by_slug:
        walk(slug)
    return errors


def _validate_tasks(root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, Path] = {}
    tasks = []
    for task in iter_task_files(root):
        slug = task.slug
        if slug in seen:
            errors.append(
                f"duplicate slug {slug!r}: {seen[slug]} and {task.path}"
            )
        else:
            seen[slug] = task.path
        tasks.append(task)
        t = task.type
        if t not in ALL_TYPES:
            errors.append(f"{task.path}: invalid type {t!r}")
            continue
        st = task.status
        expected_folder = STATUS_FOLDER.get(st)
        if expected_folder and task.folder != expected_folder:
            errors.append(
                f"{task.path}: status {st!r} does not match folder {task.folder!r}"
            )
        errors.extend(_validate_common(task))
        if t in UNIQUE_TYPES:
            if st not in UNIQUE_STATUSES:
                errors.append(f"{task.path}: invalid unique status {st!r}")
            if task.folder == "ongoing":
                errors.append(f"{task.path}: unique type in ongoing/")
            if t == "unique-project":
                if not task.data.get("project") or not task.data.get("phase"):
                    errors.append(f"{task.path}: unique-project needs project and phase")
            if due_date(task.data) is None:
                errors.extend(_forbid_placement(task))
            continue
        if t in RECURRING_TYPES:
            if st not in RECURRING_STATUSES:
                errors.append(f"{task.path}: invalid recurring status {st!r}")
            if task.folder == "pending" and st != "pending":
                errors.append(f"{task.path}: unstarted recurring needs status pending")
            if task.folder == "ongoing" and st != "ongoing":
                errors.append(f"{task.path}: live recurring needs status ongoing")
            if task.data.get("start") is not None:
                errors.append(f"{task.path}: recurring has no start")
            if st == "pending" and due_date(task.data) is None:
                errors.extend(_forbid_placement(task))
            errors.extend(_validate_recurrence(task.path, task.data, t))
            continue
        if t == "maintenance":
            if st not in MAINTENANCE_STATUSES:
                errors.append(f"{task.path}: invalid maintenance status {st!r}")
            if task.folder not in {"ongoing", "canceled"}:
                errors.append(f"{task.path}: maintenance lives in ongoing/ or canceled/")
            if task.data.get("start") is not None or task.data.get("due") is not None:
                errors.append(f"{task.path}: maintenance has no start or due")
            if until_date(task.data) is not None or (
                task.data.get("until_event") not in (None, "", False)
            ):
                errors.append(f"{task.path}: maintenance has no until")
            errors.extend(_validate_recurrence(task.path, task.data, t))
    errors.extend(_validate_after_graph(tasks))
    return errors


def _validate_recurrence(path: Path, data: dict, t: str) -> list[str]:
    errors: list[str] = []
    until = as_date(data.get("until"))
    until_event = data.get("until_event")
    event_set = until_event not in (None, "", False)
    if t in {"recurring-independent", "recurring-project"}:
        if bool(until is not None) == bool(event_set):
            errors.append(
                f"{path}: recurring needs until XOR until_event"
            )
    if t == "recurring-project":
        if not data.get("project") or not data.get("phase"):
            errors.append(f"{path}: recurring-project needs project and phase")
    if data.get("times") is not None:
        errors.append(f"{path}: times is not a field")
    cad = cadence_of(data)
    kind = str(cad.get("kind") or "").strip().lower()
    if kind not in CADENCE_KINDS:
        errors.append(f"{path}: invalid cadence.kind {kind!r}")
        return errors
    if kind == "weekdays":
        names = weekday_names(cad)
        raw = cad.get("days") or []
        if not names:
            errors.append(f"{path}: weekdays cadence needs days")
        if isinstance(raw, list):
            for item in raw:
                name = str(item).strip().lower()[:3]
                if name not in WEEKDAYS:
                    errors.append(f"{path}: invalid weekday {item!r}")
    if kind == "interval":
        every = cad.get("every")
        unit = str(cad.get("unit") or "").strip().lower()
        anchor = as_date(cad.get("anchor"))
        if not isinstance(every, int) or every < 1:
            errors.append(f"{path}: interval needs positive every")
        if unit not in INTERVAL_UNITS:
            errors.append(f"{path}: invalid interval unit {unit!r}")
        if anchor is None:
            errors.append(f"{path}: interval needs anchor")
    if kind == "month-weekday":
        raw = cad.get("day")
        name = "" if raw in (None, "", False) else str(raw).strip().lower()[:3]
        n = cad.get("n")
        if not name:
            errors.append(f"{path}: month-weekday needs day")
        elif name not in WEEKDAYS:
            errors.append(f"{path}: invalid weekday {raw!r}")
        values = [n] if isinstance(n, int) else n
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(item, int) or not 1 <= item <= 5 for item in values)
        ):
            errors.append(f"{path}: month-weekday needs n from 1 to 5")
    return errors


def _validate_projects(root: Path) -> list[str]:
    errors: list[str] = []
    base = projects_dir(root)
    if not base.is_dir():
        return errors
    seen: dict[str, Path] = {}
    for status in PROJECT_STATUSES:
        d = base / status
        if not d.is_dir():
            continue
        for proj in sorted(p for p in d.iterdir() if p.is_dir()):
            slug = proj.name
            if slug in seen:
                errors.append(f"duplicate project slug {slug!r}")
            seen[slug] = proj
            hub = proj / f"{slug}.md"
            if not hub.is_file():
                errors.append(f"missing project hub {hub}")
                continue
            data, _body = split_frontmatter(hub.read_text(encoding="utf-8"))
            st = str(data.get("status") or "").strip()
            if st and st != status:
                errors.append(f"{hub}: status {st!r} != folder {status}")
            phases_dir = proj / "phases"
            if phases_dir.is_dir():
                phase_slugs = {p.stem for p in phases_dir.glob("*.md")}
                for phase_path in sorted(phases_dir.glob("*.md")):
                    pdata, pbody = split_frontmatter(
                        phase_path.read_text(encoding="utf-8")
                    )
                    pst = str(pdata.get("status") or "").strip()
                    if pst and pst not in PHASE_STATUSES:
                        errors.append(f"{phase_path}: invalid phase status {pst!r}")
                    proj_ref = str(pdata.get("project") or "").strip()
                    if proj_ref and proj_ref != slug:
                        errors.append(
                            f"{phase_path}: project {proj_ref!r} != {slug!r}"
                        )
                    deps = pdata.get("depends_on") or []
                    if isinstance(deps, list):
                        for dep in deps:
                            dep_s = str(dep).strip()
                            if dep_s and dep_s not in phase_slugs:
                                errors.append(
                                    f"{phase_path}: depends_on missing phase {dep_s!r}"
                                )
                    _ = pbody
    return errors


def _validate_links(root: Path) -> list[str]:
    errors: list[str] = []
    base = user_dir(root)
    if not base.is_dir():
        return errors
    for path in sorted(base.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            href = m.group(2).strip()
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            href = href.split("#", 1)[0].split("?", 1)[0]
            if not href:
                continue
            target = (path.parent / href).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path}: link escapes repo {href}")
                continue
            if not target.exists():
                errors.append(f"{path}: broken link {href}")
    return errors
