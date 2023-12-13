from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto
from typing import Any, List, Optional

import openpectus.aggregator.data.database as database
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class DBModel(DeclarativeBase):
    """ Base model for data entity classes. """
    registry = database.reg
    id: Mapped[int] = mapped_column(primary_key=True)


class ProcessUnitData(DBModel):
    """Represents a live process unit (engine). """

    __tablename__ = "ProcessUnitData"

    engine_id: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    runtime_msec: Mapped[int] = mapped_column()
    current_user_role: Mapped[str] = mapped_column()
    # users = JSONField()  # List[User] ?
    # def set_state(self, state: ProcessUnitState):


class BatchJobData(DBModel):
    """ Represents a historical run of a process unit. """

    __tablename__ = "BatchJobData"

    engine_id: Mapped[str] = mapped_column()
    computer_name: Mapped[str] = mapped_column()
    uod_name: Mapped[str] = mapped_column()
    started_date: Mapped[Optional[datetime]] = mapped_column()
    completed_date: Mapped[Optional[datetime]] = mapped_column()

    _contributors_json: Mapped[Optional[dict[str, Any]]] = mapped_column(type_=JSON, name="contributors")

    @property
    def contributors(self) -> List[str]:
        """ Typed accessor for the _contributors_json field. """
        if self._contributors_json is None:
            return []
        return self._contributors_json["v"]

    @contributors.setter
    def contributors(self, value: List[str]):
        """ Note: Because is a limitation in JSON storage change tracking, never mutate the value. Always assign a new
        instance containg the new value.

        Details: https://github.com/Open-Pectus/Open-Pectus/issues/251. """
        self._contributors_json = {"v": value}

    # tags_info: TagsInfo = TagsInfo(map={})
    # runlog: JSON = JSON()
    # method: Method = Method(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


# class BatchJobProcessValuesData(DBModel):
#     #batch_id: foreign key to
#     # values

class PlotLogEntryValue(DBModel):
    __tablename__ = "PlotLogEntryValues"
    plot_log_entry_id: Mapped[int] = mapped_column(ForeignKey('PlotLogEntries.id'))
    # value: Mapped[str | float | int | None] = mapped_column()
    value_str: Mapped[Optional[str]] = mapped_column()
    value_float: Mapped[Optional[float]] = mapped_column()
    value_int: Mapped[Optional[int]] = mapped_column()


class ProcessValueType(StrEnum):
    STRING = auto()
    FLOAT = auto()
    INT = auto()
    CHOICE = auto()


class PlotLogEntry(DBModel):
    __tablename__ = "PlotLogEntries"
    name: Mapped[str] = mapped_column()
    values: Mapped[List[PlotLogEntryValue]] = relationship(cascade="all, delete-orphan")
    value_unit: Mapped[str | None] = mapped_column()
    value_type: Mapped[ProcessValueType] = mapped_column()
    plot_log_id: Mapped[int] = mapped_column(ForeignKey('PlotLogs.id'))
    plot_log: Mapped[PlotLog] = relationship(back_populates='entries')


class PlotLog(DBModel):
    __tablename__ = "PlotLogs"
    engine_id: Mapped[str] = mapped_column()
    entries: Mapped[List[PlotLogEntry]] = relationship(
        back_populates='plot_log',
        cascade="all, delete-orphan"
    )
