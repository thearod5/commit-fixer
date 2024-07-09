import math

from safa_cmd.constants import LINE_LENGTH


def print_title(title: str) -> None:
    """
    Prints title surrounding by bar.
    :param title: The title to print.
    :return: None
    """
    bar_length = (LINE_LENGTH - len(title)) // 2
    print("\n", "-" * bar_length, title, "-" * bar_length)


def print_bar(factor: float = 1, length: int = None) -> None:
    """
    Prints bar to STD OUT.
    :param factor: Multiplying factor for bar.
    :param length: The length of the bar to print.
    :return: None
    """
    if not length:
        length = math.floor(LINE_LENGTH * factor)
    print("-" * length)
