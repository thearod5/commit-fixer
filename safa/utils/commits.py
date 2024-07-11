from datetime import datetime
from typing import Dict, List, Optional, Tuple, cast

import git
from git import Blob, Commit, Repo

from safa.utils.markdown import list_formatter
from safa.utils.menu import input_confirm, input_option


def select_commits(repo: Repo) -> List[Commit]:
    """
    Prompts user to select which commits to import.
    :param repo: The repository to select commits from.
    :return: List of commits to import.
    """
    commit_import_options = ["single commit", "multiple commits"]
    commit_import_option = input_option(commit_import_options)
    if commit_import_option == "single commit":
        commits = [input_commit(repo, many=False)]
    elif commit_import_option == "multiple commits":
        if input_confirm(title="Import all commits?"):
            branch_name = select_branch(repo)
            commits = [c for c in repo.iter_commits(rev=branch_name, reverse=True)]
        else:
            commits = cast(List[Commit], input_commit(repo, many=True))
    else:
        raise Exception(f"Expected answer to be one of {commit_import_options}")
    return commits


def input_commit(repo: Repo, n_commits: int = 5, prompt: str = "Select Commit", many: bool = False) -> Commit | List[Commit]:
    """
    Prompts user to select commit.
    :param repo: Repository to select commit from.
    :param n_commits: The number of commits to display.
    :param prompt: The title to prompt user with.
    :param many: Whether user can select many commits.
    :return: Commit selected.
    """

    page = 0
    branch_name = select_branch(repo)
    branch_commits = [c for c in repo.iter_commits(rev=branch_name)]

    max_pages = len(branch_commits) // n_commits
    max_pages = max_pages if len(branch_commits) % n_commits == 0 else max_pages + 1
    id2commit = {commit_repr(c): c for i, c in enumerate(branch_commits)}
    commit_keys = list(id2commit.keys())

    running = True
    selected_commits = []
    while running:
        actions = []

        if page < max_pages - 1:
            actions.append("next_page")
        if page > 0:
            actions.append("previous_page")
        if page < max_pages - 1:
            actions.append("last_page")
        if page > 0:
            actions.append("first_page")

        if many:
            actions.append("input_sha")
            actions.append("finish_selection")

        start_idx = page * n_commits
        end_idx = start_idx + n_commits
        page_commits_keys = commit_keys[start_idx: end_idx]
        items = page_commits_keys + actions

        group2items = {"Commit": [k for k in page_commits_keys], "Actions": actions}
        title = f"{prompt}\nPage:{page}/{max_pages}"
        if many:
            title += f"\nCommits: {[commit_repr(c) for c in selected_commits]}"
        selected_commit_id = input_option(items, title=title, group2items=group2items)
        if selected_commit_id == "next_page":
            page = page if page >= max_pages else page + 1
        elif selected_commit_id == "previous_page":
            page = page - 1 if page > 0 else 0
        elif selected_commit_id == "last_page":
            page = max_pages - 1
        elif selected_commit_id == "input_sha":
            inputted_commits = [repo.commit(s.strip()) for s in input("HEXSHA(s):").split(",")]
            selected_commits.extend(inputted_commits)
        elif selected_commit_id == "finish_selection":
            return selected_commits
        elif selected_commit_id == "first_page":
            page = 0
        else:
            selected_commit = id2commit[selected_commit_id]
            if many:
                selected_commits.append(selected_commit)
            else:
                return selected_commit
    raise Exception("")


def get_repo_commit(repo: Optional[git.Repo] = None, repo_path: Optional[str] = None) -> Commit:
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

    title, change_msg = msg.split("\n\n")
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
    blob_str = blob.data_stream.read().decode("utf-8")
    return cast(str, blob_str)
