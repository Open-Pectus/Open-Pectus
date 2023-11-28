import logging
from typing import Dict, List

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
import openpectus.aggregator.models as Mdl
from openpectus.aggregator.models import EngineData
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher

logger = logging.getLogger(__name__)

class Aggregator:
    def __init__(self, dispatcher: AggregatorDispatcher) -> None:
        # self.channel_map: Dict[str, ChannelInfo] = {}
        # """ channel data, indexed by channel_id"""
        self._engine_data_map: Dict[str, EngineData] = {}
        """ all client data except channels, indexed by engine_id """
        self.dispatcher = dispatcher

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

    def register_engine_data(self, engine_data: EngineData):
        self._engine_data_map[engine_data.engine_id] = engine_data

    def set_readings(self, engine_id: str, readings: List[Mdl.ReadingInfo]):
        try:
            self._engine_data_map[engine_id].readings = readings
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set readings.')

    def upsert_tag_values(self, engine_id: str, tag_values: List[Mdl.TagValue]):
        try:
            engine_data = self._engine_data_map[engine_id]
            for tag_value in tag_values:
                engine_data.tags_info.upsert(tag_value.name, tag_value.value, tag_value.value_unit)
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to upsert tag values.')

    def set_runlog(self, engine_id: str, runlog: Mdl.RunLog):
        try:
            self._engine_data_map[engine_id].runlog = runlog
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set run log.')

    def set_control_state(self, engine_id: str, control_state: Mdl.ControlState):
        try:
            self._engine_data_map[engine_id].control_state = control_state
        except KeyError:
            logger.error(f'No engine registered under id {engine_id} when trying to set control state.')

    def get_method(self, engine_id: str) -> AM.MethodMsg | None:
        engine_data = self._engine_data_map.get(engine_id)
        if engine_data is None:
            return None

        logger.info(f"Returned local method with {len(engine_data.method.lines)} lines")
        return AM.MethodMsg(method=engine_data.method)

    async def set_method(self, engine_id: str, method: Mdl.Method) -> bool:
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
