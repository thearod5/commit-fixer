from typing import Dict, List, Tuple

import git

from safa.api.safa_client import SafaClient
from safa.data.artifact_json import ArtifactJson
from safa.data.file_change import FileChange
from safa.safa_config import SafaConfig
from safa.tools.projects import create_commit_data
from safa.tools.utils.generate_diff_summary import generate_summary
from safa.tools.utils.git_helpers import get_file_content_before, get_staged_diffs, stage_files
from safa.utils.markdown import list_formatter
from safa.utils.menu import input_confirm, input_option
from safa.utils.printers import print_commit_response, print_title


def run_committer(config: SafaConfig, client: SafaClient):
    """
    Reads staged changes and generates commit details (i.e. title, changes). Allows user to edit afterwards.
    :param config: The configuration of the tool.
    :return:
    """
    print_title("Committer Tool")
    project_data = get_safa_project(config, client)
    artifact_map = create_artifact_name_lookup(project_data["artifacts"])

    repo = git.Repo(config.repo_path)
    stage_files(repo)
    file2diff = get_staged_diffs(repo)
    if len(file2diff) == 0:
        print("No changes staged for commit.")
        return

    changes = create_file_changes(file2diff, artifact_map, repo)
    title, changes = generate_summary(changes, project_data["specification"])

    title, changes = run_commit_menu(repo, title, changes)
    if input_confirm("Add commit to SAFA project?", default_value="y"):
        project_version = client.create_version(config.project_id, "revision")
        commit_data = create_commit_safa_changes(project_version, list(file2diff.keys()), title, changes)
        commit_response = client.commit(project_version["versionId"], commit_data)
        print_commit_response(commit_response)
        print(f"Commit finished! See project @ https://app.safa.ai/project?version={config.get_version_id()}")


def create_commit_safa_changes(project_version, files: List[str], title: str, changes: List[str]):
    artifacts = [{
        "name": title,
        "summary": "",
        "body": list_formatter(changes),
        "type": "Commit"
    }]
    traces = [{
        "targetName": title,
        "sourceName": f
    } for f in files]
    return create_commit_data(project_version, artifacts_added=artifacts, traces_added=traces)


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


def run_commit_menu(repo: git.Repo, title: str, changes: List[str]) -> Tuple[str, List[str]]:
    """
    Runs commit management menu.
    :param repo: Repository that commit is being applied to.
    :param title: The current title of the commit.
    :param changes: The current changes to the commit.
    :return: None
    """
    print_title("Commit Menu")
    menu_options = ["Edit Title", "Edit Change", "Remove Change", "Add Change", "Commit"]
    while True:
        print_commit_message(title, changes, format_type="numbered")
        selected_option = input_option(menu_options)
        option_num = menu_options.index(selected_option)

        if option_num == 0:
            title = input("New Title:")
        elif option_num == 1:
            change_num = int(input("Change ID:"))
            changes[change_num - 1] = input("New Change:")
        elif option_num == 2:
            change_num = int(input("Change ID:"))
            changes.pop(change_num - 1)
        elif option_num == 3:
            changes.append(input("New Change:"))
        elif option_num == 4:
            repo.index.commit(to_commit_message(title, changes))
            return title, changes
        else:
            raise Exception("Invalid option")


def get_safa_project(config: SafaConfig, client: SafaClient):
    """
    Reads SAFA project.
    :param config: Configuration detailing account details and project.
    :return: The project data.
    """
    print("...retrieving safa project...")
    project_data = client.get_version(config.version_id)
    print("Project Name: ", project_data["name"])
    return project_data


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
