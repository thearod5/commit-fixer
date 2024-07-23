from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, cast

ACTIONS = ["next_page", "previous_page", "last_page", "first_page", "select_all", "finish_selection"]
ACTION_GROUPS = {"Actions": ACTIONS}
ACTION2KEY = {
    "next_page": "n",
    "previous_page": "p",
    "last_page": "l",
    "first_page": "f",
    "select_all": "a",
    "finish_selection": "d",
}
KEY2ACTION = {v: k for k, v in ACTION2KEY.items()}
ItemMapType = Dict[str, str]

ACTION2NAME = {
    "next_page": "Next Page",
    "previous_page": "Previous Page",
    "last_page": "Last Page",
    "first_page": "First Page",
    "select_all": "Select All"
}


@dataclass
class MenuProperties:
    """
    :param items: The items to display in menu.
    :param page_items: The maximum number of item to show per page.
    :param title: The title of the menu.
    :param many: Whether many items allowed to be selected.
    """
    items: List[str]
    # User Settings
    many: bool = False
    page_items: int = 5
    title: str = "Options"
    finish_selection_title: str = "Done"
    selected_title = "Selected"
    page_title = "Page"
    default_group: str = "Items"  # Group name if no groups provided
    item2key: ItemMapType = None  # type:ignore
    item2name: ItemMapType = None  # type:ignore
    group2items: Dict = None  # type: ignore
    custom_actions: Dict[str, Callable[[], List[str]]] = field(default_factory=dict)
    # State Properties
    selected_items: List[str] = field(default_factory=list)
    _page: int = 0
    _max_pages: int = field(init=False)
    _key2item: ItemMapType = None  # type: ignore

    def __post_init__(self) -> None:
        """
        Calculates item keys, names and other menu properties.
        :return: None
        """
        if self.item2name is None:
            self.item2name = {item: item for item in self.items}
        if self.group2items is None:
            self.group2items = {self.default_group: self.items}
        if self.item2key is None:
            items = get_item_from_groups(self.group2items)
            self.item2key = {item: str(i) for i, item in enumerate(items)}
        self._max_pages = _calculate_max_pages(len(self.items), self.page_items)
        self._key2item = {v: k for k, v in self.item2key.items()}

    def get_title_details(self) -> str:
        """
        Creates title for menu.
        :param self: Page menu to create title for.
        :return: The menu title.
        """
        details = []
        if self._max_pages > 1:
            details.append(f"{self.page_title}:{self._page + 1}/{self._max_pages}")
        if self.many:
            details.append(f"\n{self.selected_title}: {self.selected_items}")
        return "\n".join(details).strip()

    def get_item(self, key: str) -> str:
        """
        Returns item with given key.
        :param key: The key selected by user.
        :return: The item associated with given key.
        """
        return self._key2item[key]

    def create_options(self, entity_type: str) -> Dict:
        """
        Creates options for entity.
        :param entity_type: Type of entity to create options for.
        :return:
        """
        assert entity_type in {"items", "actions"}
        if entity_type == "items":
            page_items = self.get_page_items()
            filtered_groups = filter_groups(self.group2items, page_items)
            return create_menu_options(filtered_groups, self.item2key, self.item2name)
        elif entity_type == "actions":
            available_actions = self.get_available_actions()
            filtered_groups = filter_groups(ACTION_GROUPS, available_actions)
            return create_menu_options(filtered_groups, ACTION2KEY, self.create_action2name())
        else:
            raise Exception(f"Unknown entity: {entity_type}")

    def create_action2name(self) -> Dict[str, str]:
        """
        :return: Returns map of actions to their display names.
        """
        actions = {**ACTION2NAME, "finish_selection": self.finish_selection_title}
        return actions

    def get_page_items(self) -> List[str]:
        """
        Construct map of page items id to their display names.
        TODO: Allow different keys for page items.
        :return: Map of page item id to their display names.
        """
        start_idx = self._page * self.page_items
        end_idx = start_idx + self.page_items
        page_items = self.items[start_idx: end_idx]
        return page_items

    def get_available_actions(self) -> List[str]:
        """
        :return: List of available actions depending on current page.
        """
        actions = []
        if self._page < self._max_pages - 1:
            actions.append("next_page")
            if self._max_pages > 2:
                actions.append("last_page")

        if self._page > 0:
            actions.append("previous_page")
            if self._max_pages > 2:
                actions.append("first_page")
        if self.many:
            actions.append("finish_selection")
            actions.append("select_all")
        return actions

    def perform_menu_action(self, action_key: str) -> Optional[List[str]]:
        """
        Performs menu action.
        :param self: Menu to perform action on.
        :param action_key: Key of action to perform.
        :return: None
        """
        action = KEY2ACTION[action_key]
        if action == "next_page":
            self._page = self._page if self._page >= self._max_pages else self._page + 1
        elif action == "previous_page":
            self._page = self._page - 1 if self._page > 0 else 0
        elif action == "last_page":
            self._page = self._max_pages - 1
        elif action == "first_page":
            self._page = 0
        elif action == "finish_selection":
            return self.selected_items
        elif action == "select_all":
            return self.items
        else:
            raise Exception(f"Unexpected menu action: {action}")
        return None


def create_menu_options(_groups: Dict, item2key: Dict, item2name: Dict) -> Dict:
    _groups = cast(Dict, _groups)
    new_groups = {}
    for k, v in _groups.items():
        if isinstance(v, list):
            new_groups[k] = {item2key[item]: item2name[item] for item in v}
        else:
            new_groups[k] = v
    return new_groups


def filter_groups(_groups: Dict, items: List[str]):
    new_groups = {}
    for k, v in _groups.items():
        new_v = [v_item for v_item in v if v_item in items] if isinstance(v, list) else filter_groups(v, items)
        if len(new_v) > 0:
            new_groups[k] = new_v
    return new_groups


def _calculate_max_pages(n_items: int, n_item_per_page: int) -> int:
    """
    Calculates how many pages it will take to display items.
    :param n_items: Total number of items.
    :param n_item_per_page: Items to display per page.
    :return: Number of pages needed.
    """
    max_pages = n_items // n_item_per_page
    max_pages = max_pages if n_items % n_item_per_page == 0 else max_pages + 1
    return max_pages


def get_item_from_groups(groups: Dict) -> List[str]:
    items = []
    for k, v in groups.items():
        if isinstance(v, list):
            items.extend(v)
        else:
            items.extend(get_item_from_groups(v))
    return items
