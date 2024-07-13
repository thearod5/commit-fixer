from typing import Dict

import git

from safa.utils.menus.inputs import input_option
from safa.utils.menus.printers import print_title


def get_staged_diffs(repo: git.Repo) -> Dict[str, str]:
    """
    Gets the changes changed and extracts their diffs.
    :param repo: The repository to extract staged changes from.
    :return: Map from file to diff.
    """
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]

    file2diff = {}
    for file in staged_files:
        try:
            diff = repo.git.diff('HEAD', file)
            file2diff[file] = diff
        except git.exc.GitCommandError:
            # Handle the case where the file has been deleted
            content_before = get_file_content_before(repo, file)
            if content_before:
                diff = "\n".join(f"- {line}" for line in content_before.splitlines())
                file2diff[file] = diff

    return file2diff


def get_file_content_before(repo, file_path):
    """
    Get the content of the file before the staged changes.
    :param repo: The repository that file exists in.
    :param file_path: The path of the file.
    :return: The content of the file before the staged changes.
    """
    try:
        content_before = repo.git.show(f'HEAD:{file_path}')
    except git.exc.GitCommandError:
        content_before = None
    return content_before


def stage_files(repo: git.Repo) -> None:
    """
    Displays the files that have been changed to the user and indicates which files are staged and which are not.
    :param repo: The repository to analyze.
    :return: List of changed files and untracked files.
    """
    print_title("Repository")

    changed_files = [item.a_path for item in repo.index.diff(None)] + repo.untracked_files
    staged_files = [item.a_path for item in repo.index.diff("HEAD")]

    if len(staged_files) == 0:
        print("No staged files.")
    else:
        print("Staged files:")
        for i, file in enumerate(staged_files):
            print(f"{i + 1}. {file}")

    if len(changed_files) == 0:
        return
    to_stage = input_option(changed_files, title="Unstaged Files", many=True, page_items=len(changed_files))
    repo.index.add(to_stage)
