import os
import shutil
import uuid
from dataclasses import dataclass
from typing import Optional, Tuple

from git import Repo

from safa.api.client_factory import create_safa_client
from safa.api.safa_client import SafaClient
from safa.config.safa_config import SafaConfig
from safa.utils.fs import write_file_content
from tests.live.infra.constants import TEST_OUTPUT_DIR


@dataclass
class RepoFactory:
    repo_path: Optional[str] = None
    repo_folder_path: str = TEST_OUTPUT_DIR
    repo: Optional[Repo] = None

    def __post_init__(self) -> None:
        """
        Optionally create repo if flagged.
        :return:None
        """
        if not self.repo_path:
            self.repo_path = os.path.join(self.repo_folder_path, str(uuid.uuid4()))
        self.create()

    def create(self) -> None:
        """
        Creates repository at repo path.
        :return: None
        """
        assert self.repo_path is not None, f"Repository path is not initialized."
        os.makedirs(self.repo_path, exist_ok=True)
        self.repo = Repo.init(self.repo_path)

    def commit_file(self, file_name: str, file_content: str, commit_msg: str = "Writing content to file") -> None:
        """
        Writes content to file and commits it to the repo.
        :param file_name: Name of file.
        :param file_content: Contents of file.
        :param commit_msg: Message to commit with.
        :return: None
        """
        assert self.repo_path is not None, f"Repository path is not initialized."
        assert self.repo is not None, f"Repository is not initialized."
        file_path = os.path.join(self.repo_path, file_name)
        write_file_content(file_path, file_content)
        self.repo.index.add([file_path])
        self.repo.index.commit(message=commit_msg)

    def get_safa_client(self) -> Tuple[SafaConfig, SafaClient]:
        """
        Create SAFA config and client for current
        :return:
        """
        assert self.repo_path is not None, f"Repository path is not initialized."
        config = SafaConfig.from_repo(self.repo_path)
        client = create_safa_client(config)
        return config, client

    def cleanup(self):
        """
        Cleans up the repository.
        :return:
        """
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)
            shutil.rmtree(self.repo_folder_path)
