import logging
from datetime import datetime
from typing import List

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.routers.dto as D
import openpectus.aggregator.models as Mdl
import openpectus.protocol.aggregator_messages as AM
from fastapi import APIRouter, Depends, Response
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.models import EngineData

logger = logging.getLogger(__name__)
router = APIRouter(tags=["process_unit"])


def create_pu(item: EngineData) -> D.ProcessUnit:
    # TODO define source of all fields
    unit = D.ProcessUnit(
        id=item.engine_id or "(error)",
        name=f"{item.computer_name} ({item.uod_name})",
        state=D.ProcessUnitState.Ready(state=D.ProcessUnitStateEnum.READY),
        location="Unknown location",
        runtime_msec=189309,
        current_user_role=D.UserRole.ADMIN,
    )
    return unit


@router.get("/process_unit/{unit_id}")
def get_unit(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> D.ProcessUnit | None:
    ci = agg.engine_data_map.get(unit_id)
    if ci is None:
        return None
    return create_pu(item=ci)


@router.get("/process_units")
def get_units(agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[D.ProcessUnit]:
    units: List[D.ProcessUnit] = []
    for engine_id, item in agg.engine_data_map.items():
        unit = create_pu(item)
        units.append(unit)
    return units


@router.get("/process_unit/{unit_id}/process_values")
def get_process_values(
        unit_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[D.ProcessValue]:
    # parm last_seen

    response.headers["Cache-Control"] = "no-store"

    client_data = agg.engine_data_map.get(unit_id)
    if client_data is None:
        return []

    tags_info = client_data.tags_info.map

    # print("Readings", client_data.readings)
    # print("Tags", tags_info)

    pvs: List[D.ProcessValue] = []
    for r in client_data.readings:
        ti = tags_info.get(r.tag_name)
        if ti is not None:
            pvs.append(D.ProcessValue.from_message(r, ti))
    return pvs


@router.post("/process_unit/{unit_id}/execute_command")
async def execute_command(unit_id: str, command: D.ExecutableCommand, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    # logger.debug("execute_command", str(command))
    if command is None or command.command is None or command.command.strip() == '':
        logger.error("Cannot invoke empty command")
        return D.ServerErrorResponse(message="Cannot invoke empty command")

    # print("command.command", command.command)

    lines = command.command.splitlines(keepends=False)
    line_count = len(lines)
    if line_count < 1:
        logger.error("Cannot invoke command with no lines")
        return D.ServerErrorResponse(message="Cannot invoke command with no lines")

    if command.source == D.CommandSource.UNIT_BUTTON:
        # Make simple commands title cased, eg 'start' -> 'Start
        # TODO remove once frontend is updated to title cased commands
        code = lines[0]
        code = code.title()
        msg = AM.InvokeCommandMsg(name=code)
    else:
        msg = AM.InjectCodeMsg(pcode=command.command)

    logger.info(f"Sending msg '{str(msg)}' of type {type(msg)} to client '{unit_id}'")
    await agg.dispatcher.rpc_call(unit_id, msg)


@router.get("/process_unit/{unit_id}/process_diagram")
def get_process_diagram(unit_id: str) -> D.ProcessDiagram:
    return D.ProcessDiagram(svg="")


@router.get('/process_unit/{unit_id}/command_examples')
def get_command_examples(unit_id: str) -> List[D.CommandExample]:
    return [
        D.CommandExample(name="Some Example", example="Some example text"),
        D.CommandExample(name="Watch Example", example="""
Watch: Block Time > 3s
    Mark: A
Mark: X

Watch: Block Time > 7s
    Mark: B
Mark: Y""")
    ]


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> D.RunLog:
    engine_data = agg.engine_data_map.get(unit_id)
    if engine_data is None:
        logger.warning("No client data - thus no runlog")
        return D.RunLog(lines=[])

    def from_line_model(msg: Mdl.RunLogLine) -> D.RunLogLine:
        cmd = D.ExecutableCommand(
                command=msg.command_name,
                name=None,
                source=D.CommandSource.METHOD
        )
        line = D.RunLogLine(
            id=0,   # TODO change type int to str
            command=cmd,
            start=datetime.fromtimestamp(msg.start),
            end=None if msg.end is None else datetime.fromtimestamp(msg.end),
            progress=None,
            start_values=[],
            end_values=[],
            forcible=None,  # TODO map forcible,forced,cancellable and cancelled
            forced=None,
            cancellable=None,
            cancelled=None
        )
        return line

    logger.info(f"Got runlog with {len(engine_data.runlog.lines)} lines")
    return D.RunLog(
        lines=list(map(from_line_model, engine_data.runlog.lines)))


@router.get('/process_unit/{unit_id}/method')
def get_method(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> D.Method:
    engine_data = agg.engine_data_map.get(unit_id)
    if engine_data is None:
        logger.warning("No client data - thus no method")
        return D.Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])

    def from_model(msg: Mdl.Method) -> D.Method:
        return D.Method(
            lines=[D.MethodLine(id=line.id, content=line.content) for line in msg.lines],
            started_line_ids=[_id for _id in msg.started_line_ids],
            executed_line_ids=[_id for _id in msg.executed_line_ids],
            injected_line_ids=[_id for _id in msg.injected_line_ids],
        )

    print("Returned client method")
    return from_model(engine_data.method)


@router.post('/process_unit/{unit_id}/method')
async def save_method(unit_id: str, method: D.Method, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    msg = M.MethodMsg(
        lines=[M.MethodLineMsg(id=line.id, content=line.content) for line in method.lines],
        started_line_ids=[_id for _id in method.started_line_ids],
        executed_line_ids=[_id for _id in method.executed_line_ids],
        injected_line_ids=[_id for _id in method.injected_line_ids],
    )

    if not await agg.set_method(engine_id=unit_id, method=msg):
        return D.ServerErrorResponse(message="Failed to set method")


@router.get('/process_unit/{unit_id}/plot_configuration')
def get_plot_configuration(unit_id: str) -> D.PlotConfiguration:
    return D.PlotConfiguration(
        color_regions=[],
        sub_plots=[],
        process_value_names_to_annotate=[],
        x_axis_process_value_names=[]
    )


@router.get('/process_unit/{unit_id}/plot_log')
def get_plot_log(unit_id: str) -> D.PlotLog:
    return D.PlotLog(entries={})


@router.get('/process_unit/{unit_id}/control_state')
def get_control_state(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> D.ControlState:

    def from_message(state: Mdl.ControlState) -> D.ControlState:
        return D.ControlState(
            is_running=state.is_running,
            is_holding=state.is_holding,
            is_paused=state.is_paused)

    engine_data = agg.engine_data_map.get(unit_id)
    if engine_data is None:
        logger.warning("No client data - thus no control state")
        return D.ControlState.default()

    return from_message(engine_data.control_state)


@router.post('/process_unit/{unit_id}/run_log/force_line/{line_id}')
def force_run_log_line(unit_id: str, line_id: int):
    pass


@router.post('/process_unit/{unit_id}/run_log/cancel_line/{line_id}')
def cancel_run_log_line(unit_id: str, line_id: int):
    pass
