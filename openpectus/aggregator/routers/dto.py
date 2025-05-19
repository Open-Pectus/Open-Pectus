from __future__ import annotations

import logging
from datetime import datetime
from enum import StrEnum, auto
from typing import Literal

import openpectus.aggregator.models as Mdl
from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import SkipJsonSchema

SystemStateEnum = Mdl.SystemStateEnum


class Dto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # deliver undefined instead of null for None values. Adapted from:
    # https://github.com/fastapi/fastapi/issues/3314#issuecomment-962932368
    def model_dump(self, *args, **kwargs):
        kwargs.pop('exclude_none', None)
        return super().model_dump(*args, exclude_none=True, **kwargs)


class AuthConfig(Dto):
    use_auth: bool
    authority_url: str | SkipJsonSchema[None] = None
    client_id: str | SkipJsonSchema[None] = None
    well_known_url: str | SkipJsonSchema[None] = None

    def __str__(self) -> str:
        if self.use_auth:
            return (f'{self.__class__.__name__}(authority_url="{self.authority_url}", ' +
                    f'client_id="{self.client_id}", well_known_url="{self.well_known_url}")')
        else:
            return f'{self.__class__.__name__}(use_auth={self.use_auth})'


class ServerErrorResponse(Dto):
    error: bool = True
    message: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(message="{self.message}")'


class ServerSuccessResponse(Dto):
    message: str | SkipJsonSchema[None] = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(message="{self.message}")'


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

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}", example="{self.example}")'


class UserRole(StrEnum):
    VIEWER = auto()
    ADMIN = auto()


class ControlState(Dto):
    is_running: bool
    is_holding: bool
    is_paused: bool

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(is_running={self.is_running}, ' +
                f'is_holding={self.is_holding}, is_paused={self.is_paused})')

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
    location: str | SkipJsonSchema[None] = None
    runtime_msec: int | SkipJsonSchema[None] = None
    current_user_role: UserRole
    uod_author_name: str | SkipJsonSchema[None] = None
    uod_author_email: str | SkipJsonSchema[None] = None
    # users: list[User] ?

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", name="{self.name}", state={self.state})'


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()
    CHOICE = auto()
    NONE = auto()


class ProcessValueCommandNumberValue(Dto):
    value: float | int
    value_unit: str | SkipJsonSchema[None] = None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    valid_value_units: list[str] | SkipJsonSchema[None] = None
    """ For values with a unit, provides the list valid alternative units """
    value_type: Literal[ProcessValueType.INT] | Literal[ProcessValueType.FLOAT]
    """ Specifies the type of allowed values. """

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(value={self.value}, value_unit="{self.value_unit}")'


class ProcessValueCommandFreeTextValue(Dto):
    value: str
    value_type: Literal[ProcessValueType.STRING]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(value="{self.value}")'


class ProcessValueCommandChoiceValue(Dto):
    value: str
    value_type: Literal[ProcessValueType.CHOICE]
    options: list[str]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(value="{self.value}")'


class ProcessValueCommand(Dto):
    command_id: str | SkipJsonSchema[None] = None
    name: str
    command: str
    disabled: bool | SkipJsonSchema[None] = None
    """ Indicates whether the command button should be disabled. """
    value: (ProcessValueCommandNumberValue |
            ProcessValueCommandFreeTextValue |
            ProcessValueCommandChoiceValue |
            SkipJsonSchema[None]) = None

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(command_id="{self.command_id}", name="{self.name}", ' +
                f'command="{self.command}", value={self.value})')


ProcessValueValueType = float | int | str | SkipJsonSchema[None]


def get_ProcessValueType_from_value(value: ProcessValueValueType) -> ProcessValueType:
    if value is None:
        return ProcessValueType.NONE
    if isinstance(value, str):
        return ProcessValueType.STRING
    if isinstance(value, int):
        return ProcessValueType.INT
    if isinstance(value, float):
        return ProcessValueType.FLOAT


class ProcessValue(Dto):
    """ Represents a process value. """
    name: str
    value: ProcessValueValueType = None
    value_formatted: str | SkipJsonSchema[None] = None
    value_unit: str | SkipJsonSchema[None] = None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    value_type: ProcessValueType
    """ Specifies the type of allowed values. """
    commands: list[ProcessValueCommand] | SkipJsonSchema[None] = None
    direction: Mdl.TagDirection
    simulated: bool | SkipJsonSchema[None] = None

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(name="{self.name}", value="{self.value}", ' +
                f'value_unit="{self.value_unit}", value_formatted="{self.value_formatted}"), ' +
                f'simulated="{self.simulated}"')

    @staticmethod
    def create(tag: Mdl.TagValue) -> ProcessValue:
        return ProcessValue(
            name=tag.name,
            value=tag.value,
            value_formatted=tag.value_formatted,
            value_type=get_ProcessValueType_from_value(tag.value),
            value_unit=tag.value_unit,
            commands=[],
            direction=tag.direction,
            simulated=tag.simulated
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
    command_id: str | SkipJsonSchema[None] = None
    command: str  # full command string, e.g. "start" or "foo: bar"
    source: CommandSource
    name: str | SkipJsonSchema[None] = None
    value: (ProcessValueCommandNumberValue |
            ProcessValueCommandFreeTextValue |
            ProcessValueCommandChoiceValue |
            SkipJsonSchema[None]) = None

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(command_id="{self.command_id}", ' +
                f'command="{self.command}", name="{self.name}", value={self.value})')


class RunLogLine(Dto):
    id: str
    command: ExecutableCommand
    start: datetime
    end: datetime | SkipJsonSchema[None] = None
    progress: float | SkipJsonSchema[None] = None  # between 0 and 1
    start_values: list[ProcessValue]
    end_values: list[ProcessValue]
    forcible: bool | SkipJsonSchema[None] = None
    cancellable: bool | SkipJsonSchema[None] = None
    forced: bool | SkipJsonSchema[None] = None
    cancelled: bool | SkipJsonSchema[None] = None

    def __str__(self) -> str:
        if self.cancelled:
            return f'{self.__class__.__name__}(id="{self.id}", command="{self.command}", cancelled={self.cancelled})'
        elif self.forced:
            return f'{self.__class__.__name__}(id="{self.id}", command="{self.command}", forced={self.forced})'
        elif self.progress is not None:
            return f'{self.__class__.__name__}(id="{self.id}", command="{self.command}", progress={self.progress})'
        else:
            return f'{self.__class__.__name__}(id="{self.id}", command="{self.command}")'

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

    def __str__(self) -> str:
        lines = [str(line) for line in self.lines]
        return f'{self.__class__.__name__}(lines={lines})'

    @staticmethod
    def empty() -> RunLog:
        return RunLog(lines=[])


class MethodLine(Dto):
    id: str
    content: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", content="{self.content}")'


class Method(Dto):
    lines: list[MethodLine]
    version: int
    last_author: str

    def __str__(self) -> str:
        lines = [str(line) for line in self.lines]
        return f'{self.__class__.__name__}(lines="{lines}", version="{self.version}", last_author="{self.last_author}")'

    @staticmethod
    def empty() -> Method:
        return Method(lines=[], version=0, last_author='')

    @staticmethod
    def from_model(method: Mdl.Method) -> Method:
        return Method(
            lines=[MethodLine(id=line.id, content=line.content) for line in method.lines],
            version=method.version,
            last_author=method.last_author
        )

class MethodVersion(Dto):
    version: int

class MethodState(Dto):
    started_line_ids: list[str]
    executed_line_ids: list[str]
    injected_line_ids: list[str]

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(started_line_ids={self.started_line_ids}, ' +
                f'executed_line_ids={self.executed_line_ids}, injected_line_ids={self.injected_line_ids})')

    @staticmethod
    def empty() -> MethodState:
        return MethodState(started_line_ids=[], executed_line_ids=[], injected_line_ids=[])

    @staticmethod
    def from_model(method_state: Mdl.MethodState) -> MethodState:
        return MethodState(started_line_ids=[_id for _id in method_state.started_line_ids],
                           executed_line_ids=[_id for _id in method_state.executed_line_ids],
                           injected_line_ids=[_id for _id in method_state.injected_line_ids])

class MethodAndState(Dto):
    method: Method
    state: MethodState

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(method={self.method}, state={self.state})'

    @staticmethod
    def empty() -> MethodAndState:
        return MethodAndState(method=Method.empty(), state=MethodState.empty())

    @staticmethod
    def from_models(method: Mdl.Method, method_state: Mdl.MethodState) -> MethodAndState:
        return MethodAndState(
            method=Method.from_model(method),
            state=MethodState.from_model(method_state)
        )


class ActiveUser(Dto):
    id: str
    name: str

    @staticmethod
    def from_model(active_user: Mdl.ActiveUser) -> ActiveUser:
        return ActiveUser(id=active_user.id, name=active_user.name)


class ActiveUsers(Dto):
    active_users: list[ActiveUser]

    @staticmethod
    def empty() -> ActiveUsers:
        return ActiveUsers(active_users=[])


class PlotColorRegion(Dto):
    process_value_name: str
    # Color string compatible with css e.g.:
    # '#aa33bb', 'rgb(0,0,0)', 'rgba(0,0,0,0)', 'red'
    value_color_map: dict[str | int | float, str]


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
        return PlotConfiguration(process_value_names_to_annotate=[],
                                 color_regions=[],
                                 sub_plots=[],
                                 x_axis_process_value_names=[])


# This class originally existed only to workaround the issue that OpenApi spec
# (or Pydantic) cannot express that elements in a list can be
# None/null/undefined.
# Properties on an object can be optional, so we use that via this
# wrapping class to express None values in the PlotLogEntry.values list.
# Feel free to refactor to remove this class if it becomes possible to
# express the above without it, and there is no other need for this class.
class PlotLogEntryValue(Dto):
    value: ProcessValueValueType = None
    tick_time: float


class PlotLogEntry(Dto):
    name: str
    values: list[PlotLogEntryValue]
    value_unit: str | SkipJsonSchema[None] = None
    value_type: ProcessValueType


class PlotLog(Dto):
    entries: dict[str, PlotLogEntry]


class RecentRun(Dto):
    """ Represents a historical run of a process unit. """
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

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_id="{self.engine_id}", run_id="{self.run_id}")'


class RecentRunMethod(Dto):
    id: str
    run_id: str
    method: Method
    method_state: MethodState

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", run_id="{self.run_id}")'


class RecentRunCsv(Dto):
    filename: str
    csv_content: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(filename="{self.filename}")'


class ErrorLogSeverity(StrEnum):
    Warning = auto()
    Error = auto()


class AggregatedErrorLogEntry(Dto):
    message: str
    created_time: datetime
    severity: ErrorLogSeverity
    occurrences: int = 1

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(message="{self.message}", created_time={self.created_time}, ' +
                f'severity={self.severity}, occurrences={self.occurrences})')

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

    def __str__(self) -> str:
        entries = [str(entry) for entry in self.entries]
        return f'{self.__class__.__name__}(entries="{entries}")'

    @staticmethod
    def from_model(model: Mdl.AggregatedErrorLog) -> AggregatedErrorLog:
        return AggregatedErrorLog(entries=[AggregatedErrorLogEntry.from_model(entry) for entry in model.entries])


class BuildInfo(Dto):
    build_number: str
    git_sha: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(build_number="{self.build_number}", git_sha="{self.git_sha}")'


# Lsp models

class TagDefinition(Dto):
    name: str
    unit: str | None = None
    # possibly value_type:

class CommandDefinition(Dto):
    name: str
    validator: str | None = None

class UodDefinition(Dto):
    # name: str
    # filename: str
    commands: list[CommandDefinition]
    system_commands: list[CommandDefinition]
    tags: list[TagDefinition]

    @staticmethod
    def from_model(model: Mdl.UodDefinition) -> UodDefinition:
        return UodDefinition(
            commands=[CommandDefinition(name=c.name, validator=c.validator) for c in model.commands],
            system_commands=[CommandDefinition(name=c.name, validator=c.validator) for c in model.system_commands],
            tags=[TagDefinition(name=t.name, unit=t.unit) for t in model.tags]
        )
