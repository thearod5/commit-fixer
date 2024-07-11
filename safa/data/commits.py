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
