import sys
from typing import Dict, List

import git
from safa.safa_client import Safa
from safa.safa_store import SafaStore

from src.commit_fixer.config import CommitConfig
from src.commit_fixer.data.artifact_json import ArtifactJson
from src.commit_fixer.data.file_change import FileChange
from src.commit_fixer.generate import generate_summary


def run(config: CommitConfig):
    project_data = get_safa_project(config)
    artifact_map = create_artifact_map(project_data["artifacts"])

    repo = git.Repo(config.repo_path)
    file2diff = get_staged_diffs(repo)
    if len(file2diff) == 0:
        print("No changes staged for commit.")
        sys.exit(0)

    changes = create_file_changes(file2diff, artifact_map, repo)
    title, changes = generate_summary(changes, project_data["specification"])

    run_commit_menu(repo, title, changes)


def create_file_changes(file2diff, artifact_map: Dict[str, ArtifactJson], repo) -> List[FileChange]:
    """
    Augments file diffs with artifact summary and file before changes.
    :param file2diff: Map of file to its diffs for those to convert.
    :param artifact_map: Artifact name lookup table.
    :param repo: Git repository to use to get file state before change.
    :return: List of file changes.
    """
    changes: List[FileChange] = []
    for file, diff in file2diff.items():
        file_artifact = artifact_map.get(file, None)
        content_before = get_file_content_before(repo, file)
        changes.append(FileChange(
            file=file,
            diff=diff,
            content_before=content_before,
            summary=file_artifact["summary"] if file_artifact else None
        ))
    return changes


def run_commit_menu(repo, title, changes):
    menu_options = ["Edit title", "Edit changes", "Add change", "Commit"]
    running = True
    while running:
        print_commit_message(title, changes)
        for i, menu_option in enumerate(menu_options):
            print(f"{i + 1})", menu_option)
        option = input(">")
        option_num = int(option)

        if option_num == 1:
            title = input("New Title:")
        elif option_num == 2:
            change_num = int(input("Change Number"))
            changes[change_num - 1] = input("New Change:")
        elif option_num == 3:
            changes.append(input("New Change:"))
        elif option_num == 4:
            repo.index.commit(to_commit_message(title, changes))
            running = False
        else:
            raise Exception("Invalid option")


def get_file_content_before(repo, file_path):
    """
    Get the content of the file before the staged changes.
    """
    try:
        content_before = repo.git.show(f'HEAD:{file_path}')
    except git.exc.GitCommandError:
        content_before = None
    return content_before


def get_safa_project(config):
    client_store = SafaStore(config.cache_file_path)
    client = Safa(client_store)
    client.login(config.email, config.password)
    project_data = client.get_project_data(config.version_id)
    return project_data


def get_staged_diffs(repo):
    """
    Get the staged diffs using Git.
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


def create_artifact_map(artifacts: List[Dict]):
    artifact_map = {}
    for artifact in artifacts:
        artifact_map[artifact["name"]] = artifact
    return artifact_map


def changes_to_message(change_messages: List[str]):
    """
    Formats list of changes as a Markdown list.
    :param change_messages: List of diff summaries.
    :return: String delimited changes as a Markdown list.
    """
    content = '\n'.join(["- " + c for c in change_messages])
    return content


def to_commit_message(title, changes):
    return f"{title}\n\n{changes_to_message(changes)}"


def print_commit_message(title, changes):
    print(to_commit_message(title, changes))
