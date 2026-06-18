import unittest
import tempfile
import os
import shutil

from file_manager.core import *
from file_manager.cli import build_parser


class TestCore(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = self.tmpdir.name

        # файл
        self.src_file = os.path.join(self.base, "source.txt")
        with open(self.src_file, "w", encoding="utf-8") as f:
            f.write("hello test")

        # папка + вложения
        self.folder = os.path.join(self.base, "folder")
        os.makedirs(self.folder, exist_ok=True)

        self.nested = os.path.join(self.folder, "nested")
        os.makedirs(self.nested, exist_ok=True)

        with open(os.path.join(self.folder, "a.py"), "w", encoding="utf-8") as f:
            f.write("print(1)")
        with open(os.path.join(self.nested, "b.txt"), "w", encoding="utf-8") as f:
            f.write("data")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_copy_file_creates_copy_in_same_dir(self):
        copy_path = copy_file(self.src_file)
        self.assertTrue(os.path.exists(copy_path))
        self.assertTrue(os.path.basename(copy_path).startswith("copy_"))

        with open(copy_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "hello test")

    def test_copy_file_missing_raises(self):
        missing = os.path.join(self.base, "missing.txt")
        with self.assertRaises(FileNotFoundError):
            copy_file(missing)

    def test_delete_file_removes_file(self):
        self.assertTrue(os.path.exists(self.src_file))
        delete_path(self.src_file)
        self.assertFalse(os.path.exists(self.src_file))

    def test_delete_folder_removes_folder(self):
        self.assertTrue(os.path.isdir(self.folder))
        delete_path(self.folder)
        self.assertFalse(os.path.exists(self.folder))

    def test_count_files_recursive(self):
        # source.txt + folder/a.py + folder/nested/b.txt = 3
        self.assertEqual(count_files(self.base), 3)

    def test_find_files_by_regex(self):
        matches = find_files(self.base, r"\.py$")
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0].endswith("a.py"))

    def test_add_creation_date_on_file(self):
        renamed = add_creation_date(self.src_file)
        self.assertEqual(len(renamed), 1)
        self.assertTrue(os.path.exists(renamed[0]))
        self.assertFalse(os.path.exists(self.src_file))

    def test_analyse_returns_total_and_summary(self):
        total, summary = analyse(self.base)
        self.assertIsInstance(total, int)
        self.assertIsInstance(summary, dict)
        self.assertTrue(total > 0)
        self.assertIn("source.txt", summary)


class TestCLI(unittest.TestCase):
    def test_parse_copy_args(self):
        parser = build_parser()
        args = parser.parse_args(["copy", "a.txt"])
        self.assertEqual(args.command, "copy")
        self.assertEqual(args.path, "a.txt")

    def test_parse_delete_args(self):
        parser = build_parser()
        args = parser.parse_args(["delete", "a.txt"])
        self.assertEqual(args.command, "delete")
        self.assertEqual(args.path, "a.txt")

    def test_parse_find_args(self):
        parser = build_parser()
        args = parser.parse_args(["find", "folder", r"\.txt$"])
        self.assertEqual(args.command, "find")
        self.assertEqual(args.directory, "folder")
        self.assertEqual(args.pattern, r"\.txt$")


if __name__ == "__main__":
    unittest.main()
