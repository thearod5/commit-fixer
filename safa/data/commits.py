from typing import List, TypeVar, TypedDict

EntityType = TypeVar('EntityType')


class DeltaType(TypedDict):
    added: List[EntityType]
    removed: List[EntityType]
    modified: List[EntityType]


class DiffDataType(TypedDict):
    artifacts: DeltaType
    traces: DeltaType
