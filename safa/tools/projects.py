import os
from typing import Dict, List, Optional, Tuple

import git
from git import Commit, Repo
from tqdm import tqdm

from safa.api.constants import STORE_PROJECT_KEY
from safa.api.safa_client import SafaClient
from safa.constants import EMPTY_TREE_HEXSHA
from safa.safa_config import SafaConfig
from safa.utils.commit_store import CommitStore
from safa.utils.commits import select_commits
from safa.utils.diffs import calculate_diff
from safa.utils.fs import read_file
from safa.utils.menu import input_confirm, input_option
from safa.utils.printers import version_repr


def refresh_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Refresh project data.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    version_id = config.get_version_id()
    client.store.delete(STORE_PROJECT_KEY, version_id)
    client.get_version(version_id)


def delete_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Deletes safa project.
    :param config: Safa account and project configuration.
    :param client: Client used to delete project.
    :return: None
    """
    projects = client.get_projects()
    project_lookup_map = {p["name"]: p for p in projects}

    project_name = input_option(list(project_lookup_map.keys()))
    selected_project = project_lookup_map[project_name]
    project_id = selected_project['projectId']
    client.delete_project(selected_project['projectId'])
    if project_id == config.project_id:
        config.clear_project()
    print("Project Deleted:", selected_project["name"])


def list_projects(config: SafaConfig, client: SafaClient) -> None:
    """
    Lists SAFA projects accessible to user.
    :param config: Safa account and project configuration.
    :param client: The client used to retrieve projects.
    :return: None
    """
    projects = client.get_projects()
    project_lookup_map = {p["name"]: p for p in projects}
    print("\n".join(project_lookup_map.keys()))


def files_to_artifacts(file_paths: List[str], base_path: str) -> List[Dict]:
    """
    Creates artifacts for files.
    :param file_paths: Path to files to create artifacts for.
    :param base_path: Repository base path used to create artifact name.
    :return: List of artifacts.
    """
    artifacts = []
    for file_path in file_paths:
        file_content = read_file(file_path)
        artifacts.append({
            "name": os.path.relpath(file_path, base_path),
            "summary": "",
            "body": file_content,
            "type": "Code"
        })
    return artifacts


def run_push_project(config: SafaConfig, client: SafaClient):
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
        version_type = ("major" if i % 100 == 0 else "minor") if i % 10 == 0 else "revision"
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
            if input_confirm("Set as current project?"):
                config.set_project(project_id, last_commit_version_id, commit.hexsha)
            if input_confirm("Run summarization job?"):
                client.summarize(last_commit_version_id)


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
