import os
import sys
from typing import Callable, Dict, List, Tuple

from dotenv import load_dotenv

from safa.safa_client import SafaClient
from safa_cmd.safa.http_client import HttpClient
from safa_cmd.safa.safa_store import SafaStore
from safa_cmd.tools.search import run_search
from safa_cmd.utils.fs import clean_path
from safa_cmd.utils.printers import print_title

SRC_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(SRC_PATH)

from safa_cmd.tools.projects import run_projects
from safa_cmd.config import SafaConfig
from safa_cmd.tools.committer import run_committer
from safa_cmd.tools.configure import configure_account, configure_project
from safa_cmd.utils.menu import input_confirm, input_option

safa_banner = (
    """
███████╗ █████╗ ███████╗ █████╗             █████╗ ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗           ██╔══██╗██║
███████╗███████║█████╗  ███████║           ███████║██║
╚════██║██╔══██║██╔══╝  ██╔══██║           ██╔══██║██║
███████║██║  ██║██║     ██║  ██║    ██╗    ██║  ██║██║
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═╝    ╚═╝  ╚═╝╚═╝                        
        Making your documentation work for you.
                  https://safa.ai
    """
)
usage_msg = (
    """
    SAFA could not define the real repository path. 
    
    There are two ways to set this path:
    1. Create safa.env file at inferred repository path
        `SAFA_REPO_PATH=...`
    2. Pass repo path as arguments to SAFA command like so:
        ```Usage: $ safa [REPO_PATH] [ENV_FILE_PATH]```
    """
)
ToolType = Callable[[SafaConfig, SafaClient], None]
TOOLS: Dict[str, Tuple[ToolType, List[str]]] = {
    "Commit": (run_committer, ["project"]),
    "Search": (run_search, ["project"]),
    "Manage Projects": (run_projects, ["project"]),
    "Configure Project": (configure_project, ["user"]),
    "Configure Account": (configure_account, ["*"]),  # type: ignore
}


def main() -> None:
    """
    Allows users to run tools.
    :return: None
    """
    print("\n", safa_banner.strip())

    repo_path = clean_path(sys.argv[1]) if len(sys.argv) >= 2 else os.path.abspath("")
    env_file_path = sys.argv[2] if len(sys.argv) >= 3 else None
    config = SafaConfig.from_repo(repo_path, env_file_path)

    if config.is_configured():
        client = create_safa_client(config)
    else:
        client = configure(config)
    print("User successfully logged in.")

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


def create_safa_client(config):
    base_url = os.environ.get("BASE_URL", "https://api.safa.ai")
    http_client = HttpClient(base_url, global_parameters={"verify": False})
    store = SafaStore(cache_file_path=config.cache_file_path)
    client = SafaClient(store, http_client=http_client)
    if config.email is None:
        print("Account email was not found.")
        configure_account(config)
    client.login(config.email, config.password)
    return client


configure_message_template = (
    """
To configure your SAFA project, we are going to create the following

.safa
    /.env: Contains ENV variables linking your account and project.
    /chroma: Creates vector store to easily conduct search.
    """
)


def configure(config: SafaConfig) -> SafaClient:
    print(f"\nRepository Root: {config.repo_path}\n")
    if not os.path.isdir(config.config_path):
        if input_confirm("Is this the root of your repository?"):
            os.makedirs(config.config_path, exist_ok=True)
        else:
            print(usage_msg)
            sys.exit(-1)

    configure_message = configure_message_template.format(config.repo_path)
    print_title("Welcome to your new project.")
    print(configure_message)

    if not input_confirm("Do you want to continue configuration?"):
        print("Okay :)")
        sys.exit(-1)

    print_title("Account Configuration", factor=0.5)
    configure_account(config)

    client = create_safa_client(config)

    print_title("Project Configuration")
    configure_project(config, client)

    print("Configuration Finished.")
    return client


def configure_repo_path() -> str:
    """
    Extracts the repository path from env or from arguments.
    :return: Repository path.
    """
    repo_path = os.path.expanduser(sys.argv[1]) if len(sys.argv) == 2 else os.path.abspath("")
    env_file_path = os.path.join(repo_path, ".safa")
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
