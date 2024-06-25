import asyncio
import logging
import time
from datetime import UTC, datetime, timezone

import openpectus.aggregator.models as Mdl
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import RecentRunRepository, PlotLogRepository, RecentEngineRepository
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import EngineData
from openpectus.protocol.models import SystemTagName, MethodStatusEnum

logger = logging.getLogger(__name__)

EngineDataMap = dict[str, EngineData]
persistance_threshold_seconds = 5


class FromEngine:
    def __init__(self, engine_data_map: EngineDataMap, publisher: FrontendPublisher):
        self._engine_data_map = engine_data_map
        self.publisher = publisher
        self.was_connected = False
        self.is_connected = False

    def register_engine_data(self, engine_data: EngineData):
        # Why do we do this?
        # - initially because run_started is a value we generated - could calculate it again looking at plot log values
        #   the value is used when _ to  _ 

        # repo = RecentEngineRepository(database.scoped_session())
        # recent_engine = repo.get_recent_engine_by_engine_id(engine_id=engine_data.engine_id)
        # if recent_engine is not None:
        #     # update engine provided data with RecentEngine db data
        #     engine_data.run_data.run_started = recent_engine.run_started        
        logger.info(f"Data for engine {engine_data.engine_id} registered")
        self._engine_data_map[engine_data.engine_id] = engine_data

    def engine_connected(self, engine_id: str):
        logger.info("engine_connected")
        self.is_connected = True
        if self.was_connected:
            self.engine_reconnected()
            return
        
        self.was_connected = True
    #     if not engine_id in self._engine_data_map.keys():
    #         logger.info(f"Pre-registered engine {engine_id} connected")
    #         repo = RecentEngineRepository(database.scoped_session())
    #         recent_engine = repo.get_recent_engine_by_engine_id(engine_id=engine_id)
    #         if recent_engine is None:
    #             raise KeyError("Preregisttered engine had no RecenEngine data. What to do?")            
            
    #         engine_data = Mdl.EngineData(
    #                 engine_id=engine_id,
    #                 computer_name=recent_engine.com,
    #                 uod_name=register_engine_msg.uod_name,
    #                 location=register_engine_msg.location,
    #                 engine_version=register_engine_msg.engine_version
    #             )


    def engine_disconnected(self, engine_id: str):
        self.is_connected = False
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

    def engine_reconnected(self):
        logger.info("engine_reconnected")

    def run_started(self):  # to replace run_id_changed guessing
        raise NotImplementedError()
    
    def run_stopped(self):
        raise NotImplementedError()
    

    def uod_info_changed(self, engine_id: str, readings: list[Mdl.ReadingInfo], plot_configuration: Mdl.PlotConfiguration,
                         hardware_str: str):
        try:
            self._engine_data_map[engine_id].readings = readings
            self._engine_data_map[engine_id].plot_configuration = plot_configuration
            self._engine_data_map[engine_id].hardware_str = hardware_str
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set uod info.')

    def tag_values_changed(self, engine_id: str, changed_tag_values: list[Mdl.TagValue]):
        plot_log_repo = PlotLogRepository(database.scoped_session())
        recent_run_repo = RecentRunRepository(database.scoped_session())
        recent_engine_repo = RecentEngineRepository(database.scoped_session())

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
                self._run_id_changed(plot_log_repo, recent_run_repo, recent_engine_repo, engine_data, changed_tag_value)

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
            recent_engine_repo: RecentEngineRepository,
            engine_data: EngineData,
            run_id_tag: Mdl.TagValue):
        """ Handles persistance related to start and end of a run """

        # Check whether we've been restarted while a run was ongoing. If so, we need to
        # prepare the engine_data state the run to continue by setting engine_data properties
        if engine_data.run_id is None and run_id_tag.value is not None:
            # yes, our run_id was not set but the incoming run_id tag was set.
            # depending on recent_engine state this either means the run was already running
            # or that it just started
            recent_engine = recent_engine_repo.get_recent_engine_by_engine_id(engine_data.engine_id)
            if recent_engine is not None and recent_engine.run_id is not None and recent_engine.run_stopped is None:
                if recent_engine.run_id == run_id_tag.value:
                    engine_data.tags_info.upsert(run_id_tag)  # sets engine_data.run_id
                    engine_data.run_data.run_started = recent_engine.run_started

        logger.info(f"RunId changed from {engine_data.run_id} to {run_id_tag.value}, Engine: {engine_data.engine_id}")
        if run_id_tag.value is None and engine_data.run_id is None:
            # Engine was reconnected            
            # if recent_engine is not None:
            #     if recent_engine.run_started is not None and recent_engine.run_stopped is None:
                    

            logger.info("Engine has no active run")
        elif run_id_tag.value is None and engine_data.run_id is not None:
            # Run stopped
            logger.info(f"Run was stopped. Saving Recent Run. Engine: {engine_data.engine_id}")
            recent_run_repo.store_recent_run(engine_data)
            recent_engine_repo.mark_recent_engine_stopped(engine_data)
            engine_data.run_data.error_log = Mdl.ErrorLog.empty()
            asyncio.create_task(self.publisher.publish_error_log_changed(engine_data.engine_id))
        elif run_id_tag.value is not None and engine_data.run_id is not None:
            # Ongoing run. run_id was only detected as changed because of aggregator restart
            assert run_id_tag.value == engine_data.run_id
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
        time_threshold_exceeded = latest_persisted_tick_time is None \
            or latest_tag_tick_time - latest_persisted_tick_time > persistance_threshold_seconds
        # time_threshold_exceeded = latest_persisted_tick_time is None \
        #     or time.time() - latest_persisted_tick_time > persistance_threshold_seconds
        if engine_data.run_id is not None and time_threshold_exceeded:
            tag_values_to_persist = [tag_value.copy() for tag_value in engine_data.tags_info.map.values()
                                     if latest_persisted_tick_time is None
                                     or tag_value.tick_time > latest_persisted_tick_time]
            logger.info(f"Persisting {len(tag_values_to_persist)} of possible {len(engine_data.tags_info.map.keys())}")
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
            engine_data.run_data.error_log.entries.extend(error_log.entries)
            asyncio.create_task(self.publisher.publish_error_log_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set error log.')


class FromFrontend:
    def __init__(self, engine_data_map: EngineDataMap, dispatcher: AggregatorDispatcher):
        self._engine_data_map = engine_data_map
        self.dispatcher = dispatcher

    async def method_saved(self, engine_id: str, method: Mdl.Method) -> bool:
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
