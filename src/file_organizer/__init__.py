"""Sort files into category folders with a one-command undo."""

from __future__ import annotations

from file_organizer.core.organizer import (
    category_for,
    plan_moves,
    undo,
)

__version__ = "1.1.0"

__all__ = ["category_for", "plan_moves", "undo", "__version__"]
