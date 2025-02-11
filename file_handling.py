import json
import os

# Dynamic json file location
script_dir = os.path.abspath(os.path.dirname(__file__))
json_dir = os.path.join(script_dir, "json")

LAST_SCANNED_FILE = os.path.join(json_dir, "last_scanned_folder.json")


def find_abs_path(folder_to_scan: str) -> dict:
    """
    Check if the given path is an absolute path and if it exists.

    Args:
        folder_to_scan (str): The folder to check.

    Returns:
        dict: A dictionary with information about the folder path.

    """
    # Validation
    if not folder_to_scan.strip():
        return {
            "path": None,
            "type": None,
            "exists": False,
            "error": "Empty path provided.",
        }

    result = {"path": None, "type": None, "exists": False, "error": None}
    folder_to_scan = os.path.expanduser(folder_to_scan)

    # If absolute path is valid
    if os.path.isabs(folder_to_scan):
        if os.path.isdir(folder_to_scan):
            result.update({"path": folder_to_scan, "type": "absolute", "exists": True})

        else:
            result["error"] = f"Absolute path [{folder_to_scan}] doesnt exist."
            return result

    else:
        return result

    return result


def find_rel_path(folder_to_scan: str, script_dir: str) -> dict:
    """
    Check if the given path is a relative path and if it exists.

    Args:
        folder_to_scan (str): The folder to check.
        script_dir (str): The script's directory to resolve relative paths.

    Returns:
        dict: A dictionary with information about the folder path.

    Raises:
        FileNotFoundError: If the relative path does not exist.
        ValueError: If the folder is outside the script directory.
    """
    # Validation
    if not folder_to_scan.strip():
        return {
            "path": None,
            "type": None,
            "exists": False,
            "error": "Empty path provided.",
        }

    script_dir = os.path.abspath(os.path.expanduser(script_dir))

    if not os.path.exists(script_dir):
        return {
            "path": None,
            "type": None,
            "exists": False,
            "error": f"Base script dir {script_dir} does not exist.",
        }

    folder_to_scan = os.path.expanduser(folder_to_scan)
    abs_path = os.path.abspath(os.path.join(script_dir, folder_to_scan))

    # If outside relative path
    if not os.path.commonpath([abs_path, script_dir]) == script_dir:
        return {
            "path": None,
            "type": None,
            "exists": False,
            "error": f"Folder '{folder_to_scan}' is outside '{script_dir}'.",
        }

    # If relative path is valid
    if os.path.isdir(abs_path):
        rel_path = os.path.relpath(abs_path, script_dir)
        return {"path": rel_path, "type": "relative", "exists": True, "error": None}

    # No match for rel paths
    return {
        "path": None,
        "type": None,
        "exists": False,
        "error": f"Relative path '{folder_to_scan}' does not exist.",
    }


def search_system(folder_to_scan: str) -> dict:
    """
    Search the entire system for the folder name.

    Args:
        folder_to_scan (str): The folder to search for.

    Returns:
        dict: A dictionary with the search result, including the folder's path if found.

    Raises:
        FileNotFoundError: If the folder cannot be found in the system.
        PermissionError: If access to some directories is denied.
    """
    result = {"path": None, "type": None, "exists": False, "error": None}
    search_paths = ["/home/nati/Desktop", "/"]

    print(f"\033[33mScanning for {folder_to_scan}\033[0m")
    try:
        for base_path in search_paths:
            # Priority search in Desktop, and then ROOT
            print(f"\033[33mScanning base path:\033[0m {base_path}")
            for root, dirs, _ in os.walk(base_path, followlinks=True):
                # Add to result dict if found
                if folder_to_scan in dirs:
                    result["path"] = os.path.join(root, folder_to_scan)
                    result["exists"] = True
                    result["type"] = "sys_search"
                    print(f"\033[33mFound folder at:\033[0m {result['path']}")
                    return result

    except KeyboardInterrupt:
        result["error"] = "Search interrupted by user."
        return result

    except PermissionError:
        result["error"] = (
            f"Permission denied while searching for \n\t[{folder_to_scan}]"
        )
        raise PermissionError(result["error"])

    except OSError as e:
        result["error"] = f"OS Error while searching for\nt\t[{folder_to_scan}]:\n{e}"
        raise OSError(result["error"])

    raise FileNotFoundError(f"Folder '{folder_to_scan}' not found in system search.")


def extract_file_data(folder_path: str) -> list:
    """
    Extracts file data (name, extension, size) from the specified folder path.

    Args:
        folder_path (str): The path of the folder to scan for files.

    Returns:
        list: A list of dictionaries containing file information:
            - "name" (str): The file name without extension.
            - "extension" (str): The file extension.
            - "size(B)" (int): The size of the file in bytes.
    """
    files_data = []
    try:
        # Iterate each file in dir, and extract information
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            if os.path.isfile(file_path):
                file_name, file_ext = os.path.splitext(file)
                file_size = os.path.getsize(file_path)
                files_data.append(
                    # Construct info object
                    {
                        "name": file_name,
                        "extension": file_ext,
                        "size(B)": file_size,
                        "folder_path": folder_path,
                    }
                )

    except PermissionError:
        raise PermissionError(f"Permission denied while accessing {folder_path}.")

    except OSError as e:
        raise OSError(f"OS error while reading folder {folder_path}: {e}")

    return files_data


def scan_files(folder: str) -> dict:
    """
    Scan for a folder based on user input.

    Checks if the input is:
    - An absolute path (if the folder exists).
    - A relative path within the current directory.
    - A folder name in the current directory.

    Returns:
        dict: A dictionary containing:
            - "path" (str | None): The resolved path of the folder.
            - "type" (str | None): The type ("absolute", "relative", "folder_name").
            - "exists" (bool): True if the folder exists, otherwise False.
            - "error" (str | None): Error message if an exception occurs.

    Raises:
        FileNotFoundError: If the folder does not exist.
    Throws:
        PermissionError: If access to the folder is denied.
        OSError: For other OS-related errors.
        Exception: For any unexpected errors.
    """
    # storage dict for result
    result = {"path": None, "type": None, "exists": False, "error": None}

    # Sanitize input
    folder_to_scan = os.path.expanduser(folder)  # expand if needed
    try:
        # If absolute path detected
        result = find_abs_path(folder_to_scan)
        if result["exists"]:
            save_last_scanned_folder(result["path"])
            return result

        # If relative path detected
        script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        result = find_rel_path(folder_to_scan, script_dir)

        if result["exists"]:
            save_last_scanned_folder(os.path.abspath(result["path"]))
            print(f"Saved result: {result['path']}\nPath:{result['path']}")
            return result

        # If search needed
        result = search_system(folder_to_scan)

        if result["exists"]:
            save_last_scanned_folder(result["path"])
            return result

        # Default (input mirroring)
        result["exists"] = False
        result["path"] = folder_to_scan

        # File data in found folder
        try:
            # Scan files and get data
            folder_path = result["path"]
            files_data = extract_file_data(folder_path)
            result["files"] = files_data

        except PermissionError:
            result["error"] = f"Permission denied while accessing {folder_path}."

        except OSError as e:
            result["error"] = f"OS error while reading folder {folder_path}"

    except PermissionError as e:
        result["error"] = str(e)
    except FileNotFoundError as e:
        result["error"] = str(e)
    except OSError as e:
        result["error"] = f"OS error: {e}"
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"

    return result


def save_last_scanned_folder(folder_path: str) -> None:
    """
    Saves the last scanned folder path to a JSON file.

    Args:
        folder_path (str): The folder path to save.

    Raises:
        IOError: If the file cannot be written.
    """

    try:
        # Save new last scanned folder each time
        data = {"last_scanned_folder": folder_path}
        with open(LAST_SCANNED_FILE, "w") as f:
            json.dump(data, f)

    except IOError as e:
        raise IOError(f"Error saving the last scanned folder: {str(e)}")


def get_last_scanned_folder() -> str:
    """
    Retrieves the last scanned folder from the saved JSON file.

    Returns:
        str: The last scanned folder path, or None if not found.

    Raises:
        json.JSONDecodeError: If the JSON file is corrupted or unreadable.
        IOError: If there's an error reading the file.
    """
    if not os.path.exists(LAST_SCANNED_FILE):
        # Create new if doesnt exist
        with open(LAST_SCANNED_FILE, "w") as f:
            json.dump({"last_scanned_folder": ""}, f)
            return ""

    try:
        # read from file
        with open(LAST_SCANNED_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_scanned_folder", "")

    except FileNotFoundError:
        raise FileNotFoundError("Last scanned folder file not found.")

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Error reading last scan data: {str(e)}", doc="json", pos=0
        )

    except IOError as e:
        raise IOError(f"Error reading last scanned folder: {str(e)}")
