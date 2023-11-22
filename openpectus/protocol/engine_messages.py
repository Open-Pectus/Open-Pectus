from typing import List

import openpectus.protocol.messages as M
from pydantic import BaseModel


class EngineMessage(M.MessageBase):
    engine_id: str | None


class RegisterEngineMsg(M.MessageBase):
    """ Doesn't extend EngineMessage, because we don't have the engine_id yet """
    computer_name: str
    uod_name: str
    # uod file hash, file change date


class ReadingCommand(BaseModel):
    name: str
    command: str


class ReadingInfo(BaseModel):
    label: str
    tag_name: str
    valid_value_units: List[str] | None
    commands: List[ReadingCommand]


class UodInfoMsg(EngineMessage):
    readings: List[ReadingInfo]


TagValueType = str | int | float | None


class TagValue(BaseModel):
    name: str = ""
    value: TagValueType = None
    value_unit: str | None


class TagsUpdatedMsg(EngineMessage):
    tags: List[TagValue] = []


class RunLogLine(BaseModel):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: List[TagValue]
    end_values: List[TagValue]


class RunLogMsg(EngineMessage):
    id: str
    lines: List[RunLogLine]


class ControlStateMsg(EngineMessage):
    is_running: bool
    is_holding: bool
    is_paused: bool

    @classmethod
    def default() -> 'ControlStateMsg':
        return ControlStateMsg(is_running=False, is_holding=False, is_paused=False)
