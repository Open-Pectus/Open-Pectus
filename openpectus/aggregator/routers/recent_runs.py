from typing import List

import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository, RecentRunRepository

router = APIRouter(tags=["recent_runs"], prefix='/recent_runs')


@router.get("/")
def get_recent_runs() -> List[Dto.RecentRun]:
    repo = RecentRunRepository(database.scoped_session())
    return list(map(Dto.RecentRun.from_orm, repo.get_all()))


@router.get("/{run_id}")
def get_recent_run(run_id: str) -> Dto.RecentRun:
    repo = RecentRunRepository(database.scoped_session())
    return Dto.RecentRun.from_orm(repo.get_by_run_id(run_id))


@router.get('/{run_id}/method-and-state')
def get_recent_run_method_and_state(run_id: str) -> Dto.MethodAndState:
    repo = RecentRunRepository(database.scoped_session())
    return Dto.MethodAndState.from_orm(repo.get_method_and_state_by_run_id(run_id))


@router.get('/{id}/run_log')
def get_recent_run_run_log(id: str) -> Dto.RunLog:
    return Dto.RunLog(lines=[])


@router.get('/{run_id}/plot_configuration')
def get_recent_run_plot_configuration(run_id: str) -> Dto.PlotConfiguration:
    repo = RecentRunRepository(database.scoped_session())
    return Dto.PlotConfiguration.from_orm(repo.get_plot_configuration_by_run_id(run_id))


@router.get('/{run_id}/plot_log')
def get_recent_run_plot_log(run_id: str) -> Dto.PlotLog:
    repo = PlotLogRepository(database.scoped_session())
    plot_log_model = repo.get_plot_log(run_id)
    if plot_log_model is None:
        return Dto.PlotLog(entries={})
    return Dto.PlotLog.from_orm(plot_log_model)


@router.get('/{id}/csv_json')
def get_recent_run_csv_json(id: str) -> Dto.RecentRunCsv:
    return Dto.RecentRunCsv(filename=f'RecentRun-{id}.csv', csv_content='some;CSV;here\nand;more;here')


@router.get('/{id}/csv_file', response_class=StreamingResponse)
def get_recent_run_csv_file(id: str) -> StreamingResponse:
    file_content = 'some;CSV;here\nand;more;here'
    file_name = f'RecentRun-{id}.csv'
    return StreamingResponse(
        content=iter([file_content]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment;filename="{file_name}"'}
    )
