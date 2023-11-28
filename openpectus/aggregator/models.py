import logging
from datetime import datetime
from enum import StrEnum, auto
from typing import Dict, List

import openpectus.protocol.models as Mdl
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# aliases so users of this file don't have to know about the protocol models
RunLogLine = Mdl.RunLogLine
RunLog = Mdl.RunLog
ControlState = Mdl.ControlState
Method = Mdl.Method
MethodLine = Mdl.MethodLine
ReadingCommand = Mdl.ReadingCommand
ReadingInfo = Mdl.ReadingInfo


class ChannelStatusEnum(StrEnum):
    Unknown = auto()
    Connected = auto()
    Registered = auto()
    Disconnected = auto()


TagValueType = int | float | str | None
""" Represents the possible types of a tag value"""


class TagInfo(BaseModel):
    name: str
    value: TagValueType
    value_unit: str | None
    updated: datetime


class TagsInfo(BaseModel):
    map: Dict[str, TagInfo]

    def get(self, tag_name: str):
        return self.map.get(tag_name)

    def upsert(self, name: str, value: TagValueType, unit: str | None):
        current = self.map.get(name)
        now = datetime.now()
        if current is None:
            current = TagInfo(name=name, value=value, value_unit=unit, updated=now)
            self.map[name] = current
        else:
            if current.value != value:
                current.value = value
                current.updated = now

            if current.value_unit != unit:
                logger.warning(f"Tag '{name}' changed unit from '{current.value_unit}' to '{unit}'. This is unexpected")


class EngineData(BaseModel):
    engine_id: str
    computer_name: str
    uod_name: str
    readings: List[Mdl.ReadingInfo] = []
    tags_info: TagsInfo = TagsInfo(map={})
    runlog: RunLog = RunLog(lines=[])
    control_state: ControlState = ControlState(is_running=False, is_holding=False, is_paused=False)
    method: Method = Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])
