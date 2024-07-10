import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from safa.utils.fs import clean_path, write_file_content

CONFIG_FOLDER = ".safa"
ENV_FILE = ".env"
CHROMA_FOLDER = "vector_store"
CACHE_FILE = ".cache"


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
    # user defined
    email: Optional[str]
    password: Optional[str]
    project_id: Optional[str]
    version_id: Optional[str]

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
            # User Paths
            repo_path=repo_path,
            email=os.environ.get("SAFA_EMAIL"),
            password=os.environ.get("SAFA_PASSWORD"),
            project_id=os.environ.get("SAFA_PROJECT_ID"),
            version_id=os.environ.get("SAFA_VERSION_ID"),
            # Config paths
            config_path=config_path,
            env_file_path=env_file_path,
            cache_file_path=cache_file_path,
            vector_store_path=vector_store_path
        )

    def to_env(self):
        """
        Converts config to env file.
        :return: None
        """
        vars_to_store = ["repo_path", "email", "password", "project_id", "version_id", "cache_file_path"]

        env_line_items = [
            f"SAFA_{k.upper()}={getattr(self, k)}"
            for k in vars_to_store
        ]
        env_content = "\n".join(env_line_items)
        write_file_content(self.env_file_path, env_content)
        print(f"Configuration file written to {self.env_file_path}")

    def is_configured(self) -> bool:
        """
        Whether all necessary SAFA variables are configured.
        :return: Whether config contains necessary information.
        """
        return (
                os.path.exists(self.env_file_path) and
                os.path.exists(self.cache_file_path) and
                self.email and
                self.password and
                self.project_id and
                self.version_id
        )

    def get_version_id(self) -> str:
        """
        Returns version id if exists, otherwise error is thrown.
        :return: Configured version ID.
        """
        if self.version_id:
            return self.version_id
        raise Exception("Project version is not configured.")

    def __repr__(self) -> str:
        """
        :return: string representation of the configuration.
        """
        config_items = {
            "Repository": self.repo_path,
            "Account": self.email,
            "Project ID": self.project_id,
            "Version ID": self.version_id
        }
        item_display = [f"{k}={v}" for k, v in config_items.items()]
        return "\n".join(item_display)
