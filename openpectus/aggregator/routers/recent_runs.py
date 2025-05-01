from typing import List

import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
import openpectus.aggregator.data.models as Db
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openpectus.aggregator.csv_generator import generate_csv_string
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository, RecentRunRepository
from openpectus.aggregator.routers.auth import UserRolesValue, has_access
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

router = APIRouter(tags=["recent_runs"], prefix='/recent_runs')


def get_recent_run_or_fail(user_roles: UserRolesValue, run_id: str) -> Db.RecentRun:
    repo = RecentRunRepository(database.scoped_session())
    recent_run = repo.get_by_run_id(run_id)
    if recent_run is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Recent Run not found')
    if not has_access(recent_run, user_roles):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail={'missing_roles': recent_run.required_roles})
    return recent_run


@router.get("/", response_model_exclude_none=True)
def get_recent_runs(user_roles: UserRolesValue) -> List[Dto.RecentRun]:
    repo = RecentRunRepository(database.scoped_session())
    return list(map(Dto.RecentRun.model_validate, filter(lambda rr: has_access(rr, user_roles), repo.get_all())))


@router.get("/{run_id}", response_model_exclude_none=True)
def get_recent_run(user_roles: UserRolesValue, run_id: str) -> Dto.RecentRun:
    recent_run = get_recent_run_or_fail(user_roles, run_id)
    return Dto.RecentRun.model_validate(recent_run)


@router.get('/{run_id}/method-and-state', response_model_exclude_none=True)
def get_recent_run_method_and_state(user_roles: UserRolesValue, run_id: str) -> Dto.MethodAndState:
    get_recent_run_or_fail(user_roles, run_id)
    repo = RecentRunRepository(database.scoped_session())
    method_and_state = repo.get_method_and_state_by_run_id(run_id)
    if method_and_state is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Method and state not found')
    return Dto.MethodAndState.model_validate(method_and_state)


@router.get('/{run_id}/run_log', response_model_exclude_none=True)
def get_recent_run_run_log(user_roles: UserRolesValue, run_id: str) -> Dto.RunLog:
    repo = RecentRunRepository(database.scoped_session())
    get_recent_run_or_fail(user_roles, run_id)
    run_log_db = repo.get_run_log_by_run_id(run_id)
    if run_log_db is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Run Log not found')
    run_log_mdl = Mdl.RunLog.model_validate(run_log_db)
    return Dto.RunLog(lines=list(map(Dto.RunLogLine.from_model, run_log_mdl.lines)))


@router.get('/{run_id}/plot_configuration', response_model_exclude_none=True)
def get_recent_run_plot_configuration(user_roles: UserRolesValue, run_id: str) -> Dto.PlotConfiguration:
    repo = RecentRunRepository(database.scoped_session())
    get_recent_run_or_fail(user_roles, run_id)
    plot_configuration = repo.get_plot_configuration_by_run_id(run_id)
    if plot_configuration is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Plot Configuration not found')
    return Dto.PlotConfiguration.model_validate(plot_configuration)


@router.get('/{run_id}/plot_log', response_model_exclude_none=True)
def get_recent_run_plot_log(user_roles: UserRolesValue, run_id: str) -> Dto.PlotLog:
    get_recent_run_or_fail(user_roles, run_id)
    plot_repo = PlotLogRepository(database.scoped_session())
    plot_log_model = plot_repo.get_plot_log(run_id)
    if plot_log_model is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Plot Log not found')
    return Dto.PlotLog.model_validate(plot_log_model)


@router.get('/{run_id}/csv_json', response_model_exclude_none=True)
def get_recent_run_csv_json(user_roles: UserRolesValue, run_id: str) -> Dto.RecentRunCsv:
    recent_run = get_recent_run_or_fail(user_roles, run_id)

    plot_log_repo = PlotLogRepository(database.scoped_session())
    plot_log_model = plot_log_repo.get_plot_log(run_id)
    if plot_log_model is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Plot Log not found')

    plot_log = Dto.PlotLog.model_validate(plot_log_model)
    csv_string = generate_csv_string(plot_log, Dto.RecentRun.model_validate(recent_run))
    filename = f'{recent_run.engine_id}_{recent_run.started_date:%Y%m%d_%H%M%S}.csv'
    return Dto.RecentRunCsv(filename=filename, csv_content=csv_string.getvalue())


@router.get('/{run_id}/error_log', response_model_exclude_none=True)
def get_recent_run_error_log(user_roles: UserRolesValue, run_id: str) -> Dto.AggregatedErrorLog:
    get_recent_run_or_fail(user_roles, run_id)
    repo = RecentRunRepository(database.scoped_session())
    error_log = repo.get_error_log_by_run_id(run_id)
    if error_log is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Error Log not found')
    return Dto.AggregatedErrorLog.from_model(Mdl.AggregatedErrorLog.model_validate(error_log))
