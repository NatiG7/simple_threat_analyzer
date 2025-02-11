import os
import stat
import sys
import time

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


def print_dir_summary(folder: str) -> None:
    """
    Prints a summary of the contents of a directory.

    Args:
        folder (str): The directory to summarize.

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If access to the directory is denied.
    """

    if not os.path.isabs(folder):
        folder = os.path.join(os.getcwd(), folder)

    try:
        if not os.path.isdir(folder):
            print(f"{RED}Error:{RESET} [{folder}] is not a valid dir.")
            return

        # List directories and files only in the top-level folder
        entries = os.listdir(folder)
        subdirs = [
            entry for entry in entries if os.path.isdir(os.path.join(folder, entry))
        ]
        files = [
            entry for entry in entries if os.path.isfile(os.path.join(folder, entry))
        ]

        # Display directories
        print(f"{GREEN}Subdirectories:{RESET}")
        for subdir in subdirs:
            dir_stat = os.stat(os.path.join(folder, subdir))
            dir_perms = stat.filemode(dir_stat.st_mode)
            print(f"\t{CYAN}|{dir_perms}|{RESET} {WHITE}{subdir}{RESET}")

        # Display files with details
        print(f"{YELLOW}\nFiles:{RESET}")
        for file in files:
            file_path = os.path.join(folder, file)
            file_stat = os.stat(file_path)
            file_perms = stat.filemode(file_stat.st_mode)
            file_size = os.path.getsize(file_path)  # Size in bytes
            mod_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path))
            )
            print(
                f"\t{CYAN}|{file_perms}|{RESET}{WHITE}{file}{RESET}{MAGENTA}|{file_size} bytes|{RESET}{YELLOW}Last Modified: {mod_time}{RESET}"
            )

    except FileNotFoundError as e:
        print(f"{RED}Error: {e}{RESET}")

    except PermissionError as e:
        print(f"{RED}Permission denied: {e}{RESET}")

    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")


def print_after_scan(scan_result: dict) -> None:
    """
    Prints scan results and directory summary.

    Args:
        scan_result (dict): Dictionary containing scan details.

    Raises:
        KeyError: If required keys are missing from scan_result.
    """

    try:
        # Dont print if no valid dir
        if scan_result is None or scan_result.get("path") is None:
            print(f"{RED}No valid directory found.{RESET}")
            return

        # Print summary and details about files etc.
        print(f"\n{GREEN}Scan completed with the following results:{RESET}")
        print(f"{BLUE}Path:{RESET} {WHITE}{scan_result.get('path')}{RESET}")
        print(f"{BLUE}Exists:{RESET} {WHITE}{scan_result.get('exists')}{RESET}")
        print(f"{BLUE}Type:{RESET} {WHITE}{scan_result.get('type')}{RESET}")
        print(
            f"{RED}Error: {RESET}{WHITE}{scan_result.get('error') if scan_result.get('error') else 'No error'}{RESET}"
        )
        print(f"{YELLOW}Printing directory summary:{RESET}")
        print_dir_summary(scan_result["path"])

    except KeyError as e:
        print(f"{RED}Missing key in scan result: {e}{RESET}")

    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")

def bye_bye() -> None:
    """
    Prints a goodbye message and exits the program.

    This function is used to print a farewell message and then terminate 
    the program using sys.exit(). It does not return any value.
    """
    print("Goodbye")
    sys.exit()