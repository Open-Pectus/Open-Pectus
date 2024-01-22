import logging
from datetime import datetime
from typing import List, Iterable

from openpectus.aggregator.data.models import RecentRunMethodAndState, ProcessValueType, RecentRun, PlotLogEntryValue, \
    get_ProcessValueType_from_value, PlotLog, PlotLogEntry, RecentRunPlotConfiguration, RecentRunRunLog
from openpectus.aggregator.models import TagValue, ReadingInfo, EngineData
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


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
            entry.name = reading.tag_name
            return entry

        entries = map(map_reading, engine_data.readings)

        self.db_session.add(plot_log)
        self.db_session.add_all(entries)
        self.db_session.commit()

        # store info from existing tags
        for tag in engine_data.tags_info.map.values():
            self.store_new_tag_info(engine_data.engine_id, run_id, tag)


    def store_new_tag_info(self, engine_id: str, run_id: str, tag: TagValue):
        existing_plot_log_entry = self.get_plot_log_entry(engine_id, run_id, tag)
        if existing_plot_log_entry is None:
            logger.debug(f'tag {tag.name} was not found in readings')
            return
        existing_plot_log_entry.value_unit = tag.value_unit
        existing_plot_log_entry.value_type = get_ProcessValueType_from_value(tag.value)
        self.db_session.add(existing_plot_log_entry)
        self.db_session.commit()

    def get_plot_log(self, run_id: str) -> PlotLog | None:
        return self.db_session.scalar(
            select(PlotLog)
            .join(PlotLog.entries)
            .join(PlotLogEntry.values)
            .where(PlotLog.run_id == run_id)
        )

    def get_plot_log_entry(self, engine_id: str, run_id: str, tag: TagValue) -> PlotLogEntry | None:
        return self.db_session.scalar(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
            .where(PlotLogEntry.name == tag.name)
            .where(PlotLog.run_id == run_id)
        )

    def get_plot_log_entries(self, engine_id: str, run_id: str) -> Iterable[PlotLogEntry]:
        return self.db_session.scalars(
            select(PlotLogEntry)
            .join(PlotLog)
            .where(PlotLog.engine_id == engine_id)
            .where(PlotLog.run_id == run_id)
        ).all()

    def store_tag_values(self, engine_id: str, run_id: str, tags: List[TagValue]):
        plot_log_entries = self.get_plot_log_entries(engine_id, run_id)

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


class RecentRunRepository(RepositoryBase):
    def store_recent_run(self, engine_data: EngineData):
        if engine_data.run_id is None: raise ValueError('misisng run_id when trying to store recent run')
        if engine_data.run_data.run_started is None: raise ValueError('misisng run_started when trying to store recent run')
        recent_run = RecentRun()
        recent_run.engine_id = engine_data.engine_id
        recent_run.run_id = engine_data.run_id
        recent_run.computer_name = engine_data.computer_name
        recent_run.uod_name = engine_data.uod_name
        recent_run.started_date = engine_data.run_data.run_started
        recent_run.completed_date = datetime.now()
        # recent_run.contributers = engine_data.

        method_and_state = RecentRunMethodAndState()
        method_and_state.run_id = engine_data.run_id
        method_and_state.method = engine_data.method
        method_and_state.state = engine_data.run_data.method_state

        plot_configuration = RecentRunPlotConfiguration()
        plot_configuration.run_id = engine_data.run_id
        plot_configuration.process_value_names_to_annotate = engine_data.plot_configuration.process_value_names_to_annotate
        plot_configuration.color_regions = engine_data.plot_configuration.color_regions
        plot_configuration.sub_plots = engine_data.plot_configuration.sub_plots
        plot_configuration.x_axis_process_value_names = engine_data.plot_configuration.x_axis_process_value_names

        run_log = RecentRunRunLog()
        run_log.run_id = engine_data.run_id
        run_log.lines = engine_data.run_data.runlog.lines

        self.db_session.add(recent_run)
        self.db_session.add(method_and_state)
        self.db_session.add(plot_configuration)
        self.db_session.add(run_log)
        self.db_session.commit()

    def get_by_run_id(self, run_id: str) -> RecentRun | None:
        return self.db_session.scalar(select(RecentRun).where(RecentRun.run_id==run_id))

    def get_by_engine_id(self, engine_id: str) -> Iterable[RecentRun]:
        return self.db_session.scalars(
            select(RecentRun)
            .where(RecentRun.engine_id == engine_id)
        ).all()

    def get_all(self) -> Iterable[RecentRun]:
        return self.db_session.scalars(select(RecentRun)).all()

    def get_method_and_state_by_run_id(self, run_id: str):
        return self.db_session.scalar(select(RecentRunMethodAndState).where(RecentRunMethodAndState.run_id==run_id))

    def get_plot_configuration_by_run_id(self, run_id: str):
        return self.db_session.scalar(select(RecentRunPlotConfiguration).where(RecentRunPlotConfiguration.run_id==run_id))

    def get_run_log_by_run_id(self, run_id: str):
        return self.db_session.scalar(select(RecentRunRunLog).where(RecentRunRunLog.run_id==run_id))
