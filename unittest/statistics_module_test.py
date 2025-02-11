import io
import os
import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import statistics_module
from statistics_module import *


class TestStatisticsModule(unittest.TestCase):

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="Summary\nFile: test.txt\nSize: 1234\nRisk: Low\n",
    )
    @patch("os.listdir", return_value=["log_1234567890.log", "log_1234567891.log"])
    @patch(
        "statistics_module.get_latest_log_filename", return_value="log_1234567891.log"
    )
    def test_last_scan_statistics(
        self, mock_get_latest_log_filename, mock_listdir, mock_open_file
    ):
        
        self.maxDiff = None
        # Setting up mock data
        logs_dir = "/home/nati/Desktop/Software_PET/Python/end_project/logs"
        log_file_content = """Summary
        File: test.txt
        Size: 1234
        Risk: Low
        """

        # Test the last_scan_statistics function
        last_scan_statistics()
        expected_log_path = os.path.join(
            os.path.dirname(os.path.abspath(os.path.dirname(__file__))),
            logs_dir,
            "log_1234567891.log",
        )
        # Verify that the log file was opened correctly
        mock_open_file.assert_called_with(expected_log_path, "r")

        # Ensure that the last scan statistics were printed
        expected_output = (
        f"Script-dir:{os.path.abspath(os.path.dirname(__file__))}\n"
        f"Logs-dir:{logs_dir}\n"
        f"Last-log:log_1234567891.log\n\n"
        "Summary\n"
        "Folder: Unknown\n"
        "Files in folder: 1\n"
        "Extensions:\n\ttxt\n"
        "Largest file: test.txt at 1234 bytes\n"
        "Smallest file: test.txt at 1234 bytes\n"
        "Suspicious files: 0\n"
        )

        # Check that the printed output matches the expected format
        with patch("sys.stdout", new=io.StringIO()) as mock_stdout:
            last_scan_statistics()
            output = mock_stdout.getvalue()
            self.assertEqual(output.strip(), expected_output.strip())

    def test_format_extensions(self):
        # Test the format_extensions function
        extensions = {"txt", "jpg", "pdf", "png", "docx"}
        formatted_extensions = format_extensions(extensions, max_per_line=3)
        formatted_lines = formatted_extensions.split("\n\t\t")

        for line in formatted_lines:
            extensions_in_line = line.split(", ")
            self.assertTrue(
                len(extensions_in_line) <= 3,
                f"Line contains more than {3} extensions: {extensions_in_line}",
            )

        formatted_extensions_set = set(", ".join(formatted_lines).split(", "))
        self.assertEqual(
            formatted_extensions_set,
            extensions,
            f"Extensions in formatted output do not match input set. Expected: {extensions}, Got: {formatted_extensions_set}",
        )

    def test_get_latest_log_filename(self):
        # Mock directory contents
        logs_dir = "logs"
        log_files = ["log_1234567890_SALT.log", "log_1234567891_SALT.log"]

        # Test the get_latest_log_filename function
        with patch("os.listdir", return_value=log_files):
            latest_log = get_latest_log_filename(logs_dir)
            self.assertEqual(latest_log, "log_1234567891_SALT.log")

    def test_format_extensions_invalid(self):
        # Test invalid input for format_extensions
        with self.assertRaises(ValueError):
            format_extensions("invalid", max_per_line=3)  # extensions should be a set

        with self.assertRaises(ValueError):
            format_extensions(
                {"txt", "jpg"}, max_per_line=-1
            )  # max_per_line should be positive integer

    @patch("os.listdir")
    def test_get_latest_log_filename_no_log(self, mock_listdir):
        # Test if no log files exist
        mock_listdir.return_value = []

        latest_log = get_latest_log_filename("logs")

        # Ensure None is returned when no log files are found
        self.assertIsNone(latest_log)


if __name__ == "__main__":
    unittest.main()


