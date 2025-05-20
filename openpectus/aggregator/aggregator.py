import asyncio
import copy
import logging
from datetime import datetime, timezone

from fastapi_websocket_rpc import RpcChannel
import openpectus.aggregator.models as Mdl
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import RecentRunRepository, PlotLogRepository, RecentEngineRepository
from openpectus.aggregator.frontend_publisher import FrontendPublisher, PubSubTopic
from openpectus.aggregator.models import EngineData
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from openpectus.protocol.models import SystemTagName, MethodStatusEnum
from openpectus.aggregator.exceptions import AggregatorCallerException, AggregatorInternalException

logger = logging.getLogger(__name__)

EngineDataMap = dict[str, EngineData]


class FromEngine:
    def __init__(self, engine_data_map: EngineDataMap, publisher: FrontendPublisher):
        self._engine_data_map = engine_data_map
        self.publisher = publisher

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_data_map={self._engine_data_map}, publisher={self.publisher})'

    def register_engine_data(self, engine_data: EngineData):
        engine_id = engine_data.engine_id
        logger.debug(f"Data for engine {engine_id} registered")
        self._engine_data_map[engine_id] = engine_data

        self._try_restore_reconnected_engine_data(engine_data)

        asyncio.create_task(self.publisher.publish_process_units_changed())
        asyncio.create_task(self.publisher.publish_control_state_changed(engine_data.engine_id))

    def _try_restore_reconnected_engine_data(self, engine_data: EngineData):
        engine_id = engine_data.engine_id
        logger.debug(f"Trying to restore engine data for recent engine: {engine_id}")
        with database.create_scope():
            repo = RecentEngineRepository(database.scoped_session())
            recent_engine = repo.get_recent_engine_by_engine_id(engine_id)
        if recent_engine is not None:  # reconnecting an existing engine
            if recent_engine.run_id is not None:  # that was in an active run when disconnected
                run_id = recent_engine.run_id
                logger.debug(f"Applying run_data {run_id=} from recent_engine")
                if recent_engine.run_started is None:
                    logger.warning("Recent engine had a run without run_started value. Using now as run_started")
                    run_started = datetime.now(timezone.utc)
                else:
                    run_started = recent_engine.run_started
                engine_data.run_data = Mdl.RunData.empty(run_id=run_id, run_started=run_started)
                engine_data.contributors = set(recent_engine.contributors)
            else:
                logger.info("Recent engine data has no active run")
        else:
            logger.info("No recent engine data found")

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

    def run_started(self, msg: EM.RunStartedMsg):
        engine_id = msg.engine_id
        engine_data = self._engine_data_map.get(engine_id)
        with database.create_scope():
            if engine_data is None:
                logger.error("No engine data available on run_started for engine " + engine_id)
                return
            if not engine_data.has_run():
                engine_data.reset_run()
                engine_data.run_data = Mdl.RunData.empty(
                    run_id=msg.run_id,
                    run_started=datetime.fromtimestamp(msg.started_tick, timezone.utc)
                )
            elif engine_data.run_data.run_id == msg.run_id:
                # be idempotent and just accept this duplicate message
                logger.warning("Event run_started occurred with same id as the current run. Ignoring")
            else:
                _run_id = engine_data.run_data.run_id
                logger.error(f"Current run_id {_run_id} does not match RunStartedMsg run_id {msg.run_id}")
                recent_run_repo = RecentRunRepository(database.scoped_session())
                try:
                    recent_run_repo.store_recent_run(engine_data)
                    logger.info(f"Stopping existing run and store it as recent run {_run_id=}")
                    engine_data.reset_run()
                except Exception:
                    logger.error(f"Failed to persist recent run {_run_id=}", exc_info=True)

            plot_log_repo = PlotLogRepository(database.scoped_session())
            plot_log_repo.create_plot_log(engine_data, msg.run_id)

        asyncio.create_task(self.publisher.publish_control_state_changed(engine_id))
        logger.info(f"Run {msg.run_id} started")

    def run_stopped(self, msg: EM.RunStoppedMsg):
        engine_id = msg.engine_id
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error("No engine data available on run_stopped for engine " + engine_id)
            return
        if not engine_data.has_run():
            logger.warning("No engine run_data available on run_stopped for engine " + engine_id)
            return

        with database.create_scope():
            recent_run_repo = RecentRunRepository(database.scoped_session())
            _run_id = engine_data.run_data.run_id
            if _run_id != msg.run_id:
                logger.error(
                    "Run_id mismatch in run_stopped. " +
                    f"engine {engine_id}, run_data run_id: {engine_data.run_data.run_id}, message run_id: {_run_id}")
                logger.warning(f"Saving existing run {_run_id}. No data is available for the other run")
                try:
                    recent_run_repo.store_recent_run(engine_data)
                    logger.info(f"Stored recent run {_run_id=}")
                except Exception:
                    logger.error(f"Failed to persist recent run {_run_id=}")
                engine_data.reset_run()
            else:
                engine_data.run_data.runlog = msg.runlog
                engine_data.method_state = msg.method_state
                try:
                    recent_run_repo.store_recent_run(engine_data)
                    logger.info(f"Stored recent run {_run_id=}")
                except Exception:
                    logger.error(f"Failed to persist recent run {_run_id=}")

        # clear current run_data
        engine_data.reset_run()
        asyncio.create_task(self.publisher.publish_control_state_changed(engine_id))
        asyncio.create_task(self.publisher.publish_method_state_changed(engine_id))
        asyncio.create_task(self.publisher.publish_run_log_changed(engine_id))
        logger.info(f"Run {msg.run_id} stopped")

    def uod_info_changed(
            self,
            engine_id: str,
            readings: list[Mdl.ReadingInfo],
            commands: list[Mdl.CommandInfo],
            uod_definition: Mdl.UodDefinition,
            plot_configuration: Mdl.PlotConfiguration,
            hardware_str: str,
            required_roles: set[str],
            data_log_interval_seconds: float):
        try:
            self._engine_data_map[engine_id].readings = readings
            self._engine_data_map[engine_id].commands = commands
            self._engine_data_map[engine_id].uod_definition = uod_definition
            self._engine_data_map[engine_id].plot_configuration = plot_configuration
            self._engine_data_map[engine_id].hardware_str = hardware_str
            self._engine_data_map[engine_id].required_roles = required_roles
            self._engine_data_map[engine_id].data_log_interval_seconds = data_log_interval_seconds
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set uod info.')

    def tag_values_changed(self, engine_id: str, changed_tag_values: list[Mdl.TagValue]):
        with database.create_scope():
            plot_log_repo = PlotLogRepository(database.scoped_session())

            engine_data = self._engine_data_map.get(engine_id)
            if engine_data is None:
                logger.error(f'No engine registered under id {engine_id} when trying to upsert tag values.')
                return

            for changed_tag_value in changed_tag_values:
                if changed_tag_value.name == SystemTagName.METHOD_STATUS.value and engine_data.has_run():
                    if changed_tag_value.value == MethodStatusEnum.ERROR:
                        engine_data.run_data.interrupted_by_error = True
                    else:
                        engine_data.run_data.interrupted_by_error = False

                was_inserted = engine_data.tags_info.upsert(changed_tag_value)

                if changed_tag_value.name in [
                    SystemTagName.METHOD_STATUS.value,
                    SystemTagName.SYSTEM_STATE.value,
                    SystemTagName.RUN_ID.value,
                ]:
                    asyncio.create_task(self.publisher.publish_process_units_changed())

                # if a tag doesn't appear with value until after start and run_id, we need to store the info here
                if was_inserted and engine_data.has_run():
                    plot_log_repo.store_new_tag_info(engine_data.engine_id, engine_data.run_data.run_id, changed_tag_value)

            self._persist_tag_values(engine_data, plot_log_repo)

    def __run_id_changed(
            self,
            plot_log_repo: PlotLogRepository,
            recent_run_repo: RecentRunRepository,
            engine_data: EngineData,
            run_id_tag: Mdl.TagValue):
        """ Handles persistance related to start and end of a run """
        raise NotImplementedError("not needed anymore")

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
        if not engine_data.has_run():
            return
        assert engine_data.run_data is not None  # would be nice to have this given by the has_run() result

        latest_persisted_tick_time = engine_data.run_data.latest_persisted_tick_time
        tag_values = engine_data.tags_info.map.values()
        latest_tag_tick_time = max([tag.tick_time for tag in tag_values]) if len(tag_values) > 0 else 0
        time_threshold_exceeded = latest_persisted_tick_time is None\
            or latest_tag_tick_time - latest_persisted_tick_time > engine_data.data_log_interval_seconds

        if engine_data.run_data.run_id is not None and time_threshold_exceeded:
            tag_values_to_persist = [tag_value.model_copy() for tag_value in engine_data.tags_info.map.values()
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
            plot_log_repo.store_tag_values(engine_data.engine_id, engine_data.run_data.run_id, tag_values_to_persist)
            engine_data.run_data.latest_persisted_tick_time = highest_tick_time_to_persist
            engine_data.run_data.latest_tag_time = highest_tick_time_to_persist

    def runlog_changed(self, engine_id: str, run_id: str, runlog: Mdl.RunLog):
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error(f'No engine registered under id {engine_id} when trying to set run log.')
            return
        if not engine_data.has_run():
            logger.error(f"No run_data available for engine {engine_id}, can't set runlog")
            return
        if engine_data.run_data.run_id is None or engine_data.run_data.run_id != run_id:
            logger.error(
                "Run_id mismatch in runlog_changed. " +
                f"engine {engine_id}, run_data run_id: {engine_data.run_data.run_id}, message run_id: {run_id}")
            return

        if engine_data.run_data.runlog != runlog:
            engine_data.run_data.runlog = runlog
            asyncio.create_task(self.publisher.publish_run_log_changed(engine_id))

    def control_state_changed(self, engine_id: str, control_state: Mdl.ControlState):
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error(f'No engine registered under id {engine_id} when trying to set control state.')
            return
        if engine_data.control_state != control_state:
            engine_data.control_state = control_state
            asyncio.create_task(self.publisher.publish_control_state_changed(engine_id))

    def method_state_changed(self, engine_id: str, method_state: Mdl.MethodState):
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error(f'No engine registered under id {engine_id} when trying to set method state.')
            return
        if engine_data.method_state != method_state:
            engine_data.method_state = method_state
            asyncio.create_task(self.publisher.publish_method_state_changed(engine_id))

    def error_log_changed(self, engine_id: str, error_log: Mdl.ErrorLog):
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error(f'No engine registered under id {engine_id} when trying to set error log.')
            return
        engine_data.error_log.aggregate_with(error_log)
        asyncio.create_task(self.publisher.publish_error_log_changed(engine_id))


class FromFrontend:
    def __init__(self, engine_data_map: EngineDataMap, dispatcher: AggregatorDispatcher, publisher: FrontendPublisher):
        self._engine_data_map = engine_data_map
        self.dispatcher = dispatcher
        self.publisher = publisher
        self.dead_man_switch_user_ids: dict[str, str] = dict()
        self.publisher.register_on_disconnect(self.on_ws_disconnect)
        self.publisher.pubsub_endpoint.methods.event_notifier.register_subscribe_event(self.user_subscribed_pubsub)  # type: ignore

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_data_map={self._engine_data_map}, dispatcher={self.dispatcher})'

    async def method_saved(self, engine_id: str, method: Mdl.Method, user_name: str) -> int:
        existing_version = self._engine_data_map[engine_id].method.version
        version_to_overwrite = method.version
        logger.debug(f"Save method version: {method.version}")
        if existing_version != version_to_overwrite:
            raise AggregatorCallerException(f"Method version mismatch: trying to overwrite version {version_to_overwrite}" +
                                            f"when existing version is {existing_version}")
        # Take shallow copy and increment version
        new_method = copy.copy(method)
        new_method.version += 1

        try:
            response = await self.dispatcher.rpc_call(engine_id, message=AM.MethodMsg(method=new_method))
            if isinstance(response, M.ErrorMessage):
                logger.error(f"Failed to set method. Engine response: {response.message}")
                if response.caller_error:
                    raise AggregatorCallerException(response.message)
                else:
                    raise AggregatorInternalException(response.message)
        except Exception as e:
            logger.error("Failed to set method", exc_info=True)
            raise e

        # update local method state
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is not None:
            engine_data.method = new_method
            engine_data.contributors.add(user_name)
            asyncio.create_task(self.publisher.publish_method_changed(engine_id))
        return new_method.version

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

    def get_dead_man_switch_user_ids(self, topics: list[str]):
        return (topic.split("/")[1] for topic in topics if topic.startswith(PubSubTopic.DEAD_MAN_SWITCH))

    async def user_subscribed_pubsub(self, subscriber_id: str, topics: list[str]):
        for user_id in self.get_dead_man_switch_user_ids(topics):
            self.dead_man_switch_user_ids[subscriber_id] = user_id

    async def on_ws_disconnect(self, subscriber_id: str):
        user_id = self.dead_man_switch_user_ids[subscriber_id]
        user_has_other_dead_man_switch = len([other_user_id for other_user_id in self.dead_man_switch_user_ids.values() if other_user_id == user_id]) > 1
        if(user_has_other_dead_man_switch): return
        for engine_data in self._engine_data_map.values():
            popped_user_id = engine_data.active_users.pop(user_id, None)
            if(popped_user_id != None):
                asyncio.create_task(self.publisher.publish_active_users_changed(engine_data.engine_id))

    async def register_active_user(self, engine_id: str, user_id: str, user_name: str):
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.warning(f"Cannot register active user, engine {engine_id} not found")
            return False
        engine_data.active_users[user_id] = (Mdl.ActiveUser(
            id=user_id,
            name=user_name,
        ))
        asyncio.create_task(self.publisher.publish_active_users_changed(engine_id))
        return True

    async def unregister_active_user(self, engine_id: str, user_id: str):
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.warning(f"Cannot unregister active user, engine {engine_id} not found")
            return False
        if engine_data.active_users.pop(user_id, None) is None:
            logger.warning(f"Couldn't unregister active user, user with id {user_id} was not found")
            return False
        asyncio.create_task(self.publisher.publish_active_users_changed(engine_id))
        return True

class Aggregator:
    def __init__(self, dispatcher: AggregatorDispatcher, publisher: FrontendPublisher, secret: str = "") -> None:
        self._engine_data_map: EngineDataMap = {}
        """ all client data except channels, indexed by engine_id """
        self.dispatcher = dispatcher
        self.from_frontend = FromFrontend(self._engine_data_map, dispatcher, publisher)
        self.from_engine = FromEngine(self._engine_data_map, publisher)
        self.secret = secret

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(dispatcher={self.dispatcher}, ' +
                f'from_frontend={self.from_frontend}, from_engine={self.from_engine})')

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
