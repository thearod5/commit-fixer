import json

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.utils.menus.page_menu import input_menu_paged


def run_job_module(config: SafaConfig, client: SafaClient):
    """

    :param config:
    :param client:
    :return:
    """
    jobs = client.get_user_jobs()
    job_displays = [json.dumps(j, indent=1) for j in jobs]
    input_menu_paged(job_displays, many=True)
