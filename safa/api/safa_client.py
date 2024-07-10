from typing import Callable, Dict, List, Optional, cast

from safa.api.constants import SAFA_AUTH_TOKEN, STORE_PROJECT_KEY
from safa.api.http_client import HttpClient
from safa.api.safa_store import SafaStore


class SafaClient:
    BASE_URL = "https://api.safa.ai"

    def __init__(self, store: Optional[SafaStore] = None, http_client: Optional[HttpClient] = None):
        """
        Creates new client to interact with SAFA api.
        :param store: Used to store intermediate results.
        """
        if store is None:
            store = SafaStore()
        if http_client is None:
            http_client = HttpClient(SafaClient.BASE_URL)
        self.http_client = http_client
        self.store = store

    def login(self, email: str, password: str) -> None:
        """
        Authenticates user using SAFA credentials.
        :param email: SAFA account email.
        :param password: SAFA account password.
        :return: Auth token.
        """

        self.http_client.post("login", {"email": email, "password": password})
        if SAFA_AUTH_TOKEN not in self.http_client.session.cookies:
            raise Exception("Login failed, SAFA-TOKEN not found in cookies")

    def get_version(self, version_id: str, **kwargs) -> Dict:
        """
        Retrieves project with version ID.
        :param version_id: ID of version of project to retrieve.
        :param kwargs: Additional keyword arguments to get_or_store.
        :return: The project data.
        """

        def get_data():
            project_data = self.http_client.get(f"projects/versions/{version_id}")
            return project_data

        return self.get_or_store(STORE_PROJECT_KEY, version_id, get_data, **kwargs)

    def get_projects(self, **kwargs) -> List[Dict]:
        """
        Returns the list of projects accessible to user.
        :param kwargs: Additional keyword arguments to get_or_store
        :return: List of projects.
        """

        def get_data():
            projects = self.http_client.get("projects")
            return projects

        result = self.get_or_store(STORE_PROJECT_KEY, "user_projects", get_data, **kwargs)
        return cast(List[Dict], result)

    def get_project_versions(self, project_id: str) -> List[Dict]:
        """
        Retrieves the project versions for given project ID.
        :param project_id: ID of project whose versions are to be retrieved.
        :return: List of project versions objects.
        """
        response = self.http_client.get(f"projects/{project_id}/versions")
        return cast(List[Dict], response)

    def commit(self, version_id: str, commit_data: Dict) -> Dict:
        """
        Commits data to version.
        :param version_id: ID of version to save commit data to.
        :param commit_data: Contains artifacts and trace links to modify.
        :return: Commit response.
        """
        response = self.http_client.post(f"projects/versions/{version_id}/commit", data=commit_data)
        return cast(Dict, response)

    def summarize(self, version_id: str):
        """
        Summarizes project.
        :param version_id: ID of version of artifacts to use.
        :return: Job response.
        """
        response = self.http_client.post(f"projects/versions/{version_id}/summarize", data={})
        return cast(Dict, response)

    def create_version(self, project_id: str, version_type: str = "revision") -> Dict:
        assert version_type in ["revision", "major", "minor"]
        project_version = self.http_client.post(f"projects/{project_id}/versions/{version_type}")
        return project_version

    def get_or_store(self, entity_type: str, entity_id: str, get_lambda: Callable, use_store: bool = True) -> Dict:
        """
        Checks store for entity, if found returns it, otherwise get_lambda is called and processed.
        :param entity_type: The type of entity being retrieved.
        :param entity_id: ID of entity.
        :param get_lambda: Callable used to retrieve entity data.
        :param use_store: Whether to use store to save results.
        :return: The entity data.
        """
        if use_store and self.store.has(entity_type, entity_id):
            return cast(Dict, self.store.get(entity_type, entity_id))
        else:
            entity_data = get_lambda()
            if use_store:
                self.store.save(entity_type, entity_id, entity_data)
            return cast(Dict, entity_data)

    def search_by_prompt(self, query: str, version_id: str, search_types: List[str]) -> List[str]:
        """
        Searches artifacts against query.
        :param query: The prompt used to search for related artifacts.
        :param version_id: ID of the version of the project to search.
        :param search_types: The types of artifacts to search in.
        :return: Artifact Ids of related artifacts.
        """
        payload = {
            "mode": "PROMPT",
            "prompt": query,
            "searchTypes": search_types
        }
        res = self.http_client.post(f"search/{version_id}", payload)
        return cast(List[str], res["artifactIds"])

    def create_project(self, name: str, description: str) -> Dict:
        """
        Creates new project.
        :param name: Name of the project.
        :param description: Description of the project.
        :return: The request response.
        """
        payload = {"name": name, "description": description}
        response = self.http_client.post("projects", data=payload)
        return cast(Dict, response)

    def delete_project(self, project_id: str) -> None:
        """
        Deletes project with given ID.
        :param project_id: ID of project to delete.
        :return: Response to request.
        """
        self.http_client.delete(f"projects/{project_id}")
