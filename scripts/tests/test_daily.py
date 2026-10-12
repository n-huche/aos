from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import date

from helpers import (
    AOSTest,
    _git,
    mark,
    section_items,
    seed_daily,
    write_recurring,
    write_unique,
)

from aos_lib.yamlfm import split_frontmatter


class DailyTest(AOSTest):
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
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
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
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
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
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
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
        self.assertIn("| send | 1 |", month)
        tomorrow = self.root / "user/daily/2026/2026-09/2026-09-17.md"
        self.assertTrue(tomorrow.is_file())
        self.assertNotIn("| routine | tasks |", tomorrow.read_text(encoding="utf-8"))

    def test_routine_score_matches_any_report_part(self) -> None:
        from aos_lib.daily import routine_score
        from aos_lib.schedule import month_path, render_month

        path = month_path(self.root, 2026, 9)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            render_month(
                2026,
                9,
                {16: {7: "sistemas pessoais", 8: "Dormir", 9: "box upkeep"}},
            ),
            encoding="utf-8",
        )
        hours = {f"{hour:02d}:00": "null" for hour in range(24)}
        hours["07:00"] = "sistemas pessoais, Trabalhos da faculdade"
        hours["08:00"] = "dormir"
        hours["09:00"] = "tiktok"
        score, deviations = routine_score(self.root, date(2026, 9, 16), hours)
        self.assertEqual(score, "67%")
        self.assertEqual(deviations, [("09:00", "tiktok", ["box upkeep"])])

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
        path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
        self.aos("reindex")
        text = day.read_text(encoding="utf-8")
        self.assertIn("## Completed tasks", text)
        self.assertIn("tasks/completed/send.md", text)
        self.assertIn("| 07:00 | tiktok |", text)
        self.assertIn("## Notes, optional", text)
        self.assertIn("kept", text)
        self.assertNotIn("| routine | tasks |", text)
        from aos_lib.schedule import parse_month

        cells = parse_month(
            (self.root / "user/schedule/2026/2026-09.md").read_text(encoding="utf-8")
        )
        self.assertEqual(cells[16][8], "null")

    def _hour_table(self, iso: str, *, notes_heading: str | None, note: str | None) -> str:
        lines = [f"# {iso}", "", "| hour | did |", "| --- | --- |"]
        for hour in range(24):
            lines.append(f"| {hour:02d}:00 | null |")
        if notes_heading and note:
            lines.extend(["", notes_heading, "", note, ""])
        else:
            lines.append("")
        return "\n".join(lines)

    def test_legacy_notes_are_read_validated_and_kept(self) -> None:
        from aos_lib.daily import extract_notes

        iso = "2026-09-15"
        legacy = self._hour_table(iso, notes_heading="## Notes, optional", note="kept the note")
        self.assertEqual(
            extract_notes(legacy),
            "## Notes, optional\n\nkept the note\n",
        )
        day = seed_daily(self.root, iso, legacy)
        self.aos("validate")
        self.aos("daily-close", iso, today="2026-09-16")
        text = day.read_text(encoding="utf-8")
        self.assertIn("## Notes, optional\n", text)
        self.assertIn("kept the note", text)
        self.assertNotIn("## Notes\n", text)
        self.aos("validate")

    def test_new_daily_is_generated_with_notes(self) -> None:
        from aos_lib.daily import extract_notes, render_daily, render_open_daily

        when = date(2026, 9, 16)
        hours = {f"{hour:02d}:00": "null" for hour in range(24)}
        closed = render_daily(when, hours, "null", "null", [], [], "kept the note")
        opened = render_open_daily(when, hours, [], "kept the note")
        for text in (closed, opened):
            self.assertIn("## Notes\n", text)
            self.assertIn("kept the note", text)
            self.assertNotIn("Notes, optional", text)
            self.assertEqual(extract_notes(text), "## Notes\n\nkept the note\n")
        day = seed_daily(self.root, when.isoformat(), closed)
        self.aos("validate")
        self.aos("daily-close", when.isoformat(), today="2026-09-17")
        text = day.read_text(encoding="utf-8")
        self.assertIn("## Notes\n", text)
        self.assertIn("kept the note", text)
        self.assertNotIn("Notes, optional", text)
