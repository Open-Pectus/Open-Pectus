from __future__ import annotations
from datetime import datetime
from enum import StrEnum, auto
from typing import Literal, List, Dict
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
import logging

import openpectus.aggregator.deps as agg_deps
from openpectus.protocol.aggregator import Aggregator, ChannelInfo, ReadingDef, TagInfo
from openpectus.protocol.messages import (
    ControlStateMsg,
    InjectCodeMsg,
    InvokeCommandMsg,
    RunLogLineMsg
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["process_unit"])


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


class UserRole(StrEnum):
    VIEWER = auto()
    ADMIN = auto()


class ControlState(BaseModel):
    is_running: bool
    is_holding: bool
    is_paused: bool

    @staticmethod
    def from_message(state: ControlStateMsg) -> ControlState:
        return ControlState(
            is_running=state.is_running,
            is_holding=state.is_holding,
            is_paused=state.is_paused)

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


def create_pu(item: ChannelInfo) -> ProcessUnit:
    # TODO define source of all fields
    unit = ProcessUnit(
        id=item.client_id or "(error)",
        name=f"{item.engine_name} ({item.uod_name})",
        state=ProcessUnitState.Ready(state=ProcessUnitStateEnum.READY),
        location="Unknown location",
        runtime_msec=189309,
        current_user_role=UserRole.ADMIN,
    )
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


ProcessValueValueType = str | float | int | None


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
    def from_message(r: ReadingDef, ti: TagInfo) -> ProcessValue:
        return ProcessValue(
            name=r.label,
            value=ti.value,
            value_type=get_ProcessValueType_from_value(ti.value),
            value_unit=ti.value_unit,
            commands=[]
        )
        # commands=[ProcessValueCommand(name=c.name, command=c.command) for c in r.commands])


@router.get("/process_unit/{unit_id}/process_values")
def get_process_values(unit_id: str, response: Response, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[ProcessValue]:
    # parm last_seen

    response.headers["Cache-Control"] = "no-store"

    client_data = agg.client_data_map.get(unit_id)
    if client_data is None:
        return []

    tags_info = client_data.tags_info.map

    #print("Readings", client_data.readings)
    #print("Tags", tags_info)

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
    METHOD = auto()


class ExecutableCommand(BaseModel):
    command: str  # full pcode command string, e.g. "Start" or "foo: bar" or multiple pcode lines
    source: CommandSource
    name: str | None


@router.post("/process_unit/{unit_id}/execute_command")
async def execute_command(unit_id: str, command: ExecutableCommand, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    #logger.info("execute_command", str(command))
    if command is None or command.command is None or command.command.strip() == '':
        logger.error("Cannot invoke empty command")
        return ServerErrorResponse(message="Cannot invoke empty command")

    #print("command.command", command.command)

    lines = command.command.splitlines(keepends=False)
    line_count = len(lines)
    if line_count == 0:
        logger.error("Cannot invoke command with no lines")
        return ServerErrorResponse(message="Cannot invoke command with no lines")
    elif line_count > 1:
        # TODO this should be a seperate end point
        msg = InjectCodeMsg(pcode=command.command)
    else:
        code = lines[0]
        # Make simple commands title cased, eg 'start' -> 'Start
        # TODO remove once frontend is updated to title cased commands
        code = code.title()
        msg = InvokeCommandMsg(name=code)

    # if ":" in cmd_line:
    #     split = command.command.split(":", maxsplit=1)
    #     cmd_name, cmd_args = split[0], split[1]  # TODO watch out for "" vs None as cmd_args
    # else:
    #     if " " not in cmd_line:  # TODO remove once frontend is updated to title cased commands
    #         cmd_line = cmd_line.title()
    #     cmd_name, cmd_args = cmd_line, None

    # msg = InvokeCommandMsg(name=cmd_name, arguments=cmd_args)
    logger.debug(f"Sending msg '{str(msg)}' to client '{unit_id}'")
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
        CommandExample(name="Some Example", example="Some example text"),
        CommandExample(name="Watch Example", example="""
Watch: Block Time > 0.2s
    Mark: A
Mark: X""")
    ]


class RunLogLine(BaseModel):
    id: int
    command: ExecutableCommand
    start: datetime
    end: datetime | None
    progress: float | None  # between 0 and 1
    start_values: List[ProcessValue]  # ProcessValue.commands will be None
    end_values: List[ProcessValue]    # ProcessValue.commands will be None
    # TODO state: hold state values such as Waiting, Started, Cancelled, Forced, Completed, Failed
    # TODO start_values and end_values take up space. Consider ways to avoid loading the full runlog
    # - a 'changes_since' parameter to avoid reloading data that is already known
    # and/or
    # - an additional endpoint to get details that can be loaded on demand (e.g. on hover)


class RunLog(BaseModel):
    lines: List[RunLogLine]


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> RunLog:
    client_data = agg.client_data_map.get(unit_id)
    if client_data is None:
        logger.warning("No client data - thus no runlog")
        return RunLog(lines=[])

    def from_line_msg(msg: RunLogLineMsg) -> RunLogLine:
        cmd = ExecutableCommand(
                command=msg.command_name,
                name=None,
                source=CommandSource.METHOD
        )
        line = RunLogLine(
            id=0,
            command=cmd,
            start=datetime.fromtimestamp(msg.start),
            end=None,
            progress=None,
            start_values=[],
            end_values=[]
        )
        return line

    return RunLog(
        lines=list(map(from_line_msg, client_data.runlog.lines)))


class MethodLine(BaseModel):
    id: str
    content: str


class Method(BaseModel):
    lines: List[MethodLine]
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]


@router.get('/process_unit/{unit_id}/method')
def get_method(unit_id: str) -> Method:
    return Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


@router.post('/process_unit/{unit_id}/method')
def save_method(unit_id: str, method: Method) -> None:
    pass


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


@router.get('/process_unit/{unit_id}/plot_configuration')
def get_plot_configuration(unit_id: str) -> PlotConfiguration:
    return PlotConfiguration(
        color_regions=[],
        sub_plots=[],
        process_value_names_to_annotate=[],
        x_axis_process_value_names=[]
    )


# This class exists only to workaround the issue that OpenApi spec (or Pydantic) cannot express that elements in a list can be None/null/undefined.
# Properties on an object can be optional, so we use that via this wrapping class to express None values in the PlotLogEntry.values list.
# Feel free to refactor to remove this class if it becomes possible to express the above without it.
class PlotLogEntryValue(BaseModel):
    value: ProcessValueValueType


class PlotLogEntry(BaseModel):
    name: str
    values: List[PlotLogEntryValue]
    value_unit: str | None
    value_type: ProcessValueType


class PlotLog(BaseModel):
    entries: Dict[str, PlotLogEntry]


@router.get('/process_unit/{unit_id}/plot_log')
def get_plot_log(unit_id: str) -> PlotLog:
    return PlotLog(entries={})


@router.get('/process_unit/{unit_id}/control_state')
def get_control_state(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> ControlState:
    client_data = agg.client_data_map.get(unit_id)
    if client_data is None:
        logger.warning("No client data - thus no control state")
        return ControlState.default()

    return ControlState.from_message(client_data.control_state)
