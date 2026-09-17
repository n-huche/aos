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


def commit_user(root: Path, message: str) -> bool:
    if not is_git_repo(root):
        return False
    git(root, "add", "-A", "--", "user")
    status = git(root, "status", "--porcelain", "--", "user")
    if not status.stdout.strip():
        return False
    proc = subprocess.run(
        ["git", *_identity_args(), "commit", "-m", message],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git commit failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return True


def push_if_origin(root: Path) -> None:
    if not origin_exists(root):
        return
    proc = git(root, "push")
    if proc.returncode != 0:
        raise RuntimeError(f"git push failed: {proc.stderr.strip() or proc.stdout.strip()}")
