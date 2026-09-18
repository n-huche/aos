from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _identity_args() -> list[str]:
    name = os.environ.get("AOS_GIT_NAME", "AOS")
    email = os.environ.get("AOS_GIT_EMAIL", "aos@localhost")
    return ["-c", f"user.name={name}", "-c", f"user.email={email}"]


def is_git_repo(root: Path) -> bool:
    return (root / ".git").exists()


def git(root: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = ["git", *args]
    return subprocess.run(
        cmd,
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
    )


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
    if git_root == root:
        git(root, "add", "-A", "--", "user")
        status = git(root, "status", "--porcelain", "--", "user")
    else:
        git(git_root, "add", "-A")
        status = git(git_root, "status", "--porcelain")
    if not status.stdout.strip():
        return False
    proc = subprocess.run(
        ["git", *_identity_args(), "commit", "-m", message],
        cwd=git_root,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git commit failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return True


def push_if_origin(root: Path) -> None:
    git_root = user_git_root(root)
    if not origin_exists(git_root):
        return
    proc = git(git_root, "push")
    if proc.returncode != 0:
        raise RuntimeError(f"git push failed: {proc.stderr.strip() or proc.stdout.strip()}")
