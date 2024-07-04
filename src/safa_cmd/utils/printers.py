from safa_cmd.constants import LINE_LENGTH


def print_title(title: str) -> None:
    """
    Prints title surrounding by bar.
    :param title: The title to print.
    :return: None
    """
    bar_length = LINE_LENGTH - len(title) // 2
    print("-" * bar_length, title, "-" * bar_length)
