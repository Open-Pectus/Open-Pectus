import logging

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, Depends, Response, HTTPException
from openpectus.aggregator import command_util
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.command_examples import examples
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository, RecentEngineRepository
from openpectus.aggregator.routers.auth import UserIdValue, has_access, UserRolesValue, UserNameValue
from pydantic.json_schema import SkipJsonSchema
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

logger = logging.getLogger(__name__)
router = APIRouter(tags=["process_unit"])


def map_pu(engine_data: Mdl.EngineData) -> Dto.ProcessUnit:
    state = Dto.ProcessUnitState.Ready(state=Dto.ProcessUnitStateEnum.READY)
    if engine_data.system_state is not None and engine_data.system_state.value == Mdl.SystemStateEnum.Running:
        state = Dto.ProcessUnitState.InProgress(
            state=Dto.ProcessUnitStateEnum.IN_PROGRESS,
            progress_pct=0  # TODO: how do we know the progress_pct?
        )
    elif engine_data.has_run() and engine_data.run_data.interrupted_by_error:
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
        uod_author_name=engine_data.uod_author_name,
        uod_author_email=engine_data.uod_author_email
    )
    return unit


def get_registered_engine_data_or_fail(engine_id: str, user_roles: UserRolesValue, agg: Aggregator) -> Mdl.EngineData:
    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    if not has_access(engine_data, user_roles):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail={'missing_roles': list(engine_data.required_roles)})
    return engine_data


@router.get("/process_unit/{unit_id}", response_model_exclude_none=True)
def get_unit(user_roles: UserRolesValue, unit_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)) \
        -> Dto.ProcessUnit:
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    return map_pu(engine_data=engine_data)


@router.get("/process_units", response_model_exclude_none=True)
def get_units(user_roles: UserRolesValue, agg: Aggregator = Depends(agg_deps.get_aggregator)) -> list[Dto.ProcessUnit]:
    units: list[Dto.ProcessUnit] = []
    all_engine_data = agg.get_all_registered_engine_data()
    for engine_data in all_engine_data:
        if not has_access(engine_data, user_roles):
            continue
        unit = map_pu(engine_data)
        units.append(unit)
    # append recent engines from the database
    repo = RecentEngineRepository(database.scoped_session())
    recent_engines = repo.get_recent_engines()
    for recent_engine in recent_engines:
        if not has_access(recent_engine, user_roles):
            continue
        if recent_engine.engine_id not in [e.engine_id for e in all_engine_data]:
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


@router.get("/process_unit/{engine_id}/process_values", response_model_exclude_none=True)
def get_process_values(
        user_roles: UserRolesValue,
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> list[Dto.ProcessValue]:
    response.headers["Cache-Control"] = "no-store"

    engine_data = get_registered_engine_data_or_fail(engine_id, user_roles, agg)
    tags_info = engine_data.tags_info.map
    process_values: list[Dto.ProcessValue] = []
    for reading in engine_data.readings:
        tag_value = tags_info.get(reading.tag_name)
        if tag_value is not None:
            try:
                cmds = command_util.create_reading_commands(tag_value, reading)
                process_values.append(Dto.ProcessValue.create_w_commands(tag_value, cmds))
            except Exception as ex:
                logger.error(f"Error creating commands for process value '{reading.tag_name}': {ex}")
    return process_values


@router.get('/process_unit/{engine_id}/all_process_values', response_model_exclude_none=True)
def get_all_process_values(
        user_roles: UserRolesValue,
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)
) -> list[Dto.ProcessValue]:
    response.headers["Cache-Control"] = "no-store"
    engine_data = get_registered_engine_data_or_fail(engine_id, user_roles, agg)
    tags_info = engine_data.tags_info.map
    process_values: list[Dto.ProcessValue] = []
    for tag_value in tags_info.values():
        matching_reading = next((r for r in engine_data.readings if r.tag_name == tag_value.name), None)
        if matching_reading is not None:
            try:
                cmds = command_util.create_reading_commands(tag_value, matching_reading)
                process_values.append(Dto.ProcessValue.create_w_commands(tag_value, cmds))
            except Exception as ex:
                logger.error(f"Error creating commands for process value '{matching_reading.tag_name}': {ex}")
        else:
            process_values.append(Dto.ProcessValue.create(tag_value))
    return process_values


@router.post("/process_unit/{unit_id}/execute_command", response_model_exclude_none=True)
async def execute_command(
        user_name: UserNameValue,
        user_roles: UserRolesValue,
        unit_id: str,
        command: Dto.ExecutableCommand,
        agg: Aggregator = Depends(agg_deps.get_aggregator)):
    if __debug__:
        print("ExecutableCommand", command)
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
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

    # for now, all users issuing a command become contributors. may nee to filter that somehow
    # and when wo we clear the contributors?
    engine_data.contributors.add(user_name)
    return Dto.ServerSuccessResponse()


@router.get("/process_unit/{unit_id}/process_diagram", response_model_exclude_none=True)
def get_process_diagram(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.ProcessDiagram:
    return Dto.ProcessDiagram(svg="")


@router.get('/process_unit/{unit_id}/command_examples', response_model_exclude_none=True)
def get_command_examples(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> list[Dto.CommandExample]:
    commands: list[Dto.CommandExample] = []
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    commands.append(Dto.CommandExample(name="--- UOD Commands ---", example=""))
    commands.extend(command_util.create_command_examples(engine_data.commands))
    commands.append(Dto.CommandExample(name="--- Example Commands ---", example=""))
    commands.extend(examples)
    return commands


@router.get('/process_unit/{unit_id}/run_log', response_model_exclude_none=True)
def get_run_log(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.RunLog:
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    if not engine_data.has_run():
        return Dto.RunLog.empty()
    else:
        return Dto.RunLog(
            lines=list(map(Dto.RunLogLine.from_model, engine_data.run_data.runlog.lines))
        )


@router.get('/process_unit/{unit_id}/method-and-state', response_model_exclude_none=True)
def get_method_and_state(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.MethodAndState:
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    return Dto.MethodAndState.from_models(engine_data.method, engine_data.method_state)


@router.get('/process_unit/{unit_id}/method', response_model_exclude_none=True)
def get_method(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.Method:
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    return Dto.Method.from_model(engine_data.method)


@router.post('/process_unit/{unit_id}/method', response_model_exclude_none=True)
async def save_method(
        user_name: UserNameValue,
        user_roles: UserRolesValue,
        unit_id: str,
        method_dto: Dto.Method,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.MethodVersion:
    _ = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    method_mdl = Mdl.Method(
        lines=[Mdl.MethodLine(id=line.id, content=line.content) for line in method_dto.lines],
        version=method_dto.version,
        last_author=user_name
    )
    new_version = await agg.from_frontend.method_saved(engine_id=unit_id, method=method_mdl, user_name=user_name)
    return Dto.MethodVersion(version=new_version)


@router.get('/process_unit/{unit_id}/plot_configuration', response_model_exclude_none=True)
def get_plot_configuration(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.PlotConfiguration:
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    return Dto.PlotConfiguration.model_validate(
        # assumes Dto.PlotConfiguration and Mdl.PlotConfiguration are identical, change this when they diverge
        engine_data.plot_configuration)


@router.get('/process_unit/{unit_id}/plot_log', response_model_exclude_none=True)
def get_plot_log(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.PlotLog:
    plot_log_repo = PlotLogRepository(database.scoped_session())
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    if engine_data is None or not engine_data.has_run():
        return Dto.PlotLog(entries={})
    plot_log_model = plot_log_repo.get_plot_log(engine_data.run_data.run_id)
    if plot_log_model is None:
        return Dto.PlotLog(entries={})
    # assumes Dto.PlotLog and Mdl.PlotLog are identical, change this when they diverge
    return Dto.PlotLog.model_validate(plot_log_model)


@router.get('/process_unit/{unit_id}/control_state', response_model_exclude_none=True)
def get_control_state(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.ControlState:
    def from_message(state: Mdl.ControlState) -> Dto.ControlState:
        return Dto.ControlState(
            is_running=state.is_running,
            is_holding=state.is_holding,
            is_paused=state.is_paused)

    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    return from_message(engine_data.control_state)


@router.get('/process_unit/{unit_id}/error_log', response_model_exclude_none=True)
def get_error_log(
        user_roles: UserRolesValue,
        unit_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.AggregatedErrorLog:
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    return Dto.AggregatedErrorLog.from_model(engine_data.error_log)


@router.post('/process_unit/{unit_id}/run_log/force_line/{line_id}', response_model_exclude_none=True)
async def force_run_log_line(
        user_name: UserNameValue,
        user_roles: UserRolesValue,
        unit_id: str,
        line_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)):
    _ = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    if not await agg.from_frontend.request_force(engine_id=unit_id, line_id=line_id, user_name=user_name):
        return Dto.ServerErrorResponse(message="Force request failed")
    return Dto.ServerSuccessResponse(message="Force successfully requested")


@router.post('/process_unit/{unit_id}/run_log/cancel_line/{line_id}', response_model_exclude_none=True)
async def cancel_run_log_line(
        user_name: UserNameValue,
        user_roles: UserRolesValue,
        unit_id: str,
        line_id: str,
        agg: Aggregator = Depends(agg_deps.get_aggregator)):
    _ = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    if not await agg.from_frontend.request_cancel(engine_id=unit_id, line_id=line_id, user_name=user_name):
        return Dto.ServerErrorResponse(message="Cancel request failed")
    return Dto.ServerSuccessResponse(message="Cancel successfully requested")


@router.get('/process_units/system_state_enum', response_model_exclude_none=True)
def expose_system_state_enum() -> Dto.SystemStateEnum:
    return Mdl.SystemStateEnum.Running


@router.get('/process_unit/{unit_id}/active_users', response_model_exclude_none=True)
async def get_active_users(
        user_roles: UserRolesValue,
        unit_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)) -> list[Dto.ActiveUser]:
    response.headers["Cache-Control"] = "no-store"
    engine_data = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    active_users = engine_data.active_users.values()
    return list(map(Dto.ActiveUser.from_model, active_users))


@router.post('/process_unit/{unit_id}/register_active_user', response_model_exclude_none=True)
async def register_active_user(
        user_id_from_token: UserIdValue,
        user_name: UserNameValue,
        user_roles: UserRolesValue,
        unit_id: str,
        user_id: str | SkipJsonSchema[None] = None,
        agg: Aggregator = Depends(agg_deps.get_aggregator)):
    _ = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    resolved_user_id = user_id_from_token or user_id
    if(resolved_user_id == None):
        return Dto.ServerErrorResponse(message="User registration failed due to missing user_id")
    action_result = await agg.from_frontend.register_active_user(
        engine_id=unit_id,
        user_id=resolved_user_id,
        user_name=user_name,
    )
    if not action_result:
        return Dto.ServerErrorResponse(message="User registration failed")
    return Dto.ServerSuccessResponse(message="User successfully registered")

@router.post('/process_unit/{unit_id}/unregister_active_user', response_model_exclude_none=True)
async def unregister_active_user(
        user_id_from_token: UserIdValue,
        user_roles: UserRolesValue,
        unit_id: str,
        user_id: str | SkipJsonSchema[None] = None,
        agg: Aggregator = Depends(agg_deps.get_aggregator)):
    _ = get_registered_engine_data_or_fail(unit_id, user_roles, agg)
    resolved_user_id = user_id_from_token or user_id
    if(resolved_user_id == None):
        return Dto.ServerErrorResponse(message="User unregistration failed due to missing user_id")
    action_result = await agg.from_frontend.unregister_active_user(
        engine_id=unit_id,
        user_id=resolved_user_id,
    )
    if not action_result:
        return Dto.ServerErrorResponse(message="User unregistration failed")
    return Dto.ServerSuccessResponse(message="User successfully unregistered")
