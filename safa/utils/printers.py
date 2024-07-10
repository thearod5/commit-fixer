import math
from typing import Dict, List, Optional

from safa.constants import LINE_LENGTH


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


def print_commit_response(response: Dict, keys: Optional[List[str]] = None) -> None:
    """
    Prints committed entities summaries to the console.
    :param response: Commit response.
    :param keys: Keys to print in response.
    :return: None
    """
    if keys is None:
        keys = ["artifacts", "traces"]
    for entity_type in keys:
        for mod_type, mod_items in response[entity_type].items():
            n_items = len(mod_items)
            if n_items > 0:
                print(f"{entity_type}: {mod_type}: {n_items}")
