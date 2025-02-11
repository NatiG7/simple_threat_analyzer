import json
import os
import time

from file_handling import get_last_scanned_folder

# JSON File locations in script dir, in json folder
script_dir = os.path.abspath(os.path.dirname(__file__))
json_dir = os.path.join(script_dir, "json")

# Create a json dir if not found
if not os.path.exists(json_dir):
    os.makedirs(json_dir)

# Dynamic file locations
LAST_SCANNED_FILE = os.path.join(json_dir, "last_scanned_folder.json")
SAFE_FILES_FILE = os.path.join(json_dir, "safe_files.json")


def init_jsons() -> None:
    """
    Initializes the JSON files if they dont exist.
    """

    if not os.path.exists(LAST_SCANNED_FILE):
        with open(LAST_SCANNED_FILE, "w") as json_f:
            json.dump({"last_scanned_folder": ""}, json_f, indent=4)

    if not os.path.exists(SAFE_FILES_FILE):
        with open(SAFE_FILES_FILE, "w") as json_f:
            json.dump({"safe_files": []}, json_f, indent=4)


# call whenever this module is loaded, checking for availablity of json and sons
init_jsons()

def mark_file_as_safe() -> None:
    """
    Marks a file as safe if it exists in the last scanned folder.

    The function prompts the user for a file name and adds it to the list
    of safe files if found in the last scanned folder.
    """

    last_scanned_folder = get_last_scanned_folder()

    if not last_scanned_folder:
        print("\033[31mNo last scanned folder found. Scan a folder first.\033[0m")
        return

    # Get filename from user
    file_name = input("Enter the file name to mark as safe: ").strip()

    if not file_name:
        print("\033[33mNo file name provided.\033[0m")

    # Load safe files list and get file location in folder as a path
    safe_files = load_safe_files()
    file_path = os.path.join(last_scanned_folder, file_name)

    if os.path.exists(file_path):
        # add new entries.
        safe_files.add(file_path)
        save_safe_files(safe_files)
        print(f"\033[32mFile '{file_name}' has been marked as safe.\033[0m")
    else:
        print(
            f"\033[31mFile '{file_name}' was not found in the last scanned folder.\033[0m"
        )


def load_safe_files() -> set:
    """
    Loads the list of safe files from a JSON file.

    Returns:
        set: A set of file paths marked as safe.
    """

    # Return empty set if no file found
    if not os.path.exists(SAFE_FILES_FILE):
        return set()

    try:
        # Read from file, gets the dict from key 'safe_files'
        with open(SAFE_FILES_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("safe_files", []))

    except json.JSONDecodeError:
        print(f"Error reading from JSON")
        return set()

    except FileNotFoundError:
        print(f"Error, {SAFE_FILES_FILE} not found")
        return set()

    except Exception as e:
        print(f"Error loading safe files: {e}")
        return set()


def save_safe_files(safe_files: set) -> None:
    """
    Saves the set of safe files to a JSON file.

    Args:
        safe_files (set): A set of file paths marked as safe.
    """

    try:
        with open(SAFE_FILES_FILE, "w") as f:
            json.dump({"safe_files": list(safe_files)}, f, indent=4)

    except Exception as e:
        print(f"Error saving safe files: {e}")


def should_ignore_file(file_name: str, folder_path: str) -> bool:
    """
    Checks if a file should be ignored in the scan based on the 'safe' list.

    Args:
        file_name (str): Name of the file.
        folder_path (str): Path of the folder containing the file.

    Returns:
        bool: True if the file should be ignored, False otherwise.
    """



    safe_files = load_safe_files()
    file_path = os.path.join(folder_path)
    return file_path in safe_files
