import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from dotenv import load_dotenv

from safa.utils.fs import clean_path, write_file_content

CONFIG_FOLDER = ".safa"
PROJECT_ENV_FILE = "project.env"
USER_ENV_FILE = "user.env"
ROOT_ENV_FILE = "root.env"
CHROMA_FOLDER = "vector_store"
CACHE_FILE = "cache.json"
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
    # llm
    llm_key: str
    # config specific
    config_path: str
    vector_store_path: str
    cache_file_path: str
    # -- env files
    root_env_file_path: str
    user_env_file_path: str
    project_env_file_path: str
    # Account Settings
    email: Optional[str]
    password: Optional[str]
    # Project Settings
    project_id: Optional[str]
    version_id: Optional[str]
    commit_id: Optional[str]
    # Property references
    user_env_properties = ["email", "password"]
    root_env_properties = ["llm_key", "repo_path", "base_url"]
    project_env_properties = ["project_id", "version_id", "commit_id"]
    repr_properties = ["base_url", "repo_path", "email", "project_id", "version_id", "commit_id"]
    is_configured_paths = ["user_env_file_path", "project_env_file_path", "cache_file_path"]
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
        self.save()

    def clear_project(self) -> None:
        """
        Removes project settings details and saves configuration.
        :return: None
        """
        self.set_project(None, None, None)
        self.save()

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

    def set_project(self, project_id: Optional[str], version_id: Optional[str], commit_id: Optional[str] = None):
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

        self.save()
        print(f"New project has been set: https://app.safa.ai/versions/{self.version_id}")

    def set_commit_id(self, commit_id: str) -> None:
        """
        Sets the current project commit.
        :param commit_id: The commit associated with project version.
        :return: None
        """
        self.commit_id = commit_id
        self.save()

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

    def save(self):
        """
        Converts config to env file.
        :return: None
        """
        self.__write_env_file(self, self.root_env_properties, self.root_env_file_path)
        self.__write_env_file(self, self.project_env_properties, self.project_env_file_path)
        self.__write_env_file(self, self.user_env_properties, self.user_env_file_path)

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
        user_env_file_path = os.path.join(config_path, USER_ENV_FILE)
        project_env_file_path = os.path.join(config_path, PROJECT_ENV_FILE)
        vector_store_path = os.path.join(config_path, CHROMA_FOLDER)
        cache_file_path = os.path.join(config_path, CACHE_FILE)
        root_env_file_path = root_env_file_path if root_env_file_path else os.path.join(config_path, ROOT_ENV_FILE)

        SafaConfig.__load_env_files(user_env_file_path, project_env_file_path, root_env_file_path)

        return SafaConfig(
            repo_path=repo_path,
            llm_key=os.environ.get("SAFA_LLM_KEY"),
            # Config paths
            config_path=config_path,
            user_env_file_path=user_env_file_path,
            project_env_file_path=project_env_file_path,
            root_env_file_path=root_env_file_path,
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

    @staticmethod
    def __load_env_files(*env_files: Optional[str]) -> None:
        """
        Loads list of env files in order, last one has highest precedence.
        :param env_files: List of env files.
        :return: None
        """
        for env_file in env_files:
            if env_file and os.path.exists(env_file):
                load_dotenv(env_file)

    @staticmethod
    def __write_env_file(config: "SafaConfig", properties: List[str], env_file_path) -> None:
        """
        Extracts properties from config and writes them as ENV file.
        :param config: The config to extract properties from.
        :param properties: The properties to extract from config.
        :param env_file_path: Path to save env file.
        :return: None
        """
        property2value = {k: getattr(config, k) for k in properties}
        env_line_items = [
            f"SAFA_{k.upper()}={getattr(config, k)}"
            for k, v in property2value.items() if v is not None
        ]
        if len(env_line_items) == 0:
            return
        env_content = "\n".join(env_line_items)
        write_file_content(env_file_path, env_content)
        print(f"Configuration file written to {env_file_path}")
