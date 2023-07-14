from __future__ import annotations
from datetime import datetime
from enum import StrEnum, auto
from typing import Literal, List
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

import openpectus.aggregator.deps as agg_deps
from openpectus.protocol.aggregator import Aggregator, ChannelInfo, ReadingDef, TagInfo
from openpectus.protocol.messages import InvokeCommandMsg


router = APIRouter(tags=["process_unit"])


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


class UserRole(StrEnum):
    VIEWER = auto()
    ADMIN = auto()


class ProcessUnit(BaseModel):
    """Represents a process unit. """
    id: str
    name: str
    state: ProcessUnitState.Ready | ProcessUnitState.InProgress | ProcessUnitState.NotOnline
    location: str | None
    runtime_msec: int | None
    current_user_role: UserRole
    # users: List[User] ?


def create_pu(item: ChannelInfo) -> ProcessUnit:
    # TODO define source of all fields
    unit = ProcessUnit(
            id=item.client_id or "(error)",
            name=f"{item.engine_name} ({item.uod_name})",
            state=ProcessUnitState.Ready(state=ProcessUnitStateEnum.READY),
            location="Unknown location",
            runtime_msec=189309,
            current_user_role=UserRole.ADMIN)
    return unit


@router.get("/process_unit/{unit_id}")
def get_unit(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> ProcessUnit | None:
    ci = agg.get_client_channel(client_id=unit_id)
    if ci is None:
        return None
    return create_pu(ci)


@router.get("/process_units")
def get_units(agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[ProcessUnit]:
    units: List[ProcessUnit] = []
    for channel_id, item in agg.channel_map.items():
        unit = create_pu(item)
        units.append(unit)
    return units


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()
    CHOICE = auto()


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


def get_ProcessValueType_from_value(value: str | float | int | None) -> ProcessValueType:
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
    value: str | float | int | None
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    value_type: ProcessValueType
    """ Specifies the type of allowed values. """
    commands: List[ProcessValueCommand] | None

    @staticmethod
    def from_message(r: ReadingDef, ti: TagInfo) -> ProcessValue:
        return ProcessValue(
                name=r.label,
                value=ti.value,
                value_type=get_ProcessValueType_from_value(ti.value),
                value_unit=ti.value_unit,
                commands=[])
                # commands=[ProcessValueCommand(name=c.name, command=c.command) for c in r.commands])


@router.get("/process_unit/{unit_id}/process_values")
def get_process_values(unit_id: str, response: Response, agg: Aggregator = Depends(agg_deps.get_aggregator)) \
        -> List[ProcessValue]:
    # parm last_seen

    response.headers["Cache-Control"] = "no-store"

    client_data = agg.client_data_map.get(unit_id)
    if client_data is None:
        return []

    tags_info = client_data.tags_info.map

    print("Readings", client_data.readings)
    print("Tags", tags_info)

    pvs: List[ProcessValue] = []
    for r in client_data.readings:
        ti = tags_info.get(r.tag_name)
        if ti is not None:
            pvs.append(ProcessValue.from_message(r, ti))
    return pvs


class CommandSource(StrEnum):
    PROCESS_VALUE = auto()
    MANUALLY_ENTERED = auto()
    UNIT_BUTTON = auto()


class ExecutableCommand(BaseModel):
    command: str  # full command string, e.g. "start" or "foo: bar"
    source: CommandSource
    name: str | None


@router.post("/process_unit/{unit_id}/execute_command")
async def execute_command(unit_id: str, command: ExecutableCommand, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    print("command", str(command))
    cmd_line = command.command
    if ":" in cmd_line:
        split = command.command.split(":", maxsplit=1)
        cmd_name, cmd_args = split[0], split[1]  # TODO watch out for "" vs None as cmd_args
    else:
        cmd_name, cmd_args = cmd_line, None

    msg = InvokeCommandMsg(name=cmd_name, arguments=cmd_args)
    await agg.send_to_client(client_id=unit_id, msg=msg)


class ProcessDiagram(BaseModel):
    svg: str


@router.get("/process_unit/{unit_id}/process_diagram")
def get_process_diagram(unit_id: str) -> ProcessDiagram:
    return ProcessDiagram(svg="")


class CommandExample(BaseModel):
    name: str
    example: str


@router.get('/process_unit/{unit_id}/command_examples')
def get_command_examples(unit_id: str) -> List[CommandExample]:
    return [
        CommandExample(name="Some Example", example="Some example text")
    ]


class RunLogLine(BaseModel):
    id: int
    command: ExecutableCommand
    start: datetime
    end: datetime | None
    progress: float | None  # between 0 and 1
    start_values: List[ProcessValue]
    end_values: List[ProcessValue]


class RunLog(BaseModel):
    lines: List[RunLogLine]


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str) -> RunLog:
    return RunLog(lines=[])


@router.get('/process_unit/{unit_id}/method')
def get_method(unit_id: str) -> str:
    return ''


class PlotColorRegion(BaseModel):
    process_value_name: str
    value_color_map: dict[str | int | float, str]  # color string compatible with css e.g.: '#aa33bb', 'rgb(0,0,0)', 'rgba(0,0,0,0)', 'red'


class PlotAxis(BaseModel):
    label: str
    process_value_names: List[str]
    y_max: int | float
    y_min: int | float


class SubPlot(BaseModel):
    axes: List[PlotAxis]
    ratio: int | float


class PlotConfiguration(BaseModel):
    color_regions: List[PlotColorRegion]
    sub_plots: List[SubPlot]


@router.get('/process_unit/{unit_id}/plot_configuration')
def get_plot_configuration(unit_id: str) -> PlotConfiguration:
    return PlotConfiguration(color_regions=[], sub_plots=[])
