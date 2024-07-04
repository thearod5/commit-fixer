from typing import Dict

import git


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
    """
    try:
        content_before = repo.git.show(f'HEAD:{file_path}')
    except git.exc.GitCommandError:
        content_before = None
    return content_before


def show_changes(repo):
    changed_files = [item.a_path for item in repo.index.diff(None)]
    untracked_files = repo.untracked_files

    print("\nChanged files:")
    for i, file in enumerate(changed_files):
        print(f"{i + 1}. {file}")

    print("\nUntracked files:")
    for i, file in enumerate(untracked_files):
        print(f"{len(changed_files) + i + 1}. {file}")

    return changed_files + untracked_files


def prompt_user_for_staging(repo, files):
    to_stage = []
    while True:
        user_input = input(
            "Enter the numbers of the files you want to stage, separated by spaces (or 'a' to stage all, 'q' to quit): ").strip()

        if user_input.lower() == 'a':
            to_stage = files
            break
        elif user_input.lower() == 'q':
            break
        else:
            indices = user_input.split()
            for index in indices:
                try:
                    file_index = int(index) - 1
                    if file_index >= 0 and file_index < len(files):
                        to_stage.append(files[file_index])
                except ValueError:
                    print(f"Invalid input: {index}")

            if to_stage:
                break
    repo.index.add(files)
    return to_stage
