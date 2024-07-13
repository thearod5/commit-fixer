import sys
from typing import Any, Dict, List, Optional

from safa.utils.printers import print_title


def input_option(
        options: Dict | List[str],
        retries=0,
        max_retries=3,
        title: str = "Options",
        allow_many: bool = False,
        groups: Optional[Dict[str, List[str]]] = None,
        item2keys: Optional[Dict[str, str]] = None
):
    """
    Prompts user to select an option.
    :param options: List of options.
    :param retries: Current retry count.
    :param max_retries: Maximum number of retries.
    :param title: Title displayed before options
    :param allow_many: Allows multiple options to be selected (including empty option).
    :param groups: Map of group names to their item in that group.
    :param item2keys: Map of item to key to show in menu.
    :return: Option selected.
    """
    if retries >= max_retries:
        raise Exception("Max retries has been reached.")

    if isinstance(options, list):
        options = {o: o for o in options}
    if groups is None:
        groups = {title: list(options.keys())}
    else:
        print_title(title, factor=.25)
    options["exit"] = "Exit"
    groups["---"] = ["exit"]
    ignore = ["Exit"]

    key2option = print_groups(options, groups=groups, option2key=item2keys)  # type: ignore

    instructions = "Enter the options as a comma-delimited list (or 'a' for all)" if allow_many else "Enter the option number"

    if len(options) == 2:
        option_keys = list(options.keys())
        return option_keys if allow_many else option_keys[0]

    try:
        option = input(f"\n{instructions}:").lower().strip()

        if option == str(len(options)):
            print("Good Bye :)")
            sys.exit(0)
        if allow_many:
            if option == "a":
                return list([v for v in options.values() if v not in ignore])
            else:
                selected_indices = [int(o.strip()) for o in option.split(",") if len(o) > 0]
                selected_options = [key2option[idx] for idx in selected_indices]
                return selected_options
        else:
            return key2option[option]
    except Exception as e:
        print(e)
        return input_option(options, retries=retries + 1)


def get_item_displays(options: List[Any]) -> Dict[str, str]:
    """
    Returns list of strings representing how to display each item.
    :param options: List of options to display to user.
    :return: List of display strings.
    """
    item_displays = {}
    for i, option in enumerate(options):
        prefix = f"{i + 1})"
        item_displays[option] = f"{prefix} {option}"
    return item_displays
