from typing import List

import openpectus.aggregator.models as Mdl
from fastapi import Depends
from openpectus.aggregator.data import database
from openpectus.aggregator.data.models import PlotLog, PlotLogEntry, BatchJobData
from openpectus.aggregator.models import EngineData
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

        def map_reading(reading: Mdl.ReadingInfo):
            # tag = engine_data.tags_info.get(reading.tag_name)
            entry = PlotLogEntry()
            entry.plot_log = plot_log
            entry.name = reading.label
            # entry.value_unit = tag.value_unit
            # entry.value_type = type(tag.value)
            # entry.values = [tag.value]
            return entry

        entries = list(map(map_reading, engine_data.readings))
        plot_log.entries = entries

        self.session.add(plot_log)
        self.session.add_all(entries)

    def store_plot_log_entry_values(self, engine_id: str, tags: List[Mdl.TagValue]):


        self.session.scalar(select(PlotLog).join(PlotLogEntry).where(PlotLog.engine_id == engine_id))


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
