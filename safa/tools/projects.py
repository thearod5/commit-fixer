import os
from typing import Dict, List, Optional

from safa.api.constants import STORE_PROJECT_KEY
from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.utils.fs import list_paths, list_python_files, read_file
from safa.utils.menu import input_option
from safa.utils.printers import print_commit_response, print_title


def run_project_management(config: SafaConfig, client: SafaClient) -> None:
    """
    Allows user to create, delete, or list projects.
    :param config: Account and repository configuration.
    :param client: Client used to access SAFA API.
    :return: None
    """
    selected_option = input_option(["refresh_project", "create_project", "delete_project", "list_projects"])
    if selected_option == "refresh_project":
        refresh_project(config, client)
    elif selected_option == "create_project":
        create_new_project(config, client)
    elif selected_option == "delete_project":
        delete_project(client)
    elif selected_option == "list_projects":
        list_projects(client)
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
    name = input("Name:")
    description = input("Description:")

    directories = [p for p, f in list_paths(config.repo_path) if os.path.isdir(p) and f[0] != "."]
    selected_directories = input_option(directories, title="Select Sub-Directory (empty for root dir)", allow_many=True)
    if len(selected_directories) > 0:
        python_files = list_python_files(selected_directories)
    else:
        python_files = list_python_files(config.repo_path)

    code_artifacts = files_to_artifacts(python_files, config.repo_path)

    # Create project
    print("...(1) creating project...")
    project_data = client.create_project(name, description)
    config.project_id = project_data["projectId"]
    project_version = project_data["projectVersion"]
    version_id = project_data["projectVersion"]["versionId"]
    config.version_id = version_id

    print("...(2) saving entities...")
    commit_data = create_commit_data(project_version, artifacts_added=code_artifacts)
    commit_response = client.commit(version_id, commit_data)
    print_commit_response(commit_response)

    print("...(3) starting summary job...")
    client.summarize(version_id, )
    print("Job has been submitted! You will get an email when its done.")
    config.to_env()


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


def create_commit_data(project_version: Dict,
                       artifacts_added: Optional[List[Dict]] = None,
                       traces_added: Optional[List[Dict]] = None) -> Dict:
    """
    Creates commit request with parameters filled in.
    :param project_version: Project version to commit to.
    :param artifacts_added: Artifacts being added in commit.
    :param traces_added: Traces being added in commit.
    TODO: Add other parameters as needed.
    :return: Commit data.
    """
    if artifacts_added is None:
        artifacts_added = []
    if traces_added is None:
        traces_added = []
    return {
        "commitVersion": project_version,
        "artifacts": {
            "added": artifacts_added,
            "modified": [],
            "removed": []
        },
        "traces": {
            "added": traces_added,
            "modified": [],
            "removed": []
        }
    }
