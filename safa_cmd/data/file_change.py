from dataclasses import dataclass


@dataclass
class FileChange:
    file: str
    diff: str
    content_before: str
    summary: str
