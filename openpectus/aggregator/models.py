import logging
from datetime import datetime
from enum import StrEnum, auto

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
PlotColorRegion = Mdl.PlotColorRegion
PlotAxis = Mdl.PlotAxis
SubPlot = Mdl.SubPlot
PlotConfiguration = Mdl.PlotConfiguration
ErrorLogEntry = Mdl.ErrorLogEntry
ErrorLog = Mdl.ErrorLog
SystemStateEnum = Mdl.SystemStateEnum
TagDirection = Mdl.TagDirection


class ChannelStatusEnum(StrEnum):
    Unknown = auto()
    Connected = auto()
    Registered = auto()
    Disconnected = auto()


TagValueType = int | float | str | None
""" Represents the possible types of a tag value"""


class TagsInfo(BaseModel):
    map: dict[str, Mdl.TagValue]

    def get(self, tag_name: str):
        return self.map.get(tag_name)

    def upsert(self, tag_value: Mdl.TagValue) -> bool:
        current = self.map.get(tag_value.name)
        if current is None:
            self.map[tag_value.name] = tag_value
            return True  # was inserted
        else:
            if current.value_unit != tag_value.value_unit:
                logger.warning(f"Tag '{tag_value.name}' changed unit from '{current.value_unit}' to " +
                               f"'{tag_value.value_unit}'. This is unexpected")
            current.value = tag_value.value
            current.tick_time = tag_value.tick_time
            return False  # was updated


class RunData(BaseModel):
    run_started: datetime | None = None
    method_state: MethodState = MethodState.empty()
    runlog: RunLog = RunLog(lines=[])
    latest_persisted_tick_time: float | None = None
    error_log: ErrorLog = ErrorLog.empty()
    interrupted_by_error: bool = False


class EngineData(BaseModel):
    engine_id: str
    computer_name: str
    engine_version: str
    hardware_str: str = "N/A"
    uod_name: str
    location: str
    readings: list[Mdl.ReadingInfo] = []
    tags_info: TagsInfo = TagsInfo(map={})
    control_state: ControlState = ControlState(is_running=False, is_holding=False, is_paused=False)
    method: Method = Method.empty()
    run_data: RunData = RunData()
    plot_configuration: PlotConfiguration = PlotConfiguration.empty()

    @property
    def runtime(self):
        return self.tags_info.get(Mdl.SystemTagName.RUN_TIME)

    @property
    def run_id(self):
        run_id_tag = self.tags_info.get(Mdl.SystemTagName.RUN_ID)
        return str(run_id_tag.value) if run_id_tag is not None and run_id_tag.value is not None else None

    @property
    def system_state(self):
        return self.tags_info.get(Mdl.SystemTagName.SYSTEM_STATE)
