from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aos_lib.cadence import (
    add_interval,
    add_months,
    day_complete,
    done_count,
    index_dates,
    occurs_on,
)
from aos_lib.yamlfm import dump_yaml, join_frontmatter, parse_yaml, split_frontmatter


class CadenceTest(unittest.TestCase):
    def test_jan31_plus_one_month_clamps(self) -> None:
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2024, 1, 31), 1), date(2024, 2, 29))

    def test_interval_from_anchor_keeps_original_day(self) -> None:
        anchor = date(2026, 1, 31)
        self.assertEqual(add_interval(anchor, 1, 1, "months"), date(2026, 2, 28))
        self.assertEqual(add_interval(anchor, 2, 1, "months"), date(2026, 3, 31))
        self.assertEqual(add_interval(anchor, 3, 1, "months"), date(2026, 4, 30))

    def test_weekdays_occurs(self) -> None:
        data = parse_yaml("cadence:\n  kind: weekdays\n  days: [wed, thu]\n")
        self.assertTrue(occurs_on(data, date(2026, 9, 16)))
        self.assertTrue(occurs_on(data, date(2026, 9, 17)))
        self.assertFalse(occurs_on(data, date(2026, 9, 18)))

    def test_pending_recurring_does_not_occur(self) -> None:
        pending = parse_yaml(
            "type: recurring-independent\n"
            "status: pending\n"
            "cadence:\n  kind: daily\n"
        )
        self.assertFalse(occurs_on(pending, date(2026, 9, 16)))
        live = parse_yaml(
            "type: recurring-independent\n"
            "status: ongoing\n"
            "cadence:\n  kind: weekdays\n  days: [tue, fri]\n"
        )
        self.assertFalse(occurs_on(live, date(2026, 9, 16)))
        self.assertTrue(occurs_on(live, date(2026, 9, 18)))

    def test_interval_index_anchor_today_and_yesterday(self) -> None:
        today = date(2026, 9, 16)
        data_today = parse_yaml(
            "done_on: []\ncadence:\n  kind: interval\n  every: 2\n  unit: months\n  anchor: 2026-09-16\n"
        )
        self.assertEqual(
            index_dates(data_today, today),
            [date(2026, 9, 16), date(2026, 11, 16)],
        )
        data_y = parse_yaml(
            "done_on: []\ncadence:\n  kind: interval\n  every: 2\n  unit: months\n  anchor: 2026-09-15\n"
        )
        self.assertEqual(index_dates(data_y, today), [date(2026, 11, 15)])

    def test_done_on_roundtrip(self) -> None:
        data = {
            "type": "recurring-independent",
            "status": "ongoing",
            "done_on": [date(2026, 9, 16)],
            "cadence": {"kind": "daily"},
        }
        dumped = dump_yaml(data)
        parsed = parse_yaml(dumped)
        self.assertEqual(parsed["done_on"], [date(2026, 9, 16)])
        text = join_frontmatter(data, "# Title\n")
        again, body = split_frontmatter(text)
        self.assertEqual(again["status"], "ongoing")
        self.assertEqual(again["done_on"], [date(2026, 9, 16)])
        self.assertIn("# Title", body)

    def test_done_today_hides_today(self) -> None:
        today = date(2026, 9, 16)
        data = parse_yaml(
            "status: ongoing\n"
            "done_on: [2026-09-16]\n"
            "cadence:\n  kind: daily\n"
        )
        self.assertEqual(done_count(data, today), 1)
        self.assertTrue(day_complete(data, today))
        self.assertEqual(index_dates(data, today), [date(2026, 9, 17)])

    def test_first_monday_of_month(self) -> None:
        data = parse_yaml(
            "status: ongoing\n"
            "done_on: []\n"
            "cadence:\n  kind: month-weekday\n  day: mon\n  n: 1\n"
        )
        self.assertTrue(occurs_on(data, date(2026, 9, 7)))
        self.assertFalse(occurs_on(data, date(2026, 9, 14)))
        self.assertTrue(occurs_on(data, date(2026, 10, 5)))
        self.assertEqual(
            index_dates(data, date(2026, 9, 7)),
            [date(2026, 9, 7), date(2026, 10, 5)],
        )
        self.assertEqual(index_dates(data, date(2026, 9, 24)), [date(2026, 10, 5)])
        done = parse_yaml(
            "status: ongoing\n"
            "done_on: [2026-10-05]\n"
            "cadence:\n  kind: month-weekday\n  day: mon\n  n: 1\n"
        )
        self.assertEqual(index_dates(done, date(2026, 9, 24)), [date(2026, 11, 2)])

    def test_first_and_third_monday(self) -> None:
        data = parse_yaml(
            "status: ongoing\n"
            "done_on: []\n"
            "cadence:\n  kind: month-weekday\n  day: mon\n  n: [1, 3]\n"
        )
        self.assertTrue(occurs_on(data, date(2026, 10, 5)))
        self.assertFalse(occurs_on(data, date(2026, 10, 12)))
        self.assertTrue(occurs_on(data, date(2026, 10, 19)))
        self.assertEqual(index_dates(data, date(2026, 9, 24)), [date(2026, 10, 5)])
        self.assertEqual(
            index_dates(data, date(2026, 10, 5)),
            [date(2026, 10, 5), date(2026, 10, 19)],
        )

    def test_fifth_weekday_skips_a_short_month(self) -> None:
        data = parse_yaml(
            "status: ongoing\n"
            "done_on: []\n"
            "cadence:\n  kind: month-weekday\n  day: mon\n  n: 5\n"
        )
        self.assertFalse(occurs_on(data, date(2026, 9, 28)))
        self.assertTrue(occurs_on(data, date(2026, 11, 30)))
        self.assertEqual(index_dates(data, date(2026, 9, 1)), [date(2026, 11, 30)])



from helpers import (  # noqa: E402
    AOSTest,
    headings,
    section_items,
    write_recurring,
)


class CadenceIndexTest(AOSTest):
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
