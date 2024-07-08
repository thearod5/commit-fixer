import os
from typing import Dict, List

from safa_sdk.safa_client import SafaClient
from safa_sdk.util import read_file

from safa_cmd.config import SafaConfig
from safa_cmd.utils.fs import list_paths, list_python_files
from safa_cmd.utils.menu import input_option
from safa_cmd.utils.printers import print_title


def run_projects(config: SafaConfig) -> None:
    """
    Allows user to create, delete, or list projects.
    :param config: Account and repository configuration.
    :return: None
    """
    selected_option = input_option(["create_project", "delete_project", "list_projects"])

    client = SafaClient()
    client.login(config.email, config.password)
    if selected_option == "create_project":
        create_new_project(config, client)
    elif selected_option == "delete_project":
        delete_project(client)
    elif selected_option == "list_projects":
        list_projects(client)
    else:
        raise Exception(f"Invalid option: {selected_option}")


def create_new_project(config: SafaConfig, client: SafaClient) -> None:
    """
    Creates a new project, uploads code, and starts HGEN documentation.
    :param config: Configuration details.
    :param client: Client used to create project with.
    :return:None
    """
    print_title("Creating New Project")
    name = input("Name:")
    description = input("Description:")

    directories = [p for p in list_paths(config.repo_path) if os.path.isdir(p) and p[0] != "."]
    selected_directories = input_option(directories, title="Select Sub-Directory (empty for root dir)", allow_many=True)
    if len(selected_directories) > 0:
        python_files = list_python_files(selected_directories)
    else:
        python_files = list_python_files(config.repo_path)

    code_artifacts = files_to_artifacts(python_files, config.repo_path)
    commit_data = {
        "artifacts": {
            "added": code_artifacts,
            "modified": [],
            "removed": []
        },
        "traces": {
            "added": [],
            "modified": [],
            "removed": []
        }
    }

    # Create project
    print("...(1) creating project...")
    project_data = client.create_project(name, description)
    version_id = project_data["projectVersion"]["versionId"]
    config.version_id = version_id

    print("...(2) saving entities...")
    commit_response = client.commit(version_id, commit_data)

    print("...(3) starting hgen job...")
    artifact_ids = [a["id"] for a in commit_response["artifacts"]["added"]]
    client.hgen(version_id, {
        "artifacts": artifact_ids,
        "targetTypes": ["Functional Requirement", "Feature"]
    })
    print("Done!")


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
