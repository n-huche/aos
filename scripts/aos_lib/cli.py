from __future__ import annotations

import argparse
import sys
from datetime import date

from .config import get_root
from .daily import daily_close
from .index import reindex
from .up import run_up
from .validate import validate
from .watch import watch, watch_loop


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aos", description="Agency Operating System")
    sub = p.add_subparsers(dest="cmd", required=True)
    ri = sub.add_parser("reindex", help="apply checks, rebuild tasks.md and the schedule")
    ri.add_argument(
        "--no-commit",
        action="store_true",
        help="rebuild without committing or pushing the vault",
    )
    w = sub.add_parser("watch", help="watch tasks.md and reindex on checkbox")
    w.add_argument(
        "--loop",
        action="store_true",
        help="restart watch() after a crash until interrupted",
    )
    dc = sub.add_parser("daily-close", help="close day D (default: yesterday)")
    dc.add_argument("date", nargs="?", help="YYYY-MM-DD to close")
    dc.add_argument(
        "--no-commit",
        action="store_true",
        help="close the day without committing or pushing the vault",
    )
    sub.add_parser("validate", help="check types, slugs, cadence, links")
    up = sub.add_parser(
        "up",
        help="install calendar crontab, catch-up missed days, start watch if dead",
    )
    up.add_argument("--quiet", action="store_true", help="no stdout on success")
    up.add_argument(
        "--watch-only",
        action="store_true",
        help="only ensure the watch process; no crontab or catch-up",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)
    root = get_root()
    cmd = args.cmd
    if cmd == "reindex":
        path = reindex(root, commit=not args.no_commit)
        print(path)
        return 0
    if cmd == "watch":
        if args.loop:
            watch_loop(root)
        else:
            watch(root)
        return 0
    if cmd == "up":
        actions = run_up(root, quiet=args.quiet, watch_only=args.watch_only)
        if any(a.startswith("watch-failed") for a in actions):
            if args.quiet:
                print("watch-failed", file=sys.stderr)
            return 1
        return 0
    if cmd == "daily-close":
        d = date.fromisoformat(args.date) if args.date else None
        path = daily_close(root, d, commit=not args.no_commit)
        print(path)
        return 0
    if cmd == "validate":
        errors = validate(root)
        if errors:
            for err in errors:
                print(err, file=sys.stderr)
            return 1
        print("ok")
        return 0
    parser.error(f"unknown command {cmd}")
    return 2
