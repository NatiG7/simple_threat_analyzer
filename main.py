import file_deleter_module as fileDeleter
import file_handling as fileHandler
import json_module as jsonHandler
import statistics_module as Statisticals
import threat_handling as threatHandler
from utility_module import bye_bye, print_after_scan


def selected_scan_files() -> None:
    """
    Selected option 1, takes input from user
    builds a result dictionary from scan
    and prints scan summary.

    Raises:
        KeyboardInterrupt: When user cancels
    """
    try:
        folder_to_scan: str = input("Enter folder name or path: ").strip()
        result = fileHandler.scan_files(folder_to_scan)
        print_after_scan(result)

    except KeyboardInterrupt:
        raise KeyboardInterrupt(f"Interrupted by user.")

    except Exception as e:
        print(f"Error occured while running scan and printing :\n\t{e}")


def main() -> None:
    """
    Main code block, displays options for different actions
    and also takes user input.
    """
    print("~~~ Welcome to Virus & Spyware Detection Software ~~~")
    print(
        """
    Please select an option:\n
    1) Scan files in directory
    2) Check suspicious files
    3) Mark safe files
    4) Last scan statistics
    5) Delete suspicious files
    6) EXIT
    """
    )

    try:
        user_selection = int(input("Option: "))

        options = {
            1: selected_scan_files,
            2: threatHandler.check_suspicious_files,
            3: jsonHandler.mark_file_as_safe,
            4: Statisticals.last_scan_statistics,
            5: fileDeleter.delete_suspicious_files,
            6: bye_bye,
        }

        # Call the function from user option if valid
        options.get(user_selection)()

    except ValueError:
        print("Please enter a valid number.")


if __name__ == "__main__":
    main()
