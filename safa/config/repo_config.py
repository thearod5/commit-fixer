from dataclasses import dataclass
from typing import List

from safa.config.base_config import BaseConfig
from safa.constants import DEFAULT_BASE_URL, ROOT_ENV_FILE


@dataclass(repr=False)
class RepoConfig(BaseConfig):
    """
    :param repo_path: Path to repository root.
    :param base_url: Base URL for SAFA API to use.
    """
    repo_path: str
    base_url: str = DEFAULT_BASE_URL

    @staticmethod
    def get_file_name() -> str:
        return ROOT_ENV_FILE

    @staticmethod
    def get_display_properties() -> List[str]:
        return ["repo_path", "base_url"]
