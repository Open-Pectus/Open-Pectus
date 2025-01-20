from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from typing import Dict

from openpectus.aggregator.models import Method, MethodState, PlotConfiguration, RunLog, AggregatedErrorLog
from sqlalchemy import JSON, ForeignKey, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, attribute_keyed_dict


class DBModel(DeclarativeBase):
    """ Base model for data entity classes. """
    id: Mapped[int] = mapped_column(primary_key=True)
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


class RecentEngine(DBModel):
    __tablename__ = "RecentEngines"

    engine_id: Mapped[str] = mapped_column(unique=True)
    run_id: Mapped[str | None] = mapped_column()
    run_started: Mapped[datetime | None] = mapped_column()
    run_stopped: Mapped[datetime | None] = mapped_column()
    name: Mapped[str] = mapped_column()
    system_state: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    last_update: Mapped[datetime] = mapped_column()
    contributors: Mapped[list[str]] = mapped_column(type_=JSON, default=[])
    required_roles: Mapped[set[str]] = mapped_column(type_=JSON, default=[])


class RecentRun(DBModel):
    """ Represents a historical run of a process unit. """
    __tablename__ = "RecentRuns"
    engine_id: Mapped[str] = mapped_column()
    run_id: Mapped[str] = mapped_column()
    engine_computer_name: Mapped[str] = mapped_column()
    engine_version: Mapped[str] = mapped_column()
    engine_hardware_str: Mapped[str] = mapped_column()
    aggregator_computer_name: Mapped[str] = mapped_column()
    aggregator_version: Mapped[str] = mapped_column()
    uod_name: Mapped[str] = mapped_column()
    uod_filename: Mapped[str] = mapped_column()
    uod_author_name: Mapped[str] = mapped_column()
    uod_author_email: Mapped[str] = mapped_column()
    started_date: Mapped[datetime] = mapped_column()
    completed_date: Mapped[datetime] = mapped_column()
    contributors: Mapped[list[str]] = mapped_column(type_=JSON, default=[])  # really a set but this cannot be mapped?
    required_roles: Mapped[list[str]] = mapped_column(type_=JSON, default=[])  # really a set but this cannot be mapped?


class RecentRunMethodAndState(DBModel):
    __tablename__ = "RecentRunMethodAndStates"
    run_id: Mapped[str] = mapped_column()
    method: Mapped[Method] = mapped_column(type_=JSON)
    state: Mapped[MethodState] = mapped_column(type_=JSON)


class RecentRunRunLog(DBModel):
    __tablename__ = "RecentRunRunLogs"
    run_id: Mapped[str] = mapped_column()
    run_log: Mapped[RunLog] = mapped_column(type_=JSON)


class RecentRunErrorLog(DBModel):
    __tablename__ = "RecentRunErrorLogs"
    run_id: Mapped[str] = mapped_column()
    error_log: Mapped[AggregatedErrorLog] = mapped_column(type_=JSON)


class RecentRunPlotConfiguration(DBModel):
    __tablename__ = "RecentRunPlotConfigurations"
    run_id: Mapped[str] = mapped_column()
    plot_configuration: Mapped[PlotConfiguration] = mapped_column(type_=JSON)


class PlotLogEntryValue(DBModel):
    __tablename__ = "PlotLogEntryValues"
    plot_log_entry_id: Mapped[int] = mapped_column(ForeignKey('PlotLogEntries.id'))
    tick_time: Mapped[float] = mapped_column()
    value_str: Mapped[str | None] = mapped_column()
    value_float: Mapped[float | None] = mapped_column()
    value_int: Mapped[int | None] = mapped_column()

    @property
    def value(self):
        if self.value_int is not None:
            return self.value_int
        if self.value_float is not None:
            return self.value_float
        if self.value_str is not None:
            return self.value_str


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
    values: Mapped[list[PlotLogEntryValue]] = relationship(cascade="all, delete-orphan")
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
