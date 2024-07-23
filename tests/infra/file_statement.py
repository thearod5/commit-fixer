import os.path
from dataclasses import dataclass

from tests.infra.constants import COMMAND_TYPE, COMMENT_SYM, ENV_VAR_KEY


@dataclass
class FileInstruction:
    type: str  # either comment, command
    text: str

    def get_command(self) -> str:
        assert self.type == COMMAND_TYPE
        end_idx = self._get_comment_idx() if self.has_comment() else len(self.text)
        command_text = self.text[:end_idx].strip()
        command_value = self._perform_variable_substitution(command_text)
        return command_value

    def get_comment(self) -> str:
        comment_idx = self._get_comment_idx()
        return self.text[comment_idx + 1:].strip()

    def has_comment(self) -> bool:
        return COMMENT_SYM in self.text

    def _get_comment_idx(self) -> int:
        self.has_comment(), f"`{self.text}` does not contain a comment."
        return self.text.find(COMMENT_SYM)

    @staticmethod
    def _perform_variable_substitution(text: str) -> str:
        if ENV_VAR_KEY in text:
            start_idx = text.find(ENV_VAR_KEY) + 1
            end_idx = len(text.strip())
            env_var_name = text[start_idx:end_idx]
            text = os.environ[env_var_name]
        return text
