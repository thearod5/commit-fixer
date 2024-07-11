from typing import Optional

import git
from git import Commit, Diff

from safa.constants import EMPTY_TREE_HEXSHA
from safa.data.artifact import create_artifact
from safa.data.commits import DeltaType, DiffDataType
from safa.utils.commits import create_commit_artifact, decode_blob

BUG_FIX_FLAG = True


def calculate_diff(repo: git.Repo, commit: Commit, starting_commit: Optional[Commit] = None, **commit_kwargs) -> DiffDataType:
    """
    Calculates the differences to commit.
    :param repo: The repository to calculate diff for.
    :param commit: The commit whose final state is the one desired.
    :param starting_commit: The commit to start diff from, if none assume empty repository.
    :param commit_kwargs: Kwargs passed to commit artifact construction.
    :return: Delta information.
    """
    if starting_commit is None:
        starting_commit = repo.tree(EMPTY_TREE_HEXSHA)

    diffs = starting_commit.diff(commit)

    artifact_delta: DeltaType = {"added": [], "removed": [], "modified": []}
    for diff in diffs:
        add_diff_to_delta(artifact_delta, diff)

    commit_artifact = create_commit_artifact(repo, commit, **commit_kwargs)
    traces = [{
        "sourceName": a["name"],
        "targetName": commit_artifact["name"]
    } for mod_type, artifacts in artifact_delta.items()
        for a in artifacts if not BUG_FIX_FLAG or mod_type != "removed"]  # type: ignore

    artifact_delta["added"].append(commit_artifact)
    commit_data: DiffDataType = {
        "artifacts": artifact_delta,
        "traces": {
            "added": traces,
            "removed": [],
            "modified": []
        }
    }
    return commit_data


def add_diff_to_delta(delta_data: DeltaType, diff: Diff) -> None:
    """
    Translates diff to commit data.
    :param delta_data: Commit data to be added to.
    :param diff: Diff to translate.
    :return: None
    """
    if diff.new_file:
        delta_data["added"].append(create_artifact(
            name=diff.b_path, type="Code", body=decode_blob(diff.b_blob)
        ))
    elif diff.deleted_file:
        delta_data["removed"].append(create_artifact(
            name=diff.a_path, type="Code", body=""
        ))
    else:
        if diff.renamed_file:
            delta_data["removed"].append(create_artifact(
                name=diff.a_path, type="Code", body=""
            ))
            delta_data["added"].append(create_artifact(
                name=diff.b_path, type="Code", body=decode_blob(diff.b_blob)
            ))
        else:
            delta_data["modified"].append(create_artifact(
                name=diff.b_path, type="Code", body=decode_blob(diff.b_blob)
            ))
