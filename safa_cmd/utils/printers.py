import math
from typing import Optional

from safa_cmd.constants import LINE_LENGTH


def print_title(title: str, factor: float = 1) -> None:
    """
    Prints title surrounding by bar.
    :param title: The title to print.
    :return: None
    """
    line_length = math.floor(LINE_LENGTH * factor)
    bar_length = (line_length - len(title)) // 2
    print("\n", "-" * bar_length, title, "-" * bar_length)


def print_bar(factor: float = 1, length: Optional[int] = None, char: str = "-") -> None:
    """
    Prints bar to STD OUT.
    :param factor: Multiplying factor for bar.
    :param length: The length of the bar to print.
    :param char: The character to print bar with.
    :return: None
    """
    if not length:
        length = math.floor(LINE_LENGTH * factor)
    print(char * length)
