# Py-File-Mover
A Python script that moves files given a list or a folder containing them

This Python 3.x CLI script was made to move/copy files, given either a list of their paths or a folder path containing them.

## Parameters

```
usage: file_mover.py [-h] [-V] [-C] {move,copy} {files,folder} ...

positional arguments:
  {move,copy}           The operation to do on the files (move or copy;
                        mandatory)

options:
  -h, --help            show this help message and exit
  -V, --overwrite       Allow overwritting existing files
  -C, --create-out-dir  Create output directory and subdirectories if they
                        don't exist

Input mode:
  The following are valid input modes:

  {files,folder}
    files               Move/copy a list of files
    folder              Move/copy files from a specified folder

--------------------------------------------------------------------------

usage: file_mover.py {move,copy} files [-h] file_list

positional arguments:
  file_list   The list of files to be processed (mandatory)

options:
  -h, --help  show this help message and exit

--------------------------------------------------------------------------

usage: file_mover.py {move,copy} folder [-h] [-R] [-w WILDCARD]
                                        in_folder out_folder

positional arguments:
  in_folder             The folder where the to-be processed files are
                        (mandatory)
  out_folder            The folder where the processed files will be
                        (mandatory)

options:
  -h, --help            show this help message and exit
  -R, --recursive       Process files recursively
  -w WILDCARD, --wildcard WILDCARD
                        A wildcard specifying which files to process (default:
                        ALL)
```

## How to use

1. Download the contents of the repository to an empty folder of your choice.
2. Run the following commands:

   ```
   $ python -m venv env
   $ source env/bin/activate   # If you're on Linux, or
   > .\env\Scripts\activate    # If you're on Windows
   $ python -m pip install -r requirements.txt
   ```

   This will install PyInstaller, to be able to generate a binary executable.
3. (Optional) Run the following command to create a binary executable:

   ```
   $ pyinstaller -F file_mover.py
   ```

   The result will be in the `dist` directory.
