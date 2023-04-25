from datetime import datetime
from enum import StrEnum, auto
from typing import List, Literal

from fastapi import FastAPI
from pydantic import BaseModel

# TODO
# - add lsp thingys
# - start (manage) lsp server instance for each client
# - aggregator-engine protocol


# Start env in docker
# ../docker compose up --build

# start local
# python -m uvicorn main:app --reload --port 8300

# check generation openapi.json() from build action, see https://github.com/tiangolo/fastapi/issues/2877
# possibly https://pypi.org/project/fastapi-openapi-generator/

# hints for
# https://stackoverflow.com/questions/67849806/flask-how-to-automate-openapi-v3-documentation

# Look into this https://stackoverflow.com/questions/74137116/how-to-hide-a-pydantic-discriminator-field-from-fastapi-docs
# Final / Literal ...

title = "Pectus Aggregator"
print(f"*** {title} ***")
app = FastAPI(title=title)


class ProcessUnitStateEnum(StrEnum):
    """ Represents the state of a process unit. """
    READY = auto()
    IN_PROGRESS = auto()
    NOT_ONLINE = auto()


class ProcessUnitState():
    class Ready(BaseModel):
        state: Literal[ProcessUnitStateEnum.READY]

    class InProgress(BaseModel):
        state: Literal[ProcessUnitStateEnum.IN_PROGRESS]
        progress_pct: int

    class NotOnline(BaseModel):
        state: Literal[ProcessUnitStateEnum.NOT_ONLINE]
        last_seen_date: datetime


class ProcessUnit(BaseModel):
    """Represents a process unit. """

    id: int
    name: str
    state: ProcessUnitState.Ready | ProcessUnitState.InProgress | ProcessUnitState.NotOnline
    location: str | None
    runtime_msec: int | None
    # users: List[User] ?

# @app.get("/to_expose_process_unit_state_enum_in_openapi")
# def to_expose_process_unit_state_enum_in_openapi() -> ProcessUnitStateEnum:
#     return Type[ProcessUnitStateEnum]

@app.get("/process_unit/{id}")
def get_unit(id: int) -> ProcessUnit:
    return ProcessUnit(
        id=3,
        name="Foo",
        state=ProcessUnitState.Ready(),  # type: ignore
        location="H21.5",
        runtime_msec=189309,
    )


@app.get("/process_units")
def get_units() -> List[ProcessUnit]:
    return [
        ProcessUnit(
            id=3,
            name="Foo",
            state=ProcessUnitState.InProgress(progress_pct=75),  # type: ignore
            location="H21.5",
            runtime_msec=189309,
        )]


class BatchJob(BaseModel):
    """ Represents a current or historical run of a process unit. """
    id: int
    unit_id: int
    unit_name: str
    completed_date: datetime
    contributors: List[str] = []


@app.get("/batch_job/{id}")
def get_batch(id: int) -> BatchJob:
    dt = datetime(2023, 3, 21, 12, 31, 57, 0)
    return BatchJob(id=id, unit_id=3, unit_name="Foo", completed_date=dt, contributors=[])


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()


class ProcessValue(BaseModel):
    """ Represents a process value. """
    name: str
    value: str | float | int | None
    value_unit: str | None
    """ The unit string to display with the value, if any, e.g. 's', 'L/s' or '°C' """
    value_type: ProcessValueType
    """ Specifies the type of allowed values. """
    writable: bool
    options: List[str] | None


@app.get("/process_unit/{id}/process_values")
def get_process_values(id: int) -> List[ProcessValue]:  # naming?, parm last_seen
    return [ProcessValue(name="A-Flow", value=54, value_unit="L", writable=False, options=None,
            value_type=ProcessValueType.STRING)]


class ProcessValueUpdate(BaseModel):
    name: str
    value: str | float | int


@app.post("/process_unit/{id}/process_value")
def set_process_value(id: int, update: ProcessValueUpdate):
    pass
