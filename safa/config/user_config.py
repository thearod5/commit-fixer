from dataclasses import dataclass
from typing import List, Optional

from safa.config.base_config import BaseConfig
from safa.constants import USER_ENV_FILE


@dataclass(repr=False)
class UserConfig(BaseConfig):
    """
    :param email: SAFA account email.
    :param password: SAFA account password.
    """

    email: Optional[str]
    password: Optional[str]

    @staticmethod
    def get_file_name() -> str:
        return USER_ENV_FILE

    @staticmethod
    def get_display_properties() -> List[str]:
        return ["email"]

    def has_account(self) -> bool:
        """
        :return: Whether configuration has account details.
        """
        return self.email is not None and self.password is not None

    def set_account(self, email: Optional[str], password: Optional[str]):
        """
        Sets default account.
        :param email: SAFA account email.
        :param password: SAFA account password
        :return: None
        """
        self.email = email
        self.password = password
        self.save()

    def clear_account(self) -> None:
        """
        Removes account settings details and saves configuration.
        :return: None
        """
        self.set_account(None, None)
        self.save()
