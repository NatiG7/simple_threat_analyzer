import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import threat_handling
from threat_handling import *


class TestFileScanner(unittest.TestCase):

    @patch("builtins.open", mock_open(read_data="file1\nfile2"))
    @patch("os.path.exists", return_value=True)
    @patch("os.path.abspath", return_value="/path/to/folder")
    @patch("os.path.join", side_effect=lambda *args: "/".join(args))
    def test_get_threats_success(self, mock_join, mock_abspath, mock_exists):
        # Test for successful file reading
        names, extensions = get_threats()
        self.assertEqual(names, ["file1", "file2"])
        self.assertEqual(extensions, ["file1", "file2"])

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_threats_file_not_found(self, mock_open):
        # Test for FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            get_threats()

    @patch("builtins.open", side_effect=PermissionError)
    def test_get_threats_permission_error(self, mock_open):
        # Test for PermissionError
        with self.assertRaises(PermissionError):
            get_threats()

    @patch("builtins.open", side_effect=IsADirectoryError)
    def test_get_threats_is_a_directory_error(self, mock_open):
        # Test for IsADirectoryError
        with self.assertRaises(IsADirectoryError):
            get_threats()

    @patch("threat_handling.scan_files", return_value={"path": "/fake/path"})
    @patch(
        "threat_handling.extract_file_data",
        return_value=[
            {
                "name": "file1",
                "extension": ".txt",
                "size(B)": 500,
                "folder_path": "/fake/path",
            }
        ],
    )
    @patch("threat_handling.should_ignore_file", return_value=False)
    @patch("threat_handling.get_threats", return_value=(["file1"], [".txt"]))
    @patch("threat_handling.verify_pe_header", return_value=False)
    @patch("threat_handling.Logger.generate_log_filename", return_value="test_log.log")
    @patch("threat_handling.Logger.write_to_log")
    def test_assess_threats(
        self,
        mock_write_to_log,
        mock_generate_log_filename,
        mock_verify_pe_header,
        mock_threat,
        mock_scan,
        mock_stuff,
        mock_lol,
    ):
        # Test for the assess_threats function
        files = [
            {
                "name": "file1",
                "extension": ".txt",
                "size(B)": 500,
                "folder_path": "/fake/path",
            }
        ]
        assess_threats(files)
        mock_write_to_log.assert_called_once()
        self.assertIn("Risk level", mock_write_to_log.call_args[0][1])

    @patch("builtins.open", mock_open(read_data=b"\x50\x45\x00\x00"))
    def test_verify_pe_header_success(self):
        # Test for PE header verification
        result = verify_pe_header("/path/to/file.exe")
        self.assertTrue(result)

    @patch("builtins.open", mock_open(read_data=b"\x00\x00\x00\x00"))
    def test_verify_pe_header_failure(self):
        # Test for failure to verify PE header
        result = verify_pe_header("/path/to/file.exe")
        self.assertFalse(result)

    @patch("threat_handling.input", return_value="/fake/path")
    @patch("threat_handling.scan_files", return_value={"path": "/fake/path"})
    @patch("threat_handling.extract_file_data", return_value=[])
    @patch(
        "os.path.exists", return_value=True
    )  # Mock os.path.exists to always return True
    def test_check_suspicious_files_no_files(
        self, mock_extract_file_data, mock_scan_files, mock_input, mock_exists
    ):
        # Test when no files are found in the scanned directory
        with patch("builtins.print") as mock_print:
            check_suspicious_files()
            mock_print.assert_called_with("No files found in '/fake/path'.")

    @patch("threat_handling.input", return_value="/fake/path")
    @patch("threat_handling.scan_files", return_value={"path": "/fake/path"})
    @patch(
        "threat_handling.extract_file_data",
        return_value=[
            {
                "name": "file1",
                "extension": ".txt",
                "size(B)": 500,
                "folder_path": "/fake/path",
            }
        ],
    )
    @patch("threat_handling.should_ignore_file", return_value=False)
    @patch("threat_handling.get_threats", return_value=(["file1"], [".txt"]))
    @patch("threat_handling.verify_pe_header", return_value=False)
    @patch("threat_handling.Logger.generate_log_filename", return_value="test_log.log")
    @patch("threat_handling.Logger.write_to_log")
    @patch(
        "os.path.exists", return_value=True
    )  # Mock os.path.exists to always return True
    def test_check_suspicious_files_success(
        self,
        mock_write_to_log,
        mock_generate_log_filename,
        mock_verify_pe_header,
        mock_get_threats,
        mock_should_ignore_file,
        mock_extract_file_data,
        mock_scan_files,
        mock_input,
        mock_exists,
    ):
        # Test for a successful scan and threat assessment
        with patch("builtins.print") as mock_print:
            check_suspicious_files()
            mock_print.assert_called_with("\033[92mScan logged succesfully.\033[0m")


if __name__ == "__main__":
    unittest.main()
