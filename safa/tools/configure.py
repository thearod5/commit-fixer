from getpass import getpass

from safa.safa_config import SafaConfig
from safa.utils.menu import input_confirm


def run_configure_account(config: SafaConfig) -> None:
    """
    Configures account email and password.
    :param config: Configuration used to set account details in.
    :param client: Client used to access SAFA API.
    :return:None
    """
    if config.has_account():
        if input_confirm(f"Would you like to override your current account ({config.email})?", default_value="n"):
            config.clear_account()
            return run_configure_account(config)
        return

    email = input("Safa Account Email:")
    password = getpass("Safa Account Password:")
    config.set_account(email, password)
