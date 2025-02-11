import os
from typing import Dict, List, Tuple, Union

import logging_module as Logger
from file_handling import extract_file_data, scan_files
from json_module import should_ignore_file


def get_threats() -> Tuple[List[str], List[str]]:
    """
    Reads the suspicious file names and types from the respective text files.

    This function attempts to open and read two files that contain lists of
    suspicious file names and file extensions. It returns these lists if
    successfully read, otherwise, it raises an appropriate error.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
                                        - suspicious file names
                                        - suspicious file extensions

    Raises:
        FileNotFoundError: If one or both of the required files are not found.
        PermissionError: If there is a permission issue accessing the files.
        IsADirectoryError: If the path points to a directory instead of a file.
        IOError: For any I/O related errors during file reading.
        Exception: For any unexpected errors.
    """
    # Files in the wordlist folder
    project_dir = os.path.dirname(os.path.abspath(__file__))
    suspicious_names_file = os.path.join(
        project_dir, "wordlists", "suspicious_file_names.txt"
    )
    suspicious_extensions_file = os.path.join(
        project_dir, "wordlists", "suspicious_file_types.txt"
    )

    try:
        # Read from files and split each line into list elem
        with open(suspicious_names_file, "r") as name_f:
            threat_names = name_f.read().splitlines()

        with open(suspicious_extensions_file, "r") as ext_f:
            threat_ext = ext_f.read().splitlines()

        return threat_names, threat_ext

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: One or more files were not found.")

    except PermissionError:
        raise PermissionError(f"Permission denied when trying to read the files.")

    except IsADirectoryError:
        raise IsADirectoryError(f"Error: Expected a file, but found a directory.")

    except IOError:
        raise IOError(f"Error: Input/Output error occurred.")

    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def check_suspicious_files() -> None:
    """
    Prompts the user for a folder path
        -scans the folder for files
        -assesses threats for each file.

    Generates log data for each file checked with statistics.
    """
    folder_to_scan: str = input("Enter folder name or path: ").strip()
    scan_result = scan_files(folder_to_scan)

    if not scan_result or not scan_result.get("path"):
        print(f"Error: Invalid scan result for '{folder_to_scan}'")
        return

    scan_path = os.path.abspath(scan_result["path"])
    if not os.path.exists(scan_path):
        print(f"Error: Folder '{scan_path}' does not exist.")
        return  # Stop execution if folder is invalid

    try:
        files_in_scan = extract_file_data(scan_result["path"])

        if not files_in_scan:
            print(f"No files found in '{scan_path}'.")
            return

        assess_threats(files_in_scan)

    except FileNotFoundError as e:
        print(f"Error: The file or directory was not found: {e}")
    except ValueError as e:
        print(f"Error extracting file data: {e}")
    except Exception as e:
        print(f"Unexpected error processing files: {e}")


def assess_threats(files: List[Dict[str, Union[str, int]]]) -> None:
    """
    Assesses threats based on file names, extensions, and sizes.

    Args:
        files (List[Dict[str, Union[str, int]]]): List of dictionaries containing file information
            such as name, extension, size, and folder path.
    """

    log_storage = []
    for file_info in files:
        try:
            # File details.
            file_name = file_info["name"]
            file_ext = file_info["extension"]
            file_size = file_info["size(B)"]
            file_path = os.path.join(file_info["folder_path"], f"{file_name}{file_ext}")
            file_risk = 0
            threat_names, threat_ext = get_threats()

            # Skip on marked safe files
            if should_ignore_file(file_name, file_path):
                print(
                    f"\033[33mSkipping '{file_name}' as it is marked as \033[32msafe.\033[0m"
                )
                continue

            # Risk assessment
            if file_name in threat_names:
                file_risk += 1
            if file_ext[1::] in threat_ext:
                file_risk += 1
            if file_size > 10485760:
                file_risk += 1
            if verify_pe_header(file_path):
                file_risk += 1

            # Risk level
            risk_levels = {0: "Low", 1: "Medium", 2: "High", 3: "Severe", 4: "Critical"}
            if file_risk in risk_levels:
                risk_level = risk_levels[file_risk]

            log_content = (
                f"File: {file_name}{file_ext}\n"
                f"Path: {file_path}\n"
                f"Size: {file_size} bytes\n"
                f"Risk level : {risk_level}\n"
            )

            # PE Header logging
            if verify_pe_header(file_path):
                log_content += f"File is a portable executable.\n"

            # Add each file's check to logs.
            log_storage.append(log_content)

        except (FileNotFoundError, PermissionError) as e:
            print(f"Error proccessing file {file_info['name']}: {e}")

        except Exception as e:
            print(f"Error processing file {file_info}: {e}")

    if log_storage:
        # Write log file.
        folder_name = os.path.basename(file_info["folder_path"])
        log_filename = Logger.generate_log_filename()
        full_log = f"Log Summary for {folder_name}\n" + "\n\n".join(log_storage)
        Logger.write_to_log(log_filename, full_log)
        print(f"\033[92mScan logged succesfully.\033[0m")

    else:
        print(f"Erorr occurred while saving log.")


def verify_pe_header(file_path: str) -> bool:
    """
    Verifies if the file has a valid PE header.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file has a valid PE header, False otherwise.
    """
    try:
        # Read first 4 bytes and check if PE.
        with open(file_path, "rb") as file:
            header = file.read(4)

            return header == b"\x50\x45\x00\x00"

    except (FileNotFoundError, IOError) as e:
        print(f"Error verifying PE header for {file_path}: {e}")
        return False
