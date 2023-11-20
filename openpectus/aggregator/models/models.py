from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import Dict, List

from fastapi_websocket_rpc import RpcChannel
from openpectus.protocol.messages import RunLogMsg, ControlStateMsg, MethodMsg
from pydantic import BaseModel


class ChannelStatusEnum(StrEnum):
    Unknown = auto()
    Connected = auto()
    Registered = auto()
    Disconnected = auto()


@dataclass
class ChannelInfo:
    engine_id: str | None
    engine_name: str
    uod_name: str
    channel: RpcChannel
    status: ChannelStatusEnum = ChannelStatusEnum.Unknown


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



class ReadingCommand(BaseModel):
    name: str
    command: str


class ReadingDef(BaseModel):
    label: str
    tag_name: str
    valid_value_units: List[str] | None
    commands: List[ReadingCommand]




class EngineData(BaseModel):
    engine_id: str
    readings: List[ReadingDef] = []
    tags_info: TagsInfo = TagsInfo(map={})
    runlog: RunLogMsg = RunLogMsg.default()
    control_state: ControlStateMsg = ControlStateMsg.default()
    method: MethodMsg = MethodMsg.default()
