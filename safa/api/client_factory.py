import sys

from safa.api.http_client import HttpClient
from safa.api.safa_client import SafaClient
from safa.api.safa_store import SafaStore
from safa.safa_config import SafaConfig


def create_safa_client(config: SafaConfig) -> SafaClient:
    """
    Creates SAFA client pointing at safa api. Can be overridden with BASE_URL.
    :param config: SAFA account and project configuration.
    :return: Safa Client created.
    """
    base_url = config.base_url
    global_parameters = {"verify": False} if "localhost" in base_url else {}
    http_client = HttpClient(base_url, global_parameters=global_parameters)
    store = SafaStore(cache_file_path=config.cache_file_path)
    client = SafaClient(http_client=http_client, store=store)
    if config.email is None:
        print("Please configure account.")
        sys.exit(-1)
    client.login(config=config)
    print("User successfully logged in.")
    return client
