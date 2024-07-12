from typing import Optional, Tuple

from git import Commit, Repo

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.projects.create import run_create_project
from safa.tools.projects.select import run_select_project
from safa.utils.menu import input_option


def run_configure_project(config: SafaConfig, client: SafaClient, repo: Optional[Repo] = None) -> Tuple[str, str, Optional[Commit]]:
    """
    Prompts user to select a project or create one.
    :param config: SAFA account and project configuration.
    :param client: Client used to access SAFA API.
    :param repo: Repository associated with project to import.
    :return: project id , version id , commit id
    """
    if repo is None:
        repo = Repo(config.repo_path)
    options = ["use_current_project", "create_new_project", "select_existing"]
    if not config.has_project():
        options.remove("use_current_project")
    selected_option = input_option(options)

    # Actions
    project_commit = None
    if selected_option == "use_current_project":
        project_id, version_id = config.get_project_config()
        commit_id = config.get_commit_id()
        project_commit = repo.commit(commit_id)
    elif selected_option == "create_new_project":
        run_create_project(config, client)
        project_id, version_id = config.get_project_config()
    elif selected_option == "select_existing":
        project_id, version_id, commit_id = run_select_project(config, client)
        project_commit = repo.commit(commit_id)
    else:
        raise Exception(f"Invalid option {selected_option}")

    return project_id, version_id, project_commit
