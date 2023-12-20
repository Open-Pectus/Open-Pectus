from __future__ import annotations
import logging
from enum import StrEnum, auto
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


TagValueType = None | float | int | str


class SystemTagName(StrEnum):
    run_time = auto()
    system_state = auto()


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

    @staticmethod
    def empty() -> Method:
        return Method(lines=[])

    @staticmethod
    def from_pcode(pcode: str) -> Method:
        method = Method.empty()
        line_num: int = 1
        for line in pcode.splitlines():
            method.lines.append(MethodLine(id=f"id_{line_num}", content=line))
            line_num += 1
        return method


class MethodState(BaseModel):
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]

    @staticmethod
    def empty() -> MethodState:
        return MethodState(started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


class ControlState(BaseModel):
    is_running: bool
    is_holding: bool
    is_paused: bool
