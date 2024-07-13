from typing import Dict, Tuple

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.utils.menus.page_menu import input_menu_paged
from safa.utils.menus.printers import version_repr


def run_select_project(config: SafaConfig, client: SafaClient) -> Tuple[str, str]:
    """
    Prompts user to select project, version, and commit.
    :param config: Safa account and project configuration.
    :param client: Client used to access SAFA api.
    :return: project id, version id, and commit id selected by user.
    """
    name2project = list_projects(config, client, print_projects=False)

    # Select Project
    selected_name = input_menu_paged(list(name2project.keys()), title="Select Project", many=False)
    selected_project = name2project[selected_name]
    project_id = selected_project["projectId"]

    # Select project version
    project_versions = client.get_project_versions(project_id)
    name2versions = {version_repr(v): v for v in project_versions}
    selected_version_name = input_menu_paged(list(name2versions.keys()), title="Select Project Version")
    selected_version = name2versions[selected_version_name]
    version_id = selected_version["versionId"]

    config.set_project(project_id, version_id)

    return project_id, version_id


def list_projects(config: SafaConfig, client: SafaClient, print_projects: bool = True) -> Dict[str, Dict]:
    """
    Lists SAFA projects accessible to user.
    :param config: Safa account and project configuration.
    :param client: The client used to retrieve projects.
    :param print_projects: Whether to print projects.
    :return: None
    """
    projects = client.get_projects()
    project_lookup_map = {p["name"]: p for p in projects}
    project_names = list(project_lookup_map.keys())
    if print_projects:
        input_menu_paged(project_names, many=True, finish_selection_title="Finish Viewing")
    return project_lookup_map
