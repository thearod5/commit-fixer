import sys
from typing import Dict, List

import git
from safa_sdk.safa_client import Safa
from safa_sdk.safa_store import SafaStore

from safa_cmd.config import SafaConfig
from safa_cmd.data.artifact_json import ArtifactJson
from safa_cmd.data.file_change import FileChange
from safa_cmd.tools.comitter.generate import generate_summary
from safa_cmd.utils.markdown import list_formatter
from safa_cmd.utils.menu import prompt_option


def run_committer(config: SafaConfig):
    """
    Reads staged changes and generates commit details (i.e. title, changes). Allows user to edit afterwards.
    :param config: The configuration of the tool.
    :return:
    """
    project_data = get_safa_project(config)
    artifact_map = create_artifact_name_lookup(project_data["artifacts"])

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
    menu_options = ["Edit Title", "Edit Change", "Add Change", "Commit"]
    running = True
    while running:
        print_commit_message(title, changes, format_type="numbered")
        selected_option = prompt_option(menu_options)
        option_num = menu_options.index(selected_option)

        if option_num == 0:
            title = input("New Title:")
        elif option_num == 1:
            change_num = int(input("Change Number"))
            changes[change_num - 1] = input("New Change:")
        elif option_num == 2:
            changes.append(input("New Change:"))
        elif option_num == 3:
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


def get_safa_project(config: SafaConfig):
    """
    Reads SAFA project.
    :param config: Configuration detailing account details and project.
    :return: The project data.
    """
    client_store = SafaStore(config.cache_file_path)
    client = Safa(client_store)
    client.login(config.email, config.password)
    project_data = client.get_project_data(config.version_id)
    return project_data


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


def create_artifact_name_lookup(artifacts: List[Dict]) -> Dict:
    """
    Creates lookup map for artifact by names.
    :param artifacts: The artifacts to include in the map.
    :return: Artifact Map.
    """
    artifact_map = {}
    for artifact in artifacts:
        artifact_map[artifact["name"]] = artifact
    return artifact_map


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
