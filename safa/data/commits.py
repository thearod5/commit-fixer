from typing import List, TypeVar

from typing_extensions import Generic, TypedDict

EntityType = TypeVar('EntityType')


class DeltaType(TypedDict, Generic[EntityType]):
    added: List[EntityType]
    removed: List[EntityType]
    modified: List[EntityType]


class DiffDataType(TypedDict):
    artifacts: DeltaType
    traces: DeltaType


def create_empty_diff() -> "DiffDataType":
    """
    Creates empty diff.
    :return: The safa commit dict containing an empty diff.
    """
    return {
        "artifacts": {
            "added": [],
            "removed": [],
            "modified": []
        }, "traces": {
            "added": [],
            "removed": [],
            "modified": []
        }
    }
