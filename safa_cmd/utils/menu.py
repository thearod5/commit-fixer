import sys
from typing import Any, List

from safa_cmd.utils.printers import print_bar, print_title


def input_option(options: List[str], retries=0, max_retries=3, title: str = "Options", allow_many: bool = False):
    """
    Prompts user to select an option.
    :param options: List of options.
    :param retries: Current retry count.
    :param max_retries: Maximum number of retries.
    :param title: Title displayed before options
    :return: Option selected.
    """
    if retries >= max_retries:
        raise Exception("Max retries has been reached.")

    instructions = "Enter the options as a comma-delimited list (or 'a' for all)" if allow_many else "Enter the option number"

    print_title(title)
    print(instructions)
    max_length = 0
    for i, option in enumerate(options):
        prefix = f"{i + 1})"
        print(prefix, option)
        max_length = max(max_length, len(prefix) + len(option) + 1)
    print_bar(length=max_length)
    print(f"{len(options) + 1}) Exit")
    exit_idx = len(options)

    if not allow_many and len(options) == 1:
        return options[0]

    try:
        option = input(f"\nSelection:").lower().strip()
        if option == str(exit_idx + 1):
            print("Good Bye.")
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


def input_confirm(title: str = "Confirm?", y_option="y", n_option="n"):
    """
    Confirms with user.
    :param title: Title to display to user.
    :param y_option: Option for positive confirmation.
    :param n_option: Option for negative confirmation.
    :return: Whether user confirmed.
    """
    user_selection = input(f"{title} ({y_option}/{n_option})")
    return user_selection == y_option
