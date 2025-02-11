import os
import random

# Directory to store generated files
output_dir = "generated_files"
os.makedirs(output_dir, exist_ok=True)

# Function to create a file with random content
def create_file(filename, size_mb=None, pe_header=False):
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "wb") as f:
        if pe_header:
            f.write(b"\x50\x45\x00\x00")
            f.write(os.urandom(64))
        if size_mb:
            remaining_size = size_mb * 1024 * 1024
            if pe_header:
                remaining_size -= 60
            f.write(os.urandom(remaining_size))  # Fill with random bytes
    
    print(f"Created: {filepath} ({'PE Header' if pe_header else ''} {f'{size_mb}MB' if size_mb else ''})")

# Generate two PE header files
create_file("Document_Important.exe",size_mb=15,pe_header=True)
create_file("fake_exe2.dll", pe_header=True)

# Generate three files over 10MB
create_file("large_file1.wsf", size_mb=11)
create_file("New_Video_Message.ade", size_mb=12)
create_file("large_file3.adp", size_mb=15)
create_file("Document_Important.exe", size_mb=15,pe_header=True)

# Generate a .bat file
create_file("script.bat")

# Generate a file with "Resume_JohnDoe" in the name
create_file("Resume_JohnDoe.pdf", size_mb=1)

print("File generation complete!")
