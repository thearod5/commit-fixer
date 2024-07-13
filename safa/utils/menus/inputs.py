from typing import Dict, List, Optional

from safa.utils.menus.page_menu import input_menu_paged


def input_option(options: Dict | List[str], **kwargs):
    """

    :param options:
    :param kwargs:
    :return:
    """
    assert isinstance(options, list), f"{options}"
    return input_menu_paged(options, _properties=None, **kwargs)


def input_int(prompt: str, retries: int = 0, max_retries: int = 3) -> int:
    """
    Prompts user to input number.
    :param prompt: The prompt to display to user.
    :param retries: Current number of retries.
    :param max_retries: Maximum number of retries before raising exception.
    :return: Inputted int.
    """
    if retries >= max_retries:
        raise Exception("Expected user to provide number. Max retries reached.")
    user_response = input(prompt)
    try:
        return int(user_response)
    except:
        return input_int(prompt, retries=retries + 1)


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
