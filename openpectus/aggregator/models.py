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
MethodState = Mdl.MethodState
ReadingCommand = Mdl.ReadingCommand
ReadingInfo = Mdl.ReadingInfo
TagValue = Mdl.TagValue


class ChannelStatusEnum(StrEnum):
    Unknown = auto()
    Connected = auto()
    Registered = auto()
    Disconnected = auto()


TagValueType = int | float | str | None
""" Represents the possible types of a tag value"""



class TagsInfo(BaseModel):
    map: Dict[str, Mdl.TagValue]

    def get(self, tag_name: str):
        return self.map.get(tag_name)

    def upsert(self, tag_value: Mdl.TagValue) -> bool:
        current = self.map.get(tag_value.name)
        if current is None:
            current = tag_value
            self.map[current.name] = current
            return True # was inserted
            # Store unit and type in plot log db
        else:
            if current.value != tag_value.value:
                current.value = tag_value.value
                current.timestamp = tag_value.timestamp
                # hold latest time written to db, and if difference exceeds a threshold, insert new value in db.

            if current.value_unit != tag_value.value_unit:
                logger.warning(f"Tag '{tag_value.name}' changed unit from '{current.value_unit}' to '{tag_value.value_unit}'. This is unexpected")

            return False # was updated


class EngineData(BaseModel):
    engine_id: str
    computer_name: str
    uod_name: str
    readings: List[Mdl.ReadingInfo] = []
    tags_info: TagsInfo = TagsInfo(map={})
    runlog: RunLog = RunLog(lines=[])
    control_state: ControlState = ControlState(is_running=False, is_holding=False, is_paused=False)
    method: Method = Method.empty()
    method_state: MethodState = MethodState.empty()
    tags_last_persisted: datetime | None = None

    @property
    def runtime(self):
        self.tags_info.get(Mdl.SystemTagName.run_time)
