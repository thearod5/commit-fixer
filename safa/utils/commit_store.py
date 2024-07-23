from typing import Dict, List

from safa.data.commits import DiffDataType


class CommitStore:
    def __init__(self, version_data: Dict):
        """
        Creates store to keep track of current artifacts in a timeline of commits.
        """
        self.artifact_store: Dict[str, Dict] = self.create_artifact_store(version_data["artifacts"])
        self.trace_store: Dict[str, Dict] = {}

    def add_ids(self, commit_request: DiffDataType) -> None:
        """
        Updates request with entities ids.
        :param commit_request: Commit request data.
        :return: NOne
        """
        self._update_artifacts(commit_request["artifacts"]["modified"])
        self._update_artifacts(commit_request["artifacts"]["removed"])

        self._update_traces(commit_request["traces"]["modified"])
        self._update_traces(commit_request["traces"]["removed"])

    def save_ids(self, commit_response: DiffDataType) -> None:
        """
        Adds artifact and trace link information to commit data.
        :param commit_response: Response to commit.
        :return: None
        """
        self._add_artifacts(commit_response["artifacts"]["added"])
        self._add_artifacts(commit_response["artifacts"]["modified"])
        self._remove_artifacts(commit_response["artifacts"]["removed"])

        self._add_traces(commit_response["traces"]["added"])
        self._add_traces(commit_response["traces"]["modified"])

    def _add_artifacts(self, artifacts: List[Dict]) -> None:
        """
        Adds artifacts to store.
        :param artifacts: Artifacts to add to store.
        :return: None
        """
        for artifact in artifacts:
            self.artifact_store[artifact["name"]] = artifact

    def _add_traces(self, traces: List[Dict]) -> None:
        """
        Adds traces to store.
        :param traces: The traces to add.
        :return:None
        """
        for trace in traces:
            t_id = f"{trace['sourceName']}*{trace['targetName']}"
            self.trace_store[t_id] = trace

    def _update_artifacts(self, artifacts: List[Dict]) -> None:
        """
        Updates artifacts with ID.
        :param artifacts: The artifacts to add id to.
        :return: None
        """
        for artifact in artifacts:
            a_name = artifact["name"]
            if a_name not in self.artifact_store:
                raise Exception("Artifact ({a_name}) has not been set in store.)")
            previous_artifact = self.artifact_store[a_name]
            for key, value in previous_artifact.items():
                artifact[key] = value if key != "body" else artifact[key]

    def _update_traces(self, traces: List[Dict]) -> None:
        """
        Updates traces with ID.
        :param traces: traces to add ID to.
        :return: NOne
        """
        for trace in traces:
            t_id = self.get_tid(trace)
            trace["id"] = self.trace_store[t_id]["id"]
            if trace["sourceName"] in self.artifact_store:
                trace["sourceId"] = self.artifact_store[trace["sourceName"]]
            if trace["targetName"] in self.artifact_store:
                trace["targetId"] = self.artifact_store[trace["targetName"]]

    def _remove_artifacts(self, artifacts: List[Dict]) -> None:
        """
        Removes artifacts from store.
        :param artifacts: The artifacts to remove.
        :return: None
        """
        for artifact in artifacts:
            del self.artifact_store[artifact["name"]]

    @staticmethod
    def get_tid(trace: Dict) -> str:
        """
        Creates trace ID for trace.
        :param trace: Trace to create ID for.
        :return: Trace ID.
        """
        return f"{trace['sourceName']}*{trace['targetName']}"

    @staticmethod
    def create_artifact_store(artifacts: List[Dict]) -> Dict[str, Dict]:
        """
        Creates map of artifact names to artifact.
        :param artifacts: List of artifacts to store.
        :return: Mapping.
        """
        artifact_store = {a["name"]: a for a in artifacts}
        return artifact_store
