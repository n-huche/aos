from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

BIN = Path(__file__).resolve().parent.parent / "aos"
SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from aos_lib.index import _merge_section  # noqa: E402
from aos_lib.yamlfm import split_frontmatter  # noqa: E402


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


def mark_section(text: str, heading: str) -> str:
    cur = None
    out: list[str] = []
    for ln in text.splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip()
            out.append(ln)
            continue
        if cur == heading and ln.startswith("- [ ]"):
            ln = ln.replace("- [ ]", "- [x]", 1)
        out.append(ln)
    return "\n".join(out) + "\n"


class AOSTest(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        init_aos(self.root)

    def tearDown(self) -> None:
        self._td.cleanup()

    def env(self, today: str = TODAY) -> dict[str, str]:
        e = os.environ.copy()
        e["AOS_ROOT"] = str(self.root)
        e["AOS_TODAY"] = today
        return e

    def aos(self, *args: str, today: str = TODAY) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(
            [sys.executable, str(BIN), *args],
            env=self.env(today),
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

    def test_unique_buckets_and_undefined(self) -> None:
        write_unique(self.root, "overdue-one", "Overdue one", "2026-09-10")
        write_unique(self.root, "today-one", "Today unique", "2026-09-16")
        write_unique(self.root, "tomorrow-one", "Tomorrow", "2026-09-17")
        write_unique(self.root, "week-one", "This week", "2026-09-21")
        write_unique(self.root, "month-one", "This month", "2026-09-30")
        write_unique(self.root, "later-one", "Later", "2026-11-01")
        write_unique(self.root, "open-one", "No due", None)
        self.aos("reindex")
        text = self.tasks_md()
        self.assertEqual(
            headings(text),
            [
                "Overdue",
                "Today",
                "1 day",
                "4-7 days",
                "8-30 days",
                "+30 days",
            ],
        )
        self.assertIn("pending/overdue-one.md", section_items(text, "Overdue")[0])
        self.assertIn("pending/today-one.md", section_items(text, "Today")[0])
        self.assertIn("pending/tomorrow-one.md", section_items(text, "1 day")[0])
        self.assertIn("pending/week-one.md", section_items(text, "4-7 days")[0])
        self.assertIn("pending/month-one.md", section_items(text, "8-30 days")[0])
        self.assertIn("pending/later-one.md", section_items(text, "+30 days")[0])
        self.assertFalse((self.root / "user/tasks/pending/open-one.md").exists())
        self.assertTrue((self.root / "user/tasks/paused/open-one.md").is_file())
        self.assertNotIn("open-one", text)
        self.assertNotIn("## 2-3 days", text)
        self.assertNotIn("## Undefined", text)

    def test_daily_cadence(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertEqual(headings(text), ["Today", "1 day"])
        self.assertEqual(len(section_items(text, "Today")), 1)
        self.assertEqual(len(section_items(text, "1 day")), 1)
        self.assertIn("ongoing/water.md", section_items(text, "Today")[0])
        self.assertIn("ongoing/water.md", section_items(text, "1 day")[0])
        self.assertNotIn("## Overdue", text)

    def test_weekdays_wed_and_thu(self) -> None:
        write_recurring(
            self.root,
            "training",
            "Training",
            kind="weekdays",
            days=["wed", "thu"],
            until="2026-12-01",
        )
        self.aos("reindex", today="2026-09-16")
        text = self.tasks_md()
        self.assertEqual(headings(text), ["Today", "1 day"])
        self.aos("reindex", today="2026-09-17")
        text = self.tasks_md()
        self.assertEqual(headings(text), ["Today", "4-7 days"])
        self.assertIn("ongoing/training.md", section_items(text, "4-7 days")[0])

    def test_recurring_due_null_stays_pending(self) -> None:
        write_recurring(
            self.root,
            "habit",
            "Habit",
            kind="daily",
            until="2026-12-01",
            folder="pending",
            status="pending",
            due=None,
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertEqual(text.strip(), "# Tasks")
        self.assertFalse((self.root / "user/tasks/pending/habit.md").exists())
        self.assertTrue((self.root / "user/tasks/paused/habit.md").is_file())
        self.assertFalse((self.root / "user/tasks/ongoing/habit.md").exists())
        self.aos("daily-close", "2026-09-16", today="2026-09-17")
        daily = (self.root / "user/daily/2026/2026-09/2026-09-16.md").read_text(encoding="utf-8")
        self.assertIn("| routine | tasks |", daily)
        self.assertIn("| null | null |", daily)
        self.assertNotIn("## Failed tasks", daily)
        self.assertNotIn("**Result:**", daily)

    def test_first_check_starts_recurring(self) -> None:
        write_recurring(
            self.root,
            "habit",
            "Habit",
            kind="daily",
            until="2026-12-01",
            folder="pending",
            status="pending",
            due="2026-09-16",
        )
        self.aos("reindex")
        self.assertTrue((self.root / "user/tasks/pending/habit.md").is_file())
        text = self.tasks_md()
        self.assertIn("pending/habit.md", section_items(text, "Today")[0])
        (self.root / "user/tasks/tasks.md").write_text(
            mark_section(text, "Today"), encoding="utf-8"
        )
        self.aos("reindex")
        self.assertFalse((self.root / "user/tasks/pending/habit.md").exists())
        path = self.root / "user/tasks/ongoing/habit.md"
        self.assertTrue(path.is_file())
        data, _body = split_frontmatter(path.read_text(encoding="utf-8"))
        self.assertEqual(str(data.get("status")), "ongoing")
        self.assertEqual([d.isoformat() for d in data.get("done_on") or []], [TODAY])
        self.assertEqual(data.get("do_on").isoformat(), "2026-09-17")
        self.assertNotIn("## Today", self.tasks_md())

    def test_pending_due_is_not_the_cadence(self) -> None:
        write_recurring(
            self.root,
            "training",
            "Training",
            kind="weekdays",
            days=["tue", "fri"],
            until="2026-12-01",
            folder="pending",
            status="pending",
            due="2026-09-16",
        )
        self.aos("reindex", today="2026-09-16")
        text = self.tasks_md()
        self.assertIn("pending/training.md", section_items(text, "Today")[0])
        self.assertNotIn("## 2-3 days", text)

    def test_x_unstarted_recurring_starts(self) -> None:
        write_recurring(
            self.root,
            "habit",
            "Habit",
            kind="daily",
            until="2026-12-01",
            folder="pending",
            status="pending",
            due="2026-11-01",
        )
        write_unique(self.root, "one", "One unique", "2026-09-16")
        self.aos("reindex")
        text = mark_section(self.tasks_md(), "+30 days")
        (self.root / "user/tasks/tasks.md").write_text(text, encoding="utf-8")
        self.aos("reindex")
        self.assertFalse((self.root / "user/tasks/pending/habit.md").exists())
        path = self.root / "user/tasks/ongoing/habit.md"
        self.assertTrue(path.is_file())
        data, _body = split_frontmatter(path.read_text(encoding="utf-8"))
        self.assertEqual(str(data.get("status")), "ongoing")
        self.assertEqual([d.isoformat() for d in data.get("done_on") or []], [TODAY])

    def test_maintenance_own_folder_same_index(self) -> None:
        path = self.root / "user/tasks/ongoing/box.md"
        path.write_text(
            """---
type: maintenance
status: ongoing
infinitive: Box upkeep
done_on: []
cadence:
  kind: daily
---

# Box upkeep

## What

keep

## How

do
""",
            encoding="utf-8",
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertIn("ongoing/box.md", section_items(text, "Today")[0])
        self.aos("validate")

    def test_one_check_closes_the_day(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertEqual(
            section_items(text, "Today"),
            ["- [ ] [Drink water](ongoing/water.md)"],
        )
        self.assertEqual(
            section_items(text, "1 day"),
            ["- [ ] [Drink water](ongoing/water.md)"],
        )
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("reindex")
        rec = self.root / "user/tasks/ongoing/water.md"
        data, _body = split_frontmatter(rec.read_text(encoding="utf-8"))
        self.assertEqual([d.isoformat() for d in data.get("done_on") or []], [TODAY])
        self.assertNotIn("## Today", self.tasks_md())
        self.assertEqual(headings(self.tasks_md()), ["1 day"])

    def test_times_is_rejected(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
            times=1,
        )
        proc = subprocess.run(
            [sys.executable, str(BIN), "validate"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("times is not a field", proc.stderr)

    def test_done_on_cleared_at_close(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
            done_on=["2026-09-16"],
        )
        self.aos("daily-close", "2026-09-16", today="2026-09-17")
        daily = (self.root / "user/daily/2026/2026-09/2026-09-16.md").read_text(encoding="utf-8")
        self.assertIn("| null | 100% |", daily)
        self.assertNotIn("**Result:**", daily)
        self.assertNotIn("## Failed tasks", daily)
        self.assertIn("ongoing/water.md", daily)
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/water.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("done_on") or [], [])

    def test_interval(self) -> None:
        write_recurring(
            self.root,
            "review-now",
            "Review today",
            kind="interval",
            every=2,
            unit="months",
            anchor="2026-09-16",
            until="2027-12-01",
        )
        write_recurring(
            self.root,
            "review-y",
            "Review yesterday",
            kind="interval",
            every=2,
            unit="months",
            anchor="2026-09-15",
            until="2027-12-01",
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertIn("ongoing/review-now.md", section_items(text, "Today")[0])
        later = section_items(text, "+30 days")
        hrefs = " ".join(later)
        self.assertIn("ongoing/review-now.md", hrefs)
        self.assertIn("ongoing/review-y.md", hrefs)
        self.assertNotIn("review-y", " ".join(section_items(text, "Today")))

    def test_until_date(self) -> None:
        write_recurring(
            self.root,
            "short",
            "Short",
            kind="weekdays",
            days=["wed", "thu"],
            until="2026-09-16",
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertEqual(headings(text), ["Today"])
        self.assertNotIn("## 1 day", text)

    def test_empty_sections_omitted(self) -> None:
        write_unique(self.root, "week-only", "This week only", "2026-09-21")
        self.aos("reindex")
        text = self.tasks_md()
        self.assertEqual(headings(text), ["4-7 days"])
        self.assertTrue(text.startswith("# Tasks\n"))

    def test_overdue_only_unique(self) -> None:
        write_unique(self.root, "overdue", "Overdue unique", "2026-09-10")
        write_recurring(
            self.root,
            "daily-habit",
            "Daily",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex")
        text = self.tasks_md()
        overdue_items = section_items(text, "Overdue")
        self.assertEqual(len(overdue_items), 1)
        self.assertIn("pending/overdue.md", overdue_items[0])
        self.assertNotIn("ongoing/", " ".join(overdue_items))
        self.assertIn("ongoing/daily-habit.md", section_items(text, "Today")[0])

    def test_x_recurring_not_today_reverted(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "1 day"), encoding="utf-8")
        self.aos("reindex")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/water.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("done_on") or [], [])
        self.assertTrue((self.root / "user/tasks/ongoing/water.md").is_file())
        text = self.tasks_md()
        self.assertTrue(all("- [ ]" in ln or not ln.startswith("- [") for ln in text.splitlines()))
        self.assertIn("- [ ] [Drink water](ongoing/water.md)", section_items(text, "1 day"))

    def test_x_unique_moves_completed_on_commit(self) -> None:
        write_unique(self.root, "send-email", "Send email", "2026-09-18")
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "2-3 days"), encoding="utf-8")
        self.aos("reindex")
        old = self.root / "user/tasks/pending/send-email.md"
        new = self.root / "user/tasks/completed/send-email.md"
        self.assertFalse(old.exists())
        self.assertTrue(new.is_file())
        data, _body = split_frontmatter(new.read_text(encoding="utf-8"))
        self.assertEqual(str(data.get("status")), "completed")
        self.assertEqual(data.get("completed_on").isoformat(), TODAY)
        self.assertEqual(data.get("do_on").isoformat(), "2026-09-18")
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos reindex")
        self.assertNotIn("send-email", self.tasks_md())

    def test_no_commit_skips_vault_sync(self) -> None:
        head = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        write_unique(self.root, "send", "Send", "2026-09-16")
        self.aos("reindex", "--no-commit")
        self.aos("daily-close", "--no-commit", "2026-09-15")
        self.assertEqual(_git(self.root, "rev-parse", "HEAD").stdout.strip(), head)
        self.assertNotEqual(_git(self.root, "status", "--porcelain").stdout.strip(), "")

    def test_x_recurring_today_fills_done_on(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("reindex")
        rec = self.root / "user/tasks/ongoing/water.md"
        self.assertTrue(rec.is_file())
        data, _body = split_frontmatter(rec.read_text(encoding="utf-8"))
        done = data.get("done_on") or []
        self.assertEqual([d.isoformat() for d in done], [TODAY])
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos reindex")
        text = self.tasks_md()
        self.assertNotIn("## Today", text)
        self.assertEqual(headings(text), ["1 day"])

    def test_daily_close_until_without_x(self) -> None:
        write_recurring(
            self.root,
            "cycle",
            "Short cycle",
            kind="daily",
            until="2026-09-15",
        )
        (self.root / "user/schedule/2026/09").mkdir(parents=True, exist_ok=True)
        (self.root / "user/schedule/2026/09/15.md").write_text(
            "# 2026-09-15\n\n- [x] leftover\n", encoding="utf-8"
        )
        (self.root / "user/schedule/2026/09/16.md").write_text(
            "# 2026-09-16\n\n- [Cycle](../../../tasks/ongoing/cycle.md)\n",
            encoding="utf-8",
        )
        self.aos("daily-close", "2026-09-15")
        self.assertFalse((self.root / "user/tasks/ongoing/cycle.md").exists())
        completed = self.root / "user/tasks/completed/cycle.md"
        self.assertTrue(completed.is_file())
        data, _body = split_frontmatter(completed.read_text(encoding="utf-8"))
        self.assertEqual(str(data.get("status")), "completed")
        daily = (self.root / "user/daily/2026/2026-09/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("| null | 0% |", daily)
        self.assertNotIn("**Result:**", daily)
        self.assertIn("## Failed tasks", daily)
        self.assertIn("completed/cycle.md", daily)
        self.assertTrue((self.root / "user/schedule/2026/09/15.md").is_file())
        self.assertTrue((self.root / "user/schedule/2026/09/16.md").is_file())
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos daily-close 2026-09-15")

    def test_past_schedule_removed(self) -> None:
        """Closed columns stay. daily-close does not delete the month grid."""
        write_unique(self.root, "send", "Send", "2026-09-16", do_at="07:30")
        self.aos("reindex", today="2026-09-16")
        month = self.root / "user/schedule/2026/2026-09.md"
        self.assertTrue(month.is_file())
        self.assertIn("Send", month.read_text(encoding="utf-8"))
        self.aos("daily-close", "2026-09-15", today="2026-09-16")
        frozen = month.read_text(encoding="utf-8")
        from aos_lib.schedule import parse_month

        self.assertEqual(parse_month(frozen)[16][7], "Send")
        send = self.root / "user/tasks/pending/send.md"
        text = send.read_text(encoding="utf-8").replace(
            'do_at: ["07:30"]', 'do_at: ["09:00"]'
        )
        send.write_text(text, encoding="utf-8")
        self.aos("reindex", today="2026-09-16")
        after = parse_month(month.read_text(encoding="utf-8"))
        self.assertEqual(parse_month(frozen)[15], after[15])
        self.assertEqual(after[16][7], "null")
        self.assertEqual(after[16][9], "Send")

    def test_validate_ok_and_xor(self) -> None:
        write_unique(self.root, "ok-u", "Ok unique", "2026-09-20")
        write_recurring(
            self.root,
            "ok-r",
            "Ok rec",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex")
        proc = self.aos("validate")
        self.assertEqual(proc.stdout.strip(), "ok")
        bad = self.root / "user/tasks/ongoing/bad.md"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text(
            """---
type: recurring-independent
status: ongoing
infinitive: Bad
due: null
until: 2026-12-01
until_event: some event
done_on: []
cadence:
  kind: daily
---

# Bad
""",
            encoding="utf-8",
        )
        proc = subprocess.run(
            [sys.executable, str(BIN), "validate"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("XOR", proc.stderr)

    def test_rewrite_phase_links_on_unique_complete(self) -> None:
        proj = self.root / "user/projects/ongoing/demo"
        (proj / "phases").mkdir(parents=True, exist_ok=True)
        (proj / "demo.md").write_text(
            """---
status: ongoing
prefix: DE
---

# Demo

## Goal

g

## Plan

1. p

## Phases

- [One](phases/de-01-one.md)
""",
            encoding="utf-8",
        )
        (proj / "phases/de-01-one.md").write_text(
            """---
status: ongoing
project: demo
depends_on: []
---

# One

## Goal

c

## Plan

1. p

## Tasks

- [Send](../../../../tasks/pending/send.md)
""",
            encoding="utf-8",
        )
        path_send = write_unique(self.root, "send", "Send", "2026-09-16")
        text_send = path_send.read_text(encoding="utf-8").replace(
            "infinitive: Send",
            "infinitive: Send\nproject: demo\nphase: de-01-one",
        )
        path_send.write_text(text_send, encoding="utf-8")
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("reindex")
        phase_path = (
            self.root / "user/projects/completed/demo/phases/de-01-one.md"
        )
        phase = phase_path.read_text(encoding="utf-8")
        self.assertIn("tasks/completed/send.md", phase)
        self.assertNotIn("tasks/pending/send.md", phase)

    def test_unique_complete_drops_schedule(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-16", do_at="08:00")
        write_unique(self.root, "keep", "Keep", "2026-09-20", do_at="08:00")
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("reindex")
        from aos_lib.schedule import parse_month

        month = self.root / "user/schedule/2026/2026-09.md"
        cells = parse_month(month.read_text(encoding="utf-8"))
        self.assertNotIn("Send", cells[16][8])
        self.assertIn("Keep", cells[20][8])
        self.assertTrue((self.root / "user/tasks/completed/send.md").is_file())

    def test_watch_syncs_unique_checkbox(self) -> None:
        write_unique(self.root, "seen", "Seen", "2026-09-16")
        self.aos("reindex")
        proc = subprocess.Popen(
            [sys.executable, str(BIN), "watch"],
            env=self.env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            deadline = time.time() + 8
            started = False
            while time.time() < deadline:
                if proc.poll() is not None:
                    err = proc.stderr.read() if proc.stderr else ""
                    self.fail(f"watch exited early: {err}")
                # give watch a moment to snapshot the unchecked file
                time.sleep(0.2)
                started = True
                break
            self.assertTrue(started)
            time.sleep(0.3)
            path = self.root / "user/tasks/tasks.md"
            path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
            done = self.root / "user/tasks/completed/seen.md"
            for _ in range(30):
                if done.is_file():
                    break
                time.sleep(0.2)
            self.assertTrue(done.is_file(), "watch did not complete unique in time")
        finally:
            proc.send_signal(signal.SIGINT)
            try:
                proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate(timeout=3)

    def test_render_crontab_is_calendar_only(self) -> None:
        from aos_lib.up import render_crontab

        text = render_crontab(self.root)
        self.assertIn("daily-close", text)
        self.assertNotIn("up --quiet", text)
        self.assertNotIn("@reboot", text)
        self.assertNotIn("* * * * *", text)
        self.assertIn(f"AOS_ROOT={self.root.resolve()}", text)
        self.assertIn(str(self.root.resolve() / "scripts" / "aos"), text)

    def test_up_watch_only_starts_and_is_idempotent(self) -> None:
        from aos_lib.up import watch_running

        out = self.aos("up", "--watch-only")
        self.assertIn("watch-started", out.stdout)
        pid = int(out.stdout.strip().rsplit(":", 1)[-1])
        try:
            self.assertTrue(watch_running(self.root))
            again = self.aos("up", "--watch-only")
            self.assertIn("watch-running", again.stdout)
            self.assertIn(str(pid), again.stdout)
            self.assertFalse((self.root / "user/daily/2026/2026-09/2026-09-15.md").exists())
        finally:
            try:
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            time.sleep(0.2)

    def test_missing_close_dates(self) -> None:
        from aos_lib.daily import missing_close_dates

        today = date(2026, 9, 16)
        self.assertEqual(
            missing_close_dates(self.root, today),
            [date(2026, 9, 15)],
        )
        seeded = seed_daily(self.root, "2026-09-15", "# 15\n")
        self.assertEqual(missing_close_dates(self.root, today), [])
        seeded.unlink()
        seed_daily(self.root, "2026-09-13", "# 13\n")
        self.assertEqual(
            missing_close_dates(self.root, today),
            [date(2026, 9, 14), date(2026, 9, 15)],
        )

    def test_catch_up_after_down_day_applies_leftover_x_as_today(self) -> None:
        from aos_lib.daily import catch_up

        write_unique(self.root, "send-email", "Send email", "2026-09-15")
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
        )
        self.aos("reindex", today="2026-09-15")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        sched = self.root / "user/schedule"
        (sched / "2026/09").mkdir(parents=True, exist_ok=True)
        (sched / "2026/09/15.md").write_text("# 15\n", encoding="utf-8")
        (sched / "2026/09/16.md").write_text("# 16\n", encoding="utf-8")
        actions = catch_up(self.root, today=date(2026, 9, 16))
        self.assertIn("catch-up-close:2026-09-15", actions)
        self.assertIn("catch-up-sync:2026-09-16:2", actions)
        done_u = self.root / "user/tasks/completed/send-email.md"
        self.assertTrue(done_u.is_file())
        data, _body = split_frontmatter(done_u.read_text(encoding="utf-8"))
        self.assertEqual(data.get("completed_on").isoformat(), "2026-09-16")
        rec = self.root / "user/tasks/ongoing/water.md"
        data_r, _body = split_frontmatter(rec.read_text(encoding="utf-8"))
        self.assertEqual(
            [d.isoformat() for d in (data_r.get("done_on") or [])],
            ["2026-09-16"],
        )
        daily = (self.root / "user/daily/2026/2026-09/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("| null | 0% |", daily)
        self.assertNotIn("**Result:**", daily)
        self.assertIn("## Failed tasks", daily)
        self.assertIn("send-email.md", daily)
        self.assertIn("ongoing/water.md", daily)
        self.assertTrue((sched / "2026/09/15.md").is_file())
        self.assertTrue((sched / "2026/09/16.md").is_file())
        text = self.tasks_md()
        self.assertNotIn("send-email", text)
        self.assertNotIn("## Today", text)
        self.assertIn("ongoing/water.md", section_items(text, "1 day")[0])

    def test_catch_up_today_unique_completes_on_recovery_day(self) -> None:
        from aos_lib.daily import catch_up

        seed_daily(
            self.root,
            "2026-09-14",
            "# 2026-09-14\n\n**Result:** satisfactory\n",
        )
        write_unique(self.root, "today-task", "Today unique", "2026-09-16")
        self.aos("reindex", today="2026-09-16")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        actions = catch_up(self.root, today=date(2026, 9, 16))
        self.assertIn("catch-up-close:2026-09-15", actions)
        self.assertIn("catch-up-sync:2026-09-16:1", actions)
        done = self.root / "user/tasks/completed/today-task.md"
        self.assertTrue(done.is_file())
        data, _body = split_frontmatter(done.read_text(encoding="utf-8"))
        self.assertEqual(data.get("completed_on").isoformat(), "2026-09-16")
        daily = (self.root / "user/daily/2026/2026-09/2026-09-15.md").read_text(encoding="utf-8")
        self.assertNotIn("today-task.md", daily)

    def test_catch_up_two_missed_days(self) -> None:
        from aos_lib.daily import catch_up

        seed_daily(
            self.root,
            "2026-09-13",
            "# 2026-09-13\n\n**Result:** satisfactory\n",
        )
        write_unique(self.root, "letter", "Letter", "2026-09-14")
        self.aos("reindex", today="2026-09-14")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        sched = self.root / "user/schedule"
        (sched / "2026/09").mkdir(parents=True, exist_ok=True)
        (sched / "2026/09/14.md").write_text("# 14\n", encoding="utf-8")
        (sched / "2026/09/15.md").write_text("# 15\n", encoding="utf-8")
        (sched / "2026/09/16.md").write_text("# 16\n", encoding="utf-8")
        actions = catch_up(self.root, today=date(2026, 9, 16))
        self.assertIn("catch-up-close:2026-09-14", actions)
        self.assertIn("catch-up-close:2026-09-15", actions)
        self.assertIn("catch-up-sync:2026-09-16:1", actions)
        done = self.root / "user/tasks/completed/letter.md"
        self.assertTrue(done.is_file())
        data, _body = split_frontmatter(done.read_text(encoding="utf-8"))
        self.assertEqual(data.get("completed_on").isoformat(), "2026-09-16")
        d14 = (self.root / "user/daily/2026/2026-09/2026-09-14.md").read_text(encoding="utf-8")
        self.assertIn("## Failed tasks", d14)
        self.assertIn("letter.md", d14)
        d15 = (self.root / "user/daily/2026/2026-09/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("## Failed tasks", d15)
        self.assertIn("letter.md", d15)
        self.assertTrue((sched / "2026/09/14.md").is_file())
        self.assertTrue((sched / "2026/09/15.md").is_file())
        self.assertTrue((sched / "2026/09/16.md").is_file())

    def test_nested_user_git_daily_close_does_not_commit_parent(self) -> None:
        (self.root / ".gitignore").write_text("/user/\n", encoding="utf-8")
        _git(self.root, "rm", "-r", "--cached", "user")
        _git(self.root, "add", ".gitignore")
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=AOS",
                "-c",
                "user.email=aos@localhost",
                "commit",
                "-m",
                "aos: ignore user",
            ],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        parent_head = _git(self.root, "rev-parse", "HEAD").stdout.strip()

        user = self.root / "user"
        _git(user, "init")
        _git(user, "config", "user.name", "AOS")
        _git(user, "config", "user.email", "aos@localhost")
        _git(user, "add", "-A")
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=AOS",
                "-c",
                "user.email=aos@localhost",
                "commit",
                "-m",
                "user: fixture",
            ],
            cwd=user,
            check=True,
            capture_output=True,
            text=True,
        )

        write_unique(self.root, "letter", "Letter", "2026-09-15")
        self.aos("reindex")
        self.aos("daily-close", "2026-09-15")

        self.assertEqual(
            _git(self.root, "rev-parse", "HEAD").stdout.strip(),
            parent_head,
        )
        self.assertEqual(_git(self.root, "status", "--porcelain").stdout.strip(), "")
        log = _git(user, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos daily-close 2026-09-15")
        self.assertEqual(_git(user, "status", "--porcelain").stdout.strip(), "")
        self.assertTrue((user / "daily/2026/2026-09/2026-09-15.md").is_file())

    def test_same_project_ignores_type_order(self) -> None:
        write_project(self.root, "job", status="pending", prefix="J")
        hub = self.root / "user/projects/pending/job/job.md"
        hub.write_text(
            hub.read_text(encoding="utf-8") + "\n## Phases\n\n- [J-01](phases/j-01-learn.md)\n",
            encoding="utf-8",
        )
        phase = self.root / "user/projects/pending/job/phases"
        phase.mkdir()
        (phase / "j-01-learn.md").write_text(
            """---
status: pending
project: job
---

# J-01 Learn

## Plan

1. go

## Tasks

- [First](../../../tasks/pending/first.md)
- [Habit](../../../tasks/pending/habit.md)
""",
            encoding="utf-8",
        )
        write_unique(self.root, "other", "Other thing", "2026-09-16")
        write_recurring(
            self.root,
            "habit",
            "Habit",
            kind="daily",
            until_event="done",
            folder="pending",
            status="pending",
            due="2026-09-16",
            type_="recurring-project",
            project="job",
            phase="j-01-learn",
        )
        path = self.root / "user/tasks/pending/first.md"
        path.write_text(
            """---
type: unique-project
status: pending
do_on: 2026-09-16
completed_on: null
infinitive: First step
project: job
phase: j-01-learn
---

# First

## What

a

## How

b

## Goal

c
""",
            encoding="utf-8",
        )
        self.aos("reindex")
        items = section_items(self.tasks_md(), "Today")
        self.assertEqual(
            items,
            [
                "- [ ] [Other thing](pending/other.md)",
                "- [ ] [First step](pending/first.md)",
                "- [ ] [Habit](pending/habit.md)",
            ],
        )

    def test_index_never_stacks_blank_lines(self) -> None:
        def write(slug: str, title: str, *, extra: str, cadence: str, done: str) -> None:
            path = self.root / "user/tasks/ongoing" / f"{slug}.md"
            path.write_text(
                f"""---
type: maintenance
infinitive: {title}
status: ongoing
{extra}
done_on: [{done}]
cadence:
{cadence}
---

# {title}

## What

x

## How

y

## When

z

## Where

w
""",
                encoding="utf-8",
            )

        write("wake", "Acordar", extra='do_at: ["06:00"]', cadence="  kind: daily", done="2026-09-24")
        write("walk", "Caminhar", extra="", cadence="  kind: daily", done="2026-09-24")
        write(
            "breakfast",
            "Tomar café da manhã",
            extra='do_at: ["06:30"]',
            cadence="  kind: daily",
            done="2026-09-24",
        )
        write(
            "video",
            "Postar vídeo",
            extra="",
            cadence="  kind: weekdays\n  days: [thu]",
            done="2026-09-24",
        )
        write(
            "lunch",
            "Almoçar",
            extra='do_at: ["12:00"]',
            cadence="  kind: weekdays\n  days: [fri]",
            done="",
        )
        self.aos("reindex", today="2026-09-24")
        text = self.tasks_md()
        self.assertNotIn("\n\n\n", text)
        self.assertIn("## 4-7 days\n\n### Sem horário\n\n- [ ] [Postar vídeo]", text)
        self.assertIn(
            "### Morning\n\n- [ ] [Acordar](ongoing/wake.md)\n- [ ] [Tomar café da manhã](ongoing/breakfast.md)",
            text,
        )
        self.assertIn("### Afternoon\n\n- [ ] [Almoçar](ongoing/lunch.md)", text)
        self.assertIn("### Sem horário\n\n- [ ] [Caminhar](ongoing/walk.md)", text)

    def test_same_section_joins_after_heading(self) -> None:
        ongoing = self.root / "user/tasks/ongoing"
        pending = self.root / "user/tasks/pending"
        (ongoing / "breakfast.md").write_text(
            """---
type: maintenance
infinitive: Tomar café da manhã
status: ongoing
do_at: ["06:30"]
done_on: [2026-09-24]
cadence:
  kind: daily
---

# Café da manhã

## What

x

## How

y
""",
            encoding="utf-8",
        )
        (ongoing / "college.md").write_text(
            """---
type: recurring-independent
infinitive: Fazer trabalhos da faculdade
status: ongoing
do_on: null
until_event: Eu me formar
done_on: []
cadence:
  kind: month-weekday
  day: mon
  n: [1, 3]
---

# Faculdade

## What

x

## How

y

## When

z
""",
            encoding="utf-8",
        )
        (pending / "renew-documents.md").write_text(
            """---
type: unique-independent
infinitive: Renovar documentos
status: pending
do_on: 2026-10-24
completed_on: null
---

# Documentos

## What

x

## How

y

## Goal

z
""",
            encoding="utf-8",
        )
        self.aos("reindex", today="2026-09-24")
        text = self.tasks_md()
        section = text.split("## 8-30 days", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(section.count("### Sem horário"), 1)
        self.assertNotIn(")\n\n- [ ]", section)
        self.assertIn(
            "### Sem horário\n\n"
            "- [ ] [Fazer trabalhos da faculdade](ongoing/college.md)\n"
            "- [ ] [Renovar documentos](pending/renew-documents.md)\n",
            text,
        )

    def test_merge_keeps_task_lines_together(self) -> None:
        merged = _merge_section(
            [
                [
                    "- [ ] [Acordar](ongoing/wake.md)",
                    "### Morning",
                    "- [ ] [Caminhar](ongoing/walk.md)",
                    "- [ ] [Tomar café da manhã](ongoing/breakfast.md)",
                    "### Afternoon",
                    "- [ ] [Almoçar](ongoing/lunch.md)",
                ],
                [
                    "### Morning",
                    "- [ ] [Estudar equals](pending/equals.md)",
                    "- [ ] [Estudar Stream](pending/stream.md)",
                    "### Afternoon",
                    "- [ ] [Postar vídeo](ongoing/video.md)",
                ],
            ]
        )
        text = "\n".join(merged)
        self.assertNotIn(")\n\n- [ ]", text)
        self.assertIn("### Morning\n\n- [ ] [Caminhar]", text)
        self.assertIn(
            "- [ ] [Caminhar](ongoing/walk.md)\n- [ ] [Tomar café da manhã](ongoing/breakfast.md)",
            text,
        )
        self.assertIn(
            "- [ ] [Estudar equals](pending/equals.md)\n- [ ] [Estudar Stream](pending/stream.md)",
            text,
        )
        self.assertIn(
            "- [ ] [Almoçar](ongoing/lunch.md)",
            text,
        )
        self.assertNotIn("- [ ] [Almoçar](ongoing/lunch.md)\n### ", text)

    def test_overdue_recurring_advances_one_step(self) -> None:
        write_recurring(
            self.root,
            "water",
            "Drink water",
            kind="daily",
            until="2026-12-01",
            due="2026-09-14",
        )
        self.aos("reindex")
        self.assertIn("ongoing/water.md", section_items(self.tasks_md(), "Overdue")[0])
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Overdue"), encoding="utf-8")
        self.aos("reindex")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/water.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-09-15")
        self.assertEqual([d.isoformat() for d in data.get("done_on") or []], [TODAY])
        self.assertIn("ongoing/water.md", section_items(self.tasks_md(), "Overdue")[0])
        self.assertNotIn("- [x]", self.tasks_md())

    def test_index_uses_the_first_written_clock(self) -> None:
        path = write_unique(self.root, "split", "Split", "2026-09-16")
        text = path.read_text(encoding="utf-8").replace(
            "infinitive: Split",
            'do_at: ["18:00", "07:30"]\ninfinitive: Split',
        )
        path.write_text(text, encoding="utf-8")
        self.aos("reindex")
        items = section_items(self.tasks_md(), "Today")
        self.assertEqual(items, ["- [ ] [Split](pending/split.md)"])
        self.assertEqual(_band_items(self.tasks_md(), "Today", "Evening"), items)
        self.assertEqual(_band_items(self.tasks_md(), "Today", "Morning"), [])
        from aos_lib.schedule import parse_month

        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[16][7], "Split")
        self.assertEqual(cells[16][18], "Split")

    def test_sleep_is_one_evening_line_and_every_grid_hour(self) -> None:
        path = self.root / "user/tasks/ongoing/sleep.md"
        path.write_text(
            """---
type: maintenance
status: ongoing
infinitive: Dormir
do_at: ["22:00", "23:00", "00:00", "01:00", "02:00", "03:00", "04:00", "05:00"]
done_on: []
cadence:
  kind: daily
---

# Dormir

## What

Dormir.

## How

Deitar.
""",
            encoding="utf-8",
        )
        write_unique(self.root, "open", "Open the month", "2026-09-16", do_at="09:00")
        self.aos("reindex")
        text = self.tasks_md()
        line = "- [ ] [Dormir](ongoing/sleep.md)"
        self.assertEqual(section_items(text, "Today").count(line), 1)
        self.assertEqual(section_items(text, "1 day").count(line), 1)
        self.assertEqual(_band_items(text, "Today", "Evening"), [line])
        self.assertEqual(_band_items(text, "1 day", "Evening"), [line])
        self.assertEqual(_band_items(text, "Today", "Overnight"), [])
        self.assertEqual(_band_items(text, "1 day", "Overnight"), [])
        from aos_lib.schedule import parse_month

        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        for day in (16, 17):
            for hour in (22, 23, 0, 1, 2, 3, 4, 5):
                self.assertEqual(cells[day][hour], "Dormir")
        self.assertEqual(cells[16][9], "Open the month")
        self.assertNotEqual(cells[17][9], "Dormir")

    def test_early_unique_frees_the_window(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-18", do_at="08:00")
        self.aos("reindex", today="2026-09-16")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "2-3 days"), encoding="utf-8")
        self.aos("reindex", today="2026-09-16")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/completed/send.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-09-18")
        self.assertEqual(data.get("completed_on").isoformat(), "2026-09-16")
        from aos_lib.schedule import parse_month

        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[18][8], "null")
        self.aos("daily-close", "2026-09-18", today="2026-09-19")
        daily = (self.root / "user/daily/2026/2026-09/2026-09-18.md").read_text(encoding="utf-8")
        self.assertNotIn("## Failed tasks", daily)
        self.assertNotIn("send.md", daily)

    def test_routine_ignores_null_hours(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-16", do_at="07:00")
        self.aos("reindex")
        day = self.root / "user/daily/2026/2026-09/2026-09-16.md"
        day.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# 2026-09-16", "", "| hour | did |", "| --- | --- |"]
        for hour in range(24):
            did = "null"
            if hour == 7:
                did = "tiktok"
            lines.append(f"| {hour:02d}:00 | {did} |")
        lines.append("")
        day.write_text("\n".join(lines), encoding="utf-8")
        self.aos("daily-close", "2026-09-16", today="2026-09-17")
        text = day.read_text(encoding="utf-8")
        self.assertIn("| 0% | 0% |", text)
        self.assertIn("| 07:00 | tiktok |", text)
        month = (self.root / "user/daily/2026/2026-09/2026-09.md").read_text(encoding="utf-8")
        self.assertIn("| tiktok | 1 |", month)
        self.assertIn("| Send | 1 |", month)
        tomorrow = self.root / "user/daily/2026/2026-09/2026-09-17.md"
        self.assertTrue(tomorrow.is_file())
        self.assertNotIn("| routine | tasks |", tomorrow.read_text(encoding="utf-8"))

    def test_project_follows_its_tasks(self) -> None:
        write_project(self.root, "job", status="pending", prefix="J")
        path = write_unique(self.root, "first", "First", "2026-09-16")
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "infinitive: First",
                "infinitive: First\nproject: job\nphase: j-01",
            ),
            encoding="utf-8",
        )
        (self.root / "user/projects/pending/job/phases").mkdir()
        (self.root / "user/projects/pending/job/phases/j-01.md").write_text(
            """---
status: pending
project: job
depends_on: []
---

# J-01

## Plan

1. go

## Tasks

- [First](../../../tasks/pending/first.md)
""",
            encoding="utf-8",
        )
        self.aos("reindex")
        self.assertTrue((self.root / "user/projects/pending/job/job.md").is_file())
        task = self.root / "user/tasks/pending/first.md"
        task.write_text(
            task.read_text(encoding="utf-8").replace("do_on: 2026-09-16", "do_on: null"),
            encoding="utf-8",
        )
        self.aos("reindex")
        self.assertTrue((self.root / "user/tasks/paused/first.md").is_file())
        self.assertTrue((self.root / "user/projects/paused/job/job.md").is_file())
        phase = (
            self.root / "user/projects/paused/job/phases/j-01.md"
        ).read_text(encoding="utf-8")
        self.assertIn("status: paused", phase)

    def test_do_in_is_rejected(self) -> None:
        path = write_unique(self.root, "old", "Old", "2026-09-20")
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "infinitive: Old",
                'do_in: "09:00"\ninfinitive: Old',
            ),
            encoding="utf-8",
        )
        proc = subprocess.run(
            [sys.executable, str(BIN), "validate"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("do_in is not a field", proc.stderr)

    def test_migrate_layout_moves_paths_and_is_idempotent(self) -> None:
        from aos_lib.config import WEEKDAYS

        def paused(slug: str, title: str, when: str | None = None) -> Path:
            section = f"\n## When\n\n{when}\n" if when else ""
            path = self.root / "user/tasks/paused" / f"{slug}.md"
            path.write_text(
                f"""---
type: unique-independent
status: paused
do_on: null
completed_on: null
infinitive: {title}
---

# {title}

## What

do it

## How

step by step
{section}
## Goal

the state
""",
                encoding="utf-8",
            )
            return path

        study = paused("study-sql", "Study SQL", "12/10/2026, depois do café da manhã.")
        apply = paused("apply", "Apply")
        both = paused("both-days", "Both days")
        hours = ["# 2026-10-08", "", "| hour | did |", "| --- | --- |"]
        for hour in range(24):
            did = "walk" if hour == 8 else "null"
            hours.append(f"| {hour:02d}:00 | {did} |")
        hours.append("")
        old_hour = self.root / "user/daily/2026/10/08.md"
        old_hour.parent.mkdir(parents=True)
        old_hour.write_text("\n".join(hours), encoding="utf-8")
        (self.root / "user/daily/2026/10/09.md").write_text(
            """# 2026-10-09

**Result:** satisfactory

## Completed tasks

- [Study SQL](../../../tasks/paused/study-sql.md)

## Failed tasks

- [Apply](../../../tasks/paused/apply.md)
""",
            encoding="utf-8",
        )
        (self.root / "user/daily/2026/10/10.md").write_text(
            """# 2026-10-10

**Result:** failure

See [prior](../09/15.md).

## Completed tasks

## Failed tasks

- [Study SQL](../../../tasks/paused/study-sql.md)
- [Apply](../../../tasks/paused/apply.md)
""",
            encoding="utf-8",
        )
        (self.root / "user/daily/2026/09").mkdir(parents=True)
        (self.root / "user/daily/2026/09/15.md").write_text(
            """# 2026-09-15

**Result:** satisfactory

## Completed tasks
""",
            encoding="utf-8",
        )
        (self.root / "user/daily/2026/09.md").write_text("# old rollup\n", encoding="utf-8")
        grid = "# 2026-10\n\n| hour | 1 - thu |\n| --- | --- |\n| 07:00 | Breakfast |\n"
        (self.root / "user/schedule/2026").mkdir(parents=True)
        (self.root / "user/schedule/2026/10.md").write_text(grid, encoding="utf-8")
        day_dir = self.root / "user/schedule/2026/10"
        day_dir.mkdir()
        (day_dir / "12.md").write_text(
            "# 2026-10-12\n\n- [Study SQL](../../../tasks/paused/study-sql.md)\n",
            encoding="utf-8",
        )
        (day_dir / "13.md").write_text(
            "# 2026-10-13\n\n- [Apply](../../../tasks/paused/apply.md)\n",
            encoding="utf-8",
        )
        (day_dir / "14.md").write_text(
            "# 2026-10-14\n\n- [Both](../../../tasks/paused/both-days.md)\n",
            encoding="utf-8",
        )
        (day_dir / "16.md").write_text(
            "# 2026-10-16\n\n- [Both](../../../tasks/paused/both-days.md)\n",
            encoding="utf-8",
        )
        nov = self.root / "user/schedule/2026/11"
        nov.mkdir()
        (nov / "03.md").write_text(
            "# 2026-11-03\n\n- [Apply](../../../tasks/paused/apply.md)\n",
            encoding="utf-8",
        )
        (nov / "04.md").write_text("# 2026-11-04\n", encoding="utf-8")
        june = self.root / "user/schedule/2027/06"
        june.mkdir(parents=True)
        (june / "01.md").write_text(
            "# 2027-06-01\n\n- [Study SQL](../../../tasks/paused/study-sql.md)\n",
            encoding="utf-8",
        )
        (self.root / "user/research/paths.md").write_text(
            """# Paths

[day](../daily/2026/10/10.md)

[sched-day](../schedule/2026/10/12.md)

[grid](../schedule/2026/10.md)

Also daily/2026/09/15.md.
""",
            encoding="utf-8",
        )
        before = subprocess.run(
            [sys.executable, str(BIN), "validate"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(before.returncode, 0)
        self.assertIn("old daily", before.stderr)
        self.assertIn("old schedule", before.stderr)

        self.aos("migrate-layout", "2026-10-11")

        self.assertFalse((self.root / "user/daily/2026/10").exists())
        self.assertFalse((self.root / "user/daily/2026/09").exists())
        self.assertFalse((self.root / "user/daily/2026/09.md").exists())
        self.assertFalse((self.root / "user/schedule/2026/10.md").exists())
        self.assertFalse(day_dir.exists())
        self.assertFalse(nov.exists())
        self.assertFalse((self.root / "user/schedule/2027").exists())
        self.assertFalse((self.root / "user/daily/2026/2026-09/2026-09-16.md").exists())

        moved_hour = self.root / "user/daily/2026/2026-10/2026-10-08.md"
        self.assertIn("| 08:00 | walk |", moved_hour.read_text(encoding="utf-8"))
        self.assertNotIn("| routine | tasks |", moved_hour.read_text(encoding="utf-8"))

        oct_9 = (self.root / "user/daily/2026/2026-10/2026-10-09.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** satisfactory", oct_9)
        self.assertIn("| null | 50% |", oct_9)
        self.assertIn("paused/study-sql.md", oct_9)
        self.assertIn("paused/apply.md", oct_9)

        oct_10 = (self.root / "user/daily/2026/2026-10/2026-10-10.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** failure", oct_10)
        self.assertIn("| null | 0% |", oct_10)
        self.assertIn("../2026-09/2026-09-15.md", oct_10)
        self.assertNotIn("../09/15.md", oct_10)
        self.assertEqual(oct_10.count("| 00:00 | null |"), 1)

        sept = (self.root / "user/daily/2026/2026-09/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** satisfactory", sept)
        self.assertIn("| null | null |", sept)
        self.assertNotIn("## Failed tasks", sept)

        today = (self.root / "user/daily/2026/2026-10/2026-10-11.md").read_text(encoding="utf-8")
        hour_rows = [
            line for line in today.splitlines() if line.startswith("| ") and ":00 |" in line
        ]
        self.assertEqual(len(hour_rows), 24)
        self.assertNotIn("| routine | tasks |", today)

        month = (self.root / "user/daily/2026/2026-10/2026-10.md").read_text(encoding="utf-8")
        self.assertIn(
            f"| 09 | {WEEKDAYS[date(2026, 10, 9).weekday()]} | null | 50% |",
            month,
        )
        self.assertIn(
            f"| 10 | {WEEKDAYS[date(2026, 10, 10).weekday()]} | null | 0% |",
            month,
        )
        self.assertNotIn("| 08 |", month)
        self.assertNotIn("| 11 |", month)
        self.assertIn("| null | 25% |", month)
        sept_month = (self.root / "user/daily/2026/2026-09/2026-09.md").read_text(encoding="utf-8")
        self.assertIn(
            f"| 15 | {WEEKDAYS[date(2026, 9, 15).weekday()]} | null | null |",
            sept_month,
        )
        self.assertNotIn("old rollup", sept_month)

        renamed = (self.root / "user/schedule/2026/2026-10.md").read_text(encoding="utf-8")
        self.assertEqual(renamed, grid)

        study_text = study.read_text(encoding="utf-8")
        self.assertIn("12/10/2026", study_text)
        self.assertNotIn("2026-10-12", study_text)
        self.assertIn("2027-06-01", study_text)
        self.assertIn("do_on: null", study_text)
        apply_text = apply.read_text(encoding="utf-8")
        apply_when = apply_text.split("## When", 1)[1]
        self.assertLess(apply_when.index("2026-10-13"), apply_when.index("2026-11-03"))
        self.assertIn("do_on: null", apply_text)
        both_when = both.read_text(encoding="utf-8").split("## When", 1)[1]
        self.assertLess(both_when.index("2026-10-14"), both_when.index("2026-10-16"))

        paths = (self.root / "user/research/paths.md").read_text(encoding="utf-8")
        self.assertIn("../daily/2026/2026-10/2026-10-10.md", paths)
        self.assertIn("../schedule/2026/2026-10.md", paths)
        self.assertIn("daily/2026/2026-09/2026-09-15.md", paths)
        self.assertNotIn("daily/2026/10/10.md", paths)
        self.assertNotIn("schedule/2026/10/12.md", paths)
        self.assertNotIn("schedule/2026/10.md)", paths)

        self.aos("validate")
        first = _tree_bytes(self.root)
        self.aos("migrate-layout", "2026-10-11")
        self.assertEqual(first, _tree_bytes(self.root))

    def test_migrate_layout_defaults_to_sao_paulo_today(self) -> None:
        self.aos("migrate-layout", today="2026-10-11")
        today = self.root / "user/daily/2026/2026-10/2026-10-11.md"
        self.assertTrue(today.is_file())
        self.assertNotIn("| routine | tasks |", today.read_text(encoding="utf-8"))
        self.assertTrue((self.root / "user/daily/2026/2026-10/2026-10.md").is_file())
        first = _tree_bytes(self.root)
        self.aos("migrate-layout", today="2026-10-11")
        self.assertEqual(first, _tree_bytes(self.root))

    def test_migrate_layout_keeps_a_differing_grid(self) -> None:
        year = self.root / "user/schedule/2026"
        year.mkdir(parents=True)
        (year / "10.md").write_text("# old\n", encoding="utf-8")
        (year / "2026-10.md").write_text("# new\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(BIN), "migrate-layout", "2026-10-11"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("kept:", proc.stdout)
        self.assertEqual((year / "10.md").read_text(encoding="utf-8"), "# old\n")
        self.assertEqual((year / "2026-10.md").read_text(encoding="utf-8"), "# new\n")
        first = _tree_bytes(self.root)
        again = subprocess.run(
            [sys.executable, str(BIN), "migrate-layout", "2026-10-11"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(again.returncode, 0)
        self.assertEqual(first, _tree_bytes(self.root))

    def test_migrate_layout_keeps_an_unresolved_day(self) -> None:
        day = self.root / "user/schedule/2026/10/12.md"
        day.parent.mkdir(parents=True)
        day.write_text("# 2026-10-12\n\n- leftover note\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(BIN), "migrate-layout", "2026-10-11"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertTrue(day.is_file())
        self.assertIn("leftover note", day.read_text(encoding="utf-8"))
        first = _tree_bytes(self.root)
        again = subprocess.run(
            [sys.executable, str(BIN), "migrate-layout", "2026-10-11"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(again.returncode, 0)
        self.assertEqual(first, _tree_bytes(self.root))

    def test_migrate_vault_rewrites_history_and_is_idempotent(self) -> None:
        pending = self.root / "user/tasks/pending/send.md"
        pending.write_text(
            """---
type: unique-project
infinitive: Send the letter
status: pending
due: 2026-10-12
do_after: breakfast
completed_on: null
project: job
phase: j-01
---

# Send the letter

## What

do it

## How

step by step

## Goal

the state
""",
            encoding="utf-8",
        )
        (self.root / "user/tasks/ongoing/breakfast.md").write_text(
            """---
type: maintenance
infinitive: Breakfast
status: ongoing
do_in: "07:00"
done_on: []
cadence:
  kind: daily
---

# Breakfast

## What

eat

## How

eat

## When

every morning
""",
            encoding="utf-8",
        )
        (self.root / "user/tasks/completed/old.md").write_text(
            """---
type: unique-independent
infinitive: Finish the old one
status: completed
due: 2026-10-06
do_after: breakfast
completed_on: 2026-10-06
---

# Finish the old one

## What

done

## How

done

## Goal

done
""",
            encoding="utf-8",
        )
        (self.root / "user/tasks/ongoing/live.md").write_text(
            """---
type: recurring-independent
infinitive: Practice
status: ongoing
due: null
do_after: breakfast
until_event: the goal
project: job
done_on: []
cadence:
  kind: daily
---

# Practice

## What

practice

## How

practice

## When

after breakfast
""",
            encoding="utf-8",
        )
        hub_dir = self.root / "user/projects/pending/job"
        (hub_dir / "phases").mkdir(parents=True)
        (hub_dir / "job.md").write_text(
            """---
status: pending
due: null
prefix: J
---

# Job

## Goal

the goal

## Plan

1. do

## Phases

- [J-01](phases/j-01.md)
""",
            encoding="utf-8",
        )
        (hub_dir / "phases/j-01.md").write_text(
            """---
status: pending
due: null
project: job
---

# J-01

## Goal

the goal

## Plan

1. do

## Tasks

- [Send](../../../../tasks/pending/send.md)
""",
            encoding="utf-8",
        )
        day = self.root / "user/schedule/2026/10/12.md"
        day.parent.mkdir(parents=True)
        day.write_text(
            "# 2026-10-12\n\n- [Send](../../../tasks/pending/send.md)\n",
            encoding="utf-8",
        )
        (self.root / "user/daily/2026/10/10.md").parent.mkdir(parents=True)
        (self.root / "user/daily/2026/10/10.md").write_text(
            """# 2026-10-10

**Result:** failure

## Completed tasks

## Failed tasks

- [Send](../../../tasks/pending/send.md)
""",
            encoding="utf-8",
        )

        preview = self.aos("migrate", "--dry-run", "2026-10-11")
        self.assertIn("dry-run:", preview.stdout)
        self.assertIn("due: 2026-10-12", pending.read_text(encoding="utf-8"))
        self.assertTrue(pending.is_file())

        self.aos("migrate", "2026-10-11")

        paused = (self.root / "user/tasks/paused/send.md").read_text(encoding="utf-8")
        self.assertIn("status: paused", paused)
        self.assertNotIn("due:", paused)
        self.assertNotIn("do_on:", paused)
        self.assertNotIn("do_after:", paused)
        self.assertNotIn("do_at:", paused)
        self.assertFalse(pending.exists())
        self.assertFalse((self.root / "user/tasks/pending").exists())

        breakfast = (self.root / "user/tasks/ongoing/breakfast.md").read_text(encoding="utf-8")
        self.assertIn('do_at: ["07:00"]', breakfast)
        self.assertNotIn("do_in:", breakfast)
        self.assertIn("status: ongoing", breakfast)

        done = (self.root / "user/tasks/completed/old.md").read_text(encoding="utf-8")
        self.assertIn("do_on: 2026-10-06", done)
        self.assertNotIn("due:", done)
        self.assertNotIn("do_after:", done)

        live = (self.root / "user/tasks/ongoing/live.md").read_text(encoding="utf-8")
        self.assertIn("do_on: null", live)
        self.assertNotIn("do_after:", live)
        self.assertNotIn("\ndue:", "\n" + live)

        hub = (self.root / "user/projects/ongoing/job/job.md").read_text(encoding="utf-8")
        self.assertIn("status: ongoing", hub)
        self.assertIn("do_on: null", hub)
        self.assertFalse((self.root / "user/projects/pending").exists())
        phase = (self.root / "user/projects/ongoing/job/phases/j-01.md").read_text(encoding="utf-8")
        self.assertIn("status: paused", phase)
        self.assertIn("tasks/paused/send.md", phase)
        self.assertNotIn("tasks/pending/send.md", phase)

        self.assertFalse(day.exists())
        self.assertIn("2026-10-12", paused)
        self.assertFalse((self.root / "user/schedule/2026/2026-10.md").is_file())
        today = self.root / "user/daily/2026/2026-10/2026-10-11.md"
        self.assertTrue(today.is_file())
        self.assertNotIn("| routine | tasks |", today.read_text(encoding="utf-8"))
        month = (self.root / "user/daily/2026/2026-10/2026-10.md").read_text(encoding="utf-8")
        self.assertIn("| null | 0% |", month)
        daily = (self.root / "user/daily/2026/2026-10/2026-10-10.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** failure", daily)
        self.assertIn("tasks/paused/send.md", daily)
        self.aos("validate")
        first = _tree_bytes(self.root)
        self.aos("migrate", "2026-10-11")
        self.assertEqual(first, _tree_bytes(self.root))

    def test_october_weeks_and_maintenance_does_not_open_a_month(self) -> None:
        from aos_lib.schedule import parse_month, week_spans

        self.assertEqual(week_spans(2026, 10), [(1, 3), (4, 10), (11, 17), (18, 24), (25, 31)])
        self.assertEqual(len(week_spans(2026, 2)), 4)
        self.assertEqual(len(week_spans(2026, 5)), 6)
        box = self.root / "user/tasks/ongoing/box.md"
        box.write_text(
            """---
type: maintenance
status: ongoing
infinitive: Box upkeep
do_at: ["07:00"]
done_on: []
cadence:
  kind: daily
---

# Box upkeep

## What

keep

## How

do
""",
            encoding="utf-8",
        )
        self.aos("reindex", today="2026-10-11")
        self.assertFalse((self.root / "user/schedule/2026/2026-10.md").is_file())
        write_unique(self.root, "send", "Send", "2026-10-11", do_at="09:00")
        self.aos("reindex", today="2026-10-11")
        month = self.root / "user/schedule/2026/2026-10.md"
        text = month.read_text(encoding="utf-8")
        self.assertEqual(text.count("\n| hour |"), 5)
        self.assertIn("| hour | 1 - thu | 2 - fri | 3 - sat |", text)
        self.assertIn(
            "| hour | 4 - sun | 5 - mon | 6 - tue | 7 - wed | 8 - thu | 9 - fri | 10 - sat |",
            text,
        )
        self.assertIn("| hour | 25 - sun | 26 - mon | 27 - tue | 28 - wed | 29 - thu | 30 - fri | 31 - sat |", text)
        cells = parse_month(text)
        self.assertEqual(cells[11][9], "Send")
        self.assertEqual(cells[11][7], "Box upkeep")
        self.assertEqual(cells[1][7], "Box upkeep")
        self.assertEqual(cells[12][9], "null")
        self.assertFalse((self.root / "user/schedule/2026/2026-11.md").is_file())

    def test_recurring_projects_cadence_through_until(self) -> None:
        from aos_lib.schedule import parse_month

        write_recurring(
            self.root,
            "training",
            "Training",
            kind="weekdays",
            days=["tue", "fri"],
            until="2026-11-30",
            due="2026-10-01",
            do_at="08:00",
            folder="pending",
            status="pending",
        )
        self.aos("reindex", today="2026-10-11")
        text = self.tasks_md()
        self.assertIn("pending/training.md", section_items(text, "Overdue")[0])
        self.assertNotIn("## 1 day", text)
        october = parse_month(
            (self.root / "user/schedule/2026/2026-10.md").read_text(encoding="utf-8")
        )
        self.assertEqual(october[1][8], "null")
        self.assertEqual(october[2][8], "Training")
        self.assertEqual(october[6][8], "Training")
        november = self.root / "user/schedule/2026/2026-11.md"
        self.assertTrue(november.is_file())
        nov = parse_month(november.read_text(encoding="utf-8"))
        self.assertEqual(nov[3][8], "Training")
        self.assertFalse((self.root / "user/schedule/2026/2026-12.md").is_file())

    def test_recurring_without_until_stops_at_the_current_month(self) -> None:
        from aos_lib.schedule import parse_month

        write_unique(self.root, "open", "Open", "2026-10-11", do_at="09:00")
        write_recurring(
            self.root,
            "habit",
            "Habit",
            kind="daily",
            due="2026-10-11",
            do_at="08:00",
            until_event="later",
        )
        self.aos("reindex", today="2026-10-11")
        cells = parse_month(
            (self.root / "user/schedule/2026/2026-10.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[10][8], "null")
        self.assertEqual(cells[11][8], "Habit")
        self.assertEqual(cells[31][8], "Habit")
        self.assertFalse((self.root / "user/schedule/2026/2026-11.md").is_file())

    def _college(self, *, until: str | None = None, until_event: str | None = None) -> None:
        lines = [
            "---",
            "type: recurring-independent",
            "infinitive: Fazer trabalhos da faculdade",
            "status: ongoing",
            "do_on: 2026-10-12",
            'do_at: ["07:00"]',
            "done_on: []",
        ]
        if until is not None:
            lines.append(f"until: {until}")
        if until_event is not None:
            lines.append(f"until_event: {until_event}")
        lines.extend(
            [
                "cadence:",
                "  kind: month-weekday",
                "  day: mon",
                "  n: [2, 4]",
                "---",
                "",
                "# Trabalhos da faculdade",
                "",
                "## What",
                "",
                "assignments",
                "",
                "## How",
                "",
                "do them",
                "",
            ]
        )
        path = self.root / "user/tasks/ongoing/college-assignments.md"
        path.write_text("\n".join(lines), encoding="utf-8")

    def _touch_month(self, year: int, month: int) -> None:
        from aos_lib.schedule import month_path

        path = month_path(self.root, year, month)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {year:04d}-{month:02d}\n", encoding="utf-8")

    def test_college_until_event_fills_existing_october_and_november(self) -> None:
        from aos_lib.schedule import parse_month

        self._touch_month(2026, 10)
        self._touch_month(2026, 11)
        self._college(until_event="graduation")
        self.aos("reindex", today="2026-10-11")
        october = parse_month(
            (self.root / "user/schedule/2026/2026-10.md").read_text(encoding="utf-8")
        )
        november = parse_month(
            (self.root / "user/schedule/2026/2026-11.md").read_text(encoding="utf-8")
        )
        label = "Fazer trabalhos da faculdade"
        self.assertEqual(october[5][7], "null")
        self.assertEqual(october[12][7], label)
        self.assertEqual(october[26][7], label)
        self.assertEqual(november[2][7], "null")
        self.assertEqual(november[9][7], label)
        self.assertEqual(november[23][7], label)
        self.assertFalse((self.root / "user/schedule/2026/2026-12.md").is_file())

    def test_college_until_fills_existing_months_and_stops_on_the_date(self) -> None:
        from aos_lib.schedule import parse_month

        self._touch_month(2026, 10)
        self._touch_month(2026, 11)
        self._touch_month(2030, 8)
        self._college(until="2030-07-01")
        self.aos("reindex", today="2026-10-11")
        october = parse_month(
            (self.root / "user/schedule/2026/2026-10.md").read_text(encoding="utf-8")
        )
        november = parse_month(
            (self.root / "user/schedule/2026/2026-11.md").read_text(encoding="utf-8")
        )
        august = parse_month(
            (self.root / "user/schedule/2030/2030-08.md").read_text(encoding="utf-8")
        )
        label = "Fazer trabalhos da faculdade"
        self.assertEqual(october[12][7], label)
        self.assertEqual(october[26][7], label)
        self.assertEqual(november[9][7], label)
        self.assertEqual(november[23][7], label)
        self.assertFalse((self.root / "user/schedule/2026/2026-12.md").is_file())
        self.assertTrue((self.root / "user/schedule/2030/2030-07.md").is_file())
        july = parse_month(
            (self.root / "user/schedule/2030/2030-07.md").read_text(encoding="utf-8")
        )
        self.assertNotIn(label, july[1].values())
        for day in august:
            self.assertNotIn(label, august[day].values())

    def test_reindex_writes_completed_on_the_open_daily(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-16", do_at="08:00")
        self.aos("reindex")
        day = self.root / "user/daily/2026/2026-09/2026-09-16.md"
        day.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# 2026-09-16", "", "| hour | did |", "| --- | --- |"]
        for hour in range(24):
            did = "tiktok" if hour == 7 else "null"
            lines.append(f"| {hour:02d}:00 | {did} |")
        lines.extend(["", "## Notes, optional", "", "kept", ""])
        day.write_text("\n".join(lines), encoding="utf-8")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("reindex")
        text = day.read_text(encoding="utf-8")
        self.assertIn("## Completed tasks", text)
        self.assertIn("tasks/completed/send.md", text)
        self.assertIn("| 07:00 | tiktok |", text)
        self.assertIn("kept", text)
        self.assertNotIn("| routine | tasks |", text)
        from aos_lib.schedule import parse_month

        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[16][8], "null")

    def test_sync_command_is_gone(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(BIN), "sync"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("sync", proc.stderr.lower())


def _tree_bytes(root: Path) -> dict[str, bytes]:
    found: dict[str, bytes] = {}
    for path in sorted((root / "user").rglob("*")):
        if path.is_file():
            found[path.relative_to(root).as_posix()] = path.read_bytes()
    return found


class GitUtilTest(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        base = Path(self._td.name)
        self.remote = base / "remote.git"
        _git(base, "init", "--bare", "-b", "main", str(self.remote))
        self.root = base / "aos"
        self.root.mkdir()
        init_aos(self.root)
        _git(self.root, "branch", "-M", "main")
        _git(self.root, "remote", "add", "origin", str(self.remote))
        _git(self.root, "push", "-u", "origin", "main")

    def tearDown(self) -> None:
        self._td.cleanup()

    def remote_head(self) -> str:
        return _git(self.remote, "rev-parse", "main").stdout.strip()

    def test_commit_waits_for_foreign_index_lock(self) -> None:
        from aos_lib import gitutil

        lock = self.root / ".git/index.lock"
        lock.write_text("", encoding="utf-8")
        seed_daily(self.root, "2026-09-15", "# day\n")
        timer = threading.Timer(0.3, lock.unlink)
        timer.start()
        try:
            with mock.patch.object(gitutil, "INDEX_LOCK_WAIT_S", 0.2):
                self.assertTrue(gitutil.commit_user(self.root, "aos: test lock"))
        finally:
            timer.join()
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos: test lock")

    def test_sync_commits_and_pushes_with_vault_identity(self) -> None:
        from aos_lib.gitutil import sync_vault

        _git(self.root, "config", "user.name", "Vault Keeper")
        _git(self.root, "config", "user.email", "keeper@vault.example")
        seed_daily(self.root, "2026-09-15", "# day\n")
        self.assertTrue(sync_vault(self.root, "aos reindex"))
        head = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.remote_head(), head)
        log = _git(self.root, "log", "-1", "--format=%an%n%ae%n%s")
        self.assertEqual(
            log.stdout.splitlines(),
            ["Vault Keeper", "keeper@vault.example", "aos reindex"],
        )
        self.assertEqual(_git(self.root, "config", "user.name").stdout.strip(), "Vault Keeper")
        self.assertEqual(
            _git(self.root, "config", "user.email").stdout.strip(),
            "keeper@vault.example",
        )

    def test_sync_skips_commit_when_clean(self) -> None:
        from aos_lib.gitutil import sync_vault

        head = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertFalse(sync_vault(self.root, "aos reindex"))
        self.assertEqual(_git(self.root, "rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual(self.remote_head(), head)

    def test_failed_push_stays_local_until_the_next_sync(self) -> None:
        import io
        from contextlib import redirect_stderr

        from aos_lib.gitutil import sync_vault

        seed_daily(self.root, "2026-09-15", "# day\n")
        url = _git(self.root, "remote", "get-url", "origin").stdout.strip()
        before = self.remote_head()
        _git(self.root, "remote", "set-url", "--push", "origin", str(self.root / "missing.git"))
        buf = io.StringIO()
        with redirect_stderr(buf):
            self.assertTrue(sync_vault(self.root, "aos reindex"))
        self.assertIn("git push failed", buf.getvalue())
        local = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(local, before)
        self.assertEqual(self.remote_head(), before)
        _git(self.root, "remote", "set-url", "--push", "origin", url)
        self.assertFalse(sync_vault(self.root, "aos reindex"))
        self.assertEqual(self.remote_head(), local)

    def test_concurrent_sync_does_not_lock_ref(self) -> None:
        import io
        from contextlib import redirect_stderr

        from aos_lib.gitutil import sync_vault

        errors: list[BaseException] = []

        def one(name: str) -> None:
            try:
                path = self.root / "user" / f"{name}.md"
                path.write_text(f"# {name}\n", encoding="utf-8")
                sync_vault(self.root, f"aos {name}")
            except BaseException as exc:  # noqa: BLE001 — recorded for the assertion
                errors.append(exc)

        buf = io.StringIO()
        with redirect_stderr(buf):
            threads = [
                threading.Thread(target=one, args=(name,)) for name in ("alpha", "beta")
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        self.assertEqual(errors, [])
        self.assertNotIn("cannot lock ref", buf.getvalue())
        for name in ("alpha", "beta"):
            shown = _git(self.remote, "cat-file", "-e", f"main:user/{name}.md", check=False)
            self.assertEqual(shown.returncode, 0, shown.stderr)

    def test_rebase_conflict_aborts_without_force(self) -> None:
        import io
        from contextlib import redirect_stderr

        from aos_lib.gitutil import sync_vault

        other = self.root.parent / "other"
        _git(self.root.parent, "clone", str(self.remote), str(other))
        _git(other, "config", "user.name", "Other")
        _git(other, "config", "user.email", "other@localhost")
        (other / "user" / "preferences.md").write_text(
            "# Preferences\n\nremote\n", encoding="utf-8"
        )
        _git(other, "add", "-A")
        _git(other, "commit", "-m", "remote edit")
        _git(other, "push")
        (self.root / "user" / "preferences.md").write_text(
            "# Preferences\n\nlocal\n", encoding="utf-8"
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            self.assertTrue(sync_vault(self.root, "aos reindex"))
        text = buf.getvalue()
        self.assertIn("rebase conflict", text)
        self.assertIn("aborted without force", text)
        self.assertNotIn("--force", text)
        self.assertFalse((self.root / ".git" / "rebase-merge").exists())
        self.assertFalse((self.root / ".git" / "rebase-apply").exists())
        local = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(self.remote_head(), local)
        self.assertEqual(
            _git(self.remote, "log", "-1", "--pretty=%s").stdout.strip(),
            "remote edit",
        )
        self.assertEqual(
            _git(self.root, "log", "-1", "--pretty=%s").stdout.strip(),
            "aos reindex",
        )

    def test_failed_push_does_not_fail_daily_close(self) -> None:
        from aos_lib.daily import daily_close

        _git(self.root, "remote", "set-url", "origin", str(self.root / "missing.git"))
        path = daily_close(self.root, date(2026, 9, 15), today=date(2026, 9, 16))
        self.assertTrue(path.is_file())
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos daily-close 2026-09-15")

    def test_git_never_prompts(self) -> None:
        from aos_lib import gitutil

        self.assertEqual(gitutil._env()["GIT_TERMINAL_PROMPT"], "0")


if __name__ == "__main__":
    unittest.main()
