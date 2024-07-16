from typing import Optional, Tuple

from git import Commit, Repo

from safa.api.safa_client import SafaClient
from safa.safa_config import SafaConfig
from safa.tools.projects.create import run_create_project
from safa.tools.projects.push import run_push_commit
from safa.tools.projects.select import run_select_project
from safa.utils.commits import input_commit
from safa.utils.menus.inputs import input_option


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
    options = ["create_new_project", "select_existing"]
    if not config.has_project():
        options.remove("use_current_project")
    selected_option = input_option(options, title="Project Creation Methods")

    # Actions
    project_commit = None
    if selected_option == "create_new_project":
        run_create_project(config, client)
        project_id, version_id = config.get_project_config()
        run_push_commit(config, client)
    elif selected_option == "select_existing":
        project_id, version_id = run_select_project(config, client)
        project_commit = input_commit(repo)
        config.set_project(project_id, version_id, commit_id=project_commit.hexsha)
    else:
        raise Exception(f"Invalid option {selected_option}")

    return project_id, version_id, project_commit
