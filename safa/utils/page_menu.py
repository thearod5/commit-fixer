from typing import Callable, Dict, List, Optional

from safa.utils.menu import input_option


class PageMenu:
    def __init__(self, items: List[str], n_item_per_page: int = 5, title: str = "Options",
                 many: bool = False, custom_actions: Optional[Dict[str, Callable]] = None):
        """
        Creates new paged selection menu.
        :param items: Items to select from.
        :param n_item_per_page: Number of items per page.
        :param title:The title of the menu.
        """
        self.items = items
        self.n_item_per_page = n_item_per_page
        self.title = title
        self.many = many
        self.max_pages = self.calculate_max_pages(len(items), n_item_per_page)
        self.page = 0
        self.custom_actions = custom_actions if custom_actions else {}
        self.selected_items: List[str] = []

    def select(self):
        if len(self.selected_items) == 1:
            return self.selected_items if self.many else self.selected_items[0]
        while True:
            start_idx = self.page * len(self.items)
            end_idx = start_idx + self.n_item_per_page
            menu_items = self.items[start_idx: end_idx]
            action_items = self.get_actions()

            group2items = {"Items": menu_items, "Actions": list(action_items.keys()), "Custom": self.custom_actions}
            items = {i: i for i in menu_items}
            items.update(action_items)

            title = f"{self.title}\nPage:{self.page + 1}/{self.max_pages}"
            if self.many:
                title += f"\nItems: {self.selected_items}"

            selected_item = input_option(items, groups=group2items)

            if selected_item in menu_items:
                if self.many:
                    self.selected_items.append(selected_item)
                else:
                    return selected_item
            elif selected_item == "finish_selection":
                return selected_item
            elif selected_item in action_items:
                self.perform_menu_action(selected_item)
            elif selected_item in self.custom_actions:
                custom_action = self.custom_actions[selected_item]
                items = custom_action()
                self.selected_items.extend(items)
            else:
                raise Exception(f"Unknown item: {selected_item}")

    def perform_menu_action(self, action: str) -> None:
        """
        Performs menu action.
        :param action: The action to perform.
        :return: None
        """
        if action == "next_page":
            self.page = self.page if self.page >= self.max_pages else self.page + 1
        elif action == "previous_page":
            self.page = self.page - 1 if self.page > 0 else 0
        elif action == "last_page":
            self.page = self.max_pages - 1
        elif action == "first_page":
            self.page = 0
        else:
            raise Exception(f"Unexpected menu action: {action}")

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
            actions["finish_selection"] = "Finish Selection"

        return actions

    @staticmethod
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
