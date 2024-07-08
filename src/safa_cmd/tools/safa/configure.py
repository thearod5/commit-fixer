import getpass
import os
from getpass import getpass
from typing import Dict

from safa_sdk.safa_client import SafaClient

from safa_cmd.config import SafaConfig
from safa_cmd.utils.menu import input_option


def configure_account(config: SafaConfig):
    if config.email is None:
        config.email = input("Safa Account Email:")
    else:
        print(f"Safa Account: {config.email}")
    if config.password is None:
        config.password = getpass("Safa Account Password:")
    else:
        print("Safa account password is set.")


def configure_project(config: SafaConfig):
    client = SafaClient()
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


def run_config_tool(config: SafaConfig):
    entity_type = input_option(["account", "project", "back"])

    if entity_type == "account":
        configure_account(config)
    elif entity_type == "project":
        configure_project(config)
    elif entity_type == "done":
        return
    else:
        raise Exception(f"Invalid entity type: {entity_type}")

    config.to_env()
    print("Configure Updated.")
    return run_config_tool(config)


def create_env(file_path: str, var2val: Dict):
    items = []
    for k, v in var2val.items():
        items.append(f"{k}={v}")

    content = "\n".join(items)
    write_file(file_path, content)


def get_or_prompt(key_id: str, prompt: str, is_password: bool = False):
    if key_id in os.environ:
        return os.environ[key_id]
    input_callable = input if is_password else getpass.getpass
    return input_callable(f"{prompt}:")
