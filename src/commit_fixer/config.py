import os
from dataclasses import dataclass


@dataclass
class CommitConfig:
    repo_path: str
    email: str
    password: str
    version_id: str
    cache_file_path: str

    @staticmethod
    def from_env():
        repo_path = os.environ["REPO_PATH"]
        email = os.environ["SAFA_EMAIL"]
        password = os.environ["SAFA_PASSWORD"]
        version_id = os.environ["SAFA_VERSION_ID"]
        cache_file_path = os.environ["CACHE_FILE_PATH"]
        return CommitConfig(repo_path=repo_path,
                            email=email,
                            password=password,
                            version_id=version_id,
                            cache_file_path=os.path.expanduser(cache_file_path))
