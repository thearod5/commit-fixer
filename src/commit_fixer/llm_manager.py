import os
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_community.llms import OpenAI
from langchain_core.messages import BaseMessage

MessageType = Tuple[str, str]


class LLMManager(ABC):
    @abstractmethod
    def invoke(self, messages: List[MessageType]) -> BaseMessage:
        pass


ALLOWED_MANAGERS: Dict[str, Callable[[str], LLMManager]] = {
    "anthropic": lambda k: ChatAnthropic(anthropic_api_key=k, model_name='claude-3-sonnet-20240229'),
    "openai": lambda k: OpenAI(openai_api_key=k)
}


def get_llm_manager() -> LLMManager:
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
