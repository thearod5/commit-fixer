import sys

from safa_cmd.config import SafaConfig
from safa_cmd.tools.comitter.runner import run_committer
from safa_cmd.tools.safa.select_project import select_project
from safa_cmd.utils.menu import prompt_option

TOOLS = {
    "Commit": run_committer,
    "Create Project": select_project
}


def run():
    config: SafaConfig = SafaConfig.from_env()
    if config.version_id:
        TOOLS.pop("Create Project")
    menu_keys = list(TOOLS.keys())

    running = True
    while running:
        option_selected = prompt_option(menu_keys)
        tool_func = TOOLS[option_selected]
        tool_func(config)


if __name__ == "__main__":
    run()
