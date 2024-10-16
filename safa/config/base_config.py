import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Type, TypeVar

from safa.config.factory import ConfigFactory

ConfigType = TypeVar("ConfigType", bound="BaseConfig")


@dataclass(repr=False)
class BaseConfig(Generic[ConfigType], ABC):
    config_dir_path: str

    @staticmethod
    @abstractmethod
    def get_file_name() -> str:
        """
        Defines abstract property for the name of file containing env properties.
        :return: The name of the file containing env properties.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_display_properties() -> List[str]:
        """
        Defines abstract property for the name of file containing env properties.
        :return: The name of the file containing env properties.
        """
        pass

    def __repr__(self) -> str:
        """
        Uses display properties to represent config.
        :return: String representation of config.
        """
        return ConfigFactory.repr(self, self.get_display_properties())

    def save(self) -> None:
        """
        Extracts properties from config and writes them as ENV file.
        :param env_file_path: Path to save env file.
        :return: None
        """
        ConfigFactory.save(self, self.get_file_path())

    def is_configured(self) -> bool:
        """
        :return: Whether config has values for all properties.
        """
        config_properties = ConfigFactory.get_config_properties(self)
        return all([getattr(self, p) is not None for p in config_properties])

    def get_file_path(self) -> str:
        """
        :return: Returns path to config file.
        """
        return os.path.join(self.config_dir_path, self.get_file_name())

    @classmethod
    def create(cls: Type[ConfigType], config_dir_path: str, **kwargs) -> ConfigType:
        """
        Creates configuration class using env to fill in default values.
        :param config_dir_path: Path to configuration directory.
        :return: Constructed instance of class.
        """
        config_path = os.path.join(config_dir_path, cls.get_file_name())
        config_vars = ConfigFactory.read_env_file(config_path) if os.path.isfile(config_path) else {}
        return ConfigFactory.create(cls, config_dir_path=config_dir_path, **config_vars, **kwargs)
