from typing import Dict, List

from safa.utils.menus.printers import print_title
from safa.utils.menus.properties import MenuProperties

ItemMapType = Dict[str, str]  # Maps item to other fields


def input_menu_paged(items: List[str] | Dict[str, str], _properties=None, **kwargs):
    """
    Constructs menu for items and performs user selection.
    :param items: The items to display in the menu.
    :param _properties: Internal properties used for recursive retrying.
    :param kwargs: Keyword arguments to menu properties.
    :return: User Selections.
    """
    if _properties is None:
        _properties = MenuProperties(items=items, **kwargs)
    if len(_properties.items) == 0:
        raise Exception("No items to select from.")
    if len(_properties.items) == 1:
        return _properties.items if _properties.many else _properties.items[0]
    title_Details = _properties.get_title_details()
    menu_options = _properties.create_options("items")
    action_options = _properties.create_options("actions")

    print_title(_properties.title)
    if title_Details:
        print(title_Details, "\n")
    print_dict(menu_options)
    print_dict(action_options)

    item_key_selected = input("Option:")

    if is_selected(menu_options, item_key_selected):
        item_selected = _properties.get_item(item_key_selected)
        if _properties.many:
            _properties.selected_items.append(item_selected)
        else:
            return item_selected

    elif is_selected(action_options, item_key_selected):
        result = _properties.perform_menu_action(item_key_selected)
        if result is not None:
            return result

    else:
        print(f"Invalid option: {item_key_selected}")
    return input_menu_paged(items, _properties=_properties)


def is_selected(options: Dict, selection: str):
    for k, v in options.items():
        if isinstance(v, dict):
            if is_selected(v, selection):
                return True
        else:
            if k == selection:
                return True
    return False


def print_dict(obj: Dict, prefix: str = "", delimiter: str = " "):
    for k, v in obj.items():
        if isinstance(v, dict):
            print(prefix + k)
            print_dict(v, prefix=prefix + delimiter, delimiter=delimiter)
        else:

            print(prefix + delimiter + k + ") " + v)
