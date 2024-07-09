from safa_cmd.config import SafaConfig
from safa_cmd.safa.safa_client import SafaClient
from safa_cmd.utils.menu import input_option


def run_search(config: SafaConfig, client: SafaClient):
    """
    Runs search on configured project
    :param config: Configuration used to get SAFA account and project.
    :param client: Client used to access SAFA API.
    :return: None
    """

    query = input("Search Query:")
    version_id = config.version_id
    project_data = client.get_version(version_id)
    possible_types = [a["name"] for a in project_data["artifactTypes"]]
    search_types = possible_types[:1] if len(possible_types) < 2 else input_option(possible_types,
                                                                                   allow_many=True,
                                                                                   title="Search Types")
    if len(search_types) == 0:
        print("No artifacts to search.")
        return
    artifact_ids = client.search_by_prompt(query, version_id, search_types)
    artifacts = [a["name"] for a in project_data["artifacts"] if a["id"] in artifact_ids]
    print(f"Found {len(artifacts)}")
    print("\n".join(artifacts))
