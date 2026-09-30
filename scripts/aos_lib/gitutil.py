from __future__ import annotations

import fcntl
import os
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

GIT_LOCK_NAME = "aos-git.lock"
# Another git (editor, agent) can hold index.lock for a moment.
INDEX_LOCK_TRIES = 6
INDEX_LOCK_WAIT_S = 2.0
PUSH_TIMEOUT_S = 120


def _identity_args() -> list[str]:
    name = os.environ.get("AOS_GIT_NAME", "AOS")
    email = os.environ.get("AOS_GIT_EMAIL", "aos@localhost")
    return ["-c", f"user.name={name}", "-c", f"user.email={email}"]


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
def git_lock(root: Path) -> Iterator[None]:
    """Serialize AOS writes to one git repo: watch sync, cron daily-close, catch-up."""
    fd = os.open(_git_dir(root) / GIT_LOCK_NAME, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _git_retry(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git; wait and retry while another process holds index.lock."""
    proc = git(root, *args)
    for _ in range(INDEX_LOCK_TRIES - 1):
        if proc.returncode == 0 or "index.lock" not in proc.stderr:
            break
        time.sleep(INDEX_LOCK_WAIT_S)
        proc = git(root, *args)
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


def commit_user(root: Path, message: str) -> bool:
    git_root = user_git_root(root)
    if not is_git_repo(git_root):
        return False
    pathspec = ["--", "user"] if git_root == root else []
    with git_lock(git_root):
        add = _git_retry(git_root, "add", "-A", *pathspec)
        if add.returncode != 0:
            raise RuntimeError(f"git add failed: {_output(add)}")
        status = git(git_root, "status", "--porcelain", *pathspec)
        if not status.stdout.strip():
            return False
        proc = _git_retry(git_root, *_identity_args(), "commit", "-m", message)
        if proc.returncode != 0:
            raise RuntimeError(f"git commit failed: {_output(proc)}")
    return True


def _has_unpushed(git_root: Path) -> bool:
    proc = git(git_root, "rev-list", "--count", "@{upstream}..HEAD")
    if proc.returncode != 0:
        # No upstream yet: let `git push` decide.
        return True
    return proc.stdout.strip() != "0"


def push_if_origin(root: Path) -> bool:
    """Push the user repo when it has commits origin does not. True if it pushed.

    A push that failed earlier is retried here, even with nothing new to commit.
    """
    git_root = user_git_root(root)
    if not origin_exists(git_root):
        return False
    if not _has_unpushed(git_root):
        return False
    try:
        proc = git(git_root, "push", timeout=PUSH_TIMEOUT_S)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git push timed out after {PUSH_TIMEOUT_S}s") from exc
    if proc.returncode != 0:
        raise RuntimeError(f"git push failed: {_output(proc)}")
    return True


def push_or_warn(root: Path) -> None:
    """Push pending commits. A failure is printed, not raised: watch retries it."""
    try:
        push_if_origin(root)
    except RuntimeError as exc:
        sys.stderr.write(f"aos: {exc}\n")
        sys.stderr.flush()
