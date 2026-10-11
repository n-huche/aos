from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import os
import signal
import time

from helpers import (
    AOSTest,
)


class UpTest(AOSTest):
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
