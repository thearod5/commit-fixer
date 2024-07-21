from dataclasses import dataclass
from typing import List

from safa.config.base_config import BaseConfig
from safa.constants import LLM_ENV_FILE


@dataclass(repr=False)
class LLMConfig(BaseConfig):
    """
    :param llm_provider: Currently only supporting anthropic.
    :param llm_key: Key to LLM provider.
    """
    llm_key: str
    llm_provider: str = "anthropic"

    @staticmethod
    def get_file_name() -> str:
        return LLM_ENV_FILE

    @staticmethod
    def get_display_properties() -> List[str]:
        return ["llm_provider"]

    def set_key(self, llm_key: str) -> None:
        """
        Sets the LLM key and saves config.
        :param llm_key: Key to LLM provider.
        :return: None
        """
        self.llm_key = llm_key
        self.save()
