from typing import Dict, Optional, TypedDict


class ArtifactJson(TypedDict):
    id: str
    name: str
    content: str
    summary: str
    attributes: Dict


def create_artifact(name: Optional[str], type: Optional[str], body: Optional[str] = None, summary: Optional[str] = None) -> Dict:
    """
    Creates artifact dictionary.
    :param name: Name of the artifact
    :param type: Type of the artifact (e.g. Code)
    :param body: Content of the artifact.
    :param summary: Content summary if one exists.
    :return: Dict.
    """
    if body is None:
        body = ""
    if summary is None:
        summary = ""
    return {
        "name": name,
        "summary": summary,
        "body": body,
        "type": type
    }
