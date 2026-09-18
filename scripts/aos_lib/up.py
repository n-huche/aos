from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from .config import get_root, logs_dir
from .daily import catch_up


BIN_NAME = "aos"
WATCH_PID_NAME = "watch.pid"
UP_LOCK_NAME = "up.lock"


def aos_bin(root: Path) -> Path:
    return (root / "scripts" / BIN_NAME).resolve()


def logs(root: Path) -> Path:
    path = logs_dir(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def watch_pid_path(root: Path) -> Path:
    return logs(root) / WATCH_PID_NAME


def render_crontab(root: Path) -> str:
    root_s = str(root.resolve())
    bin_s = str(aos_bin(root))
    return (
        f"CRON_TZ=America/Sao_Paulo\n"
        f'MAILTO=""\n'
        f"PATH=/usr/bin:/bin\n"
        f"AOS_ROOT={root_s}\n"
        f"\n"
        f"0 0 * * * {bin_s} daily-close >> {root_s}/logs/daily-close.log 2>&1\n"
    )


def current_crontab() -> str | None:
    proc = subprocess.run(
        ["crontab", "-l"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def install_crontab(root: Path) -> str:
    desired = render_crontab(root)
    existing = current_crontab()
    if existing == desired:
        return "crontab-unchanged"
    proc = subprocess.run(
        ["crontab", "-"],
        input=desired,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"crontab install failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return "crontab-installed"


def _cmdline_tokens(pid: int) -> list[str]:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return []
    return [part.decode("utf-8", "replace") for part in raw.split(b"\x00") if part]


def _cmdline(pid: int) -> str:
    return " ".join(_cmdline_tokens(pid))


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _environ_text(pid: int) -> str:
    try:
        raw = Path(f"/proc/{pid}/environ").read_bytes()
    except OSError:
        return ""
    return raw.replace(b"\x00", b"\n").decode("utf-8", "replace")


def is_watch_for_root(root: Path, pid: int) -> bool:
    try:
        comm = Path(f"/proc/{pid}/comm").read_text(encoding="utf-8").strip()
    except OSError:
        return False
    if not comm.startswith("python"):
        return False
    tokens = _cmdline_tokens(pid)
    if "watch" not in tokens:
        return False
    if "up" in tokens:
        return False
    root_s = str(root.resolve())
    env = _environ_text(pid)
    if f"AOS_ROOT={root_s}" in env:
        return True
    joined = " ".join(tokens)
    if f"{root_s}/scripts/{BIN_NAME}" in joined:
        return True
    return str(aos_bin(root)) in joined


def find_watch_pids(root: Path) -> list[int]:
    proc_root = Path("/proc")
    found: list[int] = []
    if not proc_root.is_dir():
        return found
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if is_watch_for_root(root, pid):
            found.append(pid)
    return found


def read_pidfile(root: Path) -> int | None:
    path = watch_pid_path(root)
    if not path.is_file():
        return None
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None
    return pid


def write_pidfile(root: Path, pid: int) -> None:
    watch_pid_path(root).write_text(f"{pid}\n", encoding="utf-8")


def watch_running(root: Path) -> int | None:
    pids = find_watch_pids(root)
    if pids:
        write_pidfile(root, pids[0])
        return pids[0]
    pid = read_pidfile(root)
    if pid is None:
        return None
    if pid_alive(pid) and is_watch_for_root(root, pid):
        return pid
    return None


def start_watch(root: Path) -> int:
    log_path = logs(root) / "watch.log"
    logf = open(log_path, "a", encoding="utf-8")
    env = os.environ.copy()
    env["AOS_ROOT"] = str(root.resolve())
    script = Path(sys.argv[0]).resolve()
    if not script.is_file():
        script = aos_bin(root)
    proc = subprocess.Popen(
        [sys.executable, str(script), "watch", "--loop"],
        cwd=str(root),
        stdout=logf,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=env,
    )
    write_pidfile(root, proc.pid)
    return proc.pid


def _lock_fd(root: Path):
    import fcntl

    path = logs(root) / UP_LOCK_NAME
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def ensure_watch(root: Path) -> tuple[str, int | None]:
    fd = _lock_fd(root)
    try:
        existing = watch_running(root)
        if existing is not None:
            return "watch-running", existing
        pid = start_watch(root)
        time.sleep(0.4)
        if not pid_alive(pid):
            return "watch-failed", pid
        return "watch-started", pid
    finally:
        os.close(fd)


def run_up(
    root: Path | None = None,
    *,
    quiet: bool = False,
    watch_only: bool = False,
) -> list[str]:
    root = (root or get_root()).resolve()
    actions: list[str] = []
    if not watch_only:
        try:
            actions.append(install_crontab(root))
        except FileNotFoundError:
            actions.append("crontab-unavailable")
        except RuntimeError as exc:
            actions.append(f"crontab-error:{exc}")
        # Catch-up before watch: close gaps, then leftover [x] as today.
        actions.extend(catch_up(root))
    state, pid = ensure_watch(root)
    if pid is not None:
        actions.append(f"{state}:{pid}")
    else:
        actions.append(state)
    if not quiet:
        for line in actions:
            print(line)
    return actions
