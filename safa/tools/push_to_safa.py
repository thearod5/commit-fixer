from typing import Optional, Tuple

import git
from git import Commit, Repo
from tqdm import tqdm

from safa.api.safa_client import SafaClient
from safa.constants import EMPTY_TREE_HEXSHA
from safa.safa_config import SafaConfig
from safa.utils.commits import select_commits
from safa.utils.diffs import calculate_diff
from safa.utils.menu import input_confirm


def run_push_to_safa(config: SafaConfig, client: SafaClient):
    """
    Runs through git history and creates commits in SAFA.
    :param config: Configuration object containing repository path and other settings.
    :param client: SAFA client to interact with SAFA API.
    :return: None
    """
    repo = git.Repo(config.repo_path)
    project_id, version_id, s_commit = _select_project(config, client, repo)
    commits = select_commits(repo)

    for i, commit in tqdm(list(enumerate(commits))):
        # create new version
        project_version = client.create_version(project_id, "revision")

        # Create commit data
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit)
        client.commit(project_version["versionId"], commit_data)

    if input_confirm("Set as current project?") and len(commits) > 0:
        commit = commits[-1]
        config.set_project(project_id, version_id, commit.hexsha)


def _select_project(config: SafaConfig, client: SafaClient, repo: Repo) -> Tuple[str, str, Optional[Commit]]:
    """
    Prompts user to select a project or create one.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :param repo: Repository associated with project to import.
    :return: project id , version id , commit id
    """
    s_commit = None
    if config.project_id and input_confirm("Import git history to current project?"):
        project_id, version_id, commit_id = config.get_project_config()
        s_commit = repo.commit(commit_id)
    else:
        project_name = input("Project name:")
        project_description = input("Project description:")
        project = client.create_project(project_name, project_description)
        project_id = project["projectId"]
        version_id = project["projectVersion"]["versionId"]
        config.set_project(project_id, version_id, EMPTY_TREE_HEXSHA)
    return project_id, version_id, s_commit
