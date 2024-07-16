import os
import sys
from getpass import getpass
from typing import Tuple

from dotenv import load_dotenv

from safa.api.client_factory import create_safa_client
from safa.api.safa_client import SafaClient
from safa.constants import usage_msg
from safa.tools.projects.configure import run_configure_project
from safa.tools.projects.push import run_push_commit
from safa.utils.fs import write_json
from safa.utils.menus.printers import print_title

SRC_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(SRC_PATH)

from safa.safa_config import SafaConfig
from safa.utils.menus.inputs import input_confirm

configure_message_template = (
    """
Looks like SAFA needs to configure a few things:
- [{}] User
- [{}] Project
- [{}] Commit
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

    configure_message = configure_message_template.format(*get_config_status(config))

    print(configure_message)

    if not input_confirm("Continue?", default_value="y"):
        print("Okay :)")
        sys.exit(-1)

    write_json(config.cache_file_path, {})

    if config.llm_key is None:
        config.llm_key = getpass("Anthropic API Key:")
        config.save()

    if not config.has_account():
        print_title("Account Configuration", factor=0.5)
        run_configure_account(config)

    client = create_safa_client(config)

    if not config.has_project():
        print_title("Project Configuration")
        run_configure_project(config, client)

    if not config.has_commit_id():
        print_title("Commit Configuration")
        run_push_commit(config, client, set_as_current_project=True)

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


def run_configure_account(config: SafaConfig, *args) -> None:
    """
    Configures account email and password.
    :param config: Configuration used to set account details in.
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


def get_config_status(config: SafaConfig) -> Tuple[str, str, str]:
    """
    Returns the status of the configuration for each entity.
    :param config: Safa config.
    :return: User, Project, and Commit status.
    """
    user_status = "x" if config.has_account() else " "
    project_status = "x" if config.has_project() else " "
    commit_status = "x" if config.has_commit_id() else " "
    return user_status, project_status, commit_status
