import time
from typing import Callable, Dict, List, Optional, cast

from tqdm import tqdm

from safa.api.constants import SAFA_AUTH_TOKEN, STORE_PROJECT_KEY
from safa.api.http_client import HttpClient
from safa.api.safa_store import SafaStore
from safa.config.safa_config import SafaConfig
from safa.data.commits import DiffDataType


class SafaClient:

    def __init__(self, http_client: HttpClient, store: Optional[SafaStore] = None):
        """
        Creates new client to interact with SAFA api.
        :param store: Used to store intermediate results.
        :param http_client: Client used to make HTTP requests.
        """
        if store is None:
            store = SafaStore()
        self.http_client = http_client
        self.store = store

    def login(self, config: Optional[SafaConfig] = None, email: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Authenticates user using SAFA credentials.
        :param config: Safa configuration.
        :param email: SAFA account email.
        :param password: SAFA account password.
        :return: Auth token.
        """
        if config is None and (email is None or password is None):
            raise Exception("Expected config or email and password.")
        if config:
            email = config.user_config.email
            password = config.user_config.password
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
            print("...retrieving project data...")
            project_data = self.http_client.get(f"projects/versions/{version_id}")
            return project_data

        return self._get_or_store(STORE_PROJECT_KEY, version_id, get_data, **kwargs)

    def get_projects(self, **kwargs) -> List[Dict]:
        """
        Returns the list of projects accessible to user.
        :param kwargs: Additional keyword arguments to get_or_store
        :return: List of projects.
        """
        print("...retrieving projects...")
        result = self.http_client.get("projects")
        return cast(List[Dict], result)

    def get_project_versions(self, project_id: str) -> List[Dict]:
        """
        Retrieves the project versions for given project ID.
        :param project_id: ID of project whose versions are to be retrieved.
        :return: List of project versions objects.
        """
        print("...retrieving project versions...")
        response = self.http_client.get(f"projects/{project_id}/versions")
        return cast(List[Dict], response)

    def commit(self, version_id: str, commit_data: DiffDataType) -> DiffDataType:
        """
        Commits data to version.
        :param version_id: ID of version to save commit data to.
        :param commit_data: Contains artifacts and trace links to modify.
        :return: Commit response.
        """
        response = self.http_client.post(f"projects/versions/{version_id}/commit", data=commit_data)  # type:ignore
        return cast(DiffDataType, response)

    def summarize(self, version_id: str):
        """
        Summarizes project.
        :param version_id: ID of version of artifacts to use.
        :return: Job response.
        """
        print("...starting summarize project job...")
        response = self.http_client.post(f"projects/versions/{version_id}/summarize", data={})
        return cast(Dict, response)

    def summarize_artifacts(self, version_id: str, artifact_ids: List[str]):
        """
        Summarizes artifacts given.
        :return:
        """
        print("...summarizing artifacts...")
        endpoint = f"projects/versions/{version_id}/artifacts/summarize"
        payload = {"artifacts": artifact_ids}
        return self.http_client.post(endpoint, data=payload)

    def get_user_jobs(self) -> List[Dict]:
        """
        Retrieves list of jobs started by current user.
        :return: List of jobs started by current user.
        """
        response = self.http_client.get(f"jobs/user")
        return cast(List[Dict], response)

    def get_job(self, job_id: str) -> Dict:
        """
        Retrieves job by ID.
        :param job_id: ID of job.
        :return: Job Dict.
        """
        jobs = self.get_user_jobs()
        job_query = [job for job in jobs if job["id"] == job_id]

        if len(job_query) == 0:
            raise Exception("Job not found in user jobs.")
        job = job_query[0]
        return job

    def wait_for_job(self, job_id: str):
        """
        Waits until jobs is finished.
        :param job_id:
        :return:
        """
        running = True
        job = None
        progress_bar = tqdm(desc="Waiting for Job...")
        while running:
            job = self.get_job(job_id)
            if job["status"] == "IN_PROGRESS":
                time.sleep(2)
                progress_bar.update()
            else:
                running = False
        progress_bar.close()
        job_status = "NOT STARTED" if job is None else job["status"]
        print(f"Job finished with status: {job_status}")

    def create_version(self, project_id: str, version_type: str) -> Dict:
        """
        Creates new project version.
        :param project_id: ID of project.
        :param version_type: Type of version to create (e.g. major.minor.revision)
        :return: Project version dict.
        """
        assert version_type in ["revision", "major", "minor"]
        project_version = self.http_client.post(f"projects/{project_id}/versions/{version_type}")
        return cast(Dict, project_version)

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

    def _get_or_store(self, entity_type: str, entity_id: str, get_lambda: Callable, use_store: bool = True) -> Dict:
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
