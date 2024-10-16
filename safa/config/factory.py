import os
from typing import Dict, Generic, List, Type, TypeVar

from safa.utils.fs import read_file, write_file_content

ConfigType = TypeVar("ConfigType")


class ConfigFactory(Generic[ConfigType]):
    @staticmethod
    def save(config: ConfigType, env_file_path: str) -> None:
        """
        Extracts properties from config and writes them as ENV file.
        :param config: The config to extract properties from.
        :param env_file_path: Path to save env file.
        :return: None
        """
        obj_properties = ConfigFactory.get_config_properties(config)
        property2value = {k: getattr(config, k) for k in obj_properties}
        env_line_items = [
            f"{ConfigFactory.prop_to_env(k)}={getattr(config, k)}"
            for k, v in property2value.items() if v is not None
        ]
        if len(env_line_items) == 0:
            return
        env_content = "\n".join(env_line_items)
        write_file_content(env_file_path, env_content)

    @staticmethod
    def create(obj: Type[ConfigType], **kwargs) -> ConfigType:
        """
        Creates configuration class using env to fill in default values.
        :param obj: The configuration object.
        :return: Constructed instance of class.
        """
        obj_properties = ConfigFactory.get_config_properties(obj)

        construction_dict = {**kwargs}
        for obj_property in obj_properties:
            env_prop_name = ConfigFactory.prop_to_env(obj_property)
            if obj_property in kwargs:
                continue
            elif env_prop_name in os.environ:
                construction_dict[obj_property] = os.environ[env_prop_name]
            elif hasattr(obj, obj_property):
                construction_dict[obj_property] = getattr(obj, obj_property)
            else:
                construction_dict[obj_property] = None
        obj_instance = obj(**construction_dict)
        return obj_instance

    @staticmethod
    def read_env_file(file_path: str) -> Dict[str, str]:
        """
        Reads env file and returns map of config property name to values.
        :return: Map of property names to their values for config construction.
        """
        file_content = read_file(file_path)
        file_lines = [line for line in file_content.splitlines() if len(line.strip()) > 0]
        file_line_splits = [line.split("=") for line in file_lines]
        file_vars = {ConfigFactory.env_to_prop(split[0].strip()): split[1].strip() for split in file_line_splits}
        return file_vars

    @staticmethod
    def prop_to_env(property_name: str) -> str:
        """
        Converts property to env variable name.
        :param property_name: property to convert.
        :return: Name of environment variable used to fill in value.
        """
        return f"SAFA_{property_name.upper()}"

    @staticmethod
    def env_to_prop(env_name: str):
        """
        Converts ENV variable to property name.
        :param env_name: Name of environment variable.
        :return: Config property name.
        """
        return env_name.replace("SAFA_", "").lower()

    @staticmethod
    def get_config_properties(obj: ConfigType) -> List[str]:
        obj_properties = list(obj.__annotations__.keys())
        return obj_properties

    @staticmethod
    def repr(config: ConfigType, obj_properties: List[str]) -> str:
        """
        Represents config as newline delimited set of key-pair values.
        :param config: The configuration to represent.
        :param obj_properties: List of properties to use in representation of config.
        :return: String containing key-pair values.
        """
        config_items = {k.replace("_", " ").title(): getattr(config, k) for k in obj_properties}
        item_display = [f"{k}={v}" for k, v in config_items.items()]
        class_name = str(config.__class__.__name__)
        return class_name + "\n---\n" + "\n".join(item_display)
