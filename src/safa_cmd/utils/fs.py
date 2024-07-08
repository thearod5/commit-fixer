from typing import List


def write_file_content(file_path: str, file_content: str) -> None:
    """
    Writes content to file.
    :param file_path: Path to file.
    :param file_content: Content to write.
    :return: None
    """
    with open(file_path, "w") as f:
        f.write(file_content)


import os


def list_python_files(directory_paths: str | List[str]):
    """
    Returns a list of Python file paths contained within the given directory.

    Parameters:
    directory_path (str): The path to the directory to search for Python files.

    Returns:
    list: A list of Python file paths.
    """
    if isinstance(directory_paths, str):
        directory_paths = [directory_paths]
    python_files = []

    # Walk through the directory
    for directory_path in directory_paths:
        for root, _, files in os.walk(directory_path):
            for file in files:
                # Check if the file is a Python file
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

    return python_files


def list_paths(dir_path: str):
    return [os.path.join(dir_path, p) for p in os.listdir(dir_path)]
