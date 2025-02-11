import os
import random
import string
import time


def generate_salt(length: int = 64) -> str:
    """
    Generates a random salt of a given length.

    Args:
        length (int): the length of the salt in bytes.

    Returns:
        string containing a salt with given length
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_log_filename() -> str:
    """
    Generates a unique log filename based on Unix timestamp and random salt.

    Returns:
        string containg formatted log file name log_(unix_timestamp)_(generated_salt)
    """
    timestamp = int(time.time())
    salt = generate_salt()
    log_filename = f"log_{timestamp}_{salt}.log"
    return log_filename


def write_to_log(log_filename: str, content: str) -> None:
    """
    Writes the threat assessment content to the log file.

    Args:
        log_filename(str): the log name to write to or create
        content(str): log details containing threat data

    Raises:
        FileNotFoundError: If the log file cannot be found or created.
        PermissionError: If access to the log file is denied.
        OSError: If an OS-related error occurs (e.g., disk issues, path errors).
        Exception: For any other unexpected errors.
    """
    try:
        script_dir = os.path.abspath(os.path.dirname(__file__))
        logs_dir = os.path.join(script_dir,"logs")
        
        # Create logs folder if not found
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        log_path = os.path.join(logs_dir, log_filename)

        # Create log file in dir
        with open(log_path, "a") as log_file:
            log_file.write(content + "\n")
        print(f"Log written succesfully to logs directory.")

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Could not find or create file:\n\t{log_path}")

    except PermissionError:
        raise PermissionError(
            f"Error: Access denied:\n\t{log_path}.Check file permissions."
        )

    except OSError as e:
        raise OSError(f"OS Error: {e}")

    except Exception as e:
        raise Exception(f"Unexpected error writing to log file {log_filename}: {e}")
