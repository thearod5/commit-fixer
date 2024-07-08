from safa_sdk.safa_client import Safa
from safa_sdk.safa_store import SafaStore

from safa_cmd.config import SafaConfig


def create_client(config: SafaConfig) -> Safa:
    """
    Reads SAFA project.
    :param config: Configuration detailing account details and project.
    :return: The project data.
    """
    print("...retrieving safa project...")
    client_store = SafaStore(config.cache_file_path)
    client = Safa(client_store)
    client.login(config.email, config.password)
