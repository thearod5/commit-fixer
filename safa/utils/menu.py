import sys
from typing import Any, Dict, List, Optional

from safa.utils.printers import print_bar, print_title


def input_option(options: List[str], retries=0, max_retries=3, title: str = "Options", allow_many: bool = False,
                 group2items: Optional[Dict[str, str]] = None):
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

    instructions = "Enter the options as a comma-delimited list (or 'a' for all)" if allow_many else "Enter the option number"

    exit_idx = print_option_items(instructions, options, title, group2items=group2items)

    if not allow_many and len(options) == 1:
        return options[0]

    try:
        option = input(f"\n{instructions}:").lower().strip()
        if option == str(exit_idx + 1):
            print("Good Bye :)")
            sys.exit(0)
        if allow_many:
            if option == "a":
                return options
            else:
                user_items = [o for o in option.split(",") if len(o) > 0]
                selected_options = [options[int(item.strip()) - 1] for item in user_items]
                return selected_options
        else:
            option_num = int(option)
            return options[option_num - 1]
    except Exception as e:
        print(e)
        return input_option(options, retries=retries + 1)


def print_option_items(instructions, options, title, group2items: Dict[str, str] = None):
    print_title(title)

    option2item = get_item_displays(options)

    exit_idx = len(options)

    if group2items:
        for group, items in group2items.items():
            item_displays = [option2item[o] for o in items]
            print(group)
            print("\n".join(item_displays))
            print()
    else:
        print("\n".join(option2item.values()))
    max_length = max([len(d) for o, d in option2item.items()])
    print_bar(length=max_length, char=".")
    print(f"{len(options) + 1}) Exit")
    return exit_idx


def get_item_displays(options):
    item_displays = {}
    for i, option in enumerate(options):
        prefix = f"{i + 1})"
        item_displays[option] = f"{prefix} {option}"
    return item_displays


def input_with_default(prompt: str, default_value: Any):
    """
    Prompts user for input and returns it if not empty, otherwise default value is returned.
    :param prompt: The prompt to display to user.
    :param default_value: The default value.
    :return: User response or default value.
    """
    user_value = input(f"{prompt} ({default_value}):")
    if user_value.strip() == "":
        return default_value
    return user_value


def input_confirm(title: str = "Confirm?", y_option="y", n_option="n", default_value: Optional[str] = None):
    """
    Confirms with user.
    :param title: Title to display to user.
    :param y_option: Option for positive confirmation.
    :param n_option: Option for negative confirmation.
    :param default_value: Value to used if user returns empty response.
    :return: Whether user confirmed.
    """
    label = f"{title} ({y_option}/{n_option} or {default_value} if empty)" if default_value else f"{title} ({y_option}/{n_option})"
    user_selection = input(label)
    if user_selection == "":
        if default_value:
            return default_value
        else:
            return input_confirm(title=title, y_option=y_option, n_option=n_option, default_value=default_value)
    else:
        if user_selection not in [y_option, n_option]:
            return input_confirm(title=title, y_option=y_option, n_option=n_option, default_value=default_value)
    return y_option in user_selection
