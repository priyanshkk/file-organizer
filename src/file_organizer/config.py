"""Runtime configuration for the file organizer.

Environment variables are read once at import time. The log name is used for
the undo journal and the recursive flag is the default for ``plan_moves()`` and
the CLI.

Attributes:
    CATEGORIES: Mapping of folder name to lower-case file extensions.
    LOG_NAME: Name of the undo journal inside the target folder.
    DEFAULT_LOG_NAME: Backward-compatible alias of :data:`LOG_NAME`.
    RECURSIVE: Whether subfolders are included by default.
"""

from __future__ import annotations

import os

CATEGORIES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"},
    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".md",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    },
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Music": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".html",
        ".css",
        ".json",
        ".sh",
        ".sql",
    },
    "Executables": {".exe", ".msi", ".deb", ".rpm", ".dmg", ".app"},
}


def env_log_name(name: str, default: str) -> str:
    """Read a non-empty log filename from the environment.

    Args:
        name: Environment variable name.
        default: Value to use when the variable is absent or blank.

    Returns:
        The configured filename or ``default``.
    """
    value = os.environ.get(name, default).strip()
    return value or default


def env_bool(name: str, default: bool = False) -> bool:
    """Read a ``0``/``1`` boolean from the environment.

    Args:
        name: Environment variable name.
        default: Value to use when the variable is absent or unrecognised.

    Returns:
        ``True`` for ``1``, ``False`` for ``0`` or an invalid value.
    """
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized == "1":
        return True
    if normalized == "0":
        return False
    return default


LOG_NAME = env_log_name("ORGANIZER_LOG_NAME", ".organizer-log.json")
DEFAULT_LOG_NAME = LOG_NAME
RECURSIVE = env_bool("ORGANIZER_RECURSIVE")

__all__ = ["DEFAULT_LOG_NAME", "LOG_NAME", "RECURSIVE", "env_bool", "env_log_name"]
