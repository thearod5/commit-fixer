import os
from typing import Dict, List

import git

from safa.api.client_factory import create_safa_client
from safa.api.constants import STORE_PROJECT_KEY
from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.push_to_safa import run_push_to_safa
from safa.utils.commits import input_commit
from safa.utils.diffs import calculate_diff
from safa.utils.fs import read_file
from safa.utils.menu import input_option
from safa.utils.printers import print_commit_response, print_title


def run_project_management(config: SafaConfig, client: SafaClient) -> None:
    """
    Allows user to create, delete, or list projects.
    :param config: Account and repository configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    selected_option = input_option(["refresh_project", "create_project", "delete_project", "list_projects", "import_git_history"])
    if selected_option == "refresh_project":
        refresh_project(config, client)
    elif selected_option == "create_project":
        create_new_project(config, client)
    elif selected_option == "delete_project":
        delete_project(client)
    elif selected_option == "list_projects":
        list_projects(client)
    elif selected_option == "import_git_history":
        run_push_to_safa(config, client)
    else:
        raise Exception(f"Invalid option: {selected_option}")


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


def create_new_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Creates a new project, uploads code, and starts HGEN documentation.
    :param config: Configuration details.
    :param client: Client used to create project with.
    :return:None
    """
    print_title("Creating New Project")
    name = input("Project Name:")
    description = input("Project Description:")
    repo = git.Repo(config.repo_path)
    commit = input_commit(repo, prompt="Select commit to import project")

    # Calculate changes since the start
    repo = git.Repo(config.repo_path)
    commit_data = calculate_diff(repo, commit)

    # Create project
    print("...(1) creating project...")
    project_data = client.create_project(name, description)
    project_version = project_data["projectVersion"]
    version_id = project_data["projectVersion"]["versionId"]
    commit_id = commit.hexsha
    config.set_project(project_data["projectId"], version_id, commit_id)

    # Commit Entities
    print("...(2) saving entities...")
    commit_data = {**commit_data, "commitVersion": project_version}
    commit_response = client.commit(version_id, commit_data)
    print_commit_response(commit_response)

    print("...(3) starting summary job...")
    client.summarize(version_id)
    print("Job has been submitted! You will get an email when its done.")


def delete_project(client: SafaClient) -> None:
    """
    Deletes safa project.
    :param client: Client used to delete project.
    :return: None
    """
    projects = client.get_projects()
    project_lookup_map = {p["name"]: p for p in projects}

    project_name = input_option(list(project_lookup_map.keys()))
    selected_project = project_lookup_map[project_name]
    client.delete_project(selected_project['projectId'])
    print("Project Deleted:", selected_project["name"])


def list_projects(client: SafaClient) -> None:
    """
    Lists SAFA projects accessible to user.
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


if __name__ == "__main__":
    config = SafaConfig.from_repo("~/projects/safa-cmd")
    client = create_safa_client(config)
    create_new_project(config, client)
