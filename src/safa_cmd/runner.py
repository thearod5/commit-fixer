import sys

from safa_cmd.config import SafaConfig
from safa_cmd.tools.comitter.runner import run_committer
from safa_cmd.utils.menu import prompt_option

TOOLS = {
    "Generate Commit Details": run_committer,
    "Exit": None
}


def run():
    config: SafaConfig = SafaConfig.from_env()
    menu_keys = list(TOOLS.keys())

    running = True
    while running:
        option_selected = prompt_option(menu_keys)
        if option_selected.lower() == "exit":
            print("Good Bye :)")
            sys.exit(0)
        tool_func = TOOLS[option_selected]
        tool_func(config)


if __name__ == "__main__":
    run()
