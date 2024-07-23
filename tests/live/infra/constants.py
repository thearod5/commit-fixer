import os

#
# Paths
#
ROOT_TEST_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
TEST_OUTPUT_DIR = os.path.join(ROOT_TEST_PATH, "test-output")
ENV_FILE_PATH = os.path.dirname(ROOT_TEST_PATH) + "/.env"
#
# KEYS
#
COMMENT_SYM = "#"
COMMENT_TYPE = "comment"
COMMAND_TYPE = "command"
VAR_SYM = "$"
