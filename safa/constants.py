LINE_LENGTH = 60
EMPTY_TREE_HEXSHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

#
# menu.py
#
GROUP_DELIMITER = "  "
#
# runner.py
#
safa_banner = (
    """
███████╗ █████╗ ███████╗ █████╗             █████╗ ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗           ██╔══██╗██║
███████╗███████║█████╗  ███████║           ███████║██║
╚════██║██╔══██║██╔══╝  ██╔══██║           ██╔══██║██║
███████║██║  ██║██║     ██║  ██║    ██╗    ██║  ██║██║
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═╝    ╚═╝  ╚═╝╚═╝                        
        Making your documentation work for you.
    """
)
usage_msg = (
    """
    SAFA could not define the real repository path. 

    There are two ways to set this path:
    1. Create safa.env file at inferred repository path
        `SAFA_REPO_PATH=...`
    2. Pass repo path as arguments to SAFA command like so:
        ```Usage: $ safa [REPO_PATH] [ENV_FILE_PATH]```
    """
)
CODE_TYPE = "Code"

#
# Config
#
CONFIG_FOLDER = ".safa"
VECTOR_STORE_FOLDER_NAME = "vector_store"
CACHE_FILE = "cache.json"
DEFAULT_BASE_URL = "https://dev.api.safa.ai"

PROJECT_ENV_FILE = "project.env"
LLM_ENV_FILE = "llm.env"
USER_ENV_FILE = "user.env"
ROOT_ENV_FILE = "root.env"

#
# Datetime
#
SAFA_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
