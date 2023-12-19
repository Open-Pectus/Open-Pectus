from typing import List

from fastapi import Depends
from openpectus.aggregator.data import database
from openpectus.aggregator.data.models import PlotLogEntryValue, get_ProcessValueType_from_value, PlotLog, PlotLogEntry, BatchJobData
from openpectus.aggregator.models import TagValue, ReadingInfo, EngineData
from sqlalchemy import select
from sqlalchemy.orm import Session


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RepositoryBase():
    def __init__(self, session: Session = Depends(get_db)) -> None:
        self.session = session


class PlotLogRepository(RepositoryBase):
    def create_plot_log(self, engine_data: EngineData):
        plot_log = PlotLog()
        plot_log.engine_id = engine_data.engine_id

        def map_reading(reading: ReadingInfo):
            entry = PlotLogEntry()
            entry.plot_log = plot_log
            entry.name = reading.label
            return entry

        entries = list(map(map_reading, engine_data.readings))
        plot_log.entries = entries

        self.session.add(plot_log)
        self.session.add_all(entries)
        self.session.commit()

    def store_new_tag_info(self, engine_id: str, tag: TagValue):
        existing_plot_log_entry = self.get_plot_log_entry(engine_id, tag)
        if existing_plot_log_entry is None:
            raise ValueError('No existing log entry was found in db!')
        existing_plot_log_entry.value_unit = tag.value_unit
        existing_plot_log_entry.value_type = get_ProcessValueType_from_value(tag.value)
        self.session.add(existing_plot_log_entry)
        self.session.commit()

    def get_plot_log_entry(self, engine_id: str, tag: TagValue) -> PlotLogEntry | None:
        return self.session.scalar(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
            .where(PlotLogEntry.name == tag.name)
        )

    def get_plot_log_entries(self, engine_id: str) -> List[PlotLogEntry]:
        return list(self.session.scalars(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
        ).all())

    def store_tag_values(self, engine_id: str, tags: List[TagValue]):
        plot_log_entries = self.get_plot_log_entries(engine_id)

        def map_to_db_model(tag: TagValue):
            return PlotLogEntryValue(
                plot_log_entry_id=[entry for entry in plot_log_entries if entry.name == tag.name],
                value_str=tag.value if isinstance(tag.value, str) else None,
                value_float=tag.value if isinstance(tag.value, float) else None,
                value_int=tag.value if isinstance(tag.value, int) else None,
            )

        db_models = list(map(map_to_db_model, tags))
        self.session.add_all(db_models)
        self.session.commit()


class BatchJobDataRepository(RepositoryBase):

    # def upsert(self, process_unit: BatchJobData):
    #     self.session.
    #     process_unit.save()

    def get_by_id(self, id: int) -> BatchJobData | None:
        return self.session.get(BatchJobData, id)

    def get_by_engine_id(self, engine_id: str) -> BatchJobData | None:
        q = select(BatchJobData).where(BatchJobData.engine_id == engine_id)
        result = self.session.execute(q).first()
        if result is None:
            return None
        return result.tuple()[0]
