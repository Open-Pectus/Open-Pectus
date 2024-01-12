import asyncio
import logging
from datetime import datetime, timedelta

import openpectus.aggregator.models as Mdl
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import EngineData
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from openpectus.protocol.models import SystemTagName

logger = logging.getLogger(__name__)

EngineDataMap = dict[str, EngineData]


class FromEngine:
    def __init__(self, engine_data_map: EngineDataMap, publisher: FrontendPublisher):
        self._engine_data_map = engine_data_map
        self.publisher = publisher

    def register_engine_data(self, engine_data: EngineData):
        self._engine_data_map[engine_data.engine_id] = engine_data

    def readings_changed(self, engine_id: str, readings: list[Mdl.ReadingInfo]):
        try:
            self._engine_data_map[engine_id].readings = readings
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set readings.')

    def tag_values_changed(self, engine_id: str, changed_tag_values: list[Mdl.TagValue]):
        plot_log_repo = PlotLogRepository(database.scoped_session())

        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            logger.error(f'No engine registered under id {engine_id} when trying to upsert tag values.')
            return

        for changed_tag_value in changed_tag_values:
            if changed_tag_value.name == SystemTagName.run_id.value:
                self._run_id_changed(plot_log_repo, engine_data, changed_tag_value)
            was_inserted = engine_data.tags_info.upsert(changed_tag_value)
            # if a tag doesn't appear with value until after start and run_id, we need to store the info here
            if was_inserted and engine_data.run_id is not None:
                plot_log_repo.store_new_tag_info(engine_data.engine_id, engine_data.run_id, changed_tag_value)

        self._persist_tag_values(engine_data, plot_log_repo)

    def _run_id_changed(self, plot_log_repo: PlotLogRepository, engine_data: EngineData, run_id_tag: Mdl.TagValue):
        """ Handles persistance related to start and end of a run """
        logger.warning(f'run id changed to {run_id_tag.value}')
        if run_id_tag.value is None:
            # TODO: persist and clear from engine_map: method, run log,
            pass
        else:
            plot_log_repo.create_plot_log(engine_data, str(run_id_tag.value))

    def _persist_tag_values(self, engine_data: EngineData, plot_log_repo: PlotLogRepository):
        now = datetime.now()
        time_threshold_exceeded = engine_data.tags_last_persisted is None or now - engine_data.tags_last_persisted > timedelta(seconds=5)
        if engine_data.run_id is not None and time_threshold_exceeded:
            tag_values_to_persist = [tag_value for tag_value in engine_data.tags_info.map.values()
                                     if engine_data.tags_last_persisted is None
                                     or tag_value.tick_time > engine_data.tags_last_persisted.timestamp()]
            plot_log_repo.store_tag_values(engine_data.engine_id, engine_data.run_id, tag_values_to_persist)
            engine_data.tags_last_persisted = now

    def runlog_changed(self, engine_id: str, runlog: Mdl.RunLog):
        try:
            engine_data = self._engine_data_map[engine_id]
            if engine_data.runlog != runlog:
                engine_data.runlog = runlog
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
            if engine_data.method_state != method_state:
                engine_data.method_state = method_state
                asyncio.create_task(self.publisher.publish_method_state_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set control state.')


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
        # self.channel_map: Dict[str, ChannelInfo] = {}
        # """ channel data, indexed by channel_id"""
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
