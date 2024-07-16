import os
from typing import Optional, Tuple, cast

import git
from git import Commit
from tqdm import tqdm

from safa.api.safa_client import SafaClient
from safa.constants import LINE_LENGTH
from safa.data.commits import DiffDataType, create_empty_diff
from safa.safa_config import SafaConfig
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
        version_id = project_version["versionId"]

        # Create commit data
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit, prefix=f"{version_repr(project_version)}: ")
        store.add_ids(commit_data)
        commit_response = client.commit(version_id, commit_data)
        config.set_project(project_id, version_id, commit_id=commit.hexsha)
        store.save_ids(commit_response)
        summary_commit_data = _summarize_changed_files(config, client, commit_response)
        if summary_commit_data:
            summary_commit_response = client.commit(version_id, summary_commit_data)

        # Post-processing
        s_commit = commit

    if len(commits) > 0:
        print("...re-generating project summary...")  # expected: only project summary generated
        summarization_job = client.summarize(version_id)
        client.wait_for_job(summarization_job["id"])


def _summarize_changed_files(config: SafaConfig, client: SafaClient, diff: DiffDataType) -> Optional[DiffDataType]:
    """
    Summarizes files changed since last push to SAFA.
    --- Note ---
    This method is not for use outside of this module as its currently expected
     that the project data is going to be refreshed since the summaries are not being saved.
    :param config: Configuration to SAFA account and project.
    :return: The commit request containing the new artifact summaries.
    """
    version_id = config.get_version_id()
    changed_artifacts = diff["artifacts"]["modified"] + diff["artifacts"]["added"]
    id2artifact = {a["id"]: a for a in changed_artifacts}
    artifact_ids = list(id2artifact.keys())

    if len(id2artifact) == 0:
        print("No artifacts have changed since last commit.")
        return None

    print(f"... found {len(id2artifact)} changed artifacts...")
    summarized_artifacts = client.summarize_artifacts(version_id, artifact_ids)
    summary_diff = create_empty_diff()
    for a_summarized in summarized_artifacts:
        artifact = id2artifact[a_summarized["id"]]
        artifact["summary"] = a_summarized["summary"]
        summary_diff["artifacts"]["modified"].append(artifact)

    return summary_diff


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
    """
    Prompts user for version type.
    :return: One of the three types of versions.
    """
    response = input_option(["major", "minor", "revision"], title="What kind of version do you want to create?")
    return cast(str, response)
