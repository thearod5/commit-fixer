from typing import Dict, List, Optional, Tuple

import git

from safa.api.safa_client import SafaClient
from safa.data.artifact import ArtifactJson
from safa.data.file_change import FileChange
from safa.safa_config import SafaConfig
from safa.utils.commits import get_repo_commit, print_commit_message, to_commit_message
from safa.utils.diff_summary import generate_summary
from safa.utils.diffs import calculate_diff
from safa.utils.git_helpers import get_file_content_before, get_staged_diffs, stage_files
from safa.utils.menu import input_confirm, input_option
from safa.utils.printers import print_title, version_repr


def run_committer(config: SafaConfig, client: SafaClient) -> None:
    """
    Reads staged changes and generates commit details (i.e. title, changes). Allows user to edit afterwards.
    :param config: The configuration of the tool.
    :param client: Client used to access SAFA API.
    :return: None.
    """
    print_title("Committer Tool")
    project_data = get_project_data(config, client)
    artifact_map = create_artifact_name_lookup(project_data["artifacts"])

    repo = git.Repo(config.repo_path)
    stage_files(repo)
    file2diff = get_staged_diffs(repo)
    if len(file2diff) == 0:
        print("No changes staged for commit.")
    else:
        file_changes = create_file_changes(file2diff, artifact_map, repo)
        title, changes = generate_summary(file_changes, project_data["specification"])
        run_commit_menu(repo, title, changes)

    if input_confirm("Import commit to SAFA project?", default_value="y"):
        version_type = input_option(["revision", "major", "minor"])
        project_version = client.create_version(project_data["projectId"], version_type)

        new_version_id = project_version["versionId"]
        config.version_id = new_version_id
        commit = get_repo_commit(repo)
        s_commit = repo.commit(config.commit_id) if config.commit_id else None
        commit_data = calculate_diff(repo, commit, starting_commit=s_commit, prefix=f"{version_repr(project_version)}: ")
        client.commit(new_version_id, commit_data)
        config.set_project_commit(config.project_id, new_version_id, commit.hexsha)
        print(f"Commit finished! See project @ https://app.safa.ai/project?version={new_version_id}")


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
        file_artifact: Optional[ArtifactJson] = artifact_map.get(file, None)
        content_before = get_file_content_before(repo, file)
        changes.append(FileChange(
            file=file,
            diff=diff,
            content_before=content_before,
            summary=file_artifact["summary"] if file_artifact else None  # type: ignore
        ))
    return changes


def get_project_data(config: SafaConfig, client: SafaClient):
    """
    Reads SAFA project.
    :param config: Configuration detailing account details and project.
    :param client: Client used to access SAFA API.
    :return: The project data.
    """
    print("...retrieving safa project...")
    project_data = client.get_version(config.get_version_id())
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
