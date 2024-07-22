import os.path
import shutil
import sys
import uuid
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import List, Optional, Tuple
from unittest import TestCase
from unittest.mock import patch

import git
from dotenv import load_dotenv

from safa.config.safa_config import SafaConfig
from safa.runner import main
from safa.utils.fs import clean_path, read_file, write_file_content


def get_user_input():
    return input("Enter something: ")


COMMENT_KEY = "#"


@dataclass
class FileStatement:
    type: str  # either comment, command
    text: str

    def get_command(self) -> str:
        assert self.type == "command"
        end_idx = self._get_comment_idx() if self.has_comment() else len(self.text)
        command_text = self.text[:end_idx].strip()
        command_value = self._perform_variable_substitution(command_text)
        return command_value

    def get_comment(self) -> str:
        comment_idx = self._get_comment_idx()
        return self.text[comment_idx + 1:].strip()

    def has_comment(self) -> bool:
        return COMMENT_KEY in self.text

    def _get_comment_idx(self) -> int:
        self.has_comment(), f"`{self.text}` does not contain a comment."
        return self.text.find(COMMENT_KEY)

    @staticmethod
    def _perform_variable_substitution(text: str) -> str:
        if "$" in text:
            start_idx = text.find("$") + 1
            end_idx = len(text.strip())
            env_var_name = text[start_idx:end_idx]
            text = os.environ[env_var_name]
        return text


@dataclass
class TestInputFile:
    statements: List[FileStatement]

    def get_content(self) -> str:
        commands = [s.command for s in self.statements]
        return "\n".join(commands)


def read_input_statements(file_path: str) -> Tuple[List[FileStatement], str]:
    file_content = read_file(clean_path(file_path))

    statements = []
    commands = []
    for file_line in file_content.split("\n"):

        file_line = file_line.strip()
        if len(file_line) == 0:
            continue

        if file_line.startswith("#"):
            statement = FileStatement(
                type="comment",
                text=file_line
            )
        else:
            statement = FileStatement(
                type="command",
                text=file_line
            )
            commands.append(statement.get_command())
        statements.append(statement)

    return statements, "\n".join(commands)


ROOT_TEST_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_OUTPUT_DIR = os.path.join(ROOT_TEST_PATH, "test-output")

ENV_FILE_PATH = os.path.expanduser("~/projects/safa-cmd/.env")


class LiveTest:
    def __init__(self, output_path: Optional[str] = None):
        load_dotenv(ENV_FILE_PATH)
        if output_path is None:
            output_path = os.path.join(TEST_OUTPUT_DIR, str(uuid.uuid4()))
        self._clear_state()
        self.test_output_path = output_path

    def _clear_state(self):
        self.log: List[str] = []
        self.current_line = 0
        self.current_command = 0

    def run_test(self, tc: TestCase, input_file_path: str):
        self._clear_state()
        self.log.append(f"Starting test: {input_file_path}")
        statements, user_input = read_input_statements(input_file_path)
        sys.stdin = StringIO(user_input)
        #
        # Create args to test
        #
        sys.argv = ["main", '-r', self.test_output_path]

        custom_input_handler = self.create_mock_input_handler(statements)
        captured_output = StringIO()

        try:
            with (
                redirect_stdout(captured_output),
                patch('getpass.getpass', custom_input_handler),
                patch('builtins.input', custom_input_handler)
            ):
                main()

        except Exception as e:
            self.log.append(captured_output.getvalue())
            failing_statement = statements[self.current_line]
            error_msg = f"  ❌ {failing_statement.text}"
            self.log.append(error_msg)
            root_exception = e
            while root_exception.__cause__ is not None:
                root_exception = root_exception.__cause__
            self.log.append(f"Root exception: {root_exception}")

            tc.fail(error_msg)
        finally:
            self._print_logs()

    def create_mock_input_handler(self, statements):
        def custom_input(prompt=''):
            try:
                statement = statements[self.current_line]
                if statement.type == "comment":
                    self.log.append("\n" + statement.text)
                    self.current_line += 1
                    return custom_input(prompt=prompt)
                elif statement.type == "command":
                    # Previous line log
                    command = statement.get_command()
                    self.log.append(f"✅ {statement.get_comment() if statement.has_comment() else statement.text}")
                    self.current_line += 1
                    self.current_command += 1
                    print(prompt + " " + command)
                    return command
                else:
                    raise Exception(f"Expected type `{statement.type}`")
            except IndexError:
                self.log.append("Reached end of input lines")
                raise EOFError

        return custom_input

    def cleanup(self):
        # Delete the test folder
        if os.path.exists(self.test_output_path):
            shutil.rmtree(self.test_output_path)
            shutil.rmtree(TEST_OUTPUT_DIR)

    def get_safa_config(self):
        return SafaConfig.from_repo(self.test_output_path)

    def setup_git_repository(self, repo_path: Optional[str] = None):
        # Create test output folder
        self.cleanup()
        os.makedirs(self.test_output_path, exist_ok=True)

        # Create new git repository
        repo = git.Repo.init(self.test_output_path)

        new_file_path = os.path.join(self.test_output_path, "test.txt")
        write_file_content(new_file_path, "Hello World!")

        # Stage the new file
        repo.index.add([new_file_path])

        # Commit the new file
        repo.index.commit('Initial commit of test file')

    def _print_logs(self):
        print("\n".join(self.log))
        print("-" * 60)
