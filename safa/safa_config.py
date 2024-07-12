import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from dotenv import load_dotenv

from safa.utils.fs import clean_path, write_file_content

CONFIG_FOLDER = ".safa"
ENV_FILE = ".env"
CHROMA_FOLDER = "vector_store"
CACHE_FILE = ".cache"
DEFAULT_BASE_URL = "https://dev.api.safa.ai"


@dataclass
class SafaConfig:
    """
    :param repo_path: Path to the repository being targeted.
    :param email: Email of SAFA account to use.
    :param password: Password of associated SAFA account.
    :param version_id: Version ID of SAFA project to interact with.
    :param cache_file_path: Path to file used to store database results (e.g. project data)
    """
    repo_path: str
    # config specific
    config_path: str
    env_file_path: str
    vector_store_path: str
    cache_file_path: str
    # Account Settings
    email: Optional[str]
    password: Optional[str]
    # Project Settings
    project_id: Optional[str]
    version_id: Optional[str]
    commit_id: Optional[str]
    # Property references
    env_properties = ["repo_path", "email", "password", "project_id", "version_id", "commit_id"]
    repr_properties = ["repo_path", "email", "project_id", "version_id", "commit_id"]
    is_configured_paths = ["env_file_path", "cache_file_path"]
    is_configured_properties = ["repo_path", "email", "password", "project_id", "version_id", "commit_id"]
    # Root
    base_url: str = DEFAULT_BASE_URL

    def __repr__(self) -> str:
        """
        :return: string representation of the configuration.
        """
        config_items = {k.replace("_", " ").title(): getattr(self, k) for k in self.repr_properties}
        item_display = [f"{k}={v}" for k, v in config_items.items()]
        return "\n".join(item_display)

    def clear_account(self) -> None:
        """
        Removes account settings details and saves configuration.
        :return: None
        """
        self.set_account(None, None)
        self.__to_env()

    def clear_project(self) -> None:
        """
        Removes project settings details and saves configuration.
        :return: None
        """
        self.set_project_commit(None, None, None)
        self.__to_env()

    def set_account(self, email: Optional[str], password: Optional[str]):
        """
        Sets default account.
        :param email: SAFA account email.
        :param password: SAFA account password
        :return: None
        """
        self.email = email
        self.password = password
        self.__to_env()

    def set_project_commit(self, project_id: Optional[str], version_id: Optional[str], commit_id: Optional[str]):
        """
        Sets default project in configuration.
        :param project_id: ID of project.
        :param version_id: ID of project version.
        :param commit_id: Commit hexsha associated with project version.
        :return: None
        """
        self.project_id = project_id
        self.version_id = version_id
        self.commit_id = commit_id
        self.__to_env()
        print(f"New project has been set: https://app.safa.ai/versions/{self.version_id}")

    def is_configured(self) -> bool:
        """
        Whether all necessary SAFA variables are configured.
        :return: Whether config contains necessary information.
        """
        paths_configured = all([os.path.exists(getattr(self, p)) for p in self.is_configured_paths])
        properties_configured = all([getattr(self, p) is not None for p in self.is_configured_properties])
        return paths_configured and properties_configured

    def get_version_id(self) -> str:
        """
        Returns version id if exists, otherwise error is thrown.
        :return: Configured version ID.
        """
        if self.version_id:
            return self.version_id
        raise Exception("Project version is not configured.")

    def has_project(self) -> bool:
        """
        :return: Returns whether version ID is configured.
        """
        return self.project_id is not None and self.version_id is not None

    def has_account(self) -> bool:
        """
        :return: Whether configuration has account details.
        """
        return self.email is not None and self.password is not None

    def has_commit_id(self) -> bool:
        """
        :return: Whether commit is configured
        """
        return self.commit_id is not None

    def get_commit_id(self) -> str:
        """
        :return: Returns commit
        """
        assert self.commit_id is not None, "use `has_commit_id` before retrieving commit"
        return self.commit_id

    def get_project_config(self) -> Tuple[str, str]:
        """
        :return: Returns project details.
        """
        if self.project_id is None or self.version_id is None:
            raise Exception("One of project_id, version_id, or commit_id is None.")
        return self.project_id, self.version_id

    def get_configured_entities(self) -> List[str]:
        """
        Returns entities configured.
        :return: List of entities.
        """
        permissions = []
        if self.has_account():
            permissions.append("user")
        if self.has_project():
            permissions.append("project")
        return permissions

    def __to_env(self):
        """
        Converts config to env file.
        :return: None
        """
        property2value = {k: getattr(self, k) for k in self.env_properties}
        env_line_items = [
            f"SAFA_{k.upper()}={getattr(self, k)}"
            for k, v in property2value.items() if v is not None
        ]
        env_content = "\n".join(env_line_items)
        write_file_content(self.env_file_path, env_content)
        print(f"Configuration file written to {self.env_file_path}")

    @staticmethod
    def from_repo(repo_path: str, root_env_file_path: Optional[str] = None) -> "SafaConfig":
        """
        Creates configuration from repo.
        :param repo_path: Path to repo.
        :param root_env_file_path: Additional env file to include.
        :return: Config with loaded variables if they exist.
        """
        # User Setting
        repo_path = clean_path(repo_path)
        repo_path = os.environ.get("SAFA_REPO_PATH", repo_path)

        # Config-Relative paths
        config_path = os.path.join(repo_path, CONFIG_FOLDER)
        env_file_path = os.path.join(config_path, ENV_FILE)
        vector_store_path = os.path.join(config_path, CHROMA_FOLDER)
        cache_file_path = os.path.join(config_path, CACHE_FILE)

        if os.path.exists(env_file_path):
            load_dotenv(env_file_path)
        if root_env_file_path is None:
            root_env_file_path = os.path.join(repo_path, ENV_FILE)
        load_dotenv(root_env_file_path)

        return SafaConfig(
            repo_path=repo_path,
            # Config paths
            config_path=config_path,
            env_file_path=env_file_path,
            cache_file_path=cache_file_path,
            vector_store_path=vector_store_path,
            # User Paths
            email=os.environ.get("SAFA_EMAIL"),
            password=os.environ.get("SAFA_PASSWORD"),
            project_id=os.environ.get("SAFA_PROJECT_ID"),
            version_id=os.environ.get("SAFA_VERSION_ID"),
            commit_id=os.environ.get("SAFA_COMMIT_ID"),
            base_url=os.environ.get("SAFA_BASE_URL", DEFAULT_BASE_URL)
        )
