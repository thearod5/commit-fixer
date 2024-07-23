import os
from typing import List, Tuple

from safa.utils.fs import clean_path, read_file
from tests.infra.constants import COMMAND_TYPE, COMMENT_SYM, COMMENT_TYPE
from tests.infra.file_instruction import FileInstruction


def parse_input_file(file_path: str, **kwargs) -> Tuple[List[FileInstruction], str]:
    """
    Parses instructions in file.
    :param file_path: Path to file containing test instructions to parse.
    :param kwargs: Additional parameters used to complete test instructions.
    :return: Statements and list of commands to mock user input.
    """
    instruction_vars = {**{k: v for k, v in os.environ.items()}, **kwargs}
    file_content = read_file(clean_path(file_path))

    statements = []
    commands = []
    for file_line in file_content.split("\n"):

        file_line = file_line.strip()
        if len(file_line) == 0:
            continue

        if file_line.startswith(COMMENT_SYM):
            statement = FileInstruction(
                type=COMMENT_TYPE,
                text=file_line
            )
        else:
            statement = FileInstruction(
                type=COMMAND_TYPE,
                text=file_line,
                variables=instruction_vars
            )
            commands.append(statement.get_command_value())
        statements.append(statement)

    return statements, "\n".join(commands)
