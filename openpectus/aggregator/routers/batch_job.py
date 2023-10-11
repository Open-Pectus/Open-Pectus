from datetime import datetime
from typing import List

from aggregator.routers.dto import Method, RunLog
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["batch_job"])


class BatchJob(BaseModel):
    """ Represents a current or historical run of a process unit. """
    id: str
    unit_id: str
    unit_name: str
    completed_date: datetime
    contributors: List[str] = []

@router.get("/batch_job/{id}")
def get_batch_job(id: str) -> BatchJob:
    dt = datetime(2023, 3, 21, 12, 31, 57, 0)
    return BatchJob(id=id, unit_id="3", unit_name="Foo", completed_date=dt, contributors=[])

@router.get("/recent_batch_jobs")
def get_recent_batch_jobs() -> List[BatchJob]:
    return []

@router.get('/batch_job/{id}/method')
def get_batch_job_method(id: str) -> Method:
    return Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])

@router.get('/batch_job/{id}/run_log')
def get_batch_job_run_log(id: str) -> RunLog:
    return RunLog(lines=[])
