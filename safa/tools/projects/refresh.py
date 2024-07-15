import os.path
import shutil
from typing import List

import git

from safa.api.constants import STORE_PROJECT_KEY
from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.search import create_vector_store
from safa.utils.commits import get_last_repo_commit
from safa.utils.diffs import calculate_diff
from safa.utils.menus.printers import print_title


def refresh_project(config: SafaConfig, client: SafaClient, force: bool = False) -> None:
    """
    Refresh project data.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    print_title("Refreshing Project Data")
    version_id = config.get_version_id()

    if force:
        summarize_job = client.summarize(version_id)
        client.wait_for_job(summarize_job["id"])
    else:
        _summarize_changed_files(config, client)

    client.store.delete(STORE_PROJECT_KEY, version_id)
    project_data = client.get_version(version_id)
    project_artifacts = project_data["artifacts"]
    if os.path.isdir(config.vector_store_path):
        shutil.rmtree(config.vector_store_path)
    db = create_vector_store(project_artifacts, vector_store_path=config.vector_store_path)


def _summarize_changed_files(config: SafaConfig, client: SafaClient):
    """
    Summarizes files changed since last push to SAFA.
    --- Note ---
    This method is not for use outside of this module as its currently expected
     that the project data is going to be refreshed since the summaries are not being saved.
    :param config: Configuration to SAFA account and project.
    :return:
    """
    version_id = config.get_version_id()
    artifact_ids = get_changed_artifact_ids(config, client)

    if len(artifact_ids) == 0:
        print("No artifacts have changed since last commit.")
        return

    print(f"... found {len(artifact_ids)} changed artifacts...")
    summaries = client.summarize_artifacts(version_id, artifact_ids)

    print("...re-generating project summary...")
    summarization_job = client.summarize(version_id)
    client.wait_for_job(summarization_job["id"])


def get_changed_artifact_ids(config: SafaConfig, client: SafaClient) -> List[str]:
    """
    Retrieves artifact ids of artifacts changed since last push.
    :return:
    """
    repo = git.Repo(config.repo_path)

    # Calculate changed artifacts
    last_commit_id = repo.commit(config.get_commit_id())
    curr_commit_id = get_last_repo_commit(repo_path=config.repo_path)
    commit_diff = calculate_diff(repo, curr_commit_id, starting_commit=last_commit_id)

    artifacts_to_summarize = commit_diff["artifacts"]["modified"] + commit_diff["artifacts"]["added"]
    artifact_names = [a["name"] for a in artifacts_to_summarize]

    version_data = client.get_version(config.get_version_id())
    artifact_name2id = {a["name"]: a["id"] for a in version_data["artifacts"]}

    artifact_ids = [artifact_name2id[a_name] for a_name in artifact_names if a_name in artifact_name2id]
    return artifact_ids
