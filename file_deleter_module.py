import os

from statistics_module import get_latest_log_filename
from utility_module import bye_bye

# script dir and logs folder
script_dir = os.path.abspath(os.path.dirname(__file__))
logs_dir = os.path.join(script_dir, "logs")


def get_last_sus_files() -> list[tuple[str, str]]:
    """
    Reads the latest scan log from the specified directory and extracts the suspicious files
    (files with a risk level other than "Low").

    The function scans the log, ignoring the first line which contains a summary,
    and processes each entry in chunks of 6 lines (file name, file path, and risk level).
    If the risk level is not "Low", the file name and path are added to the list of suspicious files.

    Returns:
        list[tuple[str, str]]: A list of tuples containing the file name and file path of suspicious files.
    """

    # Get last scan details
    last_scan = get_latest_log_filename(logs_dir)
    last_scan_file = os.path.join(logs_dir, last_scan)

    # Store sus files in list
    suspicious_files = []
    # Read scan log
    try:
        with open(last_scan_file, "r") as log:
            log_data = log.read().splitlines()
            entry_lines_total = 6
            entry_data_start_line = 1
            # Log entries have 4 lines and 2 blank lines after every entry
            for i in range(entry_data_start_line, len(log_data), entry_lines_total):
                file_name = log_data[i].replace("File: ", "").strip()
                file_path = log_data[i + 1].replace("Path: ", "").strip()
                risk_level = log_data[i + 3].replace("Risk level : ", "").strip()

                # Add files with risk level other than low
                if risk_level != "Low":
                    suspicious_files.append((file_name, file_path))

    except FileNotFoundError:
        print("Error: File not found.")
    except PermissionError:
        print("Please check permissions.")
    except OSError:
        print("Invalid path.")
    except Exception as e:
        print(f"Error occured : {e}")

    return suspicious_files


def print_last_and_confirm(files_data: list[tuple[str, str]]) -> None:
    """
    Displays a list of files and prompts the user for confirmation before deleting them.

    Args:
        files_data (List[Tuple[str, str]]): A list of tuples, each containing a filename and its corresponding file path.

    Returns:
        None
    """
    print("List of files:")
    valid_files = [
        (filename, filepath) for filename, filepath in files_data if filename.strip()
    ]

    for filename, path in valid_files:
        print(f"\t{filename}")

    print("The following files will be deleted.")
    user_choice = input("Yes / No :\t").strip().lower()

    if user_choice == "yes":
        for filename, path in files_data:
            try:
                print(f"Deleting {filename}")
                os.remove(path)

            except FileNotFoundError:
                print(f"Error: {filename} not found.")
            except PermissionError:
                print(f"Permission denied: {filename}")
            except OSError as e:
                print(f"Error deleting {filename}: {e}")

    elif user_choice == "no":
        bye_bye()

    else:
        print("Invalid option. enter yes or no.")
        print_last_and_confirm(files_data)


def delete_from_last_scan() -> None:
    """
    Prompts the user to choose a method of deletion for suspicious files from the last scan.

    The user can select one of three options:
    A) Delete all files from the last scan, with a confirmation prompt before deletion.
    B) Choose a specific file to delete (currently not implemented).
    C) Cancel and exit the operation.

    If an invalid option is selected, the user will be prompted again.

    Returns:
        None
    """

    print(
        """
        Select method of deletion :
        A) Deletes all files from last scan
        B) Select which file to delete
        C) Cancel and exit.
        """
    )
    try:

        user_selection = input("Option:").strip().capitalize()

        # Delete all files, prompt for confirmation
        if user_selection == "A":
            last_suspicious_files = get_last_sus_files()
            # print files names to delete and ask to confirm
            print_last_and_confirm(last_suspicious_files)

        elif user_selection == "B":
            print("Chose Violence")

        elif user_selection == "C":
            bye_bye()

        else:
            print("Invalid selection.\n\tTry ( A | B | C )")
            delete_from_last_scan()

    except Exception as e:
        print(f"Unexpected error: {e}")


def delete_specific_file():
    print("Asks for a specific file to delete- ~~~ TODO? ~~~")


def delete_suspicious_files() -> None:
    """
    Prompts the user to select an option for deleting suspicious files.

    The function provides three options:
    1. Delete files from the last scan
    2. Delete a specific file by path
    0. Cancel and exit the operation.

    If the user selects an invalid option or provides an invalid input,
    an error message is displayed, and the user is prompted to select again.

    Returns:
        None
    """

    print(
        """
        Suspicious file deletion.
        \tPlease select an option
        1) Delete from last scan
        2) Delete specific file from path
        0) Cancel and exit.
        """
    )
    try:
        user_selection = int(input("Option:"))

        options = {1: delete_from_last_scan, 2: delete_specific_file, 0: bye_bye}

        options.get(user_selection)()

    except ValueError:
        print("Please enter a valid number.")
