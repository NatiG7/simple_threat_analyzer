import os
from typing import Set

script_dir = os.path.abspath(os.path.dirname(__file__))
logs_dir = os.path.join(script_dir, "logs")

# Color Codes
RESET = "\033[0m"  # Reset to default color
RED = "\033[31m"  # Errors, warnings
GREEN = "\033[32m"  # Success messages
YELLOW = "\033[33m"  # Warnings, caution
BLUE = "\033[34m"  # Directories
MAGENTA = "\033[35m"  # Special notifications
CYAN = "\033[36m"  # Information messages
WHITE = "\033[37m"  # Default light text
GRAY = "\033[90m"  # Less important details
WHITESPACE_STR = " "
DOT_STR = "."
RISK_STR = "Risk"
SIZE_STR = "Size:"
FILE_STR = "File:"


def format_extensions(extensions: Set[str], max_per_line=4):
    """
    Format a set of file extensions into lines with a maximum number of extensions per line.

    Args:
        extensions (Set[str]): A set of file extensions.
        max_per_line (int): The maximum number of extensions per line. Default is 4.

    Returns:
        str: A string with the formatted extensions, with each line containing
                a maximum of `max_per_line` extensions.
    Raises:
        ValueError: if "extensions" is not a set of strings
                    or "max_per_line" is not a valid pos integer
    """
    # Validation
    if not isinstance(extensions, set):
        raise ValueError("The 'extensions' argument must be a set.")

    if not all(isinstance(ext, str) for ext in extensions):
        raise ValueError("All elements in 'extensions' must be strings.")

    if not isinstance(max_per_line, int) or max_per_line <= 0:
        raise ValueError("'max_per_line' must be a positive integer.")

    extension_lines = []
    extensions_list = list(extensions)

    # Iterate over list and format with 'max_per_line' on each line
    for i in range(0, len(extensions_list), max_per_line):
        extension_lines.append(", ".join(extensions_list[i : i + max_per_line]))
    return "\n\t\t".join(extension_lines)


def last_scan_statistics() -> None:
    """
    Displays statistics from the most recent scan log.

    The function retrieves the latest log file, extracts relevant data such as file count,
    extensions, largest/smallest file sizes, and suspicious files, and prints the summary.

    Handles:
    - Invalid file size in log
    - Missing log directory
    - File not found errors
    - Permission issues
    - General OS errors

    Returns:
        None
    """
    script_dir = os.path.abspath(os.path.dirname(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    empty_dir_msg = "Directory empty."
    empty_log_msg = "No last scan found."

    # if no directory found or no logs
    if not logs_dir:
        return empty_dir_msg

    # get last scan and print summary
    last_scan_log = get_latest_log_filename(logs_dir)
    # Verify last scan exists
    if not last_scan_log:
        return empty_log_msg

    print(
        f"""
        Script-dir:{script_dir}
        Logs-dir:{logs_dir}
        Last-log:{last_scan_log}
        """
    )

    try:
        default_title = "Summary"
        log_file_path = os.path.join(logs_dir, last_scan_log)

        with open(log_file_path, "r") as log_f:
            # read file and extract title, folder name and file details
            log_contents = log_f.read().splitlines()
            log_title = log_contents[0] if log_contents else default_title
            print(log_title)
            folder_name = log_contents[0].split(" ")[-1] if log_contents else "Unknown"

            # statistic vars
            file_count = 0
            sus_file_count = 0
            extensions_in_file = set()
            largest_file_size = -1
            largest_file_name = ""
            smallest_file_size = float("inf")
            smalles_file_name = ""
            current_filename = ""
            unsuspicious_RISK = "Low"

            # Each line in th log
            for line in log_contents:

                # for file name
                if line.startswith(FILE_STR):
                    file_count += 1
                    parts_of_nameline = line.split(WHITESPACE_STR)
                    if len(parts_of_nameline) > 1:
                        # means this file has a name, from scan format
                        current_filename = parts_of_nameline[1].strip()
                        if DOT_STR in current_filename:
                            # extract extension
                            extensions_in_file.add(
                                current_filename.split(DOT_STR)[-1].strip()
                            )

                # for size lines
                elif line.startswith(SIZE_STR):
                    parts_of_sizeline = line.split(WHITESPACE_STR)
                    if len(parts_of_sizeline) > 1:
                        # means this file has a size, from scan format
                        try:
                            file_size = int(line.split(WHITESPACE_STR)[1].strip())
                            if file_size > largest_file_size:
                                largest_file_size = file_size
                                largest_file_name = current_filename

                            elif file_size < smallest_file_size:
                                smallest_file_size = file_size
                                smalles_file_name = current_filename

                        except ValueError:
                            print(
                                f"{YELLOW}Warning:{RESET} Invalid file size in line: {line}"
                            )
                    else:
                        print(
                            f"{YELLOW}Warning:{RESET} Missing size value in line: {line}"
                        )

                # for risk lines
                elif line.startswith(RISK_STR):
                    parts_of_riskline = line.split(WHITESPACE_STR)

                    if len(parts_of_riskline) > 3:
                        # means this file has risk level, from scan format
                        RISK_level = parts_of_riskline[3].strip()
                        if RISK_level != unsuspicious_RISK:
                            sus_file_count += 1

                    else:
                        print(f"{YELLOW}Warning:{RESET} Malformed risk line: {line}")

        # Extension in last scan in a formatted manner
        formatted_extensions = format_extensions(extensions_in_file)
        print(
            f"""
    Last scan statistics :

            {BLUE}Folder:{RESET} {folder_name}
            {GREEN}Files in folder:{RESET} {file_count}
            {CYAN}Extensions:{RESET} \n\t\t{formatted_extensions}\n
            {CYAN}Largest file:{RESET} {largest_file_name} at {largest_file_size} bytes
            {CYAN}Smallest file:{RESET} {smalles_file_name} at {smallest_file_size} bytes
            {YELLOW}Suspicious files:{RESET} {sus_file_count}
            """
        )

    except FileNotFoundError:
        print("Error: File not found.")
    except PermissionError:
        print("Please check permissions.")
    except OSError:
        print("Invalid path.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def get_latest_log_filename(log_dir: str) -> str:
    """
    Finds the latest log file in the specified directory based on the Unix timestamp in the filename.

    Args:
        log_dir (str): Directory where log files are stored.

    Returns:
        str: The filename of the latest log file.
    """
    latest_timestamp = 0
    latest_log_filename = None

    # Iterate over all files in the directory
    for filename in os.listdir(log_dir):
        if filename.startswith("log_") and filename.endswith(".log"):
            # Extract the timestamp part of the filename
            parts = filename.split("_")

            if len(parts) >= 2:
                timestamp = int(parts[1])

                # Check if this timestamp is the latest
                if timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_log_filename = filename

    return latest_log_filename
