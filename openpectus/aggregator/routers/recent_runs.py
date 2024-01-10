from datetime import datetime
from typing import List

import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["recent_runs"], prefix='/recent_runs')


@router.get("/")
def get_recent_runs() -> List[Dto.RecentRun]:
    return []


@router.get("/{id}")
def get_recent_run(id: str) -> Dto.RecentRun:
    dt = datetime(2023, 3, 21, 12, 31, 57, 0)
    return Dto.RecentRun(id=id, unit_id="3", unit_name="Foo", started_date=dt, completed_date=dt, contributors=[])


@router.get('/{id}/method-and-state')
def get_recent_run_method_and_state(id: str) -> Dto.MethodAndState:
    return Dto.MethodAndState(method=Dto.Method(lines=[]), state=Dto.MethodState(started_line_ids=[], executed_line_ids=[], injected_line_ids=[]))


@router.get('/{id}/run_log')
def get_recent_run_run_log(id: str) -> Dto.RunLog:
    return Dto.RunLog(lines=[])


@router.get('/{id}/plot_configuration')
def get_recent_run_plot_configuration(id: str) -> Dto.PlotConfiguration:
    return Dto.PlotConfiguration(
        color_regions=[],
        sub_plots=[],
        process_value_names_to_annotate=[],
        x_axis_process_value_names=[]
    )


@router.get('/{id}/plot_log')
def get_recent_run_plot_log(id: str) -> Dto.PlotLog:
    return Dto.PlotLog(entries={})


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
