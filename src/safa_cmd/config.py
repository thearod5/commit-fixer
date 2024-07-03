import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class FixerConfig:
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
    def from_env():
        load_dotenv()
        repo_path = os.environ["REPO_PATH"]
        email = os.environ["SAFA_EMAIL"]
        password = os.environ["SAFA_PASSWORD"]
        version_id = os.environ["SAFA_VERSION_ID"]
        cache_file_path = os.environ["CACHE_FILE_PATH"]
        return FixerConfig(repo_path=repo_path,
                           email=email,
                           password=password,
                           version_id=version_id,
                           cache_file_path=os.path.expanduser(cache_file_path))
