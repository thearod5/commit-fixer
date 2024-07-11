from typing import List, Optional

import git
from git import Commit, Diff
from tqdm import tqdm

from safa.api.safa_client import SafaClient
from safa.constants import EMPTY_TREE_HEXSHA
from safa.safa_config import SafaConfig
from safa.utils.commits import select_branch
from safa.utils.diffs import calculate_diff
from safa.utils.menu import input_confirm, input_option


def run_git_history(config: SafaConfig, client: SafaClient):
    """
    Runs through git history and creates commits in SAFA.
    :param config: Configuration object containing repository path and other settings.
    :param client: SAFA client to interact with SAFA API.
    :return: None
    """
    repo = git.Repo(config.repo_path)
    s_commit: Optional[Commit] = None

    if config.project_id and input_confirm("Import git history to current project?"):
        s_commit = repo.commit(config.commit_id)
        project_id, version_id, commit_id = config.get_project_config()
    else:
        project_name = input("Project name:")
        project_description = input("Project description:")
        project = client.create_project(project_name, project_description)
        project_id = project["projectId"]
        version_id = project["projectVersion"]["versionId"]
        config.set_project(project_id, version_id, EMPTY_TREE_HEXSHA)

    branch_name = select_branch(repo)

    commit = None
    for i, commit in tqdm(list(enumerate(repo.iter_commits(rev=branch_name, reverse=True)))):
        # create new version
        project_version = client.create_version(project_id, "revision")

        # Create commit data
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit)
        client.commit(project_version["versionId"], commit_data)

    if input_confirm("Set as current project?") and commit:
        config.set_project(project_id, version_id, commit.hexsha)


def get_commit_details(repo: git.Repo, commit: git.Commit):
    commit_message = commit.message
    commit_hash = commit.hexsha
    # author_name = commit.author.name
    # author_email = commit.author.email
    commit_date = commit.committed_datetime
    # Extract changed files and their state after the commit
    files_added = []
    files_modified = []
    files_deleted = []
    if not commit.parents:
        diffs: List[Diff] = commit.diff(git.NULL_TREE)
    else:
        diffs: List[Diff] = [d for parent in commit.parents for d in parent.diff(commit, create_patch=True)]

    for diff in diffs:
        file_path = diff.b_path if diff.b_path else diff.a_path
        file_content = diff.b_blob.data_stream.read().decode() if diff.b_blob else ""
        file_details = {
            "date": commit_date,
            'file_path': file_path,
            'content': file_content
        }
        if diff.deleted_file:
            files_deleted.append(file_details)
        elif diff.new_file:
            files_added.append(file_details)
        else:
            files_modified.append(file_details)
    # Create commit in SAFA
    diff_content = repo.git.diff(commit.parents[0], commit) if commit.parents else "FIRST COMMIT BUG"
    safa_commit_data = {
        'commit_message': commit_message,
        'commit_date': commit_date.isoformat(),
        'commit_diff': diff_content,
        'commit_attributes': {
            "hash": commit_hash,
        },
        'files': {
            "added": files_added,
            "modified": files_modified,
            "deleted": files_deleted
        }
    }
    return safa_commit_data


def get_or_create_project():
    option = input_option(["create new project", "select existing project"])
    if option == "create new project":
        pass
