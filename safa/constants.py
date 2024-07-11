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
                  https://safa.ai
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
