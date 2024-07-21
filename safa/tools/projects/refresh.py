import os.path
import shutil

from safa.api.constants import STORE_PROJECT_KEY
from safa.api.safa_client import SafaClient
from safa.config.safa_config import SafaConfig
from safa.tools.search import create_vector_store
from safa.utils.menus.printers import print_title


def refresh_project(config: SafaConfig, client: SafaClient, force: bool = False) -> None:
    """
    Refresh project data.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    print_title("Refreshing Project Data")
    version_id = config.project_config.get_version_id()

    client.store.delete(STORE_PROJECT_KEY, version_id)
    project_data = client.get_version(version_id)
    project_artifacts = project_data["artifacts"]
    vector_store_path = config.get_vector_store_path()
    if os.path.isdir(vector_store_path):
        shutil.rmtree(vector_store_path)
    create_vector_store(project_artifacts, vector_store_path=vector_store_path)
