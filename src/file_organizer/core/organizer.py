"""Plan, apply and undo file moves.

Planning is separated from applying so ``--dry-run`` can show the exact plan
without touching the filesystem. A JSON journal makes every applied move
reversible.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from file_organizer import config

Move = tuple[Path, Path]
Record = dict[str, str]


def category_for(path: Path, categories: dict[str, set[str]] | None = None) -> str:
    """Return the destination folder name for a file.

    Args:
        path: File whose suffix determines the category.
        categories: Optional category map; defaults to :data:`config.CATEGORIES`.

    Returns:
        A category folder name, or ``"Others"`` for unknown suffixes.
    """
    active = config.CATEGORIES if categories is None else categories
    suffix = path.suffix.lower()
    for folder, extensions in active.items():
        if suffix in extensions:
            return folder
    return "Others"


def _unique(target: Path, reserved: set[Path]) -> Path:
    """Avoid overwriting existing files or files already reserved in this run.

    Args:
        target: Preferred destination path.
        reserved: Destinations already chosen during planning; updated in place.

    Returns:
        A path that is both free and reserved for this run.
    """
    candidate = target
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = target.with_name(f"{target.stem}_{counter}{target.suffix}")
        counter += 1
    reserved.add(candidate)
    return candidate


def plan_moves(
    folder: str | Path,
    recursive: bool | None = None,
    categories: dict[str, set[str]] | None = None,
) -> list[Move]:
    """Build a list of ``(source, destination)`` pairs without moving files.

    Args:
        folder: Folder to inspect.
        recursive: Include subfolders; defaults to ``ORGANIZER_RECURSIVE``.
        categories: Optional category map; defaults to :data:`config.CATEGORIES`.

    Returns:
        Sorted source/destination pairs.

    Raises:
        ValueError: If ``folder`` is not a directory.
    """
    active = config.CATEGORIES if categories is None else categories
    include_subfolders = config.RECURSIVE if recursive is None else recursive
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")

    candidates = root.rglob("*") if include_subfolders else root.glob("*")
    reserved: set[Path] = set()
    moves: list[Move] = []

    for path in candidates:
        if not path.is_file() or path.name.startswith("."):
            continue
        relative = path.relative_to(root)
        # Files already inside a category folder are considered organized.
        if any(part in active for part in relative.parts[:-1]):
            continue
        destination_dir = root / category_for(path, active)
        moves.append((path, _unique(destination_dir / path.name, reserved)))

    return sorted(moves, key=lambda pair: str(pair[0]).lower())


def apply_moves(moves: list[Move], log_path: Path, dry_run: bool = False) -> int:
    """Perform planned moves and append them to the undo journal.

    Args:
        moves: Source/destination pairs from :func:`plan_moves`.
        log_path: Journal file to append records to.
        dry_run: Print the plan without moving or writing anything.

    Returns:
        The number of files actually moved (zero for a dry run).
    """
    records: list[Record] = []

    for source, destination in moves:
        if dry_run:
            print(f"[dry-run] {source.name} -> {destination.parent.name}/{destination.name}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        records.append({"source": str(source), "destination": str(destination)})

    if records:
        existing: list[Record] = []
        if log_path.exists():
            try:
                existing = json.loads(log_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = []
        log_path.write_text(json.dumps(existing + records, indent=2), encoding="utf-8")

    return len(records)


def undo(log_path: Path) -> int:
    """Restore every file recorded in the journal, then remove the journal.

    Args:
        log_path: Journal written by :func:`apply_moves`.

    Returns:
        The number of restored files, or ``1`` as an error exit hint when the
        journal cannot be read.
    """
    if not log_path.exists():
        print("Nothing to undo: no log file found.", file=sys.stderr)
        return 0

    try:
        records: list[Record] = json.loads(log_path.read_text(encoding="utf-8"))
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


__all__ = ["apply_moves", "category_for", "plan_moves", "undo"]
