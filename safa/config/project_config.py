from dataclasses import dataclass
from typing import List, Optional, Tuple

from safa.config.base_config import BaseConfig
from safa.constants import PROJECT_ENV_FILE


@dataclass(repr=False)
class ProjectConfig(BaseConfig):
    """
    :param project_id: SAFA project ID associated with repository.
    :param version_id: ID of current project version.
    :param commit_id: HexSHA for commit associated with last push to project.
    """
    project_id: Optional[str]
    version_id: Optional[str]
    commit_id: Optional[str]

    @staticmethod
    def get_file_name() -> str:
        return PROJECT_ENV_FILE

    @staticmethod
    def get_display_properties() -> List[str]:
        return ["project_id", "version_id", "commit_id"]

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
        :return: Whether project is configured.
        """
        return self.project_id is not None and self.version_id is not None

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
        if self.version_id:
            print(f"New project has been set: https://app.safa.ai/versions/{self.version_id}")

    def clear_project(self) -> None:
        """
        Removes project settings details and saves configuration.
        :return: None
        """
        self.set_project(None, None, None)
        self.save()
