from __future__ import annotations

import argparse
import sys
from datetime import date

from .config import get_root
from .daily import daily_close
from .index import reindex
from .layout import migrate_layout
from .up import run_up
from .validate import validate
from .vaultmigrate import migrate_vault
from .watch import watch, watch_loop


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aos", description="Agency Operating System")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reindex", help="apply checks, rebuild tasks.md and the schedule")
    w = sub.add_parser("watch", help="watch tasks.md and reindex on checkbox")
    w.add_argument(
        "--loop",
        action="store_true",
        help="restart watch() after a crash until interrupted",
    )
    dc = sub.add_parser("daily-close", help="close day D (default: yesterday)")
    dc.add_argument("date", nargs="?", help="YYYY-MM-DD to close")
    ml = sub.add_parser(
        "migrate-layout",
        help="move dailies and the schedule onto YYYY-MM paths",
    )
    ml.add_argument(
        "date",
        nargs="?",
        help="today as YYYY-MM-DD (default: America/Sao_Paulo)",
    )
    mig = sub.add_parser(
        "migrate",
        help="migrate due/do_in/do_after onto do_on, paused, and the YYYY-MM layout",
    )
    mig.add_argument(
        "--dry-run",
        action="store_true",
        help="print the path diff and write nothing",
    )
    mig.add_argument(
        "date",
        nargs="?",
        help="today as YYYY-MM-DD (default: America/Sao_Paulo)",
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
        path = reindex(root)
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
        path = daily_close(root, d)
        print(path)
        return 0
    if cmd == "migrate":
        d = date.fromisoformat(args.date) if args.date else None
        notes = migrate_vault(root, d, dry_run=args.dry_run)
        if notes:
            for line in notes:
                print(line)
        else:
            print("ok")
        if any(line.startswith("kept:") for line in notes):
            return 1
        return 0
    if cmd == "migrate-layout":
        d = date.fromisoformat(args.date) if args.date else None
        notes = migrate_layout(root, d)
        if notes:
            for line in notes:
                print(line)
        else:
            print("ok")
        if any(line.startswith("kept:") for line in notes):
            return 1
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
