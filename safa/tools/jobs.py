from safa.api.safa_client import SafaClient
from safa.config.safa_config import SafaConfig
from safa.utils.dates import format_timestamp
from safa.utils.menus.page_menu import input_menu_paged


def run_job_module(config: SafaConfig, client: SafaClient):
    """

    :param config:
    :param client:
    :return:
    """
    jobs = client.get_user_jobs()
    job_displays = [repr_job(j) for j in jobs]
    input_menu_paged(job_displays, many=True)


def repr_job(job_dict: dict) -> str:
    job_start = format_timestamp(job_dict['startedAt'])
    return f"{job_dict['name']}: {job_dict['status']}: {job_start}"
