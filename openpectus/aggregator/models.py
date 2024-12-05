from __future__ import annotations
import logging
import math
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
CommandInfo = Mdl.CommandInfo
TagValue = Mdl.TagValue
PlotColorRegion = Mdl.PlotColorRegion
PlotAxis = Mdl.PlotAxis
SubPlot = Mdl.SubPlot
PlotConfiguration = Mdl.PlotConfiguration
ErrorLogEntry = Mdl.ErrorLogEntry
ErrorLog = Mdl.ErrorLog
SystemStateEnum = Mdl.SystemStateEnum
TagDirection = Mdl.TagDirection


class AggregatedErrorLogEntry(BaseModel):
    message: str
    created_time: float
    severity: int
    occurrences: int = 1

    @staticmethod
    def from_entry(entry: ErrorLogEntry):
        return AggregatedErrorLogEntry(
            message=entry.message,
            created_time=entry.created_time,
            severity=entry.severity,
            occurrences=1
        )


class AggregatedErrorLog(BaseModel):
    entries: list[AggregatedErrorLogEntry]

    @staticmethod
    def empty() -> AggregatedErrorLog:
        return AggregatedErrorLog(entries=[])

    def clear(self):
        self.entries.clear()

    def aggregate_with(self, error_log: ErrorLog):
        """ Append the given log entries to the current log entries while deduplicating and aggregating entries. """
        latest = self.entries[-1] if len(self.entries) > 0 else None
        for entry in error_log.entries:
            assert entry is not None, "log entry should not be None"
            if latest is not None and entry.message == latest.message and entry.severity == latest.severity:
                if latest.created_time < entry.created_time:
                    latest.created_time = entry.created_time
                    latest.occurrences += 1
                elif latest.created_time == entry.created_time:
                    logger.warning(f"Duplicate log entry with same created_time: {entry.message}")
                else:
                    logger.warning(f"Duplicate log entry with earlier created_time: {entry.message}")
            else:
                latest = AggregatedErrorLogEntry.from_entry(entry)
                self.entries.append(latest)


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
            if __debug__:
                if current.tick_time > tag_value.tick_time:
                    cur_time = datetime.fromtimestamp(current.tick_time).strftime("%H:%M:%S")
                    new_time = datetime.fromtimestamp(tag_value.tick_time).strftime("%H:%M:%S")
                    logger.warning(f"Tag '{tag_value.name}' was updated with an earlier time " +
                                   f"{new_time} than the current time {cur_time}.")
            current.value = tag_value.value
            current.value_formatted = tag_value.value_formatted
            current.tick_time = tag_value.tick_time
            return False  # was updated

    def __str__(self) -> str:
        return f"TagsInfo({','.join(self.map.keys())})"

    def get_last_modified_time(self) -> datetime | None:
        if len(self.map.keys()) == 0:
            return None
        max_tick_time = max(t.tick_time for t in self.map.values())
        return datetime.fromtimestamp(max_tick_time)


class RunData(BaseModel):
    """ Represents data that strictly belongs in a specific run. """
    run_id: str
    run_started: datetime
    runlog: RunLog = RunLog.empty()
    latest_persisted_tick_time: float | None = None
    """ The time assigned to the last persisted set of values """
    latest_tag_time: float | None = None
    """ The time of the latest tag update, persisted or not """
    interrupted_by_error: bool = False

    def __str__(self) -> str:
        return f"RunData({self.run_id=}, {self.run_started=}, " + \
               f"interrupted_by_error:{self.interrupted_by_error})"

    @staticmethod
    def empty(run_id: str, run_started: datetime) -> RunData:
        return RunData(run_id=run_id, run_started=run_started)


class EngineData(BaseModel):
    engine_id: str
    computer_name: str
    engine_version: str
    hardware_str: str = "N/A"
    uod_name: str
    uod_author_name: str
    uod_author_email: str
    uod_filename: str
    location: str
    readings: list[Mdl.ReadingInfo] = []
    """ Contains the definition of the engine's process values. """
    commands: list[Mdl.CommandInfo] = []
    """ Contains the uod commands that are not related to a process value. """
    tags_info: TagsInfo = TagsInfo(map={})
    """ Contains the most current tag values. """
    control_state: ControlState = ControlState(is_running=False, is_holding=False, is_paused=False)
    method: Method = Method.empty()
    _run_data: RunData | None = None
    error_log: AggregatedErrorLog = AggregatedErrorLog.empty()
    method_state: MethodState = MethodState.empty()
    plot_configuration: PlotConfiguration = PlotConfiguration.empty()
    contributors: set[str] = set()
    required_roles: set[str] = set()
    data_log_interval_seconds: float = math.inf

    @property
    def run_data(self) -> RunData:
        if self._run_data is None:
            raise ValueError("Run data is not set. Guard access with call to has_run()")
        return self._run_data

    @run_data.setter
    def run_data(self, value: RunData):
        self._run_data = value

    @property
    def runtime(self):
        return self.tags_info.get(Mdl.SystemTagName.RUN_TIME)

    @property
    def system_state(self):
        return self.tags_info.get(Mdl.SystemTagName.SYSTEM_STATE)

    def has_run(self) -> bool:
        """ Determine whether run_data is available, that is, whether a run is active. """
        return self._run_data is not None

    def has_this_run(self, run_id: str) -> bool:
        """ Whether run_data is available and belonging to the given run_id. """
        return self.run_data is not None and self.run_data.run_id == run_id

    def reset_run(self):
        """ Clear all data associated with a run, control_state, error_log, method state (not method content) and run_data, 
        including run log and run_id. Call when run is complete to get ready for a new run. """
        self._run_data = None
        self.control_state = ControlState(is_running=False, is_holding=False, is_paused=False)
        self.error_log.clear()
        self.method_state = MethodState.empty()

    def __str__(self) -> str:
        return f"EngineData(engine_id:{self.engine_id}, control_state':{self.control_state})"
