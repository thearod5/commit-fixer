from getpass import getpass

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.projects import create_new_project
from safa.utils.commits import get_repo_commit
from safa.utils.menu import input_confirm, input_option
from safa.utils.printers import version_repr


def run_configure_account(config: SafaConfig) -> None:
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


def run_configure_project(config: SafaConfig, client: SafaClient, title: str = "How do you want to setup your project?") -> None:
    """
    Configures a SAFA project for current repository.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :param title: Prompt to user to select creating a new project or selecting an existing one.
    :return: None
    """
    project_setup_type = input_option(["create_new", "select_existing"], title=title)
    if project_setup_type == "create_new":
        create_new_project(config, client)
    elif project_setup_type == "select_existing":
        configure_existing_project(config, client)
    else:
        raise Exception("Unknown project option:" + project_setup_type)


def configure_existing_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Configures repository project from an existing project.
    :param config: Safa configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    if config.has_version_id():
        print("Current Version ID:", config.version_id)
        if input_confirm(title="Override version Id?"):
            config.clear_project()
            return configure_existing_project(config, client)
        return

    # Select Project
    project_lookup_map = {p["name"]: p for p in client.get_projects()}
    selected_project_name = input_option(list(project_lookup_map.keys()))
    selected_project = project_lookup_map[selected_project_name]
    # Select Version.
    versions = client.get_project_versions(selected_project["projectId"])
    id2version = {version_repr(v): v for v in versions}
    version_id_selected = input_option(list(id2version.keys()))
    selected_version = id2version[version_id_selected]
    # Select Commit
    commit = get_repo_commit(repo_path=config.repo_path)
    commit_id = commit.hexsha

    config.set_project(selected_project["projectId"], selected_version["versionId"], commit_id)
    print("Project version successfully configured.")
