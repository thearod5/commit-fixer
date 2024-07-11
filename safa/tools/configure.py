import os
import sys
from getpass import getpass

from dotenv import load_dotenv

from safa.api.client_factory import create_safa_client
from safa.api.safa_client import SafaClient
from safa.tools.projects import run_configure_project
from safa.utils.fs import write_json
from safa.utils.printers import print_title

SRC_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print("SRS", SRC_PATH)
sys.path.append(SRC_PATH)

from safa.safa_config import SafaConfig
from safa.utils.menu import input_confirm

configure_message_template = (
    """
To configure your SAFA project, we are going to create the following

- .safa/.env: Contains ENV variables linking your account and project.
- .safa/.cache: Cached search results for improved performance.
- .safa/chroma: Creates vector store to easily conduct search.
    """
)


def configure(config: SafaConfig) -> SafaClient:
    print_title("Safa Configuration")
    print(f"\nRepository Root: {config.repo_path}\n")

    if not os.path.isdir(config.config_path):
        if input_confirm("Is this the root of your repository?", default_value="y"):
            os.makedirs(config.config_path, exist_ok=True)
        else:
            print(usage_msg)
            sys.exit(-1)

    configure_message = configure_message_template.format(config.repo_path)

    print(configure_message)

    if not input_confirm("Continue?", default_value="y"):
        print("Okay :)")
        sys.exit(-1)

    write_json(config.cache_file_path, {})

    print_title("Account Configuration", factor=0.5)
    run_configure_account(config)

    client = create_safa_client(config)

    print_title("Project Configuration")
    run_configure_project(config, client)

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


def run_configure_account(config: SafaConfig) -> None:
    """
    Configures account email and password.
    :param config: Configuration used to set account details in.
    :param client: Client used to access SAFA API.
    :return:None
    """
    if config.has_account():
        if input_confirm(f"Would you like to override your current account ({config.email})?", default_value="n"):
            config.clear_account()
            return run_configure_account(config)
        return

    email = input("Safa Account Email:")
    password = getpass("Safa Account Password:")
    config.set_account(email, password)
