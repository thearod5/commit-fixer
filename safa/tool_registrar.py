from typing import Callable, Dict

from safa.tools.committer import run_committer
from safa.tools.configure import run_configure_account
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

}
TOOL_PERMISSIONS = {
    "committer": ["project"],
    "search": ["project"],
    "push_project": ["user", "project"],
    "refresh_project": ["user"],
    "delete_project": ["user"],
    "list_projects": ["user"],
    "project": ["*"],
    "account": ["*"]
}
TOOL_NAMES = {
    "committer": "Commit Changes",
    "search": "Search",
    "push_project": "Push",
    "refresh_project": "Refresh",
    "delete_project": "Delete",
    "list_projects": "List",
    "project": "Configure",
    "account": "Settings"
}
TOOL_GROUPS = {
    "Tools": [
        "committer",
        "search"
    ],
    "Projects": [
        "push_project",
        "delete_project",
        "list_projects",
        "refresh_project",
        "project"
    ],
    "Account": [
        "account"
    ]
}
