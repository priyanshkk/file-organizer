"""Command-line entry point for the file organizer.

Run with ``python -m file_organizer FOLDER`` or the installed ``file-organizer``
console script.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from file_organizer import config
from file_organizer.core.organizer import apply_moves, plan_moves, undo


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns:
        A parser with ``--recursive`` defaulting to ``ORGANIZER_RECURSIVE``.
    """
    parser = argparse.ArgumentParser(
        prog="file-organizer", description="Organize files into category folders."
    )
    parser.add_argument("folder", help="folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="show the plan, move nothing")
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=config.RECURSIVE,
        help=f"include subfolders (default: {int(config.RECURSIVE)})",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="only organize the top level, overriding ORGANIZER_RECURSIVE",
    )
    parser.add_argument("--undo", action="store_true", help="restore the last run")
    parser.add_argument(
        "--log",
        help=f"custom log path (default: <folder>/{config.LOG_NAME})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the organizer CLI.

    Args:
        argv: Optional argument list; defaults to ``sys.argv[1:]``.

    Returns:
        ``0`` on success, ``1`` when the target folder is invalid.
    """
    args = build_parser().parse_args(argv)
    root = Path(args.folder).expanduser().resolve()
    log_path = Path(args.log).expanduser().resolve() if args.log else root / config.LOG_NAME

    if args.undo:
        count = undo(log_path)
        print(f"Restored {count} file(s).")
        return 0

    try:
        moves = plan_moves(root, recursive=args.recursive)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not moves:
        print("Nothing to organize.")
        return 0

    count = apply_moves(moves, log_path, dry_run=args.dry_run)
    if not args.dry_run:
        print(f'Moved {count} file(s). Undo with: python organizer.py "{root}" --undo')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
