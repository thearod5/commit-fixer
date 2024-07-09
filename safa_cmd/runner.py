import os
import sys
from typing import Callable, Dict, List, Tuple

from dotenv import load_dotenv

from safa.safa_client import SafaClient
from safa_cmd.safa.http_client import HttpClient
from safa_cmd.safa.safa_store import SafaStore
from safa_cmd.tools.search import run_search
from safa_cmd.utils.printers import print_title

SRC_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(SRC_PATH)

from safa_cmd.tools.projects import run_projects
from safa_cmd.config import SafaConfig
from safa_cmd.tools.committer import run_committer
from safa_cmd.tools.configure import run_config_tool
from safa_cmd.utils.menu import input_option

safa_banner = (
    """
███████╗ █████╗ ███████╗ █████╗             █████╗ ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗           ██╔══██╗██║
███████╗███████║█████╗  ███████║           ███████║██║
╚════██║██╔══██║██╔══╝  ██╔══██║           ██╔══██║██║
███████║██║  ██║██║     ██║  ██║    ██╗    ██║  ██║██║
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═╝    ╚═╝  ╚═╝╚═╝                        
        Making your documentation work for you.
    """
)
usage_msg = (
    """
    SAFA could not define the real repository path. 
    
    There are two ways to set this path:
    1. Create safa.env file at inferred repository path
        `SAFA_REPO_PATH=...`
    2. Pass repo path as arguments to SAFA command like so:
        ```Usage: $ safa [REPO_PATH]```
    """
)
ToolType = Callable[[SafaConfig, SafaClient], None]
TOOLS: Dict[str, Tuple[ToolType, List[str]]] = {
    "Commit": (run_committer, ["*"]),
    "Setup": (run_config_tool, ["*"]),
    "Projects": (run_projects, ["user", "project"]),
    "Search": (run_search, ["user", "project"])
}


def main() -> None:
    """
    Allows users to run tools.
    :return: None
    """
    repo_path = configure_repo_path()
    config: SafaConfig = SafaConfig.from_env(repo_path)

    http_client = HttpClient("https://localhost:3000", global_parameters={"verify": False})
    store = SafaStore(cache_file_path=config.cache_file_path)
    client = SafaClient(store, http_client=http_client)
    client.login(config.email, config.password)
    print("User successfully logged in.")

    print("\n", safa_banner.strip())
    print_title("Configuration")
    print(config)

    config_permissions = get_available_permissions(config)

    running = True
    while running:
        filtered_tools = filter_tools_by_permissions(TOOLS, config_permissions)
        menu_keys = list(filtered_tools.keys())
        option_selected = input_option(menu_keys, title="Tools")
        tool_func, tool_permissions = TOOLS[option_selected]
        tool_func(config, client)


def configure_repo_path() -> str:
    """
    Extracts the repository path from env or from arguments.
    :return: Repository path.
    """
    repo_path = os.path.expanduser(sys.argv[1]) if len(sys.argv) == 2 else os.path.abspath("")
    env_file_path = os.path.join(repo_path, "safa.env")
    if not os.path.exists(env_file_path):
        print("Inferred Repository Path:", repo_path, "\n")
        print(usage_msg.strip())
        sys.exit(-1)
    load_dotenv()
    load_dotenv(env_file_path)
    os.environ["SAFA_REPO_PATH"] = repo_path
    return repo_path


def get_available_permissions(config: SafaConfig) -> List[str]:
    """
    Parses available permissions from configuration.
    Alberto: I am not checking to see if credentials or version is valid because I don't want this being really slow on login.
    :return: List of available permissions.
    """
    permissions = []
    if config.email and config.password:
        permissions.append("user")
    if config.version_id:
        permissions.append("project")
    return permissions


def filter_tools_by_permissions(tool_set: Dict, permissions: List[str]) -> Dict:
    """
    Filters for tools that meet permission levels.
    :param tool_set: Set of available tools.
    :param permissions: Set of available permissions.
    :return: Map of tool name to func for available tools.
    """
    filtered_tools = {}
    for tool_name, tool_def in tool_set.items():
        tool_func, tool_permission = tool_def
        has_permission = all([o in permissions for o in tool_permission]) or "*" in tool_permission
        if has_permission:
            filtered_tools[tool_name] = tool_func
    return filtered_tools


if __name__ == "__main__":
    main()
