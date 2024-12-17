import logging
from datetime import UTC, datetime, timedelta, timezone
from socket import gethostname
from typing import Iterable, Sequence

from openpectus import __version__
from openpectus.aggregator.data.models import (
    RecentEngine,
    ProcessValueType,
    RecentRunErrorLog, RecentRunMethodAndState, RecentRun, PlotLogEntryValue,
    RecentRunPlotConfiguration, RecentRunRunLog,
    get_ProcessValueType_from_value,
    PlotLog, PlotLogEntry
)
from openpectus.aggregator.models import TagValue, ReadingInfo, EngineData
from sqlalchemy import select
from sqlalchemy.orm import Session

from openpectus.protocol.models import SystemTagName

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

    def store_tag_values(self, engine_id: str, run_id: str, tags: list[TagValue]):
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
        """ Store a recent run. Requires that engine_data contain run_data. """
        if not engine_data.has_run():
            raise ValueError('missing run_data when trying to store recent run')
        assert engine_data.has_run(), "Run data must be set when saving recent run"
        run_id = engine_data.run_data.run_id
        recent_run = RecentRun()
        recent_run.engine_id = engine_data.engine_id
        recent_run.run_id = run_id
        recent_run.engine_computer_name = engine_data.computer_name
        recent_run.engine_version = engine_data.engine_version
        recent_run.engine_hardware_str = engine_data.hardware_str
        recent_run.aggregator_version = __version__
        recent_run.aggregator_computer_name = gethostname()
        recent_run.uod_name = engine_data.uod_name
        recent_run.uod_author_name = engine_data.uod_author_name
        recent_run.uod_author_email = engine_data.uod_author_email
        recent_run.uod_filename = engine_data.uod_filename
        recent_run.started_date = engine_data.run_data.run_started
        recent_run.completed_date = datetime.now(timezone.utc)
        current_contributors = set(recent_run.contributors or [])
        for user_name in engine_data.contributors:  # append contributers from this 'session'
            current_contributors.add(user_name)
        recent_run.contributors = list(current_contributors)  # must assign new instance in json field
        recent_run.required_roles = list(engine_data.required_roles)

        method_and_state = RecentRunMethodAndState()
        method_and_state.run_id = run_id
        method_and_state.method = engine_data.method
        method_and_state.state = engine_data.method_state

        plot_configuration = RecentRunPlotConfiguration()
        plot_configuration.run_id = run_id
        plot_configuration.plot_configuration = engine_data.plot_configuration

        run_log = RecentRunRunLog()
        run_log.run_id = run_id
        run_log.run_log = engine_data.run_data.runlog

        error_log = RecentRunErrorLog()
        error_log.run_id = run_id
        error_log.error_log = engine_data.error_log

        self.db_session.add(recent_run)
        self.db_session.add(method_and_state)
        self.db_session.add(plot_configuration)
        self.db_session.add(run_log)
        self.db_session.add(error_log)
        self.db_session.commit()

    def get_by_run_id(self, run_id: str) -> RecentRun | None:
        return self.db_session.scalar(select(RecentRun).where(RecentRun.run_id == run_id))

    def get_by_engine_id(self, engine_id: str) -> Iterable[RecentRun]:
        return self.db_session.scalars(
            select(RecentRun)
            .where(RecentRun.engine_id == engine_id)
        ).all()

    def get_all(self) -> Iterable[RecentRun]:
        return self.db_session.scalars(select(RecentRun)).all()

    def get_method_and_state_by_run_id(self, run_id: str):
        return self.db_session.scalar(select(RecentRunMethodAndState).where(RecentRunMethodAndState.run_id == run_id))

    def get_plot_configuration_by_run_id(self, run_id: str):
        return self.db_session.scalar(
            select(RecentRunPlotConfiguration.plot_configuration).where(RecentRunPlotConfiguration.run_id == run_id)
        )

    def get_run_log_by_run_id(self, run_id: str):
        return self.db_session.scalar(select(RecentRunRunLog.run_log).where(RecentRunRunLog.run_id == run_id))

    def get_error_log_by_run_id(self, run_id: str):
        return self.db_session.scalar(select(RecentRunErrorLog.error_log).where(RecentRunErrorLog.run_id == run_id))


class RecentEngineRepository(RepositoryBase):
    def get_recent_engines(self) -> Sequence[RecentEngine]:
        last_month = datetime.now() - timedelta(days=30)
        return self.db_session.scalars(
            select(RecentEngine)
            .where(RecentEngine.last_update > last_month)
        ).all()

    def get_recent_engine_by_engine_id(self, engine_id: str) -> RecentEngine | None:
        return self.db_session.scalar(select(RecentEngine).where(RecentEngine.engine_id == engine_id))

    def store_recent_engine(self, engine_data: EngineData):
        if engine_data.engine_id == "":
            raise ValueError("Missing/empty engine_id when trying to store recent_engine")
        existing = self.get_recent_engine_by_engine_id(engine_data.engine_id)
        if existing is None:
            recent_engine = RecentEngine()
        else:
            recent_engine = existing
        recent_engine.engine_id = engine_data.engine_id
        if engine_data.has_run():
            assert engine_data.run_data is not None
            recent_engine.run_id = engine_data.run_data.run_id
            recent_engine.run_started = engine_data.run_data.run_started
            contributors = set(recent_engine.contributors)
            for c in engine_data.contributors:
                contributors.add(c)
            recent_engine.contributors = list(contributors)
        else:
            recent_engine.run_id = None
            recent_engine.run_started = None
        recent_engine.run_stopped = None
        recent_engine.name = f"{engine_data.computer_name} ({engine_data.uod_name})"
        recent_engine.location = engine_data.location
        recent_engine.last_update = datetime.now(UTC)
        recent_engine.required_roles = engine_data.required_roles
        system_tag = engine_data.tags_info.get(SystemTagName.SYSTEM_STATE)
        recent_engine.system_state = str(system_tag.value) if system_tag is not None else ""
        if system_tag is None:
            logger.warning("The SYSTEM_STATE tag value was not available when saving recent_engine")
        self.db_session.add(recent_engine)
        self.db_session.commit()
