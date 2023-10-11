from datetime import datetime
from enum import StrEnum, auto
from typing import Literal, List, Dict

import openpectus.aggregator.deps as agg_deps
from aggregator.routers.dto import Method, RunLog, ProcessValueType, ProcessValue, ExecutableCommand, ProcessValueValueType, PlotConfiguration, \
    PlotLog
from fastapi import APIRouter, Depends, Response
from openpectus.protocol.aggregator import Aggregator, ChannelInfo
from openpectus.protocol.messages import InvokeCommandMsg
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


class ControlState(BaseModel):
    is_running: bool
    is_holding: bool
    is_paused: bool


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







@router.get("/process_unit/{unit_id}/process_values")
def get_process_values(unit_id: str, response: Response, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[ProcessValue]:
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


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str) -> RunLog:
    return RunLog(lines=[])


@router.get('/process_unit/{unit_id}/method')
def get_method(unit_id: str) -> Method:
    return Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])

@router.post('/process_unit/{unit_id}/method')
def save_method(unit_id: str, method: Method) -> None:
    pass


@router.get('/process_unit/{unit_id}/plot_configuration')
def get_plot_configuration(unit_id: str) -> PlotConfiguration:
    return PlotConfiguration(
        color_regions=[],
        sub_plots=[],
        process_value_names_to_annotate=[],
        x_axis_process_value_names=[]
    )


@router.get('/process_unit/{unit_id}/plot_log')
def get_plot_log(unit_id: str) -> PlotLog:
    return PlotLog(entries={})


@router.get('/process_unit/{unit_id}/control_state')
def get_control_state(unit_id: str) -> ControlState:
    return ControlState(False, False, False)
