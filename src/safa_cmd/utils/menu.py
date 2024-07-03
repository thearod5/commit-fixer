from typing import List


def prompt_option(options: List[str], retries=0, max_retries=3, title: str = "Options"):
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

    print(f"\n{title}:")
    for i, option in enumerate(options):
        print(f"{i + 1})", option)

    try:
        option = input(">")
        option_num = int(option)
        return options[option_num - 1]
    except Exception as e:
        print(e)
        return prompt_option(options, retries=retries + 1)
