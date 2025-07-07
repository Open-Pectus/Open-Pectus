from __future__ import annotations
import logging
import math
import time
from datetime import datetime
from enum import StrEnum, auto
from typing import Iterable, Literal

import openpectus.protocol.models as Mdl
from pydantic import BaseModel, ConfigDict, NonNegativeInt, Field

logger = logging.getLogger(__name__)

# aliases so users of this file don't have to know about the protocol models
RunLogLine = Mdl.RunLogLine
RunLog = Mdl.RunLog
ControlState = Mdl.ControlState
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
UodDefinition = Mdl.UodDefinition

class Method(Mdl.Method):
    version: int
    last_author: str

    @staticmethod
    def empty() -> Method:
        return Method(lines=Mdl.Method.empty().lines, version=0, last_author='')


class AggregatedErrorLogEntry(BaseModel):
    message: str
    created_time: float
    severity: int
    occurrences: int = 1

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(message="{self.message}", created_time={self.created_time}, ' +
                f'severity={self.severity}, occurrences={self.occurrences})')

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

    def __str__(self) -> str:
        entries = [str(entry) for entry in self.entries]
        return f'{self.__class__.__name__}(entries={entries})'

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
            current.simulated = tag_value.simulated
            return False  # was updated

    def __str__(self) -> str:
        tags = [str(tag) for tag in self.map.keys()]
        return f"{self.__class__.__name__}(tags={tags})"

    def get_last_modified_time(self) -> datetime | None:
        if len(self.map.keys()) == 0:
            return None
        max_tick_time = max(t.tick_time for t in self.map.values())
        return datetime.fromtimestamp(max_tick_time)

    def values(self) -> Iterable[TagValue]:
        return self.map.values()

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
        return (f'{self.__class__.__name__}(run_id="{self.run_id}", run_started={self.run_started}, ' +
                f'interrupted_by_error={self.interrupted_by_error})')

    @staticmethod
    def empty(run_id: str, run_started: datetime) -> RunData:
        return RunData(run_id=run_id, run_started=run_started)


class ActiveUser(BaseModel):
    """ Represents a user looking at the frontend details page for a process unit  """

    id: str  # oid from identity token or a made up id from frontend if Anon, used to get profile photos from ms graph api
    name: str  # Same value as emitted by openpectus.aggregator.auth.user_name

class Contributor(BaseModel):
    """ Represents a contributor to a process unit """

    id: str | None  # oid from identity token, or None if Anon
    name: str  # Same value as emitted by openpectus.aggregator.auth.user_name

    # from https://github.com/pydantic/pydantic/issues/1303#issuecomment-599712964
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class EngineData:
    """ Data stored by aggregator for each connected engine. """

    # Note: Not a BaseModel subclass since it doesn't need to be and BaseModel apparently
    # has a bug concerning the way we use _run_data, run_data and has_run().

    def __init__(self, engine_id: str, computer_name: str, engine_version: str, uod_name: str, uod_author_name: str,
                 uod_author_email: str, uod_filename: str, location: str,
                 hardware_str: str = "N/A", data_log_interval_seconds: float = math.inf) -> None:
        self.engine_id: str = engine_id
        self.computer_name: str = computer_name
        self.engine_version: str = engine_version
        self.uod_name: str = uod_name
        self.uod_author_name: str = uod_author_name
        self.uod_author_email: str = uod_author_email
        self.uod_filename: str = uod_filename
        self.location: str = location
        self.readings: list[Mdl.ReadingInfo] = []
        """ Contains the definition of the engine's process values. """
        self.commands: list[Mdl.CommandInfo] = []
        """ Contains the uod commands that are not related to a process value. """
        self.tags_info: TagsInfo = TagsInfo(map={})
        """ Contains the most current tag values. """
        self.uod_definition: Mdl.UodDefinition | None = None
        self.control_state: ControlState = ControlState(is_running=False, is_holding=False, is_paused=False)
        self.method: Method = Method.empty()
        self._run_data: RunData | None = None
        self.error_log: AggregatedErrorLog = AggregatedErrorLog.empty()
        self.method_state: MethodState = MethodState.empty()
        self.plot_configuration: PlotConfiguration = PlotConfiguration.empty()
        self.contributors: set[Contributor] = set()
        self.active_users: dict[str, ActiveUser] = dict()
        self.required_roles: set[str] = set()
        self.hardware_str: str = hardware_str
        self.data_log_interval_seconds: float = data_log_interval_seconds

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_id="{self.engine_id}", control_state={self.control_state})'

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

    def reset_run(self):
        """ Clear all data associated with a run, control_state, error_log, method state (not method content) and run_data,
        including run log and run_id. Call when run is complete to get ready for a new run. """
        self._run_data = None
        self.control_state = ControlState(is_running=False, is_holding=False, is_paused=False)
        self.error_log.clear()
        self.method_state = MethodState.empty()
        self.contributors = set()


class NotificationScope(StrEnum):
    PROCESS_UNITS_WITH_RUNS_IVE_CONTRIBUTED_TO = auto()
    PROCESS_UNITS_I_HAVE_ACCESS_TO = auto()
    SPECIFIC_PROCESS_UNITS = auto()

class NotificationTopic(StrEnum):
    RUN_START = auto()
    RUN_STOP = auto()
    RUN_PAUSE = auto()
    BLOCK_START = auto()
    NOTIFICATION_CMD = auto()
    WATCH_TRIGGERED = auto()
    NEW_CONTRIBUTOR = auto()
    METHOD_ERROR = auto()
    NETWORK_ERRORS = auto()

class WebPushNotificationPreferences(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    user_roles: set[str]
    scope: NotificationScope
    topics: set[NotificationTopic]
    process_units: set[str]



class WebPushAction(BaseModel):
    action: Literal['navigate']
    title: str
    icon: str | None = None


class WebPushData(BaseModel):
    process_unit_id: str | None = None
    contributor_id: str | None = None


class WebPushNotification(BaseModel): # see https://developer.mozilla.org/en-US/docs/Web/API/Notification/Notification#parameters for more information
    actions: list[WebPushAction] = Field(default_factory=list)  # buttons user can press
    badge: str | None = None  # url for smaller image for e.g. the notifcation bar
    body: str | None = None
    data: WebPushData = Field(default_factory=WebPushData)  # arbitrary data the frontend can use for e.g. navigating when user clicks an action button
    icon: str | None = "/assets/icons/icon-192x192.png"  # url
    image: str | None = None  # url
    renotify: bool | None = None  # if set to true, tag must also be set
    requireInteraction: bool | None = None  # notification will automatically close after a time unless this is set to True
    silent: bool | None = None  # if True, notification will not make sound or vibration
    tag: str | None = None  # an id for the notification, used for renotify
    timestamp: NonNegativeInt | None = Field(default_factory=lambda: int(time.time()*1000))  # unix timestamp in milliseconds
    title: str
    vibrate: list[NonNegativeInt] | None = None

