from typing import Dict, List

from safa.data.commits import DiffDataType


class CommitStore:
    def __init__(self):
        """
        Creates store to keep track of current artifacts in a timeline of commits.
        """
        self.artifact_store = {}
        self.trace_store = {}

    def update_request(self, commit_request: DiffDataType) -> None:
        """
        Updates request with entities ids.
        :param commit_request: Commit request data.
        :return: NOne
        """
        self._update_artifacts(commit_request["artifacts"]["modified"])
        self._update_artifacts(commit_request["artifacts"]["removed"])

        self._update_traces(commit_request["traces"]["modified"])
        self._update_traces(commit_request["traces"]["removed"])

    def process_response(self, commit_response: DiffDataType) -> None:
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
        self._remove_traces(commit_response["traces"]["removed"])

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
            artifact["id"] = self.artifact_store[artifact["name"]]["id"]

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
                trace["sourceId"] = self.artifact_store[trace["sourceName"]]["id"]
            if trace["targetName"] in self.artifact_store:
                trace["targetId"] = self.artifact_store[trace["targetName"]]["id"]

    def _remove_artifacts(self, artifacts: List[Dict]) -> None:
        """
        Removes artifacts from store.
        :param artifacts: The artifacts to remove.
        :return: None
        """
        for artifact in artifacts:
            del self.artifact_store[artifact["name"]]

    def _remove_traces(self, traces: List[Dict]) -> None:
        """
        Removes traces from store.
        :param traces: The traces in the store.
        :return: None
        """
        for trace in traces:
            t_id = self.get_tid(trace)
            del self.trace_store[t_id]

    @staticmethod
    def get_tid(trace: Dict) -> str:
        """
        Creates trace ID for trace.
        :param trace: Trace to create ID for.
        :return: Trace ID.
        """
        return f"{trace['sourceName']}*{trace['targetName']}"
