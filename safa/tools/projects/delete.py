from safa.api.safa_client import SafaClient
from safa.config.safa_config import SafaConfig


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
    project_id = input("project id to delete:")
    client.delete_project(project_id)
    if project_id == config.project_config.project_id:
        config.project_config.clear_project()
    print("Project Deleted:", project_id)
