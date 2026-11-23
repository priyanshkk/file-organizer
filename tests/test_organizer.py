import tempfile
import unittest
from pathlib import Path

import organizer


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.log = self.root / organizer.DEFAULT_LOG_NAME

    def tearDown(self):
        self.temp.cleanup()

    def test_category_for_known_and_unknown_extensions(self):
        self.assertEqual(organizer.category_for(Path("a.PNG")), "Images")
        self.assertEqual(organizer.category_for(Path("notes.md")), "Documents")
        self.assertEqual(organizer.category_for(Path("thing.xyz")), "Others")

    def test_plan_and_apply_and_undo(self):
        (self.root / "photo.png").touch()
        (self.root / "notes.txt").touch()
        (self.root / "random.xyz").touch()

        moves = organizer.plan_moves(self.root)
        self.assertEqual(len(moves), 3)
        self.assertEqual(organizer.apply_moves(moves, self.log), 3)

        self.assertTrue((self.root / "Images" / "photo.png").exists())
        self.assertTrue((self.root / "Documents" / "notes.txt").exists())
        self.assertTrue((self.root / "Others" / "random.xyz").exists())

        self.assertEqual(organizer.undo(self.log), 3)
        self.assertTrue((self.root / "photo.png").exists())
        self.assertFalse((self.root / "Images" / "photo.png").exists())
        self.assertFalse(self.log.exists())

    def test_duplicate_names_are_not_overwritten(self):
        (self.root / "a.txt").touch()
        (self.root / "Documents").mkdir()
        (self.root / "Documents" / "a.txt").write_text("original", encoding="utf-8")

        moves = organizer.plan_moves(self.root)
        destinations = [destination.name for _, destination in moves]
        self.assertIn("a_1.txt", destinations)

        organizer.apply_moves(moves, self.log)
        self.assertEqual(
            (self.root / "Documents" / "a.txt").read_text(encoding="utf-8"), "original"
        )
        self.assertTrue((self.root / "Documents" / "a_1.txt").exists())

    def test_already_organized_files_are_skipped(self):
        (self.root / "Images").mkdir()
        (self.root / "Images" / "pic.jpg").touch()
        self.assertEqual(organizer.plan_moves(self.root), [])

    def test_hidden_files_are_skipped(self):
        (self.root / ".env").touch()
        self.assertEqual(organizer.plan_moves(self.root), [])

    def test_recursive_includes_subfolders(self):
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "song.mp3").touch()
        self.assertEqual(organizer.plan_moves(self.root, recursive=True)[0][0].name, "song.mp3")


if __name__ == "__main__":
    unittest.main()
