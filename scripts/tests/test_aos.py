from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import date
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent / "aos"
SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

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
        "user/tasks/recurring",
        "user/tasks/completed",
        "user/tasks/obsolete",
        "user/tasks/canceled",
        "user/daily",
        "user/research",
        "user/schedule",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / "user/tasks/tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (root / "user/preferences.md").write_text("# Preferences\n", encoding="utf-8")
    _git(root, "init")
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
) -> Path:
    due_s = "null" if due is None else due
    completed_s = "null" if completed_on is None else completed_on
    path = root / "user" / "tasks" / folder / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
type: unique-independent
status: {status}
due: {due_s}
completed_on: {completed_s}
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
    folder: str = "recurring",
    status: str = "recurring",
    project: str | None = None,
    phase: str | None = None,
) -> Path:
    lines = [
        "---",
        f"type: {type_}",
        f"status: {status}",
    ]
    if until is not None:
        lines.append(f"until: {until}")
    if until_event is not None:
        lines.append(f"until_event: {until_event}")
    if project is not None:
        lines.append(f"project: {project}")
    if phase is not None:
        lines.append(f"phase: {phase}")
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
due: null
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
        e["AOS_GIT_NAME"] = "AOS"
        e["AOS_GIT_EMAIL"] = "aos@localhost"
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
                "Undefined",
            ],
        )
        self.assertIn("pending/overdue-one.md", section_items(text, "Overdue")[0])
        self.assertIn("pending/today-one.md", section_items(text, "Today")[0])
        self.assertIn("pending/tomorrow-one.md", section_items(text, "1 day")[0])
        self.assertIn("pending/week-one.md", section_items(text, "4-7 days")[0])
        self.assertIn("pending/month-one.md", section_items(text, "8-30 days")[0])
        self.assertIn("pending/later-one.md", section_items(text, "+30 days")[0])
        self.assertIn("pending/open-one.md", section_items(text, "Undefined")[0])
        self.assertNotIn("## 2-3 days", text)

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
        self.assertIn("recurring/water.md", section_items(text, "Today")[0])
        self.assertIn("recurring/water.md", section_items(text, "1 day")[0])
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
        self.assertIn("recurring/training.md", section_items(text, "4-7 days")[0])

    def test_recurring_project_inert_while_hub_pending(self) -> None:
        write_project(self.root, "demo", status="pending")
        write_recurring(
            self.root,
            "habit",
            "Habit",
            kind="daily",
            until="2026-12-01",
            type_="recurring-project",
            project="demo",
            phase="d-01-x",
        )
        self.aos("reindex")
        text = self.tasks_md()
        self.assertNotIn("habit.md", text)
        self.assertNotIn("## Today", text)
        self.aos("daily-close", "2026-09-16", today="2026-09-17")
        daily = (self.root / "user/daily/2026-09-16.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** satisfactory", daily)
        self.assertNotIn("## Failed tasks", daily)

        pending = self.root / "user/projects/pending/demo"
        ongoing = self.root / "user/projects/ongoing/demo"
        ongoing.parent.mkdir(parents=True, exist_ok=True)
        pending.rename(ongoing)
        self.aos("reindex")
        text = self.tasks_md()
        self.assertIn("recurring/habit.md", section_items(text, "Today")[0])

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
        self.assertIn("recurring/review-now.md", section_items(text, "Today")[0])
        later = section_items(text, "+30 days")
        hrefs = " ".join(later)
        self.assertIn("recurring/review-now.md", hrefs)
        self.assertIn("recurring/review-y.md", hrefs)
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
        self.assertNotIn("recurring/", " ".join(overdue_items))
        self.assertIn("recurring/daily-habit.md", section_items(text, "Today")[0])

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
        self.aos("sync")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/recurring/water.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("done_on") or [], [])
        self.assertTrue((self.root / "user/tasks/recurring/water.md").is_file())
        text = self.tasks_md()
        self.assertTrue(all("- [ ]" in ln or not ln.startswith("- [") for ln in text.splitlines()))
        self.assertIn("- [ ] [Drink water](recurring/water.md)", section_items(text, "1 day"))

    def test_x_unique_moves_completed_on_commit(self) -> None:
        write_unique(self.root, "send-email", "Send email", "2026-09-18")
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "2-3 days"), encoding="utf-8")
        self.aos("sync")
        old = self.root / "user/tasks/pending/send-email.md"
        new = self.root / "user/tasks/completed/send-email.md"
        self.assertFalse(old.exists())
        self.assertTrue(new.is_file())
        data, _body = split_frontmatter(new.read_text(encoding="utf-8"))
        self.assertEqual(str(data.get("status")), "completed")
        self.assertEqual(data.get("completed_on").isoformat(), TODAY)
        self.assertEqual(data.get("due").isoformat(), "2026-09-18")
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos: sync tasks")
        self.assertNotIn("send-email", self.tasks_md())

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
        self.aos("sync")
        rec = self.root / "user/tasks/recurring/water.md"
        self.assertTrue(rec.is_file())
        data, _body = split_frontmatter(rec.read_text(encoding="utf-8"))
        done = data.get("done_on") or []
        self.assertEqual([d.isoformat() for d in done], [TODAY])
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos: sync tasks")
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
            "# 2026-09-16\n\n- [Cycle](../../../tasks/recurring/cycle.md)\n",
            encoding="utf-8",
        )
        self.aos("daily-close", "2026-09-15")
        self.assertFalse((self.root / "user/tasks/recurring/cycle.md").exists())
        completed = self.root / "user/tasks/completed/cycle.md"
        self.assertTrue(completed.is_file())
        data, _body = split_frontmatter(completed.read_text(encoding="utf-8"))
        self.assertEqual(str(data.get("status")), "completed")
        daily = (self.root / "user/daily/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** failure", daily)
        self.assertIn("## Failed tasks", daily)
        self.assertIn("completed/cycle.md", daily)
        log = _git(self.root, "log", "-1", "--pretty=%s")
        self.assertEqual(log.stdout.strip(), "aos: daily-close 2026-09-15")

    def test_past_schedule_removed(self) -> None:
        sched = self.root / "user/schedule"
        (sched / "2026/09").mkdir(parents=True, exist_ok=True)
        (sched / "2026/09/14.md").write_text("# 14\n", encoding="utf-8")
        (sched / "2026/09/15.md").write_text("# 15\n", encoding="utf-8")
        (sched / "2026/09/16.md").write_text("# 16\n", encoding="utf-8")
        self.aos("daily-close", "2026-09-15")
        self.assertFalse((sched / "2026/09/14.md").exists())
        self.assertFalse((sched / "2026/09/15.md").exists())
        self.assertTrue((sched / "2026/09/16.md").exists())

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
        bad = self.root / "user/tasks/recurring/bad.md"
        bad.write_text(
            """---
type: recurring-independent
status: recurring
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
due: null
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
due: null
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
        write_unique(self.root, "send", "Send", "2026-09-16")
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("sync")
        phase = (proj / "phases/de-01-one.md").read_text(encoding="utf-8")
        self.assertIn("tasks/completed/send.md", phase)
        self.assertNotIn("tasks/pending/send.md", phase)

    def test_unique_complete_drops_schedule(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-16")
        write_unique(self.root, "keep", "Keep", "2026-09-20")
        sched = self.root / "user/schedule/2026/09"
        sched.mkdir(parents=True, exist_ok=True)
        (sched / "16.md").write_text(
            """# 2026-09-16

- [Send](../../../tasks/pending/send.md)
- [Keep](../../../tasks/pending/keep.md)
""",
            encoding="utf-8",
        )
        (sched / "20.md").write_text(
            """# 2026-09-20

- [Send](../../../tasks/pending/send.md)
""",
            encoding="utf-8",
        )
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark_section(self.tasks_md(), "Today"), encoding="utf-8")
        self.aos("sync")
        day16 = (sched / "16.md").read_text(encoding="utf-8")
        self.assertNotIn("send.md", day16)
        self.assertIn("keep.md", day16)
        self.assertFalse((sched / "20.md").is_file())
        phase_ok = self.root / "user/tasks/completed/send.md"
        self.assertTrue(phase_ok.is_file())

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
            self.assertFalse((self.root / "user/daily/2026-09-15.md").exists())
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
        (self.root / "user/daily/2026-09-15.md").write_text("# 15\n", encoding="utf-8")
        self.assertEqual(missing_close_dates(self.root, today), [])
        (self.root / "user/daily/2026-09-15.md").unlink()
        (self.root / "user/daily/2026-09-13.md").write_text("# 13\n", encoding="utf-8")
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
        rec = self.root / "user/tasks/recurring/water.md"
        data_r, _body = split_frontmatter(rec.read_text(encoding="utf-8"))
        self.assertEqual(
            [d.isoformat() for d in (data_r.get("done_on") or [])],
            ["2026-09-16"],
        )
        daily = (self.root / "user/daily/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("**Result:** failure", daily)
        self.assertIn("## Failed tasks", daily)
        self.assertIn("send-email.md", daily)
        self.assertIn("recurring/water.md", daily)
        self.assertFalse((sched / "2026/09/15.md").exists())
        self.assertTrue((sched / "2026/09/16.md").exists())
        text = self.tasks_md()
        self.assertNotIn("send-email", text)
        self.assertNotIn("## Today", text)
        self.assertIn("recurring/water.md", section_items(text, "1 day")[0])

    def test_catch_up_today_unique_completes_on_recovery_day(self) -> None:
        from aos_lib.daily import catch_up

        (self.root / "user/daily/2026-09-14.md").write_text(
            "# 2026-09-14\n\n**Result:** satisfactory\n",
            encoding="utf-8",
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
        daily = (self.root / "user/daily/2026-09-15.md").read_text(encoding="utf-8")
        self.assertNotIn("today-task.md", daily)

    def test_catch_up_two_missed_days(self) -> None:
        from aos_lib.daily import catch_up

        (self.root / "user/daily/2026-09-13.md").write_text(
            "# 2026-09-13\n\n**Result:** satisfactory\n",
            encoding="utf-8",
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
        d14 = (self.root / "user/daily/2026-09-14.md").read_text(encoding="utf-8")
        self.assertIn("## Failed tasks", d14)
        self.assertIn("letter.md", d14)
        d15 = (self.root / "user/daily/2026-09-15.md").read_text(encoding="utf-8")
        self.assertIn("## Failed tasks", d15)
        self.assertIn("letter.md", d15)
        self.assertFalse((sched / "2026/09/14.md").exists())
        self.assertFalse((sched / "2026/09/15.md").exists())
        self.assertTrue((sched / "2026/09/16.md").exists())

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
        self.assertEqual(log.stdout.strip(), "aos: daily-close 2026-09-15")
        self.assertEqual(_git(user, "status", "--porcelain").stdout.strip(), "")
        self.assertTrue((user / "daily/2026-09-15.md").is_file())


if __name__ == "__main__":
    unittest.main()
