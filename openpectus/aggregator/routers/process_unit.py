import logging
from typing import List

from openpectus.aggregator import command_util
import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto

from fastapi import APIRouter, Depends, Response
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository, RecentEngineRepository
from openpectus.aggregator.command_examples import examples

logger = logging.getLogger(__name__)
router = APIRouter(tags=["process_unit"])


def map_pu(engine_data: Mdl.EngineData) -> Dto.ProcessUnit:
    # TODO define source of all fields

    state = Dto.ProcessUnitState.Ready(state=Dto.ProcessUnitStateEnum.READY)
    if engine_data.system_state is not None and engine_data.system_state.value == Mdl.SystemStateEnum.Running:
        state = Dto.ProcessUnitState.InProgress(
            state=Dto.ProcessUnitStateEnum.IN_PROGRESS,
            progress_pct=0  # TODO: how do we know the progress_pct?
        )
    elif engine_data.run_data.interrupted_by_error:
        state = Dto.ProcessUnitState.Error(
            state=Dto.ProcessUnitStateEnum.ERROR
        )

    unit = Dto.ProcessUnit(
        id=engine_data.engine_id or "(error)",
        name=f"{engine_data.computer_name} ({engine_data.uod_name})",
        state=state,
        location=engine_data.location,
        runtime_msec=engine_data.runtime.value if (
            engine_data.runtime is not None and isinstance(engine_data.runtime.value, int)
        ) else 0,
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
    # append recent engines from the database
    repo = RecentEngineRepository(database.scoped_session())
    recent_engines = repo.get_recent_engines()
    for recent_engine in recent_engines:
        if recent_engine.engine_id not in [u.id for u in units]:
            unit = Dto.ProcessUnit(
                id=recent_engine.engine_id or "(error)",
                name=recent_engine.name,
                state=Dto.ProcessUnitState.NotOnline(
                    state=Dto.ProcessUnitStateEnum.NOT_ONLINE,
                    last_seen_date=recent_engine.last_update
                ),
                location=recent_engine.location,
                runtime_msec=0,
                current_user_role=Dto.UserRole.ADMIN,
            )
            units.append(unit)

    return units

@router.get("/process_unit/{engine_id}/process_values")
def get_process_values(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> List[Dto.ProcessValue]:
    response.headers["Cache-Control"] = "no-store"

    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        return []
    tags_info = engine_data.tags_info.map
    process_values: List[Dto.ProcessValue] = []
    for reading in engine_data.readings:
        tag_value = tags_info.get(reading.tag_name)
        if tag_value is not None:
            try:
                cmds = command_util.create_commands(tag_value, reading)
                process_values.append(Dto.ProcessValue.create_w_commands(tag_value, cmds))
            except Exception as ex:
                logger.error(f"Error creating commands for process value '{reading.tag_name}': {ex}")
    return process_values


@router.get('/process_unit/{engine_id}/all_process_values')
def get_all_process_values(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)
        ) -> List[Dto.ProcessValue]:
    response.headers["Cache-Control"] = "no-store"
    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        return []
    tags_info = engine_data.tags_info.map
    process_values: List[Dto.ProcessValue] = []
    for tag_value in tags_info.values():
        process_values.append(Dto.ProcessValue.create(tag_value))
    return process_values


@router.post("/process_unit/{unit_id}/execute_command")
async def execute_command(unit_id: str, command: Dto.ExecutableCommand, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    if __debug__:
        print("ExecutableCommand", command)

    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.error(f"No registered engine with engine_id '{unit_id}'")
        return Dto.ServerErrorResponse(message=f"No registered engine with engine_id '{unit_id}'")
    try:
        msg = command_util.parse_as_message(command, engine_data.readings)
    except Exception:
        logger.error(f"Parse error for command: {command}", exc_info=True)
        return Dto.ServerErrorResponse(message="Message parse error")
    logger.info(f"Sending msg '{str(msg)}' of type {type(msg)} to engine '{unit_id}'")
    try:
        await agg.dispatcher.rpc_call(unit_id, msg)
    except Exception:
        logger.error(f"Rpc call to engine_id '{unit_id}' failed", exc_info=True)
        return Dto.ServerErrorResponse(message="Failed to send message")
    return Dto.ServerSuccessResponse()


@router.get("/process_unit/{unit_id}/process_diagram")
def get_process_diagram(unit_id: str) -> Dto.ProcessDiagram:
    return Dto.ProcessDiagram(svg="")


@router.get('/process_unit/{unit_id}/command_examples')
def get_command_examples(unit_id: str) -> List[Dto.CommandExample]:
    return examples


@router.get('/process_unit/{unit_id}/run_log')
def get_run_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.RunLog:
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.warning("No engine data - thus no runlog")
        return Dto.RunLog.empty()

    logger.info(f"Got runlog with {len(engine_data.run_data.runlog.lines)} lines")
    return Dto.RunLog(
        lines=list(map(Dto.RunLogLine.from_model, engine_data.run_data.runlog.lines))
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

    return Dto.PlotConfiguration.validate(
        engine_data.plot_configuration)  # assumes Dto.PlotConfiguration and Mdl.PlotConfiguration are identical, change this when they diverge


@router.get('/process_unit/{unit_id}/plot_log')
def get_plot_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.PlotLog:
    plot_log_repo = PlotLogRepository(database.scoped_session())
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None or engine_data.run_id is None:
        return Dto.PlotLog(entries={})
    plot_log_model = plot_log_repo.get_plot_log(engine_data.run_id)
    if plot_log_model is None:
        return Dto.PlotLog(entries={})
    return Dto.PlotLog.validate(plot_log_model)  # assumes Dto.PlotLog and Mdl.PlotLog are identical, change this when they diverge


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


@router.get('/process_unit/{unit_id}/error_log')
def get_error_log(unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.AggregatedErrorLog:
    engine_data = agg.get_registered_engine_data(unit_id)
    if engine_data is None:
        logger.warning("No client data - thus no error log")
        return Dto.AggregatedErrorLog(entries=[])

    return Dto.AggregatedErrorLog.from_model(engine_data.run_data.error_log)


@router.post('/process_unit/{unit_id}/run_log/force_line/{line_id}')
def force_run_log_line(unit_id: str, line_id: str):
    pass


@router.post('/process_unit/{unit_id}/run_log/cancel_line/{line_id}')
def cancel_run_log_line(unit_id: str, line_id: str):
    pass


@router.get('/process_units/system_state_enum')
def expose_system_state_enum() -> Dto.SystemStateEnum:
    return Mdl.SystemStateEnum.Running
