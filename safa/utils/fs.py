import json
import os
import shutil
from typing import Any, Dict, cast


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
    if not os.path.isfile(file_path) and init_if_empty:
        write_json(file_path, {})
    file_content = read_file(file_path)
    if init_if_empty and len(file_content) == 0:
        return {}
    return cast(Dict[str, Any], json.loads(file_content))


def delete_dir(path) -> None:
    """
    Deletes all files and subdirectories in the given directory, then deletes the directory itself.
    :param path: The path to the directory to be deleted.
    """
    if not os.path.isdir(path):
        raise ValueError(f"The path {path} is not a valid directory.")

    # Remove all contents of the directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)  # Remove file or symbolic link
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directory and its contents

    # Remove the directory itself
    os.rmdir(path)
    print(f"Directory {path} and all its contents have been deleted.")
