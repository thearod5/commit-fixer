from typing import Callable, Dict, List

from safa.tools.committer import run_committer
from safa.tools.configure import run_configure_account
from safa.tools.jobs import run_job_module
from safa.tools.projects.configure import run_configure_project
from safa.tools.projects.delete import delete_project
from safa.tools.projects.push import run_push_commit
from safa.tools.projects.refresh import refresh_project
from safa.tools.projects.select import list_projects
from safa.tools.search import run_search

TOOL_FUNCTIONS: Dict[str, Callable] = {
    "committer": run_committer,
    "search": run_search,
    "push_project": run_push_commit,
    "refresh_project": refresh_project,
    "delete_project": delete_project,
    "list_projects": list_projects,
    "project": run_configure_project,
    "account": run_configure_account,
    "jobs": run_job_module

}
TOOL_PERMISSIONS: Dict[str, List[str]] = {
    "committer": ["user"],
    "search": ["project"],
    "push_project": ["user", "project"],
    "refresh_project": ["user"],
    "delete_project": ["user"],
    "list_projects": ["user"],
    "project": ["*"],
    "account": ["*"],
    "jobs": ["user"]
}
TOOL_NAMES: Dict[str, str] = {
    "committer": "Commit",
    "search": "Search",
    "push_project": "Push",
    "refresh_project": "Refresh",
    "delete_project": "Delete",
    "list_projects": "List",
    "project": "Configure",
    "account": "Settings",
    "jobs": "Jobs"
}
TOOL_GROUPS: Dict[str, List[str]] = {
    "Tools": [
        "search",
        "committer",
        "push_project",
    ],
    "Projects": [
        "delete_project",
        "list_projects",
        "refresh_project",
        "project"
    ],
    "Safa": [
        "account",
        "jobs"
    ]
}
