import traceback
from datetime import datetime
from typing import Dict, List, Optional, Tuple, cast

import git
from git import Blob, Commit, Repo

from safa.utils.markdown import list_formatter
from safa.utils.menus.inputs import input_option
from safa.utils.menus.page_menu import input_menu_paged


def select_commits(repo: Repo) -> List[Commit]:
    """
    Prompts user to select which commits to import.
    :param repo: The repository to select commits from.
    :return: List of commits to import.
    """
    commit_import_options = ["last commit", "select commits"]
    commit_import_option = input_option(commit_import_options)
    if commit_import_option == "last commit":
        commits: List[Commit] = [get_last_repo_commit(repo)]
    elif commit_import_option == "select commits":
        commits = cast(List[Commit], input_commit(repo, many=True))
    else:
        raise Exception(f"Expected answer to be one of {commit_import_options}")
    return commits


def input_commit(repo: Repo, **kwargs) -> Commit | List[Commit]:
    """
    Prompts user to select commit.
    :param repo: Repository to select commit from.
    :param n_commits: The number of commits to display.
    :param prompt: The title to prompt user with.
    :param many: Whether user can select many commits.
    :return: Commit selected.
    """
    # Calculate commits
    branch_name = select_branch(repo)
    branch_commits = [c for c in repo.iter_commits(rev=branch_name)]
    id2commit = {commit_repr(c): c for i, c in enumerate(branch_commits)}
    commit_keys = list(id2commit.keys())

    # Start selection menu
    selected_commit_ids = input_menu_paged(commit_keys, **kwargs)
    if isinstance(selected_commit_ids, list):
        return [id2commit[commit_id] for commit_id in selected_commit_ids]
    return id2commit[selected_commit_ids]


def get_last_repo_commit(repo: Optional[git.Repo] = None, repo_path: Optional[str] = None) -> Commit:
    """
    Returns the last commit at given repo.
    :param repo: Repository to pull commits.
    :param repo_path: Path to load repository from.
    :return: Commit.
    """
    if repo is None:
        repo = git.Repo(repo_path)
    last_commit = repo.head.commit
    return last_commit


def create_commit_artifact(repo: Repo, commit: Commit, prefix: str = "") -> Dict:
    """
    Creates artifact containing commit title and changes.
    :param repo: Project repository.
    :param commit: Commit to convert to artifact.
    :param prefix: Prefix to add to commit artifact name.
    :return: Artifact.
    """
    diff = repo.git.diff(commit.parents[0], commit) if commit.parents else "FIRST COMMIT BUG"
    commit_message = str(commit.message)
    title, changes = from_commit_message(commit_message)
    return {
        "name": f"{prefix}{title}",
        "summary": "\n".join(changes),
        "body": diff,
        "type": "Commit"
    }


def commit_repr(c: Commit) -> str:
    """
    Creates commit display.
    :param c: The commit to display.
    :return: String to display commit
    """
    title, changes = from_commit_message(c.message)
    commit_date = datetime.fromtimestamp(c.committed_date).strftime('%m-%d-%Y %H:%M')
    return f"{commit_date}:{title.strip()}"


def print_commit_message(title, changes, **kwargs) -> None:
    """
    Prints commit message to console.
    :param title: Title of the message.
    :param changes: The changes in the commit.
    :return: None
    """
    print(to_commit_message(title, changes, **kwargs))


def to_commit_message(title: str, changes: List[str], **kwargs) -> str:
    """
    Creates commit message with title and list of changes.
    :param title: Title of commit.
    :param changes: List of changes in commit.
    :return: Commit message.
    """
    return f"{title}\n\n{list_formatter(changes, **kwargs)}"


def from_commit_message(msg: str | bytes) -> Tuple[str, List[str]]:
    """
    Deconstructs commit message into title and list of changes.
    :param msg: Formatted commit message.
    :return: Tuple of title and list of changes.
    """
    if isinstance(msg, bytes):
        msg = str(msg)
    if "\n\n" not in msg:
        return msg, []

    try:
        title, change_msg = msg.split("\n\n")
    except Exception as e:
        traceback.print_exc()
        print("MSG::")
        print(msg)
    change_msg = cast(str, change_msg)
    changes = [c.strip() for c in change_msg.split("\n")]
    return title.strip(), changes


def select_branch(repo: git.Repo) -> str:
    """
    Prompts user to select a branch name from the repo.
    :param repo: Repository to pull branches from.
    :return: The branch name.
    """
    branches = [branch.name for branch in repo.branches]  # type: ignore
    branch_name = input_option(branches, title="Select branch name")
    return cast(str, branch_name)


def decode_blob(blob: Optional[Blob] = None) -> str:
    """
    Decodes blob to string.
    :param blob: The blob to decode.
    :return: String.
    """
    if blob is None:
        raise Exception("Expected blob to exist")
    try:
        return cast(str, blob.data_stream.read().decode("utf-8"))
    except:
        print("blob not utf-8 format.")
    try:
        return cast(str, blob.data_stream.read().decode("iso-8859-1"))

    except Exception as e:
        raise Exception("Blob is not a valid format.")
