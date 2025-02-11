import json
import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from file_handling import *


class PathHandlingTest(unittest.TestCase):

    @patch("os.path.isdir", return_value=True)
    def test_find_abs_path_valid(self, mock_isdir):
        result = find_abs_path("~/Desktop/project/dir")
        self.assertEqual(result["path"], "/home/nati/Desktop/project/dir")
        self.assertEqual(result["type"], "absolute")
        self.assertTrue(result["exists"])

    @patch("os.path.isdir", return_value=False)
    def test_find_abs_path_invalid(self, mock_isdir):
        result = find_abs_path("~/Desktop/invalid/folder")
        self.assertEqual(
            result["error"],
            "Absolute path [/home/nati/Desktop/invalid/folder] doesnt exist.",
        )
        self.assertFalse(result["exists"])

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_find_rel_path_valid(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = True  # Mocking that the relative path exists

        folder_to_scan = "~/Desktop/project/valid/folder"
        script_dir = "~/Desktop/project"
        result = find_rel_path(folder_to_scan, script_dir)

        self.assertEqual(result["path"], "valid/folder")
        self.assertEqual(result["type"], "relative")
        self.assertTrue(result["exists"])
        self.assertIsNone(result["error"])

    @patch("os.path.exists")
    @patch("os.path.isdir")
    def test_find_rel_path_invalid(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = False  # Mocking non-existent folder

        folder_to_scan = "~/Desktop/project/invalid/folder"
        script_dir = "~/Desktop/project"
        result = find_rel_path(folder_to_scan, script_dir)

        self.assertEqual(
            result["error"],
            "Relative path '/home/nati/Desktop/project/invalid/folder' does not exist.",
        )
        self.assertFalse(result["exists"])

    @patch("os.path.exists")  # Mocking os.path.exists
    @patch("os.path.isdir")  # Mocking os.path.isdir
    def test_find_rel_path_outside_script_dir(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = (
            False  # Mocking folder that is outside the script directory
        )

        folder_to_scan = "~/Python"
        script_dir = "~/Desktop/project/other"
        result = find_rel_path(folder_to_scan, script_dir)

        self.assertEqual(
            result["error"],
            f"Folder '/home/nati/Python' is outside '/home/nati/Desktop/project/other'.",
        )
        self.assertFalse(result["exists"])

    @patch("os.path.exists")  # Mocking os.path.exists
    @patch("os.path.isdir")  # Mocking os.path.isdir
    def test_find_rel_path_empty(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = False  # Mocking empty path

        folder_to_scan = ""
        script_dir = "~/Desktop/project"
        result = find_rel_path(folder_to_scan, script_dir)

        self.assertEqual(result["error"], "Empty path provided.")
        self.assertFalse(result["exists"])

    @patch("os.path.exists")  # Mocking os.path.exists
    def test_find_rel_path_invalid_script_dir(self, mock_exists):
        mock_exists.return_value = False  # Mocking non-existent script directory

        folder_to_scan = "~/Desktop/project/folder"
        script_dir = "~/Desktop/invalid_script"
        result = find_rel_path(folder_to_scan, script_dir)

        self.assertEqual(
            result["error"],
            "Base script dir /home/nati/Desktop/invalid_script does not exist.",
        )
        self.assertFalse(result["exists"])

    @patch("os.walk")
    def test_search_system_found(self, mock_walk):
        # Simulate the folder being found
        mock_walk.return_value = [
            ("/home/nati/Desktop", ["project", "other", "dir"], []),
            ("/home/nati/Desktop/project", ["valid", "invalid"], []),
            ("/home/nati/Desktop/project/valid", [], []),
        ]
        folder_to_scan = "valid"
        expected_result = {
            "path": "/home/nati/Desktop/project/valid",
            "type": "sys_search",
            "exists": True,
            "error": None,
        }

        result = search_system(folder_to_scan)

        self.assertEqual(result, expected_result)

    @patch("os.walk")
    def test_search_system_not_found(self, mock_walk):
        # Simulate the folder not being found
        mock_walk.return_value = [
            ("/home/nati/Desktop", ["project", "other", "dir"], []),
            ("/home/nati/Desktop/project", ["invalid", "other"], []),
        ]
        folder_to_scan = "valid"

        with self.assertRaises(FileNotFoundError):
            search_system(folder_to_scan)

    @patch("os.walk")
    def test_search_system_permission_error(self, mock_walk):
        # Simulate permission error during search
        mock_walk.side_effect = PermissionError("Permission denied")
        folder_to_scan = "valid"

        with self.assertRaises(PermissionError):
            search_system(folder_to_scan)

    @patch("os.walk")
    def test_search_system_interrupted(self, mock_walk):
        # Simulate interrupted search (KeyboardInterrupt)
        mock_walk.side_effect = KeyboardInterrupt
        folder_to_scan = "valid"

        result = search_system(folder_to_scan)
        self.assertEqual(result["error"], "Search interrupted by user.")
        self.assertFalse(result["exists"])

    @patch("os.walk")
    def test_search_system_os_error(self, mock_walk):
        # Simulate OS error during search
        mock_walk.side_effect = OSError("OS Error")
        folder_to_scan = "valid"

        with self.assertRaises(OSError):
            search_system(folder_to_scan)


class ScanAndDataTest(unittest.TestCase):

    # ---- Test extract_file_data ----

    @patch(
        "os.path.isfile", return_value=True
    )  # Mocking os.path.isfile to always return True
    @patch(
        "os.path.getsize", return_value=1024
    )  # Mocking os.path.getsize to return a constant size
    @patch(
        "os.listdir", return_value=["file1.txt", "file2.csv", "image.png"]
    )  # Mocking os.listdir
    def test_extract_file_data(self, mock_listdir, mock_getsize, mock_isfile):
        folder_path = "/home/nati/Desktop"

        expected_data = [
            {
                "name": "file1",
                "extension": ".txt",
                "size(B)": 1024,
                "folder_path": folder_path,
            },
            {
                "name": "file2",
                "extension": ".csv",
                "size(B)": 1024,
                "folder_path": folder_path,
            },
            {
                "name": "image",
                "extension": ".png",
                "size(B)": 1024,
                "folder_path": folder_path,
            },
        ]

        result = extract_file_data(folder_path)

        self.assertEqual(result, expected_data)

    @patch("os.listdir", side_effect=PermissionError("Permission denied"))
    def test_extract_file_data_permission_error(self, mock_listdir):
        folder_path = "/home/nati/Desktop"

        with self.assertRaises(PermissionError):
            extract_file_data(folder_path)

    @patch("os.listdir", side_effect=OSError("OS error"))
    def test_extract_file_data_os_error(self, mock_listdir):
        folder_path = "/home/nati/Desktop"

        with self.assertRaises(OSError):
            extract_file_data(folder_path)

    # ---- Test scan_files ----

    @patch("file_handling.find_abs_path")
    @patch("file_handling.find_rel_path")
    @patch("file_handling.search_system")
    def test_scan_files_absolute_path(
        self, mock_search_system, mock_find_rel_path, mock_find_abs_path
    ):
        # Mocking an absolute path check
        mock_find_abs_path.return_value = {
            "path": "/home/nati/Desktop/project",
            "type": "absolute",
            "exists": True,
        }

        folder = "/home/nati/Desktop/project"
        result = scan_files(folder)

        self.assertEqual(result["path"], "/home/nati/Desktop/project")
        self.assertEqual(result["type"], "absolute")
        self.assertTrue(result["exists"])

    @patch("file_handling.find_abs_path")
    @patch("file_handling.find_rel_path")
    @patch("file_handling.search_system")
    def test_scan_files_relative_path(
        self, mock_search_system, mock_find_rel_path, mock_find_abs_path
    ):
        # Mocking a relative path check
        mock_find_abs_path.return_value = {"path": None, "type": None, "exists": False}
        mock_find_rel_path.return_value = {
            "path": "project/dir",
            "type": "relative",
            "exists": True,
        }

        folder = "project/dir"
        result = scan_files(folder)

        self.assertEqual(result["path"], "project/dir")
        self.assertEqual(result["type"], "relative")
        self.assertTrue(result["exists"])

    @patch("file_handling.find_abs_path")
    @patch("file_handling.find_rel_path")
    @patch("file_handling.search_system")
    def test_scan_files_folder_name(
        self, mock_search_system, mock_find_rel_path, mock_find_abs_path
    ):
        # Mocking a folder name scan
        mock_find_abs_path.return_value = {"path": None, "type": None, "exists": False}
        mock_find_rel_path.return_value = {"path": None, "type": None, "exists": False}
        mock_search_system.return_value = {
            "path": "/home/nati/Desktop/project/dir",
            "type": "sys_search",
            "exists": True,
        }

        folder = "dir"
        result = scan_files(folder)

        self.assertEqual(result["path"], "/home/nati/Desktop/project/dir")
        self.assertEqual(result["type"], "sys_search")
        self.assertTrue(result["exists"])

    @patch("file_handling.find_abs_path")
    @patch("file_handling.find_rel_path")
    @patch("file_handling.search_system")
    def test_scan_files_permission_error(
        self, mock_search_system, mock_find_rel_path, mock_find_abs_path
    ):
        # Mocking permission error in the scan
        mock_find_abs_path.return_value = {"path": None, "type": None, "exists": False}
        mock_find_rel_path.return_value = {"path": None, "type": None, "exists": False}
        mock_search_system.return_value = {
            "path": None,
            "type": None,
            "exists": False,
            "error": "Permission denied",
        }

        folder = "/home/nati/Desktop/project/invalid"
        result = scan_files(folder)

        self.assertEqual(
            result["error"], f"Permission denied while accessing {folder}."
        )

    @patch("file_handling.find_abs_path")
    @patch("file_handling.find_rel_path")
    @patch("file_handling.search_system")
    def test_scan_files_os_error(
        self, mock_search_system, mock_find_rel_path, mock_find_abs_path
    ):
        # Mocking OS error in the scan
        mock_find_abs_path.return_value = {"path": None, "type": None, "exists": False}
        mock_find_rel_path.return_value = {"path": None, "type": None, "exists": False}
        mock_search_system.return_value = {
            "path": None,
            "type": None,
            "exists": False,
            "error": "OS error",
        }

        folder = "/home/nati/Desktop/project/invalid_folder"
        result = scan_files(folder)

        self.assertEqual(result["error"], f"OS error while reading folder {folder}")

    # ---- Test save_last_scanned_folder ----

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("os.path.abspath")
    @patch("os.path.dirname")
    def test_save_last_scanned_folder(
        self, mock_dirname, mock_abspath, mock_json_dump, mock_open
    ):
        # Setup mock for os.path functions to return the desired paths
        mock_dirname.return_value = "/home/nati/Desktop/Software_PET/Python/end_project"  # Path where your script is located
        mock_abspath.return_value = "/home/nati/Desktop/Software_PET/Python/end_project"  # Absolute path for the script directory

        folder_path = "/home/nati/Desktop/project"

        # Dynamically create the expected path for the JSON file
        expected_json_path = os.path.join(
            "/home/nati/Desktop/Software_PET/Python/end_project",
            "json",
            "last_scanned_folder.json",
        )

        # Call the function you're testing
        save_last_scanned_folder(folder_path)

        # Assert open was called with the correct path
        mock_open.assert_called_once_with(expected_json_path, "w")

        # Ensure json.dump was called with the correct data
        mock_json_dump.assert_called_once_with(
            {"last_scanned_folder": folder_path}, mock_open()
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_save_last_scanned_folder_io_error(self, mock_open):
        folder_path = "/home/nati/Desktop/project"

        mock_open.side_effect = IOError("File write error")

        with self.assertRaises(IOError):
            save_last_scanned_folder(folder_path)

    # ---- Test get_last_scanned_folder ----

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps({"last_scanned_folder": "/home/nati/Desktop/project"}),
    )
    def test_get_last_scanned_folder(self, mock_open):
        result = get_last_scanned_folder()

        self.assertEqual(result, "/home/nati/Desktop/project")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_get_last_scanned_folder_not_found(self, mock_json_load, mock_open):
        # Simulate FileNotFoundError by raising an exception
        mock_json_load.side_effect = FileNotFoundError(
            "Last scanned folder file not found."
        )

        # Run the function
        with self.assertRaises(FileNotFoundError) as context:
            get_last_scanned_folder()

        # Check the exception message
        self.assertTrue("Last scanned folder file not found." in str(context.exception))

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_get_last_scanned_folder_json_decode_error(self, mock_open):
        with self.assertRaises(json.JSONDecodeError):
            get_last_scanned_folder()


if __name__ == "__main__":
    unittest.main()
