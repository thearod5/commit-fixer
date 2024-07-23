from dataclasses import dataclass, field
from typing import Dict

from tests.infra.constants import COMMAND_TYPE, COMMENT_SYM, VAR_SYM


@dataclass
class FileInstruction:
    type: str  # either comment, command
    text: str
    variables: Dict[str, str] = field(default_factory=dict)

    def get_command_id(self) -> str:
        assert self.type == COMMAND_TYPE
        end_idx = self._get_comment_idx() if self.has_comment() else len(self.text)
        command_text = self.text[:end_idx].strip()
        return command_text

    def get_command_value(self) -> str:
        command_id = self.get_command_id()
        command_value = self._perform_variable_substitution(command_id, self.variables)
        return command_value

    def get_comment(self) -> str:
        comment_idx = self._get_comment_idx()
        return self.text[comment_idx + 1:].strip()

    def has_comment(self) -> bool:
        return COMMENT_SYM in self.text

    def _get_comment_idx(self) -> int:
        self.has_comment(), f"`{self.text}` does not contain a comment."
        return self.text.find(COMMENT_SYM)

    @classmethod
    def _perform_variable_substitution(cls, text: str, variables: Dict) -> str:
        var_name = None
        if VAR_SYM in text:
            var_name = cls._get_symbol_text(text, VAR_SYM)
        text = variables[var_name] if var_name else text
        return text

    @staticmethod
    def _get_symbol_text(text: str, sym: str) -> str:
        """
        Extracts the text after the symbol.
        :param text: Text containing symbol and target text.
        :param sym: The symbol to find in text.
        :return: Text after symbol.
        """
        start_idx = text.find(sym) + 1
        end_idx = len(text.strip())
        env_var_name = text[start_idx:end_idx]
        return env_var_name
