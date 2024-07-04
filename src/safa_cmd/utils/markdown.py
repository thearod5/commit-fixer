from typing import List


def list_formatter(items: List[str], format_type: str = "bullet"):
    """
    Formats a list of items as markdown.
    :param items: The items to format.
    :param format_type: One of bullet or numbered.
    :return: Formatted content as string.
    """
    formatters = {
        "bullet": list_bullet_formatter,
        "numbered": list_numbered_formatter
    }
    formatter = formatters[format_type]
    content = '\n'.join([formatter(i, c) for i, c in enumerate(items)])
    return content


def list_bullet_formatter(i: int, c: str) -> str:
    """
    Formats a bulleted list item as markdown.
    :param i: Ignored. The index of the item.
    :param c: The item to format.
    :return: Formatted list item.
    """
    return "- " + c


def list_numbered_formatter(i: int, c: str) -> str:
    """
    Formats a numbered list item as markdown.
    :param i: Index of the item.
    :param c: The item content.
    :return: Formatted list item.
    """
    return f"{i + 1}) " + c
