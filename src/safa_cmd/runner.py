import os
import sys

from dotenv import load_dotenv

SRC_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(SRC_PATH)

from safa_cmd.config import SafaConfig
from safa_cmd.tools.comitter.runner import run_committer
from safa_cmd.tools.safa.configure import run_config_tool
from safa_cmd.utils.menu import input_option

usage_msg = (
    """
    Repository Path is not set. There are two ways to set this path:
    1. Create safa.env file with `SAFA_REPO_PATH=...`
    2. Pass repo path as arguments to SAFA command like so:
        ```Usage: $ safa [REPO_PATH]```
    """
)
TOOLS = {
    "Commit": run_committer,
    "Config": run_config_tool
}


def run(repo_path: str):
    config: SafaConfig = SafaConfig.from_env(repo_path)
    menu_keys = list(TOOLS.keys())

    running = True
    while running:
        option_selected = input_option(menu_keys)
        tool_func = TOOLS[option_selected]
        tool_func(config)


def get_repo_path(*args):
    repo_path = None
    if "SAFA_REPO_PATH" in os.environ:
        repo_path = os.environ["SAFA_REPO_PATH"]
    elif len(args) == 1:
        repo_path = os.environ["SAFA_REPO_PATH"] = args[0]
    if repo_path:
        return os.path.expanduser(repo_path)
    print(usage_msg)
    sys.exit(-1)


def configure_repo_path():
    repo_path = os.path.expanduser(sys.argv[1]) if len(sys.argv) == 2 else os.path.abspath(".")
    env_file_path = os.path.join(repo_path, "safa.env")
    if not os.path.exists(env_file_path):
        print(f"Environment file not found:{env_file_path}")
        print(usage_msg)
        sys.exit(-1)
    load_dotenv(env_file_path)
    os.environ["SAFA_REPO_PATH"] = repo_path
    print("Repository:", repo_path)


if __name__ == "__main__":
    load_dotenv()
    configure_repo_path()
    run(get_repo_path(*sys.argv[1:]))
