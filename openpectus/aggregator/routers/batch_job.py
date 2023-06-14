from datetime import datetime
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["batch_job"])


class BatchJob(BaseModel):
    """ Represents a current or historical run of a process unit. """
    id: int
    unit_id: str
    unit_name: str
    completed_date: datetime
    contributors: List[str] = []


@router.get("/batch_job/{id}")
def get_batch(id: int) -> BatchJob:
    dt = datetime(2023, 3, 21, 12, 31, 57, 0)
    return BatchJob(id=id, unit_id="3", unit_name="Foo", completed_date=dt, contributors=[])


@router.get("/recent_batch_jobs")
def get_recent_batch_jobs() -> List[BatchJob]:
    return []
