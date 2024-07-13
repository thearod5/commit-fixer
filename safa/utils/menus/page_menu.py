from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from safa.utils.menu import input_option

ACTION_KEYS = ["next_page", "previous_page", "last_page", "first_page", "finish_selection"]
action2keys = {
    "next_page": "n",
    "previous_page": "p",
    "last_page": "l",
    "first_page": "f",
    "finish_selection": "finish"
}


@dataclass
class PageMenu:
    items: List[str]
    n_item_per_page: int = 5
    title: str = "Options"
    many: bool = False
    page: int = 0
    item2name: Dict[str, str] = field(default_factory=dict)
    custom_actions: Dict[str, Callable[[], List[str]]] = field(default_factory=dict)
    selected_items: List[str] = field(default_factory=list)
    finish_selection_title: str = "Finish Selection"
    max_pages: int = field(init=False)

    def __post_init__(self):
        self.max_pages = calculate_max_pages(len(self.items), self.n_item_per_page)


def input_menu_paged(items: List[str] | Dict[str, str], **kwargs):
    page_menu = PageMenu(items=items, **kwargs)
    return select(page_menu)


def select(menu: PageMenu):
    if len(menu.items) == 1:
        menu_keys = list(menu.items)
        return menu_keys if menu.many else menu_keys[0]
    while True:
        page_items, menu_items, menu_groups, item2keys = get_current_menu_page(menu)
        title = create_title(menu)
        selected_item = input_option(menu_items, groups=menu_groups, title=title, item2keys=item2keys)
        result = handle_selection(menu, selected_item, ACTION_KEYS, list(page_items.keys()))
        if result:
            return result


def get_current_menu_page(menu: PageMenu):
    page_items = get_page_items(menu)
    action_items = get_actions(menu)
    menu_groups = {
        "Items": list(page_items.keys()),
        "Actions": list(action_items.keys()),
        "Custom": menu.custom_actions
    }
    page_item_map = {i: i for i in page_items}
    menu_items = {**page_item_map, **action_items}
    return page_items, menu_items, menu_groups, action2keys


def handle_selection(menu: PageMenu,
                     selection: str,
                     action_item_keys: List[str],
                     page_items: List[str]) -> str:
    if selection in page_items:
        if menu.many:
            menu.selected_items.append(selection)
        else:
            return selection
    elif selection in action_item_keys:
        perform_menu_action(menu, selection)
    elif selection in menu.custom_actions:
        custom_action = menu.custom_actions[selection]
        custom_action_result = custom_action()
        if custom_action_result:
            menu.selected_items.extend(custom_action_result)
    else:
        available_options = page_items + action_item_keys + list(menu.custom_actions.keys())
        raise Exception(f"Unable to handle user selection ({selection}), not one of {available_options}")


def perform_menu_action(menu: PageMenu, action: str) -> Optional[List[str]]:
    """
    Performs menu action.
    :param menu: Menu to perform action on.
    :param action: The action to perform.
    :return: None
    """
    if action == "next_page":
        menu.page = menu.page if menu.page >= menu.max_pages else menu.page + 1
    elif action == "previous_page":
        menu.page = menu.page - 1 if menu.page > 0 else 0
    elif action == "last_page":
        menu.page = menu.max_pages - 1
    elif action == "first_page":
        menu.page = 0
    elif action == "finish_selection":
        return menu.selected_items
    else:
        raise Exception(f"Unexpected menu action: {action}")


def get_page_items(menu: PageMenu) -> Dict[str, str]:
    """
    Construct map of page items id to their display names.
    TODO: Allow different keys for page items.
    :return: Map of page item id to their display names.
    """
    start_idx = menu.page * menu.n_item_per_page
    end_idx = start_idx + menu.n_item_per_page
    page_items = menu.items[start_idx: end_idx]
    page_item_map = {i: i for i in page_items}
    return page_item_map


def get_actions(self) -> Dict[str, str]:
    """
    :return: Returns the available actions.
    """
    actions = {}
    if self.page < self.max_pages - 1:
        actions["next_page"] = "Next"
    if self.page > 0:
        actions["previous_page"] = "Previous"
    if self.page < self.max_pages - 1:
        actions["last_page"] = "Last Page"
    if self.page > 0:
        actions["first_page"] = "First Page"
    if self.many:
        actions["finish_selection"] = self.finish_selection_title
    return actions


def calculate_max_pages(n_items: int, n_item_per_page: int) -> int:
    """
    Calculates how many pages it will take to display items.
    :param n_items: Total number of items.
    :param n_item_per_page: Items to display per page.
    :return: Number of pages needed.
    """
    max_pages = n_items // n_item_per_page
    max_pages = max_pages if n_items % n_item_per_page == 0 else max_pages + 1
    return max_pages


def create_title(menu: PageMenu) -> str:
    """
    Creates title for menu.
    :param menu: Page menu to create title for.
    :return: The menu title.
    """
    title = f"{menu.title}\nPage:{menu.page + 1}/{menu.max_pages}"
    if menu.many:
        title += f"\nItems: {menu.selected_items}"
    return title


if __name__ == "__main__":
    input_menu_paged([c for c in "ab"], item2name={'a': 'A', 'b': "B"})
