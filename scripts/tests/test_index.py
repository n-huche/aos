from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import threading
from datetime import date

from helpers import (
    AOSTest,
    TODAY,
    _band_items,
    _git,
    headings,
    mark,
    section_items,
    write_project,
    write_recurring,
    write_unique,
)

from aos_lib.index import _merge_section
from aos_lib.yamlfm import split_frontmatter


class IndexTest(AOSTest):
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
            mark(text, heading="Today"), encoding="utf-8"
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
        text = mark(self.tasks_md(), heading="+30 days")
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
        path.write_text(mark(self.tasks_md(), heading="1 day"), encoding="utf-8")
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
        path.write_text(mark(self.tasks_md(), heading="2-3 days"), encoding="utf-8")
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
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
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
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
        self.aos("reindex")
        phase_path = (
            self.root / "user/projects/completed/demo/phases/de-01-one.md"
        )
        phase = phase_path.read_text(encoding="utf-8")
        self.assertIn("tasks/completed/send.md", phase)
        self.assertNotIn("tasks/pending/send.md", phase)

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
        overdue = section_items(self.tasks_md(), "Overdue")
        self.assertEqual(overdue.count("- [ ] [Drink water](ongoing/water.md)"), 2)
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark(self.tasks_md(), heading="Overdue", first=True), encoding="utf-8")
        self.aos("reindex")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/water.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-09-15")
        self.assertEqual([d.isoformat() for d in data.get("done_on") or []], [TODAY])
        self.assertEqual(
            section_items(self.tasks_md(), "Overdue").count(
                "- [ ] [Drink water](ongoing/water.md)"
            ),
            1,
        )
        self.assertNotIn("- [x]", self.tasks_md())

    def test_overdue_weekdays_stack_and_each_check_advances_once(self) -> None:
        write_recurring(
            self.root,
            "live-coding",
            "Live coding",
            kind="weekdays",
            days=["tue", "thu", "sat"],
            until="2026-12-01",
            due="2026-10-08",
            do_at="19:00",
        )
        self.aos("reindex", today="2026-10-11")
        line = "- [ ] [Live coding](ongoing/live-coding.md)"
        self.assertEqual(section_items(self.tasks_md(), "Overdue").count(line), 2)
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark(self.tasks_md(), heading="Overdue", first=True), encoding="utf-8")
        self.aos("reindex", today="2026-10-11")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/live-coding.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-10-10")
        self.assertEqual(section_items(self.tasks_md(), "Overdue").count(line), 1)
        path.write_text(mark(self.tasks_md(), heading="Overdue", first=True), encoding="utf-8")
        self.aos("reindex", today="2026-10-11")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/live-coding.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-10-13")
        self.assertEqual(section_items(self.tasks_md(), "Overdue"), [])
        self.assertIn(line, section_items(self.tasks_md(), "2-3 days"))

    def test_concurrent_reindex_applies_one_check_once(self) -> None:
        from aos_lib.index import reindex

        write_recurring(
            self.root,
            "live-coding",
            "Live coding",
            kind="weekdays",
            days=["tue", "thu", "sat"],
            until="2026-12-01",
            due="2026-10-10",
            do_at="19:00",
        )
        self.aos("reindex", today="2026-10-11")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark(self.tasks_md(), heading="Overdue", first=True), encoding="utf-8")
        today = date(2026, 10, 11)
        barrier = threading.Barrier(2)
        errors: list[BaseException] = []

        def once() -> None:
            try:
                barrier.wait(timeout=5)
                reindex(self.root, today, commit=False)
            except BaseException as exc:  # noqa: BLE001 — recorded for the assertion
                errors.append(exc)

        threads = [threading.Thread(target=once) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/live-coding.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-10-13")
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
        self.assertEqual(cells[16][7], "split")
        self.assertEqual(cells[16][18], "split")

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
