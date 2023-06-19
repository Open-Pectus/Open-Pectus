from datetime import datetime
from enum import StrEnum, auto
from typing import Literal, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

import openpectus.aggregator.deps as agg_deps
from openpectus.protocol.aggregator import Aggregator, ChannelInfo, TagInfo
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


class ProcessValueCommand(BaseModel):
    name: str
    command: str


class ProcessValue(BaseModel):
    """ Represents a process value. """
    name: str
    value: str | float | int | None
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    valid_value_units: List[str] | None
    """ For values with a unit, provides the list valid alternative units """
    value_type: ProcessValueType
    """ Specifies the type of allowed values. """
    writable: bool
    commands: List[ProcessValueCommand] | None  # TODO: have backend verify that no ProcessValue ever is both writable and has commands.


def create_pv(ti: TagInfo) -> ProcessValue:
    # TODO define source of all fields

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

    return ProcessValue(
        name=ti.name,
        value=ti.value,
        value_unit=ti.value_unit,
        valid_value_units=[],
        value_type=get_ProcessValueType_from_value(ti.value),
        writable=True,
        commands=[])


@router.get("/process_unit/{unit_id}/process_values")
def get_process_values(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[ProcessValue]:  # naming?, parm last_seen
    tags = agg.get_client_tags(client_id=unit_id)
    if tags is None:
        return []

    return [create_pv(ti) for ti in tags.map.values()]


class ProcessValueUpdate(BaseModel):
    name: str
    value: str | float | int


@router.post("/process_unit/{unit_id}/process_value")
def set_process_value(unit_id: str, update: ProcessValueUpdate, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    pass


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


class RunLogColumn(BaseModel):
    header: str
    type: ProcessValueType
    unit: str | None


class RunLogLine(BaseModel):
    command: ExecutableCommand
    start: datetime
    end: datetime
    additional_values: List[str | int | float]


class RunLog(BaseModel):
    additional_columns: List[RunLogColumn]
    lines: List[RunLogLine]


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str) -> RunLog:
    return RunLog(additional_columns=[], lines=[])
