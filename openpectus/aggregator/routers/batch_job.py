from datetime import datetime
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from openpectus.aggregator.routers.dto import Method, RunLog, PlotConfiguration, PlotLog
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["batch_job"])


class BatchJob(BaseModel):
    """ Represents a current or historical run of a process unit. """
    id: str
    unit_id: str
    unit_name: str
    started_date: datetime
    completed_date: datetime
    contributors: List[str] = []


class BatchJobCsv(BaseModel):
    filename: str
    csv_content: str


@router.get("/batch_job/{id}")
def get_batch_job(id: str) -> BatchJob:
    dt = datetime(2023, 3, 21, 12, 31, 57, 0)
    return BatchJob(id=id, unit_id="3", unit_name="Foo", started_date=dt, completed_date=dt, contributors=[])


@router.get("/recent_batch_jobs")
def get_recent_batch_jobs() -> List[BatchJob]:
    return []


@router.get('/batch_job/{id}/method')
def get_batch_job_method(id: str) -> Method:
    return Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


@router.get('/batch_job/{id}/run_log')
def get_batch_job_run_log(id: str) -> RunLog:
    return RunLog(lines=[])


@router.get('/batch_job/{id}/plot_configuration')
def get_batch_job_plot_configuration(id: str) -> PlotConfiguration:
    return PlotConfiguration(
        color_regions=[],
        sub_plots=[],
        process_value_names_to_annotate=[],
        x_axis_process_value_names=[]
    )


@router.get('/batch_job/{id}/plot_log')
def get_batch_job_plot_log(id: str) -> PlotLog:
    return PlotLog(entries={})


@router.get('/batch_job/{id}/csv_json')
def get_batch_job_csv_json(id: str) -> BatchJobCsv:
    return BatchJobCsv(filename=f'BatchJob-{id}.csv', csv_content='some;CSV;here\nand;more;here')


@router.get('/batch_job/{id}/csv_file', response_class=StreamingResponse)
def get_batch_job_csv_file(id: str) -> StreamingResponse:
    file_content = 'some;CSV;here\nand;more;here'
    file_name = f'BatchJob-{id}.csv'
    return StreamingResponse(
        content=iter([file_content]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment;filename="{file_name}"'}
    )
