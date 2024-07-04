from typing import List


def prompt_option(options: List[str], retries=0, max_retries=3, title: str = "Options", allow_many: bool = False):
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

    instructions = "Enter the options as a comma-delimited list (or 'a' for all)" if allow_many else "Enter the option number."

    print(f"\n{title}:")
    for i, option in enumerate(options):
        print(f"{i + 1})", option)
    print(instructions)

    try:
        option = input(">").lower().strip()
        if allow_many:
            if option == "a":
                return options
            else:
                if "," not in option:
                    print("Please enter comma-separated list.")
                    return prompt_option(options, retries=1 + retries, max_retries=max_retries, title=title, allow_many=allow_many)
                selected_options = [options[int(o.strip())] for o in option.split(",")]
                return selected_options
        else:
            option_num = int(option)
            return options[option_num - 1]
    except Exception as e:
        print(e)
        return prompt_option(options, retries=retries + 1)
