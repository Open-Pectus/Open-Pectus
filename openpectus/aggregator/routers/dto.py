from __future__ import annotations

import logging
from datetime import datetime
from enum import StrEnum, auto
from typing import Literal

import openpectus.aggregator.data.models as data_models
import openpectus.aggregator.models as Mdl
from pydantic import BaseModel

SystemStateEnum = Mdl.SystemStateEnum


class Dto(BaseModel):
    class Config:
        smart_union = True
        orm_mode = True

    # deliver undefined instead of null for None values. Adapted from https://github.com/fastapi/fastapi/issues/3314#issuecomment-962932368
    def dict(self, *args, **kwargs):
        kwargs.pop('exclude_none', None)
        return super().dict(*args, exclude_none=True, **kwargs)


class AuthConfig(Dto):
    use_auth: bool
    authority_url: str | None
    client_id: str | None
    well_known_url: str | None


class ServerErrorResponse(Dto):
    error: bool = True
    message: str


class ServerSuccessResponse(Dto):
    message: str | None = None


class ProcessUnitStateEnum(StrEnum):
    """ Represents the state of a process unit. """
    READY = auto()
    ERROR = auto()
    IN_PROGRESS = auto()
    NOT_ONLINE = auto()


class ProcessUnitState:
    class Ready(Dto):
        state: Literal[ProcessUnitStateEnum.READY]

    class Error(Dto):
        state: Literal[ProcessUnitStateEnum.ERROR]

    class InProgress(Dto):
        state: Literal[ProcessUnitStateEnum.IN_PROGRESS]
        progress_pct: int

    class NotOnline(Dto):
        state: Literal[ProcessUnitStateEnum.NOT_ONLINE]
        last_seen_date: datetime


class ProcessDiagram(Dto):
    svg: str


class CommandExample(Dto):
    name: str
    example: str


class UserRole(StrEnum):
    VIEWER = auto()
    ADMIN = auto()


class ControlState(Dto):
    is_running: bool
    is_holding: bool
    is_paused: bool

    @staticmethod
    def default() -> ControlState:
        return ControlState(
            is_running=False,
            is_holding=False,
            is_paused=False)


class ProcessUnit(Dto):
    """Represents a process unit. """
    id: str
    name: str
    state: ProcessUnitState.Ready | ProcessUnitState.Error | ProcessUnitState.InProgress | ProcessUnitState.NotOnline
    location: str | None
    runtime_msec: int | None
    current_user_role: UserRole
    # users: list[User] ?


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()
    CHOICE = auto()
    NONE = auto()


class ProcessValueCommandNumberValue(Dto):
    value: float | int
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    valid_value_units: list[str] | None
    """ For values with a unit, provides the list valid alternative units """
    value_type: Literal[ProcessValueType.INT] | Literal[ProcessValueType.FLOAT]
    """ Specifies the type of allowed values. """


class ProcessValueCommandFreeTextValue(Dto):
    value: str
    value_type: Literal[ProcessValueType.STRING]


class ProcessValueCommandChoiceValue(Dto):
    value: str
    value_type: Literal[ProcessValueType.CHOICE]
    options: list[str]


class ProcessValueCommand(Dto):
    command_id: str | None
    name: str
    command: str
    disabled: bool | None
    """ Indicates whether the command button should be disabled. """
    value: ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue | None


ProcessValueValueType = float | int | str | None


def get_ProcessValueType_from_value(value: ProcessValueValueType) -> ProcessValueType:
    if value is None:
        return ProcessValueType.NONE
    if isinstance(value, str):
        return ProcessValueType.STRING
    elif isinstance(value, int):
        return ProcessValueType.INT
    elif isinstance(value, float):
        return ProcessValueType.FLOAT
    else:
        raise ValueError("Invalid value type: " + type(value).__name__)


class ProcessValue(Dto):
    """ Represents a process value. """
    name: str
    value: ProcessValueValueType
    value_formatted: str | None
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    value_type: ProcessValueType
    """ Specifies the type of allowed values. """
    commands: list[ProcessValueCommand] | None
    direction: Mdl.TagDirection

    @staticmethod
    def create(tag: Mdl.TagValue) -> ProcessValue:
        return ProcessValue(
            name=tag.name,
            value=tag.value,
            value_formatted=tag.value_formatted,
            value_type=get_ProcessValueType_from_value(tag.value),
            value_unit=tag.value_unit,
            commands=[],
            direction=tag.direction
        )

    @staticmethod
    def create_w_commands(tag: Mdl.TagValue, commands: list[ProcessValueCommand]) -> ProcessValue:
        pv = ProcessValue.create(tag)
        pv.commands = commands
        return pv


class CommandSource(StrEnum):
    PROCESS_VALUE = auto()
    MANUALLY_ENTERED = auto()
    UNIT_BUTTON = auto()
    """ One of the engine control commands, eg. Start or Pause"""
    METHOD = auto()


class ExecutableCommand(Dto):
    command_id: str | None
    command: str  # full command string, e.g. "start" or "foo: bar"
    source: CommandSource
    name: str | None
    value: ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue | None


class RunLogLine(Dto):
    id: str
    command: ExecutableCommand
    start: datetime
    end: datetime | None
    progress: float | None  # between 0 and 1
    start_values: list[ProcessValue]
    end_values: list[ProcessValue]
    forcible: bool | None
    cancellable: bool | None
    forced: bool | None
    cancelled: bool | None

    @staticmethod
    def from_model(model: Mdl.RunLogLine) -> RunLogLine:
        return RunLogLine(
            id=model.id,
            command=ExecutableCommand(
                command_id=None,
                command=model.command_name,
                name=None,
                source=CommandSource.METHOD,
                value=None
            ),
            start=datetime.fromtimestamp(model.start),
            end=None if model.end is None else datetime.fromtimestamp(model.end),
            progress=model.progress,
            start_values=list(map(ProcessValue.create, model.start_values)),
            end_values=list(map(ProcessValue.create, model.end_values)),
            forcible=model.forcible,
            forced=model.forced,
            cancellable=model.cancellable,
            cancelled=model.cancelled
        )


class RunLog(Dto):
    lines: list[RunLogLine]

    @staticmethod
    def empty() -> RunLog:
        return RunLog(lines=[])


class MethodLine(Dto):
    id: str
    content: str


class Method(Dto):
    lines: list[MethodLine]

    @staticmethod
    def empty() -> Method:
        return Method(lines=[])


class MethodState(Dto):
    started_line_ids: list[str]
    executed_line_ids: list[str]
    injected_line_ids: list[str]

    @staticmethod
    def empty() -> MethodState:
        return MethodState(started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


class MethodAndState(Dto):
    method: Method
    state: MethodState

    @staticmethod
    def empty() -> MethodAndState:
        return MethodAndState(method=Method.empty(), state=MethodState.empty())


class PlotColorRegion(Dto):
    process_value_name: str
    value_color_map: dict[str | int | float, str]  # color string compatible with css e.g.: '#aa33bb', 'rgb(0,0,0)', 'rgba(0,0,0,0)', 'red'


class PlotAxis(Dto):
    label: str
    process_value_names: list[str]
    y_max: int | float
    y_min: int | float
    color: str


class SubPlot(Dto):
    axes: list[PlotAxis]
    ratio: int | float


class PlotConfiguration(Dto):
    process_value_names_to_annotate: list[str]
    color_regions: list[PlotColorRegion]
    sub_plots: list[SubPlot]
    x_axis_process_value_names: list[str]

    @staticmethod
    def empty() -> PlotConfiguration:
        return PlotConfiguration(process_value_names_to_annotate=[], color_regions=[], sub_plots=[], x_axis_process_value_names=[])


# This class exists only to workaround the issue that OpenApi spec (or Pydantic) cannot express that elements in a list can be None/null/undefined.
# Properties on an object can be optional, so we use that via this wrapping class to express None values in the PlotLogEntry.values list.
# Feel free to refactor to remove this class if it becomes possible to express the above without it.
class PlotLogEntryValue(Dto):
    value: ProcessValueValueType
    tick_time: float

    @classmethod
    def from_orm(cls, obj: data_models.PlotLogEntryValue) -> PlotLogEntryValue:
        mapped = super().from_orm(obj)
        if obj.value_int is not None:
            mapped.value = obj.value_int
        if obj.value_float is not None:
            mapped.value = obj.value_float
        if obj.value_str is not None:
            mapped.value = obj.value_str
        return mapped


class PlotLogEntry(Dto):
    name: str
    values: list[PlotLogEntryValue]
    value_unit: str | None
    value_type: ProcessValueType


class PlotLog(Dto):
    entries: dict[str, PlotLogEntry]


class RecentRun(Dto):
    """ Represents a historical run of a process unit. """
    id: str
    engine_id: str
    run_id: str
    started_date: datetime
    completed_date: datetime
    uod_filename: str
    uod_author_name: str
    uod_author_email: str
    engine_computer_name: str
    engine_version: str
    engine_hardware_str: str
    aggregator_computer_name: str
    aggregator_version: str
    contributors: list[str] = []


class RecentRunMethod(Dto):
    id: str
    run_id: str
    method: Method
    method_state: MethodState


class RecentRunCsv(Dto):
    filename: str
    csv_content: str


class ErrorLogSeverity(StrEnum):
    Warning = auto()
    Error = auto()


class AggregatedErrorLogEntry(Dto):
    message: str
    created_time: datetime
    severity: ErrorLogSeverity
    occurrences: int = 1

    @staticmethod
    def from_model(model: Mdl.AggregatedErrorLogEntry) -> AggregatedErrorLogEntry:
        return AggregatedErrorLogEntry(
            message=model.message,
            created_time=datetime.fromtimestamp(model.created_time),
            severity=ErrorLogSeverity.Error if model.severity == logging.ERROR else ErrorLogSeverity.Warning,
            occurrences=model.occurrences
        )

class AggregatedErrorLog(Dto):
    entries: list[AggregatedErrorLogEntry]

    @staticmethod
    def from_model(model: Mdl.AggregatedErrorLog) -> AggregatedErrorLog:
        return AggregatedErrorLog(entries=[AggregatedErrorLogEntry.from_model(entry) for entry in model.entries])


class BuildInfo(Dto):
    build_number: str
    git_sha: str
