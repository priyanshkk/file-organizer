"""Backward-compatible launcher for the file organizer.

New code should use ``python -m file_organizer``. The ``src/`` path is
bootstrapped so this shim also works from a source checkout.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from file_organizer.__main__ import build_parser as build_parser  # noqa: E402
from file_organizer.__main__ import main as main  # noqa: E402
from file_organizer.config import DEFAULT_LOG_NAME as DEFAULT_LOG_NAME  # noqa: E402
from file_organizer.core.organizer import apply_moves as apply_moves  # noqa: E402
from file_organizer.core.organizer import category_for as category_for  # noqa: E402
from file_organizer.core.organizer import plan_moves as plan_moves  # noqa: E402
from file_organizer.core.organizer import undo as undo  # noqa: E402

__all__ = [
    "DEFAULT_LOG_NAME",
    "apply_moves",
    "build_parser",
    "category_for",
    "main",
    "plan_moves",
    "undo",
]

if __name__ == "__main__":
    raise SystemExit(main())
