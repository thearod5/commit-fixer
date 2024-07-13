from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.utils.menus.inputs import input_confirm
from safa.utils.menus.page_menu import input_menu_paged


def delete_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Deletes safa project.
    :param config: Safa account and project configuration.
    :param client: Client used to delete project.
    :return: None
    """
    projects = client.get_projects()
    if len(projects) == 0:
        print("User has no projects.")
        return
    project_lookup_map = {p["name"]: p for p in projects}
    project_keys = list(project_lookup_map.keys())
    project_name = input_menu_paged(project_keys)
    selected_project = project_lookup_map[project_name]
    if not input_confirm(f"Are you sure you want to delete project ({project_name})?", default_value="y"):
        return
    project_id = selected_project['projectId']
    client.delete_project(selected_project['projectId'])
    if project_id == config.project_id:
        config.clear_project()
    print("Project Deleted:", selected_project["name"])
