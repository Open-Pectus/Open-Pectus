from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from typing import Literal, List, Dict

import openpectus.aggregator.data.models as data_models
from openpectus.aggregator.models import TagInfo
from openpectus.protocol.models import ReadingInfo
from pydantic import BaseModel


class ServerErrorResponse(BaseModel):
    error: bool = True
    message: str


class ProcessUnitStateEnum(StrEnum):
    """ Represents the state of a process unit. """
    READY = auto()
    IN_PROGRESS = auto()
    NOT_ONLINE = auto()


class ProcessUnitState:
    class Ready(BaseModel):
        state: Literal[ProcessUnitStateEnum.READY]

    class InProgress(BaseModel):
        state: Literal[ProcessUnitStateEnum.IN_PROGRESS]
        progress_pct: int

    class NotOnline(BaseModel):
        state: Literal[ProcessUnitStateEnum.NOT_ONLINE]
        last_seen_date: datetime


class ProcessDiagram(BaseModel):
    svg: str


class CommandExample(BaseModel):
    name: str
    example: str


class UserRole(StrEnum):
    VIEWER = auto()
    ADMIN = auto()


class ControlState(BaseModel):
    is_running: bool
    is_holding: bool
    is_paused: bool

    @staticmethod
    def default() -> ControlState:
        return ControlState(
            is_running=False,
            is_holding=False,
            is_paused=False)


class ProcessUnit(BaseModel):
    """Represents a process unit. """
    id: str
    name: str
    state: ProcessUnitState.Ready | ProcessUnitState.InProgress | ProcessUnitState.NotOnline
    location: str | None
    runtime_msec: int | None
    current_user_role: UserRole
    # users: List[User] ?


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()
    CHOICE = auto()
    NONE = auto()


class ProcessValueCommandNumberValue(BaseModel):
    value: float | int
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    valid_value_units: List[str] | None
    """ For values with a unit, provides the list valid alternative units """
    value_type: Literal[ProcessValueType.INT] | Literal[ProcessValueType.FLOAT]
    """ Specifies the type of allowed values. """


class ProcessValueCommandFreeTextValue(BaseModel):
    value: str
    value_type: Literal[ProcessValueType.STRING]


class ProcessValueCommandChoiceValue(BaseModel):
    value: str
    value_type: Literal[ProcessValueType.CHOICE]
    options: List[str]


class ProcessValueCommand(BaseModel):
    name: str
    command: str
    disabled: bool | None
    """ Indicates whether the command button should be disabled. """
    value: ProcessValueCommandNumberValue | ProcessValueCommandFreeTextValue | ProcessValueCommandChoiceValue | None


ProcessValueValueType = None | float | int | str


def get_ProcessValueType_from_value(value: ProcessValueValueType) -> ProcessValueType:
    if value is None:
        return ProcessValueType.STRING  # hmm
    if isinstance(value, str):
        return ProcessValueType.STRING
    elif isinstance(value, int):
        return ProcessValueType.INT
    elif isinstance(value, float):
        return ProcessValueType.FLOAT
    else:
        raise ValueError("Invalid value type: " + type(value).__name__)


class ProcessValue(BaseModel):
    """ Represents a process value. """
    name: str
    value: ProcessValueValueType
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    value_type: ProcessValueType
    """ Specifies the type of allowed values. """
    commands: List[ProcessValueCommand] | None

    @staticmethod
    def from_message(r: ReadingInfo, ti: TagInfo) -> ProcessValue:
        return ProcessValue(
            name=r.label,
            value=ti.value,
            value_type=get_ProcessValueType_from_value(ti.value),
            value_unit=ti.value_unit,
            commands=[]
        )
        # commands=[ProcessValueCommand(name=c.name, command=c.command) for c in r.commands])


class CommandSource(StrEnum):
    PROCESS_VALUE = auto()
    MANUALLY_ENTERED = auto()
    UNIT_BUTTON = auto()
    """ One of the engine control commands, eg. Start or Pause"""
    METHOD = auto()


class ExecutableCommand(BaseModel):
    command: str  # full command string, e.g. "start" or "foo: bar"
    source: CommandSource
    name: str | None


class RunLogLine(BaseModel):
    id: int
    command: ExecutableCommand
    start: datetime
    end: datetime | None
    progress: float | None  # between 0 and 1
    start_values: List[ProcessValue]
    end_values: List[ProcessValue]
    forcible: bool | None
    cancellable: bool | None
    forced: bool | None
    cancelled: bool | None


class RunLog(BaseModel):
    lines: List[RunLogLine]


class MethodLine(BaseModel):
    id: str
    content: str


class Method(BaseModel):
    lines: List[MethodLine]


class MethodState(BaseModel):
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]


class MethodAndState(BaseModel):
    method: Method
    state: MethodState


class PlotColorRegion(BaseModel):
    process_value_name: str
    value_color_map: dict[str | int | float, str]  # color string compatible with css e.g.: '#aa33bb', 'rgb(0,0,0)', 'rgba(0,0,0,0)', 'red'


class PlotAxis(BaseModel):
    label: str
    process_value_names: List[str]
    y_max: int | float
    y_min: int | float
    color: str


class SubPlot(BaseModel):
    axes: List[PlotAxis]
    ratio: int | float


class PlotConfiguration(BaseModel):
    process_value_names_to_annotate: List[str]
    color_regions: List[PlotColorRegion]
    sub_plots: List[SubPlot]
    x_axis_process_value_names: List[str]


# This class exists only to workaround the issue that OpenApi spec (or Pydantic) cannot express that elements in a list can be None/null/undefined.
# Properties on an object can be optional, so we use that via this wrapping class to express None values in the PlotLogEntry.values list.
# Feel free to refactor to remove this class if it becomes possible to express the above without it.
class PlotLogEntryValue(BaseModel):
    value: ProcessValueValueType

    class Config:  # TODO: change in pydantic v2
        orm_mode = True

    @classmethod
    def from_orm(cls, obj: data_models.PlotLogEntryValue) -> PlotLogEntryValue:
        mapped = super().from_orm(obj)
        if obj.value_int is not None: mapped.value = obj.value_int
        if obj.value_float is not None: mapped.value = obj.value_float
        if obj.value_str is not None: mapped.value = obj.value_str
        return mapped


class PlotLogEntry(BaseModel):
    name: str
    values: List[PlotLogEntryValue]
    value_unit: str | None
    value_type: ProcessValueType

    class Config:  # TODO: change in pydantic v2
        orm_mode = True


class PlotLog(BaseModel):
    entries: Dict[str, PlotLogEntry]

    class Config:  # TODO: change in pydantic v2
        orm_mode = True


class BatchJob(BaseModel):
    """ Represents a current or historical run of a process unit. """
    id: str
    unit_id: str
    unit_name: str
    started_date: datetime
    completed_date: datetime
    contributors: List[str] = []


class BatchJobCsv(BaseModel):
    filename: str
    csv_content: str
