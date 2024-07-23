from datetime import datetime
from typing import Union

from safa.constants import SAFA_DATETIME_FORMAT


def format_timestamp(timestamp: Union[str, float], output_format: str = "%m-%d %I:%M %p") -> str:
    if isinstance(timestamp, str):
        return datetime.strptime(timestamp, SAFA_DATETIME_FORMAT).strftime(output_format)
    return datetime.fromtimestamp(timestamp).strftime(output_format)
