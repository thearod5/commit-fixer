from safa.api.constants import STORE_PROJECT_KEY
from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.search import create_vector_store
from safa.utils.menus.printers import print_title


def refresh_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Refresh project data.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    print_title("Refreshing Project Data")
    version_id = config.get_version_id()
    client.store.delete(STORE_PROJECT_KEY, version_id)
    project_data = client.get_version(version_id)
    project_artifacts = project_data["artifacts"]
    db = create_vector_store(project_data["artifacts"], vector_store_path=config.vector_store_path)
