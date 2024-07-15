import os
from typing import Optional, Tuple

import git
from git import Commit
from tqdm import tqdm

from safa.api.safa_client import SafaClient
from safa.constants import LINE_LENGTH
from safa.safa_config import SafaConfig
from safa.tools.projects.refresh import refresh_project
from safa.utils.commit_store import CommitStore
from safa.utils.commits import select_commits
from safa.utils.diffs import calculate_diff
from safa.utils.menus.inputs import input_option
from safa.utils.menus.printers import print_title, version_repr

MAJOR_INTERVAL = os.environ.get("SAFA_MAJOR_INTERVAL", 10)
MINOR_INTERVAL = os.environ.get("SAFA_MINOR_INTERVAL", 10)


def run_push_commit(config: SafaConfig, client: SafaClient, set_as_current_project: bool = False,
                    version_intervals: Tuple[int, int] = (MAJOR_INTERVAL, MINOR_INTERVAL)):
    """
    Runs through git history and creates commits in SAFA.
    :param config: Configuration object containing repository path and other settings.
    :param set_as_current_project: Whether to force setting as current project.
    :param client: SAFA client to interact with SAFA API.
    :param version_intervals: Intervals for major and minor versions. See _get_version_type for more details.
    :return: None
    """
    print_title("Pushing Commits to Project")
    if not config.has_project():
        print("Please configure project before pushing.")
        return

    repo = git.Repo(config.repo_path)
    s_commit: Optional[Commit] = None

    project_id, version_id = config.get_project_config()
    if config.has_commit_id():
        s_commit = repo.commit(config.get_commit_id())
    commits = select_commits(repo)

    version_data = client.get_version(version_id)
    store = CommitStore(version_data)

    for i, commit in tqdm(list(enumerate(commits)), ncols=LINE_LENGTH):
        # create new version
        version_type = _get_version_type(i, version_intervals) if len(commits) > 1 else input_version_type()
        project_version = client.create_version(project_id, version_type)

        # Create commit data
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit, prefix=f"{version_repr(project_version)}: ")
        store.add_ids(commit_data)
        commit_response = client.commit(project_version["versionId"], commit_data)
        store.save_ids(commit_response)
        s_commit = commit

        is_last_commit = i == len(commits) - 1

        if is_last_commit:
            last_commit_version_id = project_version["versionId"]
            config.set_project(project_id, last_commit_version_id, commit_id=commit.hexsha)
            refresh_project(config, client, force=True)


def _get_version_type(iteration_idx: int, intervals: Tuple[int, int]):
    """
    Calculates version type using intervals defined.
    :param iteration_idx: The index of the iteration.
    :param intervals: The intervals for major and minor versions
    (e.g. 10,10  = minor version every 10 revisions and a major every 10 minor versions)
    :return: The type of version at given iteration.
    """
    major_interval, minor_interval = intervals
    if iteration_idx % major_interval * minor_interval == 0 and iteration_idx > 0:
        return "major"
    elif iteration_idx % minor_interval == 0 and iteration_idx > 0:
        return "minor"
    else:
        return "revision"


def input_version_type() -> str:
    return input_option(["major", "minor", "revision"], title="What kind of version do you want to create?")
