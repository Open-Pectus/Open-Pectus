from typing import List

import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openpectus.aggregator.csv_generator import generate_csv_string
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository, RecentRunRepository

router = APIRouter(tags=["recent_runs"], prefix='/recent_runs')


@router.get("/")
def get_recent_runs() -> List[Dto.RecentRun]:
    repo = RecentRunRepository(database.scoped_session())
    return list(map(Dto.RecentRun.validate, repo.get_all()))


@router.get("/{run_id}")
def get_recent_run(run_id: str) -> Dto.RecentRun:
    repo = RecentRunRepository(database.scoped_session())
    recent_run = repo.get_by_run_id(run_id)
    if recent_run is None:
        raise HTTPException(status_code=404, detail='Recent Run not found')
    return Dto.RecentRun.validate(recent_run)


@router.get('/{run_id}/method-and-state')
def get_recent_run_method_and_state(run_id: str) -> Dto.MethodAndState:
    repo = RecentRunRepository(database.scoped_session())
    method_and_state = repo.get_method_and_state_by_run_id(run_id)
    if method_and_state is None:
        raise HTTPException(status_code=404, detail='Method and state not found')
    return Dto.MethodAndState.validate(method_and_state)


@router.get('/{run_id}/run_log')
def get_recent_run_run_log(run_id: str) -> Dto.RunLog:
    repo = RecentRunRepository(database.scoped_session())
    run_log_db = repo.get_run_log_by_run_id(run_id)
    if run_log_db is None:
        raise HTTPException(status_code=404, detail='Run Log not found')
    run_log_mdl = Mdl.RunLog.validate(run_log_db)
    return Dto.RunLog(lines=list(map(Dto.RunLogLine.from_model, run_log_mdl.lines)))


@router.get('/{run_id}/plot_configuration')
def get_recent_run_plot_configuration(run_id: str) -> Dto.PlotConfiguration:
    repo = RecentRunRepository(database.scoped_session())
    plot_configuration = repo.get_plot_configuration_by_run_id(run_id)
    if plot_configuration is None:
        raise HTTPException(status_code=404, detail='Plot Configuration not found')
    return Dto.PlotConfiguration.validate(plot_configuration)


@router.get('/{run_id}/plot_log')
def get_recent_run_plot_log(run_id: str) -> Dto.PlotLog:
    repo = PlotLogRepository(database.scoped_session())
    plot_log_model = repo.get_plot_log(run_id)
    if plot_log_model is None:
        raise HTTPException(status_code=404, detail='Plot Log not found')
    return Dto.PlotLog.validate(plot_log_model)


@router.get('/{run_id}/csv_json')
def get_recent_run_csv_json(run_id: str) -> Dto.RecentRunCsv:
    plot_log_repo = PlotLogRepository(database.scoped_session())
    recent_run_repo = RecentRunRepository(database.scoped_session())

    plot_log_model = plot_log_repo.get_plot_log(run_id)
    if plot_log_model is None:
        raise HTTPException(status_code=404, detail='Plot Log not found')

    recent_run = recent_run_repo.get_by_run_id(run_id)
    if recent_run is None:
        raise HTTPException(status_code=404, detail='Recent Run not found')

    plot_log = Dto.PlotLog.validate(plot_log_model)
    csv_string = generate_csv_string(plot_log, Dto.RecentRun.validate(recent_run))
    return Dto.RecentRunCsv(filename=f'RecentRun-{run_id}.csv', csv_content=csv_string.getvalue())



@router.get('/{id}/csv_file', response_class=StreamingResponse)
def get_recent_run_csv_file(id: str) -> StreamingResponse:
    file_content = 'some;CSV;here\nand;more;here'
    file_name = f'RecentRun-{id}.csv'
    return StreamingResponse(
        content=iter([file_content]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment;filename="{file_name}"'}
    )
