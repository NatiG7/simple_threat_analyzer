import json
import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from json_module import *


class JSONOperationsTest(unittest.TestCase):

    @patch("builtins.input", return_value="testfile.txt")
    @patch("os.path.exists", return_value=True)
    @patch("json_module.get_last_scanned_folder", return_value="/path/to/folder")
    @patch("json_module.load_safe_files", return_value=set())
    @patch("json_module.save_safe_files")
    def test_mark_file_as_safe(
        self,
        mock_save_safe_files,
        mock_load_safe_files,
        mock_get_last_scanned_folder,
        mock_exists,
        mock_input,
    ):
        mark_file_as_safe()

        # Check if the file was added to the safe list
        mock_save_safe_files.assert_called_once()
        saved_files = mock_save_safe_files.call_args[0][0]
        self.assertIn("/path/to/folder/testfile.txt", saved_files)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"safe_files": ["/path/to/file1", "/path/to/file2"]}',
    )
    def test_load_safe_files(self, mock_open):
        safe_files = load_safe_files()
        self.assertEqual(safe_files, {"/path/to/file1", "/path/to/file2"})

    @patch("builtins.open", new_callable=mock_open, read_data="{invalid_json}")
    @patch("json.load", side_effect=json.JSONDecodeError("Error", "doc", 0))
    def test_load_safe_files_empty_on_error(self, mock_json_load, mock_open):
        safe_files = load_safe_files()
        self.assertEqual(safe_files, set())  # Expecting an empty set

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_safe_files(self, mock_json_dump, mock_open):
        safe_files = {"/path/to/file3", "/path/to/file4"}
        save_safe_files(safe_files)

        # Ensure correct data is written
        mock_open.assert_called_once_with(
            "/home/nati/Desktop/Software_PET/Python/end_project/json/safe_files.json",
            "w",
        )
        mock_json_dump.assert_called_once_with(
            {"safe_files": list(safe_files)}, mock_open.return_value, indent=4
        )

    @patch("os.path.exists", return_value=True)
    @patch(
        "json_module.load_safe_files", return_value={"/path/to/file1", "/path/to/file2"}
    )
    def test_should_ignore_file(self, mock_load_safe_files, mock_exists):
        result = should_ignore_file("file1", "/path/to/")
        self.assertTrue(result)

    @patch("os.path.exists", return_value=False)
    @patch("json_module.load_safe_files", return_value=set())
    def test_should_not_ignore_file(self, mock_load_safe_files, mock_exists):
        result = should_ignore_file("file1", "/path/to/")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
