from __future__ import annotations

import fcntl
import os
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SYNC_LOCK_NAME = "aos-sync.lock"
SYNC_LOCK_TIMEOUT_S = 30.0
SYNC_ATTEMPTS = 3
SYNC_BACKOFF_S = 0.4
# Another git (editor, agent) can hold index.lock for a moment.
INDEX_LOCK_TRIES = 6
INDEX_LOCK_WAIT_S = 2.0
PUSH_TIMEOUT_S = 120


def _env() -> dict[str, str]:
    env = os.environ.copy()
    # Watch and cron have no TTY: fail fast instead of asking for a username.
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def is_git_repo(root: Path) -> bool:
    return (root / ".git").exists()


def git(
    root: Path,
    *args: str,
    check: bool = False,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = ["git", *args]
    return subprocess.run(
        cmd,
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
        env=_env(),
        timeout=timeout,
    )


def _output(proc: subprocess.CompletedProcess[str]) -> str:
    return proc.stderr.strip() or proc.stdout.strip()


def _git_dir(root: Path) -> Path:
    proc = git(root, "rev-parse", "--absolute-git-dir")
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip())
    return root / ".git"


@contextmanager
def git_lock(root: Path, timeout: float = SYNC_LOCK_TIMEOUT_S) -> Iterator[None]:
    """Exclusive lock for every AOS add, commit, pull, and push in this repo."""
    path = _git_dir(root) / SYNC_LOCK_NAME
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (BlockingIOError, InterruptedError):
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"could not lock {path.name} within {timeout:.0f}s"
                    )
                time.sleep(0.05)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _git_retry(
    root: Path,
    *args: str,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run git; wait and retry while another process holds index.lock."""
    proc = git(root, *args, timeout=timeout)
    for _ in range(INDEX_LOCK_TRIES - 1):
        if proc.returncode == 0 or "index.lock" not in proc.stderr:
            break
        time.sleep(INDEX_LOCK_WAIT_S)
        proc = git(root, *args, timeout=timeout)
    return proc


def origin_exists(root: Path) -> bool:
    if not is_git_repo(root):
        return False
    proc = git(root, "remote")
    remotes = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    return "origin" in remotes


def user_git_root(root: Path) -> Path:
    """Repo that stores user/: nested user git if present, else AOS root."""
    nested = root / "user"
    if (nested / ".git").exists():
        return nested
    return root


def sync_vault(root: Path, message: str) -> bool:
    """Commit vault changes, then pull --rebase and push. True if this call committed.

    Uses the identity already configured in the vault. Does not set or change
    user.name or user.email. No file changes means no commit; a commit left by
    a failed push still goes out. A rebase conflict is aborted, not forced.
    A failed push is printed and does not raise: the local commit stays.
    """
    git_root = user_git_root(root)
    if not is_git_repo(git_root):
        return False
    pathspec = ["--", "user"] if git_root == root else []
    try:
        with git_lock(git_root):
            return _sync_locked(git_root, message, pathspec)
    except TimeoutError as exc:
        sys.stderr.write(f"aos: {exc}\n")
        sys.stderr.flush()
        raise


def commit_user(root: Path, message: str) -> bool:
    """Same vault sync. Callers do not run git add, commit, or push themselves."""
    return sync_vault(root, message)


def _sync_locked(git_root: Path, message: str, pathspec: list[str]) -> bool:
    add = _git_retry(git_root, "add", "-A", *pathspec)
    if add.returncode != 0:
        raise RuntimeError(f"git add failed: {_output(add)}")
    status = git(git_root, "status", "--porcelain", *pathspec)
    committed = False
    if status.stdout.strip():
        proc = _git_retry(git_root, "commit", "-m", message)
        if proc.returncode != 0:
            raise RuntimeError(f"git commit failed: {_output(proc)}")
        committed = True
    if origin_exists(git_root):
        _pull_rebase_and_push(git_root)
    return committed


def _has_upstream(git_root: Path) -> bool:
    proc = git(git_root, "rev-parse", "--abbrev-ref", "@{upstream}")
    return proc.returncode == 0 and bool(proc.stdout.strip())


def _rebase_in_progress(git_root: Path) -> bool:
    git_dir = _git_dir(git_root)
    return (git_dir / "rebase-merge").is_dir() or (git_dir / "rebase-apply").is_dir()


def _pull_rebase_and_push(git_root: Path) -> None:
    last = ""
    saw_push = False
    for attempt in range(SYNC_ATTEMPTS):
        if attempt:
            time.sleep(SYNC_BACKOFF_S * attempt)
        if _has_upstream(git_root):
            try:
                pull = _git_retry(git_root, "pull", "--rebase", timeout=PUSH_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                last = f"git pull --rebase timed out after {PUSH_TIMEOUT_S}s"
                continue
            if pull.returncode != 0:
                if _rebase_in_progress(git_root):
                    abort = git(git_root, "rebase", "--abort")
                    if abort.returncode != 0:
                        sys.stderr.write(
                            f"aos: rebase --abort failed: {_output(abort)}\n"
                        )
                    sys.stderr.write(
                        "aos: rebase conflict, aborted without force: "
                        f"{_output(pull)}\n"
                    )
                    sys.stderr.flush()
                    return
                last = _output(pull) or "git pull --rebase failed"
                continue
        try:
            saw_push = True
            push = _git_retry(git_root, "push", timeout=PUSH_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            last = f"git push timed out after {PUSH_TIMEOUT_S}s"
            continue
        if push.returncode == 0:
            return
        last = _output(push) or "git push failed"
    if saw_push:
        sys.stderr.write(f"aos: git push failed: {last}\n")
    else:
        sys.stderr.write(f"aos: git pull --rebase failed: {last}\n")
    sys.stderr.flush()
