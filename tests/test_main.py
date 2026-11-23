"""Tests for the organizer CLI entry point and environment configuration."""

from __future__ import annotations

import importlib
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from file_organizer import config  # noqa: E402
from file_organizer.__main__ import build_parser, main  # noqa: E402

ENV_KEYS = ("ORGANIZER_LOG_NAME", "ORGANIZER_RECURSIVE")


class ParserTests(unittest.TestCase):
    """Cover parser defaults and environment overrides."""

    def test_default_flags(self) -> None:
        """The folder is required and recursive defaults to the config value."""
        args = build_parser().parse_args(["Downloads"])
        self.assertEqual(args.folder, "Downloads")
        self.assertEqual(args.recursive, config.RECURSIVE)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.undo)

    def test_environment_enables_recursive_by_default(self) -> None:
        """ORGANIZER_RECURSIVE=1 changes the parser default."""
        with patch.dict(os.environ, {"ORGANIZER_RECURSIVE": "1"}):
            importlib.reload(config)
            args = build_parser().parse_args(["Downloads"])
        self.assertTrue(args.recursive)

    def test_no_recursive_overrides_environment(self) -> None:
        """--no-recursive wins over a true environment default."""
        with patch.dict(os.environ, {"ORGANIZER_RECURSIVE": "1"}):
            importlib.reload(config)
            args = build_parser().parse_args(["Downloads", "--no-recursive"])
        self.assertFalse(args.recursive)

    def test_invalid_environment_values_fall_back(self) -> None:
        """Blank log names and unknown booleans use defaults."""
        env = {"ORGANIZER_LOG_NAME": "   ", "ORGANIZER_RECURSIVE": "yes"}
        with patch.dict(os.environ, env):
            importlib.reload(config)
            self.assertEqual(config.LOG_NAME, ".organizer-log.json")
            self.assertFalse(config.RECURSIVE)

    def tearDown(self) -> None:
        """Restore config constants after each test."""
        for key in ENV_KEYS:
            os.environ.pop(key, None)
        importlib.reload(config)


class EntryPointTests(unittest.TestCase):
    """Cover the CLI success, dry-run and error paths."""

    def setUp(self) -> None:
        """Create an isolated working folder."""
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        """Remove the working folder and restore config constants."""
        self.temp.cleanup()
        for key in ENV_KEYS:
            os.environ.pop(key, None)
        importlib.reload(config)

    def test_dry_run_prints_plan_without_moving(self) -> None:
        """--dry-run lists moves and leaves files where they are."""
        (self.root / "photo.png").touch()
        with redirect_stdout(io.StringIO()) as output:
            result = main([str(self.root), "--dry-run"])
        self.assertEqual(result, 0)
        self.assertIn("[dry-run] photo.png -> Images/photo.png", output.getvalue())
        self.assertTrue((self.root / "photo.png").exists())

    def test_move_and_undo_via_cli(self) -> None:
        """A real run reports the move and can be undone."""
        (self.root / "notes.txt").touch()
        with redirect_stdout(io.StringIO()) as output:
            result = main([str(self.root)])
        self.assertEqual(result, 0)
        self.assertIn("Moved 1 file(s).", output.getvalue())
        self.assertTrue((self.root / "Documents" / "notes.txt").exists())

        with redirect_stdout(io.StringIO()) as undo_output:
            undo_result = main([str(self.root), "--undo"])
        self.assertEqual(undo_result, 0)
        self.assertIn("Restored 1 file(s).", undo_output.getvalue())
        self.assertTrue((self.root / "notes.txt").exists())

    def test_environment_log_name_is_used(self) -> None:
        """ORGANIZER_LOG_NAME controls the journal filename."""
        (self.root / "song.mp3").touch()
        with (
            patch.dict(os.environ, {"ORGANIZER_LOG_NAME": "custom-log.json"}),
            redirect_stdout(io.StringIO()),
        ):
            importlib.reload(config)
            result = main([str(self.root)])
        self.assertEqual(result, 0)
        self.assertTrue((self.root / "custom-log.json").exists())

    def test_environment_recursive_is_used(self) -> None:
        """ORGANIZER_RECURSIVE=1 includes nested files without a flag."""
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "song.mp3").touch()
        with patch.dict(os.environ, {"ORGANIZER_RECURSIVE": "1"}):
            importlib.reload(config)
            with redirect_stdout(io.StringIO()) as output:
                result = main([str(self.root), "--dry-run"])
        self.assertEqual(result, 0)
        self.assertIn("[dry-run] song.mp3 -> Music/song.mp3", output.getvalue())

    def test_invalid_folder_returns_error_code(self) -> None:
        """A missing folder prints an error and returns 1."""
        with redirect_stderr(io.StringIO()) as errors:
            result = main([str(self.root / "missing")])
        self.assertEqual(result, 1)
        self.assertIn("error: Not a directory", errors.getvalue())

    def test_empty_folder_reports_nothing(self) -> None:
        """A folder with no candidate files is a no-op."""
        with redirect_stdout(io.StringIO()) as output:
            result = main([str(self.root)])
        self.assertEqual(result, 0)
        self.assertIn("Nothing to organize.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
