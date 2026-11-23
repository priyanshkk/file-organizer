"""Unit tests for planning, applying and undoing file moves."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from file_organizer.core.organizer import (  # noqa: E402
    apply_moves,
    category_for,
    plan_moves,
    undo,
)


class OrganizerCoreTests(unittest.TestCase):
    """Cover the original organizer logic with explicit arguments."""

    def setUp(self) -> None:
        """Create an isolated working folder."""
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.log = self.root / ".organizer-log.json"

    def tearDown(self) -> None:
        """Remove the working folder."""
        self.temp.cleanup()

    def test_category_for_known_and_unknown_extensions(self) -> None:
        """Suffix matching is case-insensitive and falls back to Others."""
        self.assertEqual(category_for(Path("a.PNG")), "Images")
        self.assertEqual(category_for(Path("notes.md")), "Documents")
        self.assertEqual(category_for(Path("thing.xyz")), "Others")

    def test_plan_and_apply_and_undo(self) -> None:
        """A full organize/undo cycle restores every file."""
        (self.root / "photo.png").touch()
        (self.root / "notes.txt").touch()
        (self.root / "random.xyz").touch()

        moves = plan_moves(self.root, recursive=False)
        self.assertEqual(len(moves), 3)
        self.assertEqual(apply_moves(moves, self.log), 3)

        self.assertTrue((self.root / "Images" / "photo.png").exists())
        self.assertTrue((self.root / "Documents" / "notes.txt").exists())
        self.assertTrue((self.root / "Others" / "random.xyz").exists())

        self.assertEqual(undo(self.log), 3)
        self.assertTrue((self.root / "photo.png").exists())
        self.assertFalse((self.root / "Images" / "photo.png").exists())
        self.assertFalse(self.log.exists())

    def test_duplicate_names_are_not_overwritten(self) -> None:
        """Colliding names get a numeric suffix within the run."""
        (self.root / "a.txt").touch()
        (self.root / "Documents").mkdir()
        (self.root / "Documents" / "a.txt").write_text("original", encoding="utf-8")

        moves = plan_moves(self.root, recursive=False)
        destinations = [destination.name for _, destination in moves]
        self.assertIn("a_1.txt", destinations)

        apply_moves(moves, self.log)
        self.assertEqual(
            (self.root / "Documents" / "a.txt").read_text(encoding="utf-8"), "original"
        )
        self.assertTrue((self.root / "Documents" / "a_1.txt").exists())

    def test_already_organized_files_are_skipped(self) -> None:
        """Files inside a category folder are left alone."""
        (self.root / "Images").mkdir()
        (self.root / "Images" / "pic.jpg").touch()
        self.assertEqual(plan_moves(self.root, recursive=False), [])

    def test_hidden_files_are_skipped(self) -> None:
        """Dotfiles are never moved."""
        (self.root / ".env").touch()
        self.assertEqual(plan_moves(self.root, recursive=False), [])

    def test_recursive_includes_subfolders(self) -> None:
        """Recursive planning descends into subfolders."""
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "song.mp3").touch()
        self.assertEqual(
            plan_moves(self.root, recursive=True)[0][0].name,
            "song.mp3",
        )

    def test_non_directory_is_rejected(self) -> None:
        """A missing folder raises ValueError."""
        with self.assertRaises(ValueError):
            plan_moves(self.root / "missing", recursive=False)

    def test_dry_run_changes_nothing(self) -> None:
        """Dry runs only print the plan."""
        (self.root / "photo.png").touch()
        moves = plan_moves(self.root, recursive=False)
        with redirect_stdout(io.StringIO()) as output:
            moved = apply_moves(moves, self.log, dry_run=True)
        self.assertEqual(moved, 0)
        self.assertIn("[dry-run] photo.png -> Images/photo.png", output.getvalue())
        self.assertTrue((self.root / "photo.png").exists())
        self.assertFalse(self.log.exists())

    def test_custom_categories(self) -> None:
        """A caller-supplied category map overrides the default one."""
        categories = {"Notes": {".note"}}
        self.assertEqual(category_for(Path("x.note"), categories), "Notes")
        self.assertEqual(category_for(Path("x.txt"), categories), "Others")


if __name__ == "__main__":
    unittest.main()
