import os
from dataclasses import dataclass
from typing import List, Optional, cast

from dotenv import load_dotenv

from safa.config.base_config import BaseConfig
from safa.config.llm_config import LLMConfig
from safa.config.project_config import ProjectConfig
from safa.config.repo_config import RepoConfig
from safa.config.user_config import UserConfig
from safa.constants import CACHE_FILE, CONFIG_FOLDER, VECTOR_STORE_FOLDER_NAME


@dataclass(repr=False)
class SafaConfig:
    repo_config: RepoConfig
    user_config: UserConfig
    project_config: ProjectConfig
    llm_config: LLMConfig
    config_dir_path: str
    _registered_configs = ["repo_config", "user_config", "project_config", "llm_config"]

    def __repr__(self) -> str:
        """
        :return: string representation of the configuration.
        """
        config_reprs = [repr(getattr(self, p)) for p in self._registered_configs]
        return "\n\n".join(config_reprs)

    def save(self):
        """
        Converts config to env file.
        :return: None
        """
        for config_name in self._registered_configs:
            config = getattr(self, config_name)
            config.save()
        print("Safa configuration has been saved.")

    def is_configured(self) -> bool:
        """
        Whether all necessary SAFA variables are configured.
        :return: Whether config contains necessary information.
        """
        paths_configured = all([getattr(self, p).is_configured() for p in self._registered_configs])
        return paths_configured

    def get_configured_entities(self) -> List[str]:
        """
        Returns entities configured.
        :return: List of entities.
        """
        permissions = []
        if self.user_config.has_account():
            permissions.append("user")
        if self.project_config.is_configured():
            permissions.append("project")
        return permissions

    def get_vector_store_path(self) -> str:
        """
        :return: Returns path to vector store.
        """
        return os.path.join(self.config_dir_path, VECTOR_STORE_FOLDER_NAME)

    def get_cache_file_path(self) -> str:
        """
        :return: Returns path to config cache file.
        """
        return os.path.join(self.config_dir_path, CACHE_FILE)

    def get_config(self, config_name: str) -> BaseConfig:
        """
        Retrieves child-config by name.
        :param config_name: The name of the configuration.
        :return: Config.
        """
        if not hasattr(self, config_name):
            raise Exception(f"Config `{config_name}` does not exist.")
        return cast(BaseConfig, getattr(self, config_name))

    @staticmethod
    def from_repo(repo_path: str, root_env_file_path: Optional[str] = None) -> "SafaConfig":
        """
        Creates configuration from repo.
        :param repo_path: Path to repo.
        :param root_env_file_path: Additional env file to include.
        :return: Config with loaded variables if they exist.
        """
        config_path = os.path.join(repo_path, CONFIG_FOLDER)
        if root_env_file_path is not None:
            load_dotenv(root_env_file_path)
        if not os.path.isdir(config_path):
            os.makedirs(config_path, exist_ok=True)
        repo_config: RepoConfig = RepoConfig.create(config_path, repo_path=repo_path)
        user_config = UserConfig.create(config_path)
        project_config = ProjectConfig.create(config_path)
        llm_config = LLMConfig.create(config_path)

        return SafaConfig(
            repo_config=repo_config,
            user_config=user_config,
            project_config=project_config,
            llm_config=llm_config,
            config_dir_path=config_path,
        )
