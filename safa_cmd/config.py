import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from safa_cmd.utils.fs import clean_path, write_file_content

CONFIG_FOLDER = ".safa"
ENV_FILE = ".env"
CHROMA_FOLDER = "vector_store"


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
    # user defined
    email: Optional[str]
    password: Optional[str]
    version_id: Optional[str]
    cache_file_path: Optional[str]

    @staticmethod
    def from_repo(repo_path: str, root_env_file_path: str = None):
        repo_path = clean_path(repo_path)
        config_path = os.path.join(repo_path, CONFIG_FOLDER)
        env_file_path = os.path.join(config_path, ENV_FILE)
        vector_store_path = os.path.join(config_path, CHROMA_FOLDER)

        if os.path.exists(env_file_path):
            load_dotenv(env_file_path)
        if root_env_file_path is None:
            root_env_file_path = os.path.join(repo_path, ENV_FILE)
        load_dotenv(root_env_file_path)

        # Config-Relative paths
        repo_path = os.environ.get("SAFA_REPO_PATH", repo_path)
        vector_store_path = os.environ.get("SAFA_VECTOR_STORE_PATH", vector_store_path)

        # User Settings
        email = os.environ.get("SAFA_EMAIL")
        password = os.environ.get("SAFA_PASSWORD")
        version_id = os.environ.get("SAFA_VERSION_ID")
        cache_file_path = os.environ.get("SAFA_CACHE_FILE_PATH")

        if cache_file_path:
            cache_file_path = clean_path(cache_file_path)
        return SafaConfig(repo_path=repo_path,
                          config_path=config_path,
                          env_file_path=env_file_path,
                          email=email,
                          password=password,
                          version_id=version_id,
                          cache_file_path=cache_file_path,
                          vector_store_path=vector_store_path)

    def to_env(self):
        env_vars = {}
        if self.repo_path:
            env_vars["SAFA_REPO_PATH"] = self.repo_path
        else:
            raise Exception("SAFA Repo path must be set.")
        if self.email:
            env_vars["SAFA_EMAIL"] = self.email
        if self.password:
            env_vars["SAFA_PASSWORD"] = self.password
        if self.version_id:
            env_vars["SAFA_VERSION_ID"] = self.version_id
        if self.cache_file_path:
            env_vars["SAFA_CACHE_FILE_PATH"] = self.cache_file_path

        env_line_items = [f"{k}={v}" for k, v in env_vars.items()]
        env_content = "\n".join(env_line_items)
        write_file_content(self.env_file_path, env_content)
        print(f"Configuration file written to {self.env_file_path}")

    def is_configured(self) -> bool:
        return self.env_file_path and os.path.exists(self.env_file_path) and self.email and self.password and self.version_id

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
            "Version ID": self.version_id
        }
        item_display = [f"{k}={v}" for k, v in config_items.items()]
        return "\n".join(item_display)
