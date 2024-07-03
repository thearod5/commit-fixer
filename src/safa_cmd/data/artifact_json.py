from typing import Dict, TypedDict


class ArtifactJson(TypedDict):
    name: str
    content: str
    summary: str
    attributes: Dict
