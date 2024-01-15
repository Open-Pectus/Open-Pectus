from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from typing import Any, List, Optional, Dict

import openpectus.aggregator.data.database as database
from openpectus.aggregator.models import Method, MethodState
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, attribute_keyed_dict


class DBModel(DeclarativeBase):
    """ Base model for data entity classes. """
    registry = database.reg
    id: Mapped[int] = mapped_column(primary_key=True)


class ProcessUnit(DBModel):
    """Represents a live process unit (engine). """

    __tablename__ = "ProcessUnits"

    engine_id: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    runtime_msec: Mapped[int] = mapped_column()
    current_user_role: Mapped[str] = mapped_column()
    # users = JSONField()  # List[User] ?
    # def set_state(self, state: ProcessUnitState):


class RecentRun(DBModel):
    """ Represents a historical run of a process unit. """
    __tablename__ = "RecentRuns"
    engine_id: Mapped[str] = mapped_column()
    run_id: Mapped[str] = mapped_column()
    computer_name: Mapped[str] = mapped_column()
    uod_name: Mapped[str] = mapped_column()
    started_date: Mapped[datetime] = mapped_column()
    completed_date: Mapped[datetime] = mapped_column()
    contributors: Mapped[list[str]] = mapped_column(type_=JSON, default=[])


class RecentRunMethodAndState(DBModel):
    __tablename__ = "RecentRunMethodAndStates"
    run_id: Mapped[str] = mapped_column()
    method: Mapped[Method] = mapped_column(type_=JSON)
    state: Mapped[MethodState] = mapped_column(type_=JSON)


class PlotLogEntryValue(DBModel):
    __tablename__ = "PlotLogEntryValues"
    plot_log_entry_id: Mapped[int] = mapped_column(ForeignKey('PlotLogEntries.id'))
    tick_time: Mapped[float] = mapped_column()
    value_str: Mapped[Optional[str]] = mapped_column()
    value_float: Mapped[Optional[float]] = mapped_column()
    value_int: Mapped[Optional[int]] = mapped_column()


ProcessValueValueType = str | float | int | None


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()
    CHOICE = auto()
    NONE = auto()


def get_ProcessValueType_from_value(value: ProcessValueValueType) -> ProcessValueType:
    if value is None:
        return ProcessValueType.NONE
    if isinstance(value, str):
        return ProcessValueType.STRING
    elif isinstance(value, int):
        return ProcessValueType.INT
    elif isinstance(value, float):
        return ProcessValueType.FLOAT
    else:
        raise ValueError("Invalid value type: " + type(value).__name__)


class PlotLogEntry(DBModel):
    __tablename__ = "PlotLogEntries"
    name: Mapped[str] = mapped_column()
    values: Mapped[List[PlotLogEntryValue]] = relationship(cascade="all, delete-orphan")
    value_unit: Mapped[str | None] = mapped_column()
    value_type: Mapped[ProcessValueType] = mapped_column()
    plot_log_id: Mapped[int] = mapped_column(ForeignKey('PlotLogs.id'))
    plot_log: Mapped[PlotLog] = relationship()


class PlotLog(DBModel):
    __tablename__ = "PlotLogs"
    engine_id: Mapped[str] = mapped_column()
    run_id: Mapped[str] = mapped_column()
    entries: Mapped[Dict[str, PlotLogEntry]] = relationship(
        collection_class=attribute_keyed_dict("name"),
        back_populates='plot_log',
        cascade="all, delete-orphan"
    )
