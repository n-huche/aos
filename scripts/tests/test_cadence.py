from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

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


if __name__ == "__main__":
    unittest.main()
