from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import signal
import subprocess
import time

from helpers import (
    AOSTest,
    BIN,
    mark,
    write_unique,
)


class WatchTest(AOSTest):
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
            path.write_text(mark(self.tasks_md(), heading="Today"), encoding="utf-8")
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
