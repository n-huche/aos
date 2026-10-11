from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent / "aos"
SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

TODAY = "2026-09-16"


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["git", *args]
    return subprocess.run(cmd, cwd=root, check=check, capture_output=True, text=True)


def init_aos(root: Path) -> None:
    for rel in (
        "user/projects/pending",
        "user/projects/ongoing",
        "user/projects/completed",
        "user/projects/canceled",
        "user/tasks/pending",
        "user/tasks/ongoing",
        "user/tasks/paused",
        "user/tasks/completed",
        "user/tasks/obsolete",
        "user/tasks/canceled",
        "user/projects/paused",
        "user/daily",
        "user/research",
        "user/schedule",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / "user/tasks/tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (root / "user/preferences.md").write_text("# Preferences\n", encoding="utf-8")
    _git(root, "init")
    _git(root, "config", "user.name", "AOS")
    _git(root, "config", "user.email", "aos@localhost")
    _git(root, "add", "-A")
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=AOS",
            "-c",
            "user.email=aos@localhost",
            "commit",
            "-m",
            "aos: test fixture",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def write_unique(
    root: Path,
    slug: str,
    title: str,
    due: str | None,
    *,
    folder: str = "pending",
    status: str = "pending",
    completed_on: str | None = None,
    do_at: str | None = None,
) -> Path:
    due_s = "null" if due is None else due
    completed_s = "null" if completed_on is None else completed_on
    clock = f'\ndo_at: ["{do_at}"]' if do_at else ""
    path = root / "user" / "tasks" / folder / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
type: unique-independent
status: {status}
do_on: {due_s}{clock}
completed_on: {completed_s}
infinitive: {title}
---

# {title}

## What

do it

## How

step by step

## Goal

the state
""",
        encoding="utf-8",
    )
    return path


def write_recurring(
    root: Path,
    slug: str,
    title: str,
    *,
    kind: str,
    until: str | None = None,
    until_event: str | None = None,
    days: list[str] | None = None,
    every: int | None = None,
    unit: str | None = None,
    anchor: str | None = None,
    done_on: list[str] | None = None,
    type_: str = "recurring-independent",
    folder: str = "ongoing",
    status: str = "ongoing",
    project: str | None = None,
    phase: str | None = None,
    due: str | None = None,
    times: int | None = None,
    do_at: str | None = None,
) -> Path:
    lines = [
        "---",
        f"type: {type_}",
        f"status: {status}",
        f"infinitive: {title}",
    ]
    if due is None:
        lines.append("do_on: null")
    else:
        lines.append(f"do_on: {due}")
    if do_at is not None:
        lines.append(f'do_at: ["{do_at}"]')
    if until is not None:
        lines.append(f"until: {until}")
    if until_event is not None:
        lines.append(f"until_event: {until_event}")
    if project is not None:
        lines.append(f"project: {project}")
    if phase is not None:
        lines.append(f"phase: {phase}")
    if times is not None:
        lines.append(f"times: {times}")
    if done_on:
        lines.append("done_on:")
        for d in done_on:
            lines.append(f"  - {d}")
    else:
        lines.append("done_on: []")
    lines.append("cadence:")
    lines.append(f"  kind: {kind}")
    if days is not None:
        inner = ", ".join(days)
        lines.append(f"  days: [{inner}]")
    if every is not None:
        lines.append(f"  every: {every}")
    if unit is not None:
        lines.append(f"  unit: {unit}")
    if anchor is not None:
        lines.append(f"  anchor: {anchor}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## What")
    lines.append("")
    lines.append("repeat")
    lines.append("")
    lines.append("## How")
    lines.append("")
    lines.append("mechanically")
    lines.append("")
    path = root / "user" / "tasks" / folder / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_project(
    root: Path,
    slug: str,
    *,
    status: str = "ongoing",
    prefix: str = "D",
) -> Path:
    hub_dir = root / "user" / "projects" / status / slug
    hub_dir.mkdir(parents=True, exist_ok=True)
    path = hub_dir / f"{slug}.md"
    path.write_text(
        f"""---
status: {status}
prefix: {prefix}
---

# {slug}

## Goal

the goal

## Plan

1. do
""",
        encoding="utf-8",
    )
    return path


def headings(text: str) -> list[str]:
    return [ln[3:].strip() for ln in text.splitlines() if ln.startswith("## ")]


def section_items(text: str, heading: str) -> list[str]:
    cur = None
    items: list[str] = []
    for ln in text.splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip()
            continue
        if cur == heading and ln.startswith("- "):
            items.append(ln)
    return items


def _band_items(text: str, heading: str, band: str) -> list[str]:
    cur = None
    current_band = None
    items: list[str] = []
    for ln in text.splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip()
            current_band = None
            continue
        if cur != heading:
            continue
        if ln.startswith("### "):
            current_band = ln[4:].strip()
            continue
        if current_band == band and ln.startswith("- "):
            items.append(ln)
    return items


def seed_daily(root: Path, iso: str, text: str) -> Path:
    when = date.fromisoformat(iso)
    month = f"{when.year:04d}-{when.month:02d}"
    path = root / "user/daily" / f"{when.year:04d}" / month / f"{when.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def mark(
    text: str,
    *,
    heading: str | None = None,
    slug: str | None = None,
    first: bool = False,
) -> str:
    """Check index boxes.

    A slug checks every line whose link names that task. A heading checks
    every box in that section, or only the first box when first is set.
    """
    if (slug is None) == (heading is None):
        raise ValueError("mark takes a heading or a slug")
    cur = None
    marked = False
    out: list[str] = []
    for ln in text.splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip()
        if slug is not None:
            hit = ln.startswith("- [ ]") and f"/{slug}.md" in ln
        else:
            hit = cur == heading and ln.startswith("- [ ]") and not (first and marked)
        if hit:
            ln = ln.replace("- [ ]", "- [x]", 1)
            marked = True
        out.append(ln)
    return "\n".join(out) + "\n"


class AOSTest(unittest.TestCase):

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        init_aos(self.root)

    def tearDown(self) -> None:
        self._td.cleanup()

    def env(self, today: str = TODAY, *, now: str | None = None) -> dict[str, str]:
        e = os.environ.copy()
        e["AOS_ROOT"] = str(self.root)
        e["AOS_TODAY"] = today
        if now is None:
            e.pop("AOS_NOW", None)
        else:
            e["AOS_NOW"] = now
        return e

    def aos(
        self, *args: str, today: str = TODAY, now: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(
            [sys.executable, str(BIN), *args],
            env=self.env(today, now=now),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            self.fail(
                f"aos {args} failed ({proc.returncode}):\n{proc.stderr}\n{proc.stdout}"
            )
        return proc

    def tasks_md(self) -> str:
        return (self.root / "user/tasks/tasks.md").read_text(encoding="utf-8")
