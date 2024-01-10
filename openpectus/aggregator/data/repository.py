import logging
import time
from typing import List

from openpectus.aggregator.data import database
from openpectus.aggregator.data.models import ProcessValueType, BatchJobData, PlotLogEntryValue, get_ProcessValueType_from_value, PlotLog, \
    PlotLogEntry
from openpectus.aggregator.models import TagValue, ReadingInfo, EngineData
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# from https://dev.to/tobias-piotr/patterns-and-practices-for-using-sqlalchemy-20-with-fastapi-49n8
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     engine = create_async_engine(settings.DATABASE_URL)
#     factory = async_sessionmaker(engine)
#     async with factory() as session:
#         try:
#             yield session
#             await session.commit()
#         except exc.SQLAlchemyError as error:
#             await session.rollback()
#             raise


class RepositoryBase():
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session


class PlotLogRepository(RepositoryBase):
    def create_plot_log(self, engine_data: EngineData, run_id: str):
        plot_log = PlotLog()
        plot_log.engine_id = engine_data.engine_id
        plot_log.run_id = run_id

        def map_reading(reading: ReadingInfo):
            entry = PlotLogEntry()
            entry.plot_log = plot_log
            entry.value_type = ProcessValueType.NONE
            entry.name = reading.label
            return entry

        entries = map(map_reading, engine_data.readings)

        self.db_session.add(plot_log)
        self.db_session.add_all(entries)
        self.db_session.commit()

        # store info from existing tags
        for tag in engine_data.tags_info.map.values():
            self.store_new_tag_info(engine_data.engine_id, tag)


    def store_new_tag_info(self, engine_id: str, tag: TagValue):
        existing_plot_log_entry = self.get_plot_log_entry(engine_id, tag)
        if existing_plot_log_entry is None:
            logger.debug(f'tag {tag.name} was not found in readings')
            return
        existing_plot_log_entry.value_unit = tag.value_unit
        existing_plot_log_entry.value_type = get_ProcessValueType_from_value(tag.value)
        self.db_session.add(existing_plot_log_entry)
        self.db_session.commit()

    def get_plot_log(self, engine_id: str) -> PlotLog | None:
        return self.db_session.scalar(
            select(PlotLog)
            .join(PlotLog.entries)
            .join(PlotLogEntry.values)
            .where(PlotLog.engine_id == engine_id)
        )

    def get_plot_log_entry(self, engine_id: str, tag: TagValue) -> PlotLogEntry | None:
        return self.db_session.scalar(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
            .where(PlotLogEntry.name == tag.name)
        )

    def get_plot_log_entries(self, engine_id: str) -> List[PlotLogEntry]:
        return list(self.db_session.scalars(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
        ).all())

    def store_tag_values(self, engine_id: str, tags: List[TagValue]):
        plot_log_entries = self.get_plot_log_entries(engine_id)

        def map_tag_to_entry_value(tag: TagValue):
            plot_log_entry = next((entry for entry in plot_log_entries if entry.name == tag.name), None)
            if plot_log_entry is None:
                return None
            return PlotLogEntryValue(
                plot_log_entry_id=plot_log_entry.id,
                tick_time=tag.tick_time,
                value_str=tag.value if isinstance(tag.value, str) else None,
                value_float=tag.value if isinstance(tag.value, float) else None,
                value_int=tag.value if isinstance(tag.value, int) else None,
            )

        db_models = (entry_value for entry_value in map(map_tag_to_entry_value, tags) if entry_value is not None)
        self.db_session.add_all(db_models)
        self.db_session.commit()


class BatchJobDataRepository(RepositoryBase):
    # def upsert(self, process_unit: BatchJobData):
    #     self.session.
    #     process_unit.save()

    def get_by_id(self, id: int) -> BatchJobData | None:
        return self.db_session.get(BatchJobData, id)

    def get_by_engine_id(self, engine_id: str) -> BatchJobData | None:
        q = select(BatchJobData).where(BatchJobData.engine_id == engine_id)
        result = self.db_session.execute(q).first()
        if result is None:
            return None
        return result.tuple()[0]
