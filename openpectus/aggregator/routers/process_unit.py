import logging
from typing import List

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
import openpectus.protocol.aggregator_messages as AM
from fastapi import APIRouter, Depends, Response
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository
from openpectus.aggregator.models import EngineData

logger = logging.getLogger(__name__)
router = APIRouter(tags=["process_unit"])


def map_pu(engine_data: EngineData) -> Dto.ProcessUnit:
    # TODO define source of all fields
    unit = Dto.ProcessUnit(
        id=engine_data.engine_id or "(error)",
        name=f"{engine_data.computer_name} ({engine_data.uod_name})",
        state=Dto.ProcessUnitState.Ready(state=Dto.ProcessUnitStateEnum.READY),
        location=engine_data.location,
        runtime_msec=engine_data.runtime.value if engine_data.runtime is not None and isinstance(engine_data.runtime.value, int) else 0,
        current_user_role=Dto.UserRole.ADMIN,
    )
    return unit


@router.get("/process_unit/{unit_id}")
def get_unit(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.ProcessUnit | None:
    ci = agg.get_registered_engine_data(unit_id)
    if ci is None:
        return None
    return map_pu(engine_data=ci)


@router.get("/process_units")
def get_units(agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[Dto.ProcessUnit]:
    units: List[Dto.ProcessUnit] = []
    for engine_data in agg.get_all_registered_engine_data():
        unit = map_pu(engine_data)
        units.append(unit)
    return units


@router.get("/process_unit/{engine_id}/process_values")
def get_process_values(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[Dto.ProcessValue]:
    # parm last_seen

    response.headers["Cache-Control"] = "no-store"

    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        return []

    tags_info = engine_data.tags_info.map

    # print("Readings", engine_data.readings)
    # print("Tags", tags_info)

    pvs: List[Dto.ProcessValue] = []
    for r in engine_data.readings:
        ti = tags_info.get(r.tag_name)
        if ti is not None:
            pvs.append(Dto.ProcessValue.from_message(r, ti))
    return pvs


@router.post("/process_unit/{unit_id}/execute_command")
async def execute_command(unit_id: str, command: Dto.ExecutableCommand, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    # logger.debug("execute_command", str(command))
    if command is None or command.command is None or command.command.strip() == '':
        logger.error("Cannot invoke empty command")
        return Dto.ServerErrorResponse(message="Cannot invoke empty command")

    # print("command.command", command.command)

    lines = command.command.splitlines(keepends=False)
    line_count = len(lines)
    if line_count < 1:
        logger.error("Cannot invoke command with no lines")
        return Dto.ServerErrorResponse(message="Cannot invoke command with no lines")

    if command.source == Dto.CommandSource.UNIT_BUTTON:
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
def get_process_diagram(unit_id: str) -> Dto.ProcessDiagram:
    return Dto.ProcessDiagram(svg="")


@router.get('/process_unit/{unit_id}/command_examples')
def get_command_examples(unit_id: str) -> List[Dto.CommandExample]:
    return [
        Dto.CommandExample(name="Some Example", example="Some example text"),
        Dto.CommandExample(name="Watch Example", example="""
Watch: Block Time > 3s
    Mark: A
Mark: X

Watch: Block Time > 7s
    Mark: B
Mark: Y""")
    ]


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.RunLog:
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.warning("No engine data - thus no runlog")
        return Dto.RunLog.empty()

    logger.info(f"Got runlog with {len(engine_data.run_data.runlog.lines)} lines")
    return Dto.RunLog(
        lines=list(map(Dto.RunLogLine.from_line_model, engine_data.run_data.runlog.lines))
    )


@router.get('/process_unit/{unit_id}/method-and-state')
def get_method_and_state(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.MethodAndState:
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.warning("No engine data - thus no method")
        return Dto.MethodAndState.empty()

    def from_models(method: Mdl.Method, method_state: Mdl.MethodState) -> Dto.MethodAndState:
        return Dto.MethodAndState(
            method=Dto.Method(lines=[Dto.MethodLine(id=line.id, content=line.content) for line in method.lines]),
            state=Dto.MethodState(started_line_ids=[_id for _id in method_state.started_line_ids],
                                  executed_line_ids=[_id for _id in method_state.executed_line_ids],
                                  injected_line_ids=[_id for _id in method_state.injected_line_ids])
        )

    print("Returned client method")
    return from_models(engine_data.method, engine_data.run_data.method_state)


@router.post('/process_unit/{unit_id}/method')
async def save_method(unit_id: str, method_dto: Dto.Method, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    method_mdl = Mdl.Method(lines=[Mdl.MethodLine(id=line.id, content=line.content) for line in method_dto.lines])

    if not await agg.from_frontend.method_saved(engine_id=unit_id, method=method_mdl):
        return Dto.ServerErrorResponse(message="Failed to set method")


@router.get('/process_unit/{unit_id}/plot_configuration')
def get_plot_configuration(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.PlotConfiguration:
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.warning("No engine data - thus no plot configuration")
        return Dto.PlotConfiguration.empty()

    return Dto.PlotConfiguration.validate(engine_data.plot_configuration)


@router.get('/process_unit/{unit_id}/plot_log')
def get_plot_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.PlotLog:
    plot_log_repo = PlotLogRepository(database.scoped_session())
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None or engine_data.run_id is None:
        return Dto.PlotLog(entries={})
    plot_log_model = plot_log_repo.get_plot_log(engine_data.run_id)
    if plot_log_model is None:
        return Dto.PlotLog(entries={})
    return Dto.PlotLog.from_orm(plot_log_model)


@router.get('/process_unit/{unit_id}/control_state')
def get_control_state(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.ControlState:
    def from_message(state: Mdl.ControlState) -> Dto.ControlState:
        return Dto.ControlState(
            is_running=state.is_running,
            is_holding=state.is_holding,
            is_paused=state.is_paused)

    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.warning("No client data - thus no control state")
        return Dto.ControlState.default()

    return from_message(engine_data.control_state)


@router.post('/process_unit/{unit_id}/run_log/force_line/{line_id}')
def force_run_log_line(unit_id: str, line_id: str):
    pass


@router.post('/process_unit/{unit_id}/run_log/cancel_line/{line_id}')
def cancel_run_log_line(unit_id: str, line_id: str):
    pass
