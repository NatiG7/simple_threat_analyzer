import os
import random
import string
import sys
import time
import unittest
from unittest.mock import mock_open, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logging_module
from logging_module import *


class TestLoggingModule(unittest.TestCase):

    def test_generate_salt(self):
        # Test to ensure the generated salt is of the correct length
        salt = generate_salt(64)
        self.assertEqual(len(salt), 64)

        # Test that the salt contains only letters and digits
        self.assertTrue(all(c in string.ascii_letters + string.digits for c in salt))

    @patch(
        "time.time", return_value=1609459200)
    def test_generate_log_filename(self, mock_time):
        # Generate log filename and check that it follows the format log_<timestamp>_<salt>.log
        log_filename = generate_log_filename()
        self.assertTrue(log_filename.startswith("log_1609459200_"))
        self.assertTrue(log_filename.endswith(".log"))
        self.assertEqual(len(log_filename.split("_")[2].replace(".log", "")), 64)


    @patch("builtins.open", new_callable=mock_open)  # (1st injected)
    @patch("os.makedirs")  # (2nd injected)
    @patch("os.path.exists", return_value=False)  # (3rd injected)
    def test_write_to_log_creates_file(self, mock_exists, mock_makedirs, mock_file):
        log_filename = "test_log.log"
        content = "Test log content"

        # Call the function
        logging_module.write_to_log(log_filename, content)

        # Dynamically get the expected logs directory
        expected_logs_dir = os.path.join(os.path.abspath(os.path.dirname(logging_module.__file__)), "logs")

        # Ensure the logs directory was created if it didn't exist
        mock_makedirs.assert_called_once_with(expected_logs_dir)

        # Ensure the log file was opened and written to
        expected_log_path = os.path.join(expected_logs_dir, log_filename)
        mock_file.assert_called_once_with(expected_log_path, "a")
        mock_file().write.assert_called_once_with(content + "\n")

    @patch(
        "os.path.exists", return_value=False
    )  # Mock os.path.exists to simulate directory not existing
    @patch("os.makedirs")  # Mock os.makedirs to simulate folder creation
    @patch(
        "builtins.open", new_callable=mock_open
    )  # Mock open function to prevent actual file creation
    def test_write_to_log_creates_directory(
        self, mock_open, mock_makedirs, mock_exists
    ):
        # Simulate calling write_to_log with a different log file
        log_filename = "log_1609459200_salt5678.log"
        content = "Another log entry"

        # Call the function
        write_to_log(log_filename, content)

        # Ensure the logs directory is created only once
        mock_makedirs.assert_called_once_with(
            os.path.join(os.path.abspath(os.path.dirname(logging_module.__file__)), "logs")
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_write_to_log_empty_content(self, mock_open):
        write_to_log("empty_log.log", "")

        mock_open.assert_called_once()
        mock_open().write.assert_called_once_with("\n")  # Should write just a newline


    @patch(
        "builtins.open", new_callable=mock_open
    )  # Mock open function to prevent actual file creation
    def test_write_to_log_permission_error(self, mock_open):
        # Simulate a permission error when opening the log file
        mock_open.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            write_to_log("log_test.log", "Content that causes permission error")

    @patch(
        "builtins.open", new_callable=mock_open
    )  # Mock open function to prevent actual file creation
    def test_write_to_log_os_error(self, mock_open):
        # Simulate an OS error when opening the log file
        mock_open.side_effect = OSError("OS error occurred")

        with self.assertRaises(OSError):
            write_to_log("log_test.log", "Content that causes OS error")

    @patch(
        "builtins.open", new_callable=mock_open
    )  # Mock open function to prevent actual file creation
    def test_write_to_log_unexpected_error(self, mock_open):
        # Simulate an unexpected error when opening the log file
        mock_open.side_effect = Exception("Unexpected error")

        with self.assertRaises(Exception):
            write_to_log("log_test.log", "Content that causes unexpected error")


if __name__ == "__main__":
    unittest.main()
