from dataclasses import dataclass, field
from typing import List

from tests.infra.constants import COMMAND_TYPE, COMMENT_TYPE
from tests.infra.file_instruction import FileInstruction


@dataclass
class LiveTestState:
    instructions: List[FileInstruction]
    instruction_idx: int = 0
    current_command_idx: int = 0
    # Aux
    logs: List[str] = field(default_factory=list)

    def clear(self) -> None:
        """
        Resets state to a new state.
        :return: None
        """
        self.logs = []
        self.instruction_idx = 0
        self.current_command_idx = 0

    def process_comment(self, comment: FileInstruction) -> None:
        """
        Processes comment by logging text and incrementing next instruction number.
        :param comment: The comment to process into state.
        :return: None
        """
        assert comment.type == COMMENT_TYPE
        self.logs.append("\n" + comment.text)
        self.instruction_idx += 1

    def process_command(self, command: FileInstruction) -> None:
        """
        Logs command text, increments next instruction index, and updates command idx.
        :param command: The command to process.
        :return: None
        """
        assert command.type == COMMAND_TYPE
        self.logs.append(f"✅ {command.get_comment() if command.has_comment() else command.text}")
        self.instruction_idx += 1
        self.current_command_idx += 1

    def get_current_instruction(self) -> FileInstruction:
        """
        :return: The current statement.
        """
        if self.instruction_idx >= len(self.instructions):
            self.log(f"Reached end of user input. "
                     f"Requested more than {len(self.instructions)} instructions.")
            raise EOFError
        return self.instructions[self.instruction_idx]

    def get_next_command(self) -> FileInstruction:
        """
        Processes instructions in file until a command is reached.
        :return: The text of the next command.
        """
        instruction = self.get_current_instruction()
        if instruction.type == COMMAND_TYPE:
            self.process_command(instruction)
            return instruction
        elif instruction.type == COMMENT_TYPE:
            self.process_comment(instruction)
            return self.get_next_command()
        else:
            raise Exception(f"Unknown instruction type {instruction.type}")

    def print_logs(self) -> None:
        """
        Prints the current set of logs.
        :return: None
        """
        print("\n".join(self.logs))
        print("-" * 60)

    def log(self, msg: str) -> None:
        """
        Adds message to logs.
        :param msg: Message to log.
        :return: None
        """
        self.logs.append(msg)

    def log_exception(self, e: Exception) -> None:
        """
        Logs exception.
        :param e:  Exception to add to logs.
        :return: None
        """
        root_exception = e
        while root_exception.__cause__ is not None:
            root_exception = root_exception.__cause__  # type: ignore
        self.log(f"Root exception: {root_exception}")
