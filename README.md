# Virus & Spyware Detection Software

This is a Python-based command-line tool designed to detect and manage suspicious files in a specified directory. The software provides various functionalities such as scanning files, checking suspicious files, marking files as safe, viewing scan statistics, and deleting suspicious files.

## Features

1. **Scan Files in Directory**: Scans a specified folder for potential threats.
2. **Check Suspicious Files**: Lists files marked as suspicious.
3. **Mark Safe Files**: Allows users to mark files as safe, removing them from the suspicious list.
4. **Last Scan Statistics**: Displays statistics from the most recent scan.
5. **Delete Suspicious Files**: Permanently deletes files marked as suspicious.
6. **Exit**: Exits the program.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/NatiG7/simple_threat_analyzer.git
   ```

2. Navigate to the project directory:

   ```bash
   cd simple_threat_analyzer
   ```

3. Install the required dependencies (if any):

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the program by executing `main.py` file:

```bash
python main.py
```

## Options

Upon running the program, you will be presented with the following options:

1. **Scan files in directory**: Enter the folder name or path to scan for suspicious files.
2. **Check suspicious files**: View a list of files marked as suspicious.
3. **Mark safe files**: Mark a file as safe to remove it from the suspicious list.
4. **Last scan statistics**: View statistics from the most recent scan.
5. **Delete suspicious files**: Permanently delete files marked as suspicious.
6. **EXIT**: Exit the program.

## Example

```plaintext
Option: 1
Enter folder name or path: .
Saved result: .
Path: .

Scan completed with the following results:
Path: .
Exists: True
Type: relative
Error: No error

Printing directory summary:
Subdirectories:
|drwxrwxr-x| wordlists
|drwxrwxr-x| Task Requirements
|drwxrwxr-x| generated_files
...
...
...

Files:
|-rw-rw-r--| file_handling.py | 10480 bytes | Last Modified: 2025-02-10 18:58:59
|-rw-rw-r--| logging_module.py | 2215 bytes | Last Modified: 2025-02-06 18:18:34
|-rw-rw-r--| json_module.py | 3745 bytes | Last Modified: 2025-02-10 19:37:38
...
...
...
```

## Modules

- **file_deleter_module**: Handles the deletion of suspicious files.
- **file_handling**: Manages file scanning and directory operations.
- **json_module**: Handles marking files as safe and managing JSON data.
- **statistics_module**: Provides statistics from the last scan.
- **threat_handling**: Manages suspicious file detection and handling.
- **utility_module**: Contains utility functions like printing scan results and exiting the program.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Shoutout

Thanks to [Ano-Ku](https://www.github.com/Ano-Ku) for this project. **He made me do it.**


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
