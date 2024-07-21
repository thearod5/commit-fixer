import os
from typing import Generic, List, Type, TypeVar

from safa.utils.fs import write_file_content

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

        construction_dict = {}
        for obj_property in obj_properties:
            if obj_property in kwargs:
                continue
            elif hasattr(obj, obj_property):
                construction_dict[obj_property] = getattr(obj, obj_property)
            else:
                obj_property_env_name = ConfigFactory.prop_to_env(obj_property)
                construction_dict[obj_property] = os.environ.get(obj_property_env_name, None)
        obj_instance = obj(**construction_dict, **kwargs)
        return obj_instance

    @staticmethod
    def prop_to_env(property_name: str) -> str:
        """
        Converts property to env variable name.
        :param property_name: property to convert.
        :return: Name of environment variable used to fill in value.
        """
        return f"SAFA_{property_name.upper()}"

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
