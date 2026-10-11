from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import subprocess

from helpers import (
    AOSTest,
    BIN,
    write_recurring,
    write_unique,
)


class ValidateTest(AOSTest):
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
