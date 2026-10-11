from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from helpers import (
    AOSTest,
    _band_items,
    mark,
    section_items,
    seed_daily,
    write_project,
    write_recurring,
    write_unique,
)

from aos_lib.yamlfm import split_frontmatter


class ScheduleTest(AOSTest):
    def test_past_schedule_removed(self) -> None:
        """Closed columns stay. daily-close does not delete the month grid."""
        write_unique(self.root, "send", "Send", "2026-09-16", do_at="07:30")
        self.aos("reindex", today="2026-09-16")
        month = self.root / "user/schedule/2026/2026-09.md"
        self.assertTrue(month.is_file())
        self.assertIn("send", month.read_text(encoding="utf-8"))
        self.aos("daily-close", "2026-09-15", today="2026-09-16")
        frozen = month.read_text(encoding="utf-8")
        from aos_lib.schedule import parse_month

        self.assertEqual(parse_month(frozen)[16][7], "send")
        send = self.root / "user/tasks/pending/send.md"
        text = send.read_text(encoding="utf-8").replace(
            'do_at: ["07:30"]', 'do_at: ["09:00"]'
        )
        send.write_text(text, encoding="utf-8")
        self.aos("reindex", today="2026-09-16")
        after = parse_month(month.read_text(encoding="utf-8"))
        self.assertEqual(parse_month(frozen)[15], after[15])
        self.assertEqual(after[16][7], "null")
        self.assertEqual(after[16][9], "send")

    def test_unique_complete_drops_schedule(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-16", do_at="08:00")
        write_unique(self.root, "keep", "Keep", "2026-09-20", do_at="08:00")
        self.aos("reindex")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
        self.aos("reindex")
        from aos_lib.schedule import parse_month

        month = self.root / "user/schedule/2026/2026-09.md"
        cells = parse_month(month.read_text(encoding="utf-8"))
        self.assertNotIn("send", cells[16][8])
        self.assertIn("keep", cells[20][8])
        self.assertTrue((self.root / "user/tasks/completed/send.md").is_file())

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
                self.assertEqual(cells[day][hour], "dormir")
        self.assertEqual(cells[16][9], "open the month")
        self.assertNotEqual(cells[17][9], "dormir")

    def test_early_unique_frees_the_window(self) -> None:
        write_unique(self.root, "send", "Send", "2026-09-18", do_at="08:00")
        self.aos("reindex", today="2026-09-16")
        path = self.root / "user/tasks/tasks.md"
        path.write_text(mark(self.tasks_md(), heading="2-3 days"), encoding="utf-8")
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
        self.assertIn("## First Week (01/10 - 03/10)", text)
        self.assertIn("## Fifth Week (25/10 - 31/10)", text)
        cells = parse_month(text)
        self.assertEqual(cells[11][9], "send")
        self.assertEqual(cells[11][7], "box upkeep")
        self.assertEqual(cells[1][7], "box upkeep")
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
        self.assertEqual(october[2][8], "training")
        self.assertEqual(october[6][8], "training")
        november = self.root / "user/schedule/2026/2026-11.md"
        self.assertTrue(november.is_file())
        nov = parse_month(november.read_text(encoding="utf-8"))
        self.assertEqual(nov[3][8], "training")
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
        self.assertEqual(cells[11][8], "habit")
        self.assertEqual(cells[31][8], "habit")
        self.assertFalse((self.root / "user/schedule/2026/2026-11.md").is_file())

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
        label = "fazer trabalhos da faculdade"
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
        label = "fazer trabalhos da faculdade"
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

    def test_today_hours_through_now_stay_frozen(self) -> None:
        from aos_lib.schedule import parse_month

        write_unique(self.root, "send", "Send", "2026-09-16", do_at="07:30")
        self.aos("reindex", now="2026-09-16T10:00")
        send = self.root / "user/tasks/pending/send.md"
        send.write_text(
            send.read_text(encoding="utf-8").replace('do_at: ["07:30"]', 'do_at: ["15:00"]'),
            encoding="utf-8",
        )
        write_unique(self.root, "late", "Late", "2026-09-16", do_at="08:00")
        self.aos("reindex", now="2026-09-16T10:00")
        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[16][7], "send")
        self.assertEqual(cells[16][8], "null")
        self.assertEqual(cells[16][15], "send")

    def test_same_day_unique_keeps_hours_through_the_check(self) -> None:
        from aos_lib.schedule import parse_month

        path = write_unique(self.root, "send", "Send", "2026-09-16", do_at="07:00")
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                'do_at: ["07:00"]',
                'do_at: ["07:00", "08:00", "09:00", "10:00", "11:00"]',
            ),
            encoding="utf-8",
        )
        self.aos("reindex", now="2026-09-16T10:15")
        day = self.root / "user/daily/2026/2026-09/2026-09-16.md"
        day.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# 2026-09-16", "", "| hour | did |", "| --- | --- |"]
        for hour in range(24):
            did = "send" if hour == 11 else "null"
            lines.append(f"| {hour:02d}:00 | {did} |")
        lines.append("")
        day.write_text("\n".join(lines), encoding="utf-8")
        tasks = self.root / "user/tasks/tasks.md"
        tasks.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
        self.aos("reindex", now="2026-09-16T10:15")
        month = self.root / "user/schedule/2026/2026-09.md"
        data, _body = split_frontmatter(
            (self.root / "user/tasks/completed/send.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("completed_at"), "2026-09-16T10:15")
        self.aos("reindex", now="2026-09-16T06:00")
        cells = parse_month(month.read_text(encoding="utf-8"))
        for hour in (7, 8, 9, 10):
            self.assertEqual(cells[16][hour], "send", hour)
        self.assertEqual(cells[16][11], "null")
        self.assertIn("| 11:00 | send |", day.read_text(encoding="utf-8"))

    def test_same_day_recurring_cuts_today_and_keeps_the_next_do_on(self) -> None:
        from aos_lib.schedule import parse_month

        path = write_recurring(
            self.root,
            "review",
            "Review",
            kind="daily",
            until="2026-12-01",
            due="2026-09-16",
            do_at="07:00",
        )
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                'do_at: ["07:00"]',
                'do_at: ["07:00", "08:00", "09:00", "10:00", "11:00"]',
            ),
            encoding="utf-8",
        )
        self.aos("reindex", now="2026-09-16T10:20")
        tasks = self.root / "user/tasks/tasks.md"
        tasks.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
        self.aos("reindex", now="2026-09-16T10:20")
        data, _body = split_frontmatter(
            (self.root / "user/tasks/ongoing/review.md").read_text(encoding="utf-8")
        )
        self.assertEqual(data.get("do_on").isoformat(), "2026-09-17")
        self.assertEqual(data.get("completed_at"), "2026-09-16T10:20")
        self.aos("reindex", now="2026-09-16T06:00")
        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        for hour in (7, 8, 9, 10):
            self.assertEqual(cells[16][hour], "review", hour)
        self.assertEqual(cells[16][11], "null")
        for hour in (7, 8, 9, 10, 11):
            self.assertEqual(cells[17][hour], "review", hour)

    def test_open_project_keeps_the_window(self) -> None:
        from aos_lib.schedule import parse_month

        write_project(self.root, "college", status="pending", prefix="C")
        hub = self.root / "user/projects/pending/college/college.md"
        hub.write_text(
            hub.read_text(encoding="utf-8").replace("# college", "# Trabalhos da faculdade")
            + "\n## Phases\n\n- [Write](phases/c-01-write.md)\n",
            encoding="utf-8",
        )
        phase = self.root / "user/projects/pending/college/phases"
        phase.mkdir()
        (phase / "c-01-write.md").write_text(
            """---
status: pending
project: college
depends_on: []
---

# Write

## Plan

1. go

## Tasks

- [Draft](../../../../tasks/pending/draft.md)
- [Slides](../../../../tasks/pending/slides.md)
""",
            encoding="utf-8",
        )

        def project_task(slug: str, title: str, clock: str) -> None:
            path = write_unique(self.root, slug, title, "2026-09-16", do_at=clock)
            path.write_text(
                path.read_text(encoding="utf-8")
                .replace("type: unique-independent", "type: unique-project")
                .replace(
                    f"infinitive: {title}",
                    f"infinitive: {title}\nproject: college\nphase: c-01-write",
                ),
                encoding="utf-8",
            )

        project_task("draft", "Write the draft", "09:00")
        project_task("slides", "Make the slides", "11:00")
        self.aos("reindex", now="2026-09-16T08:00")
        tasks = self.root / "user/tasks/tasks.md"
        tasks.write_text(mark(self.tasks_md(), slug="draft"), encoding="utf-8")
        self.aos("reindex", now="2026-09-16T08:00")
        month = self.root / "user/schedule/2026/2026-09.md"
        cells = parse_month(month.read_text(encoding="utf-8"))
        self.assertEqual(cells[16][9], "trabalhos da faculdade")
        self.assertEqual(cells[16][11], "trabalhos da faculdade")
        tasks.write_text(mark(self.tasks_md(), slug="slides"), encoding="utf-8")
        self.aos("reindex", now="2026-09-16T10:15")
        self.aos("reindex", now="2026-09-16T08:00")
        cells = parse_month(month.read_text(encoding="utf-8"))
        self.assertEqual(cells[16][9], "trabalhos da faculdade")
        self.assertEqual(cells[16][11], "null")

    def test_grid_labels_are_lowercase(self) -> None:
        from aos_lib.schedule import parse_month

        path = self.root / "user/tasks/ongoing/sleep.md"
        path.write_text(
            """---
type: maintenance
status: ongoing
infinitive: Dormir
do_at: ["22:00"]
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
        write_unique(
            self.root,
            "college",
            "Trabalhos da faculdade",
            "2026-09-16",
            do_at="09:00",
        )
        self.aos("reindex", now="2026-09-16T12:00")
        month = self.root / "user/schedule/2026/2026-09.md"
        text = month.read_text(encoding="utf-8")
        lines = text.splitlines()
        column = None
        header_at = None
        for index, line in enumerate(lines):
            if line.startswith("| hour |") and "16 - wed" in line:
                headers = [cell.strip() for cell in line.strip("|").split("|")]
                column = headers.index("16 - wed")
                header_at = index
                break
        self.assertIsNotNone(column)
        assert header_at is not None and column is not None
        for index in range(header_at, len(lines)):
            if lines[index].startswith("| 08:00 |"):
                cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
                cells[column] = "Dormir"
                lines[index] = "| " + " | ".join(cells) + " |"
                break
        month.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.aos("reindex", now="2026-09-16T12:00")
        cells = parse_month(month.read_text(encoding="utf-8"))
        self.assertEqual(cells[16][8], "Dormir")
        self.assertEqual(cells[16][9], "trabalhos da faculdade")
        self.assertEqual(cells[16][22], "dormir")
        self.assertIn("[Dormir](ongoing/sleep.md)", self.tasks_md())

    def test_october_2026_week_titles(self) -> None:
        from aos_lib.schedule import month_path, parse_month, render_month, week_spans, week_title

        write_unique(self.root, "send", "Send", "2026-10-11", do_at="09:00")
        seed_daily(
            self.root,
            "2026-10-01",
            """# 2026-10-01

| hour | did |
| --- | --- |
| 00:00 | null |

| routine | tasks |
| --- | --- |
| null | null |
""",
        )
        month = month_path(self.root, 2026, 10)
        month.parent.mkdir(parents=True, exist_ok=True)
        month.write_text(
            "\n".join(
                [
                    "# 2026-10",
                    "",
                    "### Legacy",
                    "",
                    "| hour | 1 - thu | 2 - fri | 3 - sat |",
                    "| --- | --- | --- | --- |",
                    "| 09:00 | Kept | null | null |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        bare = "# 2026-10\n\n| hour | 11 - sun |\n| --- | --- |\n| 09:00 | Kept |\n"
        titled = "## Third Week (11/10 - 17/10)\n\n" + bare
        self.assertEqual(parse_month(month.read_text(encoding="utf-8"))[1][9], "Kept")
        self.assertEqual(parse_month(bare)[11][9], "Kept")
        self.assertEqual(parse_month(titled)[11][9], "Kept")
        self.aos("reindex", today="2026-10-11", now="2026-10-11T08:00")
        text = month.read_text(encoding="utf-8")
        self.assertIn("### First Week (01/10 - 03/10)", text)
        self.assertIn("### Second Week (04/10 - 10/10)", text)
        self.assertIn("### Third Week (11/10 - 17/10)", text)
        self.assertIn("### Fourth Week (18/10 - 24/10)", text)
        self.assertIn("### Fifth Week (25/10 - 31/10)", text)
        self.assertNotIn("### Legacy", text)
        self.assertFalse(any(line.startswith("## ") for line in text.splitlines()))
        cells = parse_month(text)
        self.assertEqual(cells[1][9], "Kept")
        self.assertEqual(cells[11][9], "send")
        start, end = week_spans(2026, 5)[-1]
        self.assertEqual(week_title(5, start, end, 5), "Sixth Week (31/05 - 31/05)")
        self.assertIn("## Sixth Week (31/05 - 31/05)", render_month(2026, 5, {}))

    def _project_task(self, slug: str, title: str, clock: str, project: str) -> None:
        path = write_unique(self.root, slug, title, "2026-09-16", do_at=clock)
        path.write_text(
            path.read_text(encoding="utf-8")
            .replace("type: unique-independent", "type: unique-project")
            .replace(
                f"infinitive: {title}",
                f"infinitive: {title}\nproject: {project}\nphase: j-01",
            ),
            encoding="utf-8",
        )

    def test_same_project_in_one_slot_is_one_label(self) -> None:
        from aos_lib.schedule import parse_month

        write_project(self.root, "first-job", status="ongoing", prefix="J")
        self._project_task("draft", "Write the draft", "09:00", "first-job")
        self._project_task("slides", "Make the slides", "09:00", "first-job")
        self.aos("reindex", now="2026-09-16T08:00")
        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[16][9], "first-job")

    def test_independent_and_project_keep_two_labels_in_order(self) -> None:
        from aos_lib.schedule import parse_month

        write_project(self.root, "first-job", status="ongoing", prefix="J")
        write_unique(self.root, "note", "Send the note", "2026-09-16", do_at="09:00")
        self._project_task("draft", "Write the draft", "09:00", "first-job")
        self._project_task("slides", "Make the slides", "09:00", "first-job")
        self.aos("reindex", now="2026-09-16T08:00")
        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[16][9], "send the note, first-job")

    def test_frozen_hour_keeps_a_repeated_label(self) -> None:
        from aos_lib.schedule import parse_month

        write_project(self.root, "first-job", status="ongoing", prefix="J")
        self._project_task("draft", "Write the draft", "09:00", "first-job")
        self._project_task("slides", "Make the slides", "09:00", "first-job")
        self.aos("reindex", now="2026-09-16T08:00")
        month = self.root / "user/schedule/2026/2026-09.md"
        text = month.read_text(encoding="utf-8")
        self.assertIn("| first-job |", text)
        month.write_text(
            text.replace("| first-job |", "| first-job, first-job |", 1),
            encoding="utf-8",
        )
        self.aos("reindex", now="2026-09-16T09:30")
        cells = parse_month(month.read_text(encoding="utf-8"))
        self.assertEqual(cells[16][9], "first-job, first-job")
