from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig


def run_create_project(config: SafaConfig, client: SafaClient):
    """
    Prompts user to create new project.
    :param config: Safa configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    project_name = input("Project Name:")
    project_description = input("Project Description:")

    project_data = client.create_project(project_name, project_description)
    project_id = project_data["projectId"]
    version_id = project_data["projectVersion"]["versionId"]

    config.set_project_commit(project_id, version_id, None)
