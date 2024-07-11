import os
from typing import Callable, Dict, Tuple, Union

from langchain_anthropic import ChatAnthropic

MessageType = Tuple[str, str]

LLMManager = Union[ChatAnthropic]

ALLOWED_MANAGERS: Dict[str, Callable[[str], ChatAnthropic]] = {
    "anthropic": lambda k: ChatAnthropic(api_key=k, model_name='claude-3-sonnet-20240229', max_tokens=4096)  # type: ignore
}


def get_llm_manager() -> ChatAnthropic:
    """
    Reads LLM manager from env variables.
    :return: LLM Manager
    """
    llm_manager_type = os.environ["LLM_MANAGER"]
    assert llm_manager_type in ALLOWED_MANAGERS, f"Unrecognized manager `{llm_manager_type}`"
    llm_key = os.environ["LLM_KEY"]

    # Initialize the LLM providers
    llm_manager = ALLOWED_MANAGERS[llm_manager_type](llm_key)
    return llm_manager
