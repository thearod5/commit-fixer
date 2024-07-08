import os
from dataclasses import dataclass

from dotenv import load_dotenv

from safa_cmd.utils.fs import write_file_content


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
    email: str
    password: str
    version_id: str
    cache_file_path: str

    @staticmethod
    def from_env(repo_path: str):
        load_dotenv(os.path.join(repo_path, "safa.env"))
        repo_path = os.environ.get("SAFA_REPO_PATH")
        email = os.environ.get("SAFA_EMAIL")
        password = os.environ.get("SAFA_PASSWORD")
        version_id = os.environ.get("SAFA_VERSION_ID")
        cache_file_path = os.environ.get("SAFA_CACHE_FILE_PATH")
        if cache_file_path:
            cache_file_path = os.path.expanduser(cache_file_path)
        return SafaConfig(repo_path=os.path.expanduser(repo_path),
                          email=email,
                          password=password,
                          version_id=version_id,
                          cache_file_path=cache_file_path)

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
        env_file_path = os.path.join(self.repo_path, "safa.env")
        write_file_content(env_file_path, env_content)

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
