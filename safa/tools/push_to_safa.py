from typing import Dict, List, Optional, Tuple

import git
from git import Commit, Repo
from tqdm import tqdm

from safa.api.safa_client import SafaClient
from safa.constants import EMPTY_TREE_HEXSHA
from safa.data.commits import DiffDataType
from safa.safa_config import SafaConfig
from safa.utils.commit_store import CommitStore
from safa.utils.commits import select_commits
from safa.utils.diffs import calculate_diff
from safa.utils.menu import input_confirm
from safa.utils.printers import version_repr


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

    store = CommitStore()

    for i, commit in tqdm(list(enumerate(commits))):
        # create new version
        project_version = client.create_version(project_id, "revision")

        # Create commit data
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit, prefix=f"{version_repr(project_version)}: ")
        store.update_request(commit_data)
        commit_response = client.commit(project_version["versionId"], commit_data)
        store.process_response(commit_response)
        s_commit = commit

        is_last_commit = i == len(commits) - 1

        if is_last_commit:
            last_commit_version_id = project_version["versionId"]
            if input_confirm("Set as current project?"):
                config.set_project(project_id, last_commit_version_id, commit.hexsha)
            if input_confirm("Run summarization job?"):
                client.summarize(last_commit_version_id)


def _update_response(store: Dict, commit_response: DiffDataType) -> None:
    """
    Updates the current artifact ID.
    :param store: Store containing current entity details.
    :param commit_response: Response from commit.
    :return: None
    """
    _add_artifacts_to_store(store, commit_response["artifacts"]["added"])
    _add_artifacts_to_store(store, commit_response["artifacts"]["modified"])


def _add_artifacts_to_store(store: Dict, artifacts: List[Dict]):
    for a in artifacts:
        store["artifacts"][a["name"]] = a


def _select_project(config: SafaConfig, client: SafaClient, repo: Repo) -> Tuple[str, str, Optional[Commit]]:
    """
    Prompts user to select a project or create one.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :param repo: Repository associated with project to import.
    :return: project id , version id , commit id
    """
    s_commit = None
    if config.project_id and input_confirm("Use current project?"):
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
