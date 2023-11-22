from openpectus.aggregator.models import EngineData
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.aggregator_messages as AM


class Aggregator:
    def __init__(self, dispatcher: AggregatorDispatcher) -> None:
        # self.channel_map: Dict[str, ChannelInfo] = {}
        # """ channel data, indexed by channel_id"""
        self.engine_data_map: Dict[str, EngineData] = {}
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

    def get_method(self, engine_id: str) -> AM.MethodMsg | None:
        engine_data = self.engine_data_map.get(engine_id)
        if engine_data is None:
            return None

        logger.info(f"Returned local method with {len(engine_data.method.lines)} lines")
        return engine_data.method

    async def set_method(self, engine_id: str, method: AM.MethodMsg) -> bool:
        try:
            response = await self.dispatcher.rpc_call(engine_id, message=method)
            if isinstance(response, ErrorMessage):
                logger.error(f"Failed to set method. Engine response: {response.message}")
                return False
        except Exception:
            logger.error("Failed to set method", exc_info=True)
            return False

        # update local method state
        engine_data = self.engine_data_map.get(engine_id)
        if engine_data is not None:
            engine_data.method = method

        return True
