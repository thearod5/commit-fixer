from getpass import getpass

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.projects import create_new_project
from safa.utils.menu import input_confirm, input_option


def run_configure_account(config: SafaConfig, *args) -> None:
    """
    Configures account email and password.
    :param config: Configuration used to set account details in.
    :return:None
    """
    if config.email is None:
        config.email = input("Safa Account Email:")
    else:
        print(f"Safa Account: {config.email}")
    if config.password is None:
        config.password = getpass("Safa Account Password:")
    else:
        print("Safa account password is set.")

    config.to_env()


def configure_existing_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Configures repository project from an existing project.
    :param config: Safa configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    if config.version_id is None:
        project_lookup_map = {p["name"]: p for p in client.get_projects()}
        selected_project_name = input_option(list(project_lookup_map.keys()))
        selected_project = project_lookup_map[selected_project_name]

        project_versions = client.get_project_versions(selected_project["projectId"])
        pv_options = {f"{v['majorVersion']}.{v['minorVersion']}.{v['revision']}": v for v in project_versions}
        pv_selected = input_option(list(pv_options.keys()))
        selected_version = pv_options[pv_selected]
        config.project_id = selected_project["projectId"]
        config.version_id = selected_version["versionId"]
    else:
        print("Current Version ID:", config.version_id)
        if input_confirm(title="Override version Id?"):
            config.version_id = None
            return configure_existing_project(config, client)
    print("Project version successfully configured.")
    config.to_env()


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
