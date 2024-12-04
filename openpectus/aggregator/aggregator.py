import asyncio
import logging
from datetime import datetime, timezone

import openpectus.aggregator.models as Mdl
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import RecentRunRepository, PlotLogRepository, RecentEngineRepository
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import EngineData
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from openpectus.protocol.models import SystemTagName, MethodStatusEnum

logger = logging.getLogger(__name__)

EngineDataMap = dict[str, EngineData]


class FromEngine:
    def __init__(self, engine_data_map: EngineDataMap, publisher: FrontendPublisher):
        self._engine_data_map = engine_data_map
        self.publisher = publisher

    def register_engine_data(self, engine_data: EngineData):
        logger.debug(f"Data for engine {engine_data.engine_id} registered")
        self._engine_data_map[engine_data.engine_id] = engine_data
        asyncio.create_task(self.publisher.publish_process_units_changed())
        asyncio.create_task(self.publisher.publish_control_state_changed(engine_data.engine_id))

    def engine_connected(self, engine_id: str):
        logger.debug("engine_connected")

    def engine_disconnected(self, engine_id: str):
        logger.debug("engine_disconnected")
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is not None:
            with database.create_scope():
                repo = RecentEngineRepository(database.scoped_session())
                repo.store_recent_engine(engine_data)
            logger.info("Recent engine saved")
            del self._engine_data_map[engine_id]
            asyncio.create_task(self.publisher.publish_process_units_changed())
        else:
            logger.warning("No data to save for engine " + engine_id)

    def engine_reconnected(self, msg: EM.ReconnectedMsg):
        logger.info(f"Engine_reconnected. Processing ReconnectedMsg {msg.ident}")
        engine_id = msg.engine_id
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error("No engine data available on reconnect for engine " + engine_id)
            return

        # Use this to debug reconnect msg timestamps/older tags
        # created_time = datetime.fromtimestamp(msg.created_tick).strftime("%H:%M:%S")
        # logger.debug(f"ReconnectedMsg created_tick_time: {created_time})")

        # ft02 = next((tag for tag in msg.tags if tag.name == "FT02"))
        # ft02_time = datetime.fromtimestamp(ft02.tick_time).strftime("%H:%M:%S")
        # logger.debug(f"ReconnectedMsg ft02_time: {ft02_time})")

        # apply the state from msg to the current state
        engine_data.method = msg.method
        run_id_tag = next((tag for tag in msg.tags if tag.name == SystemTagName.RUN_ID), None)
        # verify consistent message
        if msg.run_id is None:
            if run_id_tag is not None and run_id_tag.value is not None:
                logger.error(f"Mismatch in ReconnectedMsg, tag run_id {run_id_tag.value}, msg run_id {msg.run_id}")
                return
        else:
            if run_id_tag is None or run_id_tag.value is None:
                logger.error(f"Mismatch in ReconnectedMsg, tag run_id {None}, msg run_id {msg.run_id}")
                return
            engine_data.run_data.run_started = datetime.fromtimestamp(msg.run_started_tick) \
                if msg.run_started_tick is not None else None
            engine_data.tags_info.upsert(run_id_tag)  # sets engine_data.run_id

        # handle possible change to recent engine
        with database.create_scope():
            repo = RecentEngineRepository(database.scoped_session())
            recent_engine = repo.get_recent_engine_by_engine_id(engine_id)
            if recent_engine is None:
                logger.info(f"Reconnected engine {engine_id} has no recent engine data")
            else:
                if recent_engine.run_id != msg.run_id and recent_engine.run_id is not None:
                    logger.info("Marking recent engine stopped ")
                    repo.mark_recent_engine_stopped(engine_data)

        # process tag values normally
        self.tag_values_changed(engine_id, msg.tags)
        logger.info(f"Done processing ReconnectedMsg {msg.ident}")

    def run_started(self):  # to replace run_id_changed guessing
        raise NotImplementedError()

    def run_stopped(self):
        raise NotImplementedError()

    def uod_info_changed(
            self,
            engine_id: str,
            readings: list[Mdl.ReadingInfo],
            commands: list[Mdl.CommandInfo],
            plot_configuration: Mdl.PlotConfiguration,
            hardware_str: str,
            required_roles: set[str],
            data_log_interval_seconds: float):
        try:
            self._engine_data_map[engine_id].readings = readings
            self._engine_data_map[engine_id].commands = commands
            self._engine_data_map[engine_id].plot_configuration = plot_configuration
            self._engine_data_map[engine_id].hardware_str = hardware_str
            self._engine_data_map[engine_id].required_roles = required_roles
            self._engine_data_map[engine_id].data_log_interval_seconds = data_log_interval_seconds
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set uod info.')

    def tag_values_changed(self, engine_id: str, changed_tag_values: list[Mdl.TagValue]):
        with database.create_scope():
            plot_log_repo = PlotLogRepository(database.scoped_session())
            recent_run_repo = RecentRunRepository(database.scoped_session())

            engine_data = self._engine_data_map.get(engine_id)
            if engine_data is None:
                logger.error(f'No engine registered under id {engine_id} when trying to upsert tag values.')
                return

            for changed_tag_value in changed_tag_values:
                if changed_tag_value.name == SystemTagName.METHOD_STATUS.value:
                    if changed_tag_value.value == MethodStatusEnum.ERROR:
                        engine_data.run_data.interrupted_by_error = True
                    else:
                        engine_data.run_data.interrupted_by_error = False

                if changed_tag_value.name == SystemTagName.RUN_ID.value:
                    self._run_id_changed(plot_log_repo, recent_run_repo, engine_data, changed_tag_value)

                was_inserted = engine_data.tags_info.upsert(changed_tag_value)

                if changed_tag_value.name in [
                    SystemTagName.METHOD_STATUS.value,
                    SystemTagName.SYSTEM_STATE.value,
                    SystemTagName.RUN_ID.value,
                ]:
                    asyncio.create_task(self.publisher.publish_process_units_changed())

                # if a tag doesn't appear with value until after start and run_id, we need to store the info here
                if was_inserted and engine_data.run_id is not None:
                    plot_log_repo.store_new_tag_info(engine_data.engine_id, engine_data.run_id, changed_tag_value)

            self._persist_tag_values(engine_data, plot_log_repo)

    def _run_id_changed(
            self,
            plot_log_repo: PlotLogRepository,
            recent_run_repo: RecentRunRepository,
            engine_data: EngineData,
            run_id_tag: Mdl.TagValue):
        """ Handles persistance related to start and end of a run """

        logger.info(f"RunId changed from {engine_data.run_id} to {run_id_tag.value}, Engine: {engine_data.engine_id}")
        if run_id_tag.value is None and engine_data.run_id is None:
            logger.info("Engine has no active run")
        elif run_id_tag.value is None and engine_data.run_id is not None:
            # Run stopped
            logger.info(f"Run was stopped. Saving Recent Run. Engine: {engine_data.engine_id}")
            recent_run_repo.store_recent_run(engine_data)
            engine_data.run_data.error_log = Mdl.AggregatedErrorLog.empty()
            asyncio.create_task(self.publisher.publish_error_log_changed(engine_data.engine_id))
        elif run_id_tag.value is not None and engine_data.run_id is not None:
            # Ongoing run. run_id was only detected as changed because of complete tags set,
            # caused by e.g. an aggregator restart
            if run_id_tag.value != engine_data.run_id:
                logger.error(f"Run_Id inconsistent, run_id tag {run_id_tag.value}, engine_data {engine_data.run_id}")
            else:
                logger.info(f"Run {run_id_tag.value} resumed")
        else:
            # Run started
            logger.info(f"A new Run was started, Engine: {engine_data.engine_id}, Run_Id: {str(run_id_tag.value)}")
            engine_data.run_data.run_started = datetime.fromtimestamp(run_id_tag.tick_time, timezone.utc)
            plot_log_repo.create_plot_log(engine_data, str(run_id_tag.value))

    def _persist_tag_values(self, engine_data: EngineData, plot_log_repo: PlotLogRepository):
        latest_persisted_tick_time = engine_data.run_data.latest_persisted_tick_time
        tag_values = engine_data.tags_info.map.values()
        latest_tag_tick_time = max([tag.tick_time for tag in tag_values]) if len(tag_values) > 0 else 0
        time_threshold_exceeded = latest_persisted_tick_time is None or latest_tag_tick_time - latest_persisted_tick_time > engine_data.data_log_interval_seconds

        if engine_data.run_id is not None and time_threshold_exceeded:
            tag_values_to_persist = [tag_value.copy() for tag_value in engine_data.tags_info.map.values()
                                     if latest_persisted_tick_time is None
                                     or tag_value.tick_time > latest_persisted_tick_time]
            """
            We manipulate the tick_time of the tagValues we persist. But it's not changing it to something that didn't
            exist in the engine, because we change the tick_time to a tick_time that comes from an actual later reading
            where those tagValues we manipulate was read and simply had not changed value since the value we have been
            reported.
            It's difficult to explain, but after this manipulation, the tagValues will still match an actual tagValue
            read in the engine, just not one reported.
            We do this because it solves a lot of issues when we later try to match values based on the tick_time.
            """
            highest_tick_time_to_persist = max([tag_Value.tick_time for tag_Value in tag_values_to_persist])
            for tag_value_to_persist in tag_values_to_persist:
                tag_value_to_persist.tick_time = highest_tick_time_to_persist

            # Note: to store tag values, the run_id is needed
            plot_log_repo.store_tag_values(engine_data.engine_id, engine_data.run_id, tag_values_to_persist)
            engine_data.run_data.latest_persisted_tick_time = highest_tick_time_to_persist
            engine_data.run_data.latest_tag_time = highest_tick_time_to_persist

    def runlog_changed(self, engine_id: str, runlog: Mdl.RunLog):
        try:
            engine_data = self._engine_data_map[engine_id]
            if engine_data.run_data.runlog != runlog:
                engine_data.run_data.runlog = runlog
                asyncio.create_task(self.publisher.publish_run_log_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set run log.')

    def control_state_changed(self, engine_id: str, control_state: Mdl.ControlState):
        try:
            engine_data = self._engine_data_map[engine_id]
            if engine_data.control_state != control_state:
                engine_data.control_state = control_state
                asyncio.create_task(self.publisher.publish_control_state_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set control state.')

    def method_state_changed(self, engine_id: str, method_state: Mdl.MethodState):
        try:
            engine_data = self._engine_data_map[engine_id]
            if engine_data.run_data.method_state != method_state:
                engine_data.run_data.method_state = method_state
                asyncio.create_task(self.publisher.publish_method_state_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set control state.')

    def error_log_changed(self, engine_id: str, error_log: Mdl.ErrorLog):
        try:
            engine_data = self._engine_data_map[engine_id]
            engine_data.run_data.error_log.aggregate_with(error_log)
            asyncio.create_task(self.publisher.publish_error_log_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set error log.')


class FromFrontend:
    def __init__(self, engine_data_map: EngineDataMap, dispatcher: AggregatorDispatcher):
        self._engine_data_map = engine_data_map
        self.dispatcher = dispatcher

    async def method_saved(self, engine_id: str, method: Mdl.Method, user_name: str) -> bool:
        try:
            response = await self.dispatcher.rpc_call(engine_id, message=AM.MethodMsg(method=method))
            if isinstance(response, M.ErrorMessage):
                logger.error(f"Failed to set method. Engine response: {response.message}")
                return False
        except Exception:
            logger.error("Failed to set method", exc_info=True)
            return False

        # update local method state
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is not None:
            engine_data.method = method
            engine_data.contributors.add(user_name)
        return True

    async def request_cancel(self, engine_id, line_id: str, user_name: str) -> bool:
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.warning(f"Cannot request cancel, engine {engine_id} not found")
            return False
        try:
            response = await self.dispatcher.rpc_call(engine_id, message=AM.CancelMsg(exec_id=line_id))
            if isinstance(response, M.ErrorMessage):
                logger.error(f"Cancel request failed. Engine response: {response.message}")
                return False
        except Exception:
            logger.error("Cancel request failed with exception", exc_info=True)
            return False
        engine_data.contributors.add(user_name)
        return True

    async def request_force(self, engine_id, line_id: str, user_name: str) -> bool:
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.warning(f"Cannot request force, engine {engine_id} not found")
            return False
        try:
            response = await self.dispatcher.rpc_call(engine_id, message=AM.ForceMsg(exec_id=line_id))
            if isinstance(response, M.ErrorMessage):
                logger.error(f"Force request failed. Engine response: {response.message}")
                return False
        except Exception:
            logger.error("Force request failed with exception", exc_info=True)
            return False
        engine_data.contributors.add(user_name)
        return True


class Aggregator:
    def __init__(self, dispatcher: AggregatorDispatcher, publisher: FrontendPublisher) -> None:
        self._engine_data_map: EngineDataMap = {}
        """ all client data except channels, indexed by engine_id """
        self.dispatcher = dispatcher
        self.from_frontend = FromFrontend(self._engine_data_map, dispatcher)
        self.from_engine = FromEngine(self._engine_data_map, publisher)

    def create_engine_id(self, register_engine_msg: EM.RegisterEngineMsg):
        """ Defines the generation of the engine_id that is uniquely assigned to each engine.

        TODO: Considerations:
            - engine name should be machine name
            - uod hash should probably be included

        Implications of the registration process
        - historical data; we should not corrupt historical data by accidentially reusing engine_id
        - number of cards shown; we should not show many irrelevant cards in frontend of superseeded engine_ids
        """
        return register_engine_msg.computer_name + "_" + register_engine_msg.uod_name

    def get_registered_engine_data(self, engine_id: str):
        return self._engine_data_map.get(engine_id)

    def get_all_registered_engine_data(self) -> list[EngineData]:
        return list(self._engine_data_map.values())

    def has_registered_engine_id(self, engine_id: str) -> bool:
        return engine_id in self._engine_data_map.keys()
