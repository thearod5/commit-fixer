import sys
from typing import Any, Dict, List, Optional

from safa.utils.printers import print_bar, print_title


def input_option(options: Dict | List[str], retries=0, max_retries=3, title: str = "Options", allow_many: bool = False,
                 groups: Optional[Dict[str, List[str]]] = None):
    """
    Prompts user to select an option.
    :param options: List of options.
    :param retries: Current retry count.
    :param max_retries: Maximum number of retries.
    :param title: Title displayed before options
    :param allow_many: Allows multiple options to be selected (including empty option).
    :param group2items: Map of group names to their item in that group.
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

    idx2option = print_groups(options, groups)

    instructions = "Enter the options as a comma-delimited list (or 'a' for all)" if allow_many else "Enter the option number"

    if not allow_many and len(options) == 1:
        return list(options.keys())[0]

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
                selected_options = [idx2option[idx] for idx in selected_indices]
                return selected_options
        else:
            option_num = int(option)
            return idx2option[option_num]
    except Exception as e:
        print(e)
        return input_option(options, retries=retries + 1)


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


def input_confirm(title: str = "Confirm?", y_option="y", n_option="n", default_value: Optional[str] = None) -> bool:
    """
    Confirms with user.
    :param title: Title to display to user.
    :param y_option: Option for positive confirmation.
    :param n_option: Option for negative confirmation.
    :param default_value: Value to used if user returns empty response.
    :return: Whether user confirmed.
    """
    valid_options = [y_option, n_option]
    if default_value and default_value not in valid_options:
        raise Exception(f"Expected {default_value} to be one of {valid_options}")
    label = f"{title} ({y_option}/{n_option} or {default_value} if empty)" if default_value else f"{title} ({y_option}/{n_option})"
    user_selection = input(label)
    if user_selection == "":
        if default_value:
            user_selection = default_value
        else:
            return input_confirm(title=title, y_option=y_option, n_option=n_option, default_value=default_value)
    else:
        if user_selection not in [y_option, n_option]:
            return input_confirm(title=title, y_option=y_option, n_option=n_option, default_value=default_value)
    return y_option in user_selection


def print_groups(options: Dict[str, str], groups: Dict[str, str | Dict], prefix: str = "", idx2option: Dict[str, str] = None):
    _verify_group_options(options.keys(), groups)
    if idx2option is None:
        idx2option = {}
    for group_name, group in groups.items():
        print(f"{prefix}{group_name}")
        if isinstance(group, list):
            for item in group:
                i = len(idx2option) + 1
                print(f"{prefix}\t{i}: {options[item]}")
                idx2option[i] = item
        else:
            print_groups(options, group, prefix=prefix + "\t", idx2option=idx2option)
    return idx2option
