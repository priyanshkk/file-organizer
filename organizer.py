"""Sort files in a folder into category directories, with a one-command undo.

Standard library only. The planning step is separate from the moving step so
you can preview exactly what would happen with --dry-run.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Music": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".html", ".css", ".json", ".sh", ".sql"},
    "Executables": {".exe", ".msi", ".deb", ".rpm", ".dmg", ".app"},
}

DEFAULT_LOG_NAME = ".organizer-log.json"


def category_for(path: Path, categories: dict[str, set[str]] = CATEGORIES) -> str:
    """Return the destination folder name for *path*."""
    suffix = path.suffix.lower()
    for folder, extensions in categories.items():
        if suffix in extensions:
            return folder
    return "Others"


def _unique(target: Path, reserved: set[Path]) -> Path:
    """Avoid overwriting existing files or files already reserved in this run."""
    candidate = target
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = target.with_name(f"{target.stem}_{counter}{target.suffix}")
        counter += 1
    reserved.add(candidate)
    return candidate


def plan_moves(
    folder: str | Path,
    recursive: bool = False,
    categories: dict[str, set[str]] = CATEGORIES,
) -> list[tuple[Path, Path]]:
    """Build a list of (source, destination) pairs without touching files."""
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    candidates = root.rglob("*") if recursive else root.glob("*")
    reserved: set[Path] = set()
    moves: list[tuple[Path, Path]] = []

    for path in candidates:
        if not path.is_file() or path.name.startswith("."):
            continue
        relative = path.relative_to(root)
        # Files already inside a category folder are considered organized.
        if any(part in categories for part in relative.parts[:-1]):
            continue
        destination_dir = root / category_for(path, categories)
        moves.append((path, _unique(destination_dir / path.name, reserved)))

    return sorted(moves, key=lambda pair: str(pair[0]).lower())


def apply_moves(
    moves: list[tuple[Path, Path]],
    log_path: Path,
    dry_run: bool = False,
) -> int:
    """Perform the planned moves and record them for undo. Returns move count."""
    records = []

    for source, destination in moves:
        if dry_run:
            print(f"[dry-run] {source.name} -> {destination.parent.name}/{destination.name}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        records.append({"source": str(source), "destination": str(destination)})

    if records:
        existing = []
        if log_path.exists():
            try:
                existing = json.loads(log_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = []
        log_path.write_text(json.dumps(existing + records, indent=2), encoding="utf-8")

    return len(records)


def undo(log_path: Path) -> int:
    """Restore every file recorded in the log, then remove the log."""
    if not log_path.exists():
        print("Nothing to undo: no log file found.", file=sys.stderr)
        return 0

    try:
        records = json.loads(log_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read log: {exc}", file=sys.stderr)
        return 1

    restored = 0
    for record in reversed(records):
        destination = Path(record["destination"])
        original = Path(record["source"])
        if not destination.exists():
            continue
        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(destination), str(original))
        restored += 1

    log_path.unlink()
    return restored


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("folder", help="folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="show the plan, move nothing")
    parser.add_argument("--recursive", action="store_true", help="include subfolders")
    parser.add_argument("--undo", action="store_true", help="restore the last run")
    parser.add_argument("--log", help="custom log path (default: <folder>/.organizer-log.json)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.folder).expanduser().resolve()
    log_path = Path(args.log).expanduser().resolve() if args.log else root / DEFAULT_LOG_NAME

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
        print(f"Moved {count} file(s). Undo with: python organizer.py \"{root}\" --undo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
