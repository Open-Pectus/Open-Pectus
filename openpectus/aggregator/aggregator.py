import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

import openpectus.aggregator.models as Mdl
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.aggregator.data.repository import PlotLogRepository
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import EngineData
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

EngineDataMap = Dict[str, EngineData]


class FromEngine:
    def __init__(self, engine_data_map: EngineDataMap, publisher: FrontendPublisher):
        self._engine_data_map = engine_data_map
        self.publisher = publisher

    def register_engine_data(self, engine_data: EngineData):
        self._engine_data_map[engine_data.engine_id] = engine_data

    def readings_changed(self, engine_id: str, readings: List[Mdl.ReadingInfo], db_session: Session):
        plot_log_repo = PlotLogRepository(db_session)
        try:
            self._engine_data_map[engine_id].readings = readings
            plot_log_repo.create_plot_log(self._engine_data_map[engine_id])
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set readings.')

    def tag_values_changed(self, engine_id: str, tag_values: List[Mdl.TagValue], db_session: Session):
        plot_log_repo = PlotLogRepository(db_session)
        try:
            engine_data = self._engine_data_map[engine_id]
            for tag_value in tag_values:
                was_inserted = engine_data.tags_info.upsert(tag_value)
                if was_inserted:
                    plot_log_repo.store_new_tag_info(engine_id, tag_value)

            now = datetime.now()
            if engine_data.tags_last_persisted is None or now - engine_data.tags_last_persisted > timedelta(seconds=5):
                plot_log_repo.store_tag_values(engine_id, tag_values)
                engine_data.tags_last_persisted = now
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to upsert tag values.')

    def runlog_changed(self, engine_id: str, runlog: Mdl.RunLog, db_session: Session):
        try:
            engine_data = self._engine_data_map[engine_id]
            if engine_data.runlog != runlog:
                engine_data.runlog = runlog
                asyncio.create_task(self.publisher.publish_run_log_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set run log.')

    def control_state_changed(self, engine_id: str, control_state: Mdl.ControlState, db_session: Session):
        try:
            engine_data = self._engine_data_map[engine_id]
            if engine_data.control_state != control_state:
                engine_data.control_state = control_state
                asyncio.create_task(self.publisher.publish_control_state_changed(engine_id))
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set control state.')

    def method_state_changed(self, engine_id: str, method_state: Mdl.MethodState, db_session: Session):
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

    def get_all_registered_engine_data(self) -> List[EngineData]:
        return list(self._engine_data_map.values())

    def has_registered_engine_id(self, engine_id: str) -> bool:
        return engine_id in self._engine_data_map.keys()
