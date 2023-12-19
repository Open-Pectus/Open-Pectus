import logging
from typing import List

from openpectus.aggregator.data import database
from openpectus.aggregator.data.models import BatchJobData, PlotLogEntryValue, get_ProcessValueType_from_value, PlotLog, PlotLogEntry
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
    pass
    # def __init__(self) -> None:
    #     self.session = get_db()


class PlotLogRepository(RepositoryBase):
    def create_plot_log(self, engine_data: EngineData, db_session: Session):
        plot_log = PlotLog()
        plot_log.engine_id = engine_data.engine_id

        def map_reading(reading: ReadingInfo):
            entry = PlotLogEntry()
            entry.plot_log = plot_log
            entry.name = reading.label
            return entry

        entries = list(map(map_reading, engine_data.readings))
        plot_log.entries = entries

        db_session.add(plot_log)
        db_session.add_all(entries)
        db_session.commit()

    def store_new_tag_info(self, engine_id: str, tag: TagValue, db_session: Session):
        existing_plot_log_entry = self.get_plot_log_entry(engine_id, tag, db_session)
        if existing_plot_log_entry is None:
            logger.debug(f'tag {tag.name} was not found in readings')
            return
        existing_plot_log_entry.value_unit = tag.value_unit
        existing_plot_log_entry.value_type = get_ProcessValueType_from_value(tag.value)
        db_session.add(existing_plot_log_entry)
        db_session.commit()

    def get_plot_log_entry(self, engine_id: str, tag: TagValue, db_session: Session) -> PlotLogEntry | None:
        return db_session.scalar(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
            .where(PlotLogEntry.name == tag.name)
        )

    def get_plot_log_entries(self, engine_id: str, db_session: Session) -> List[PlotLogEntry]:
        return list(db_session.scalars(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
        ).all())

    def store_tag_values(self, engine_id: str, tags: List[TagValue], db_session: Session):
        plot_log_entries = self.get_plot_log_entries(engine_id, db_session)

        def map_tag_to_entry_value(tag: TagValue):
            plot_log_entry = [entry for entry in plot_log_entries if entry.name == tag.name]
            if len(plot_log_entry) == 0:
                return None
            return PlotLogEntryValue(
                plot_log_entry_id=plot_log_entry[0].id,
                value_str=tag.value if isinstance(tag.value, str) else None,
                value_float=tag.value if isinstance(tag.value, float) else None,
                value_int=tag.value if isinstance(tag.value, int) else None,
            )

        db_models = [entry_value for entry_value in map(map_tag_to_entry_value, tags) if isinstance(entry_value, PlotLogEntryValue)]
        db_session.add_all(db_models)
        db_session.commit()


class BatchJobDataRepository(RepositoryBase):
    # def upsert(self, process_unit: BatchJobData):
    #     self.session.
    #     process_unit.save()

    def get_by_id(self, id: int, db_session: Session) -> BatchJobData | None:
        return db_session.get(BatchJobData, id)

    def get_by_engine_id(self, engine_id: str, db_session: Session) -> BatchJobData | None:
        q = select(BatchJobData).where(BatchJobData.engine_id == engine_id)
        result = db_session.execute(q).first()
        if result is None:
            return None
        return result.tuple()[0]
