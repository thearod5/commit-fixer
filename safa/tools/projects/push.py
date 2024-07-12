from typing import Optional

import git
from git import Commit
from tqdm import tqdm

from safa.api.safa_client import SafaClient
from safa.constants import LINE_LENGTH
from safa.safa_config import SafaConfig
from safa.utils.commit_store import CommitStore
from safa.utils.commits import select_commits
from safa.utils.diffs import calculate_diff
from safa.utils.menu import input_confirm
from safa.utils.printers import version_repr


def run_push_commit(config: SafaConfig, client: SafaClient, set_as_current_project: bool = False):
    """
    Runs through git history and creates commits in SAFA.
    :param config: Configuration object containing repository path and other settings.
    :param set_as_current_project: Whether to force setting as current project.
    :param client: SAFA client to interact with SAFA API.
    :return: None
    """
    repo = git.Repo(config.repo_path)
    s_commit: Optional[Commit] = None
    if not config.has_project():
        print("Please configure project before pushing.")
        return
    project_id, version_id = config.get_project_config()
    if config.has_commit_id():
        s_commit = repo.commit(config.get_commit_id())
    commits = select_commits(repo)

    store = CommitStore()

    for i, commit in tqdm(list(enumerate(commits)), ncols=LINE_LENGTH):
        # create new version
        version_type = ("major" if i % 100 == 0 else "minor") if i % 10 == 0 and i > 0 else "revision"
        project_version = client.create_version(project_id, version_type)

        # Create commit data
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit, prefix=f"{version_repr(project_version)}: ")
        store.update_request(commit_data)
        commit_response = client.commit(project_version["versionId"], commit_data)
        store.process_response(commit_response)
        s_commit = commit

        is_last_commit = i == len(commits) - 1

        if is_last_commit:
            last_commit_version_id = project_version["versionId"]
            if set_as_current_project or input_confirm("Set as current project?"):
                config.set_project_commit(project_id, last_commit_version_id, commit.hexsha)
            if input_confirm("Run summarization job?"):
                client.summarize(last_commit_version_id)
