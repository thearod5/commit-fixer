from typing import Callable, Dict, Tuple, Union

from langchain_anthropic import ChatAnthropic

from safa.config.llm_config import LLMConfig

MessageType = Tuple[str, str]

LLMManager = Union[ChatAnthropic]
DEFAULT_LLM_MANAGER = "anthropic"

ALLOWED_MANAGERS: Dict[str, Callable[[str], ChatAnthropic]] = {
    "anthropic": lambda k: ChatAnthropic(api_key=k, model_name='claude-3-sonnet-20240229', max_tokens=4096)  # type: ignore
}


def get_llm_manager(llm_config: LLMConfig) -> ChatAnthropic:
    """
    Reads LLM manager from env variables.
    :return: LLM Manager
    """
    llm_manager = ALLOWED_MANAGERS[llm_config.llm_provider](llm_config.llm_key)
    return llm_manager
