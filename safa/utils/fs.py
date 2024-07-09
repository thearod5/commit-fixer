import json
import os
from typing import Any, Dict, List, Tuple, Union, cast


def write_file_content(file_path: str, file_content: str) -> None:
    """
    Writes content to file.
    :param file_path: Path to file.
    :param file_content: Content to write.
    :return: None
    """
    with open(file_path, "w") as f:
        f.write(file_content)


def write_json(file_path: str, json_dict: Dict) -> None:
    """
    Writes dict as JSON to file.
    :param file_path: Path to file.
    :param json_dict: Object to write.
    :return: None
    """
    write_file_content(file_path, json.dumps(json_dict))


def list_python_files(directory_paths: Union[List[str], str]):
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


def list_paths(dir_path: str) -> List[Tuple[str, str]]:
    """
    Lists full paths and file names in directory.
    :param dir_path: Path to directory.
    :return: List of tuples.
    """
    return [(os.path.join(dir_path, p), p) for p in os.listdir(dir_path)]


def clean_path(p: str) -> str:
    """
    Expands user path and converts to absolute format.
    :param p: The path to clean.
    :return: Cleaned path.
    """
    return os.path.abspath(os.path.expanduser(p))


def read_file(file_path: str) -> str:
    """
    Reads file content.
    :param file_path: Path to file.
    :return: Content of file.
    """
    with open(file_path, "r") as f:
        return f.read()


def read_json_file(file_path: str, init_if_empty: bool = True) -> Dict[str, Any]:
    """
    Reads a JSON file.
    :param file_path: Path to json file.
    :param init_if_empty: Initializes empty dictionary in file.
    :return: File JSON as object.
    """
    file_content = read_file(file_path)
    if init_if_empty and len(file_content) == 0:
        return {}
    return cast(Dict[str, Any], json.loads(file_content))
