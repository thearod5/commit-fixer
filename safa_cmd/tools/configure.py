from getpass import getpass

from safa_cmd.config import SafaConfig
from safa_cmd.safa.safa_client import SafaClient
from safa_cmd.tools.projects import create_new_project
from safa_cmd.utils.menu import input_confirm, input_option


def configure_account(config: SafaConfig) -> None:
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


def configure_existing_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Configures repository project from an existing project.
    :param config: Safa configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    client.login(config.email, config.password)

    if config.version_id is None:
        project_lookup_map = {p["name"]: p for p in client.get_projects()}
        selected_project_name = input_option(list(project_lookup_map.keys()))
        selected_project = project_lookup_map[selected_project_name]

        project_versions = client.get_project_versions(selected_project["projectId"])
        pv_options = {f"{v['majorVersion']}.{v['minorVersion']}.{v['revision']}": v for v in project_versions}
        pv_selected = input_option(list(pv_options.keys()))
        selected_version = pv_options[pv_selected]
        config.version_id = selected_version["versionId"]
    else:
        print("Current Version ID:", config.version_id)
        if input_confirm(title="Override version Id?"):
            config.version_id = None
            return configure_existing_project(config, client)
    print("Project version successfully configured.")


def run_config_tool(config: SafaConfig, client: SafaClient):
    entity_type = input_option(["account", "project", "back"])

    if entity_type == "account":
        configure_account(config)
    elif entity_type == "project":
        project_setup_type = input_option(["create_new", "select_existing"], title="How do you want to setup your project?")
        if project_setup_type == "create_new":
            create_new_project(config, client)
        elif project_setup_type == "select_existing":
            configure_existing_project(config, client)
        else:
            raise Exception("Unknown project option:" + entity_type)
    elif entity_type == "done":
        return
    else:
        raise Exception(f"Invalid entity type: {entity_type}")

    config.to_env()
    print("Configure Updated.")
    return run_config_tool(config, client)
