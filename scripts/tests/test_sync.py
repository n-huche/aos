from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import subprocess
import tempfile
import threading
import unittest
from datetime import date
from unittest import mock

from helpers import (
    AOSTest,
    BIN,
    _git,
    init_aos,
    seed_daily,
    write_unique,
)


class SyncTest(AOSTest):
    def test_no_commit_skips_vault_sync(self) -> None:
        head = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        write_unique(self.root, "send", "Send", "2026-09-16")
        self.aos("reindex", "--no-commit")
        self.aos("daily-close", "--no-commit", "2026-09-15")
        self.assertEqual(_git(self.root, "rev-parse", "HEAD").stdout.strip(), head)
        self.assertNotEqual(_git(self.root, "status", "--porcelain").stdout.strip(), "")

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

    def test_sync_command_is_gone(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(BIN), "sync"],
            env=self.env(),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("sync", proc.stderr.lower())


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
