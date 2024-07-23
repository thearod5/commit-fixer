import sys
from contextlib import redirect_stdout
from io import StringIO
from typing import Optional
from unittest import TestCase
from unittest.mock import patch

from dotenv import load_dotenv

from safa.runner import main
from tests.infra.constants import ENV_FILE_PATH
from tests.infra.live_test_state import LiveTestState
from tests.infra.parse import parse_input_file


class LiveTestController:
    def __init__(self, repo_path: str, env_file_path: Optional[str] = None):
        """
        Creates new live test controller.
        :param repo_path: Path to repository to run test on.
        :param env_file_path: Path to env files to load configuration with.
        """
        self.repo_path = repo_path
        self.env_file_path = env_file_path or ENV_FILE_PATH

    def run_test(self, tc: TestCase, instruction_file_path: str, **kwargs) -> None:
        """
        Runs live test with commands in input file.
        :param tc: Test case used to make assertions.
        :param instruction_file_path: Path to file containing instructions to run test with.
        :param **Kwargs: variables used during test instructions
        :return: None
        """
        load_dotenv(self.env_file_path)
        instructions, user_input = parse_input_file(instruction_file_path, **kwargs)

        captured_output = StringIO()  # capture program output
        sys.stdin = StringIO(user_input)  # hijack user input with file commands

        state = LiveTestState(instructions)
        test_success = False

        def input_handler(p: str = ""):
            command = state.get_next_command()
            print(p + " " + command.text)
            return command.get_command_value()

        try:
            with (
                redirect_stdout(captured_output),
                patch('getpass.getpass', input_handler),
                patch('builtins.input', input_handler)
            ):
                state.log(f"# Starting Test\nInstructions: {instruction_file_path}\nRepo: {self.repo_path}")
                sys.argv = ["main", '-r', self.repo_path]
                main()
                test_success = True
        except Exception as e:
            state.log(f"❌ {state.get_current_instruction().text}")
            state.log_exception(e)
        finally:
            state.log(captured_output.getvalue())
            state.print_logs()
            if not test_success:
                tc.fail(f"{instruction_file_path} failed.")
