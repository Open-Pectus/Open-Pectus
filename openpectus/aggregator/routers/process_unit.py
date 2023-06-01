from datetime import datetime
from enum import StrEnum, auto
from typing import Literal, List

from fastapi import APIRouter
from pydantic import BaseModel

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
    id: int
    name: str
    state: ProcessUnitState.Ready | ProcessUnitState.InProgress | ProcessUnitState.NotOnline
    location: str | None
    runtime_msec: int | None
    current_user_role: UserRole
    # users: List[User] ?


@router.get("/process_unit/{id}")
def get_unit(id: int) -> ProcessUnit:
    return ProcessUnit(
        id=id,
        name="Foo",
        state=ProcessUnitState.Ready(state=ProcessUnitStateEnum.READY),  # type: ignore
        location="H21.5",
        runtime_msec=189309,
        user_role=UserRole.ADMIN
    )


@router.get("/process_units")
def get_units() -> List[ProcessUnit]:
    return [
        ProcessUnit(
            id=3,
            name="Foo",
            state=ProcessUnitState.InProgress(state=ProcessUnitStateEnum.IN_PROGRESS, progress_pct=75),  # type: ignore
            location="H21.5",
            runtime_msec=189309,
            current_user_role=UserRole.ADMIN
        )]


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


@router.get("/process_unit/{id}/process_values")
def get_process_values(id: int) -> List[ProcessValue]:  # naming?, parm last_seen
    return [ProcessValue(name="A-Flow", value=54, value_unit="L", valid_value_units=["L", "m3"], writable=False,
                         options=None, value_type=ProcessValueType.STRING)]


class ProcessValueUpdate(BaseModel):
    name: str
    value: str | float | int


@router.post("/process_unit/{unit_id}/process_value")
def set_process_value(unit_id: int, update: ProcessValueUpdate):
    pass


class CommandSource(StrEnum):
    PROCESS_VALUE = auto()
    MANUALLY_ENTERED = auto()
    UNIT_BUTTON = auto()


class ExecutableCommand(BaseModel):
    command: str
    source: CommandSource
    name: str | None


@router.post("/process_unit/{unit_id}/execute_command")
def execute_command(unit_id: int, command: ExecutableCommand):
    pass


class ProcessDiagram(BaseModel):
    svg: str


@router.get("/process_unit/{unit_id}/process_diagram")
def get_process_diagram(unit_id: int) -> ProcessDiagram:
    return ProcessDiagram(svg="")


class CommandExample(BaseModel):
    name: str
    example: str


@router.get('/process_unit/{unit_id}/command_examples')
def get_command_examples(unit_id: int) -> List[CommandExample]:
    return [
        CommandExample(name="Some Example", example="Some example text")
    ]


class RunLogLine(BaseModel):
    command: ExecutableCommand
    start: int
    end: int


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: int) -> List[RunLogLine]:
    return []
