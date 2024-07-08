def write_file_content(file_path: str, file_content: str) -> None:
    """
    Writes content to file.
    :param file_path: Path to file.
    :param file_content: Content to write.
    :return: None
    """
    with open(file_path, "w") as f:
        f.write(file_content)
