import logging
from typing import List

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ReadingCommand(BaseModel):
    name: str
    command: str


class ReadingInfo(BaseModel):
    label: str
    tag_name: str
    valid_value_units: List[str] | None
    commands: List[ReadingCommand]


TagValueType = str | int | float | None


class TagValue(BaseModel):
    name: str = ""
    value: TagValueType = None
    value_unit: str | None


class RunLogLine(BaseModel):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: List[TagValue]
    end_values: List[TagValue]


class RunLog(BaseModel):
    lines: List[RunLogLine]


class MethodLine(BaseModel):
    id: str
    content: str


class Method(BaseModel):
    lines: List[MethodLine]
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]


class ControlState(BaseModel):
    is_running: bool
    is_holding: bool
    is_paused: bool
