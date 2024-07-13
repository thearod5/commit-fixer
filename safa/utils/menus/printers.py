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


def version_repr(v: Dict) -> str:
    """
    Converts version to its display format.
    :param v: Project Version data.
    :return: Display string.
    """
    return f"{v['majorVersion']}.{v['minorVersion']}.{v['revision']}"


def print_option_items(options, title, group2items: Optional[Dict[str, str | Dict]] = None) -> None:
    """
    Prints options to user.
    :param options: Options to display to user.
    :param title: The title of the set of options.
    :param group2items: Optional groups used to display options in sections.
    :return: Index
    """
    _verify_group_options(options, group2items)
    print_title(title)
    print_groups(options, group2items)
    max_length = max([len(d) for o, d in option2item.items()])
    print_bar(length=max_length, char=".")
    print(f"{len(options) + 1}) Exit")


def _verify_group_options(options: List[str], group2options: Dict[str, List[str] | Dict]) -> None:
    """
    Verifies that groups reference valid options.
    :param options: List of valid options.
    :param group2options: Groups containing reference to potential options.
    :return: None
    """
    for k, v in group2options.items():
        if isinstance(v, list):
            for v_item in v:
                if v_item not in options:
                    raise Exception(f"Groups reference `{v_item}` not in options ({options}).")
        elif isinstance(v, dict):
            _verify_group_options(options, v)
        else:
            print(v)
            raise Exception(f"Expected list or dict as values but got {v}")


def print_groups(
        options: Dict[str, str],
        groups: Dict[str, str | Dict],
        prefix: str = "",
        key2option: Optional[Dict[str, str]] = None,
        option2key: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    _verify_group_options(list(options.keys()), groups)
    if key2option is None:
        key2option = {}
    if option2key is None:
        option2key = {}
    for group_name, group in groups.items():
        print(f"{prefix}{group_name}")
        if isinstance(group, list):
            for item in group:
                i = option2key[item] if item in option2key else len(key2option) + 1
                print(f"{prefix}{GROUP_DELIMITER}{i}: {options[item]}")
                key2option[str(i)] = item
        else:
            print_groups(options, group, prefix=prefix + GROUP_DELIMITER, key2option=key2option)
    return key2option
