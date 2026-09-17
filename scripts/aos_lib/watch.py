from __future__ import annotations

import ctypes
import ctypes.util
import os
import select
import struct
import sys
import time
from pathlib import Path

from .config import tasks_dir, today as today_fn
from .sync import sync

IN_MODIFY = 0x00000002
IN_CLOSE_WRITE = 0x00000008
IN_MOVED_TO = 0x00000080
IN_MOVED_FROM = 0x00000040
IN_CREATE = 0x00000100
IN_DELETE = 0x00000200
IN_ATTRIB = 0x00000004
IN_MOVE_SELF = 0x00000800

WATCH_MASK = (
    IN_MODIFY
    | IN_CLOSE_WRITE
    | IN_MOVED_TO
    | IN_MOVED_FROM
    | IN_CREATE
    | IN_DELETE
    | IN_ATTRIB
    | IN_MOVE_SELF
)

EVENT_HDR = struct.Struct("iIII")


def _inotify_fd(directory: Path) -> int | None:
    try:
        libc_name = ctypes.util.find_library("c")
        if not libc_name:
            return None
        libc = ctypes.CDLL(libc_name, use_errno=True)
        fd = -1
        if hasattr(libc, "inotify_init1"):
            fd = libc.inotify_init1(os.O_NONBLOCK)
        if fd < 0:
            fd = libc.inotify_init()
            if fd < 0:
                return None
            flags = fcntl_getfl(fd)
            fcntl_setfl(fd, flags | os.O_NONBLOCK)
        path = str(directory).encode()
        wd = libc.inotify_add_watch(fd, path, WATCH_MASK)
        if wd < 0:
            os.close(fd)
            return None
        return fd
    except OSError:
        return None


def fcntl_getfl(fd: int) -> int:
    import fcntl

    return fcntl.fcntl(fd, fcntl.F_GETFL)


def fcntl_setfl(fd: int, flags: int) -> None:
    import fcntl

    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


def _drain_inotify(fd: int) -> list[str]:
    names: list[str] = []
    while True:
        try:
            buf = os.read(fd, 65536)
        except BlockingIOError:
            break
        if not buf:
            break
        off = 0
        while off + EVENT_HDR.size <= len(buf):
            _wd, _mask, _cookie, length = EVENT_HDR.unpack_from(buf, off)
            off += EVENT_HDR.size
            raw = buf[off : off + length]
            off += length
            name = raw.split(b"\x00", 1)[0].decode("utf-8", "replace")
            names.append(name)
    return names


def _file_sig(path: Path) -> tuple[int, int, str]:
    if not path.exists():
        return (0, 0, "")
    st = path.stat()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    return (st.st_mtime_ns, st.st_size, text)


def watch(root: Path, *, poll_s: float = 1.0) -> None:
    tasks_md = tasks_dir(root) / "tasks.md"
    tasks_md.parent.mkdir(parents=True, exist_ok=True)
    if not tasks_md.exists():
        from .index import reindex

        reindex(root)
    last = _file_sig(tasks_md)
    fd = _inotify_fd(tasks_md.parent)
    sys.stderr.write(f"aos watch on {tasks_md} ({'inotify' if fd is not None else 'poll'})\n")
    sys.stderr.flush()
    try:
        while True:
            if fd is not None:
                try:
                    select.select([fd], [], [], min(poll_s, 2.0))
                except InterruptedError:
                    continue
                time.sleep(0.05)
                _drain_inotify(fd)
            else:
                time.sleep(min(poll_s, 2.0))
            sig = _file_sig(tasks_md)
            if sig == last:
                continue
            try:
                sync(root, today_fn(root))
            except Exception as exc:  # noqa: BLE001 — keep watch alive
                sys.stderr.write(f"aos watch sync error: {exc}\n")
                sys.stderr.flush()
            last = _file_sig(tasks_md)
    except KeyboardInterrupt:
        return
    finally:
        if fd is not None:
            os.close(fd)


def watch_loop(root: Path, *, poll_s: float = 1.0) -> None:
    """Restart watch() if it returns or raises, until SIGINT."""
    from .up import write_pidfile

    write_pidfile(root, os.getpid())
    sys.stderr.write(f"aos watch --loop pid={os.getpid()} root={root}\n")
    sys.stderr.flush()
    while True:
        try:
            watch(root, poll_s=poll_s)
            return
        except KeyboardInterrupt:
            return
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"aos watch loop error: {exc}\n")
            sys.stderr.flush()
            time.sleep(2)
