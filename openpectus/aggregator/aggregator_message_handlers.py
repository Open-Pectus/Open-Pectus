import logging

from openpectus.aggregator.models.models import EngineData
from openpectus.aggregator.aggregator import Aggregator
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M

logger = logging.getLogger(__name__)


class AggregatorMessageHandlers:
    def __init__(self, aggregator: Aggregator):
        self.aggregator = aggregator
        aggregator.dispatcher.set_post_handler(EM.RegisterEngineMsg, self.handle_RegisterEngineMsg)
        aggregator.dispatcher.set_post_handler(EM.UodInfoMsg, self.handle_UodInfoMsg)
        aggregator.dispatcher.set_post_handler(EM.TagsUpdatedMsg, self.handle_TagsUpdatedMsg)
        aggregator.dispatcher.set_post_handler(EM.RunLogMsg, self.handle_RunLogMsg)
        aggregator.dispatcher.set_post_handler(EM.ControlStateMsg, self.handle_ControlStateMsg)

    def get_registered_engine_data(self, engine_id: str):
        return self.aggregator.engine_data_map[engine_id] if engine_id in self.aggregator.engine_data_map.keys() else None

    async def handle_RegisterEngineMsg(self, register_engine_msg: EM.RegisterEngineMsg) -> M.SuccessMessage | M.ErrorMessage:
        """ Registers engine """
        engine_id = Aggregator.create_engine_id(register_engine_msg)
        if engine_id in self.aggregator.dispatcher.engine_id_channel_map.keys():
            logger.error(
                f"""Registration failed for engine_id {engine_id}. An engine with that engine_id already has a websocket connection. """
            )
            return AM.RegisterEngineReplyMsg(success=False)

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - engine_id reused with "same uod" should take over session, else fail as misconfigured client
        # - add machine name + uod secret

        # initialize client data
        if engine_id not in self.aggregator.engine_data_map.keys():
            self.aggregator.engine_data_map[engine_id] = EngineData(
                engine_id=engine_id,
                computer_name=register_engine_msg.computer_name,
                uod_name=register_engine_msg.uod_name
            )

        logger.debug(f"Registration successful of client {engine_id}")
        return AM.RegisterEngineReplyMsg(success=True, engine_id=engine_id)

    async def handle_UodInfoMsg(self, msg: EM.UodInfoMsg) -> M.SuccessMessage | M.ErrorMessage:
        engine_data = self.get_registered_engine_data(channel_id)
        if engine_data is None:
            return M.ErrorMessage()

        logger.debug(f"Got UodInfo from client: {str(msg)}")
        engine_data.readings = []
        for r in msg.readings:
            rd = ReadingDef(
                label=r.label,
                tag_name=r.tag_name,
                valid_value_units=r.valid_value_units,
                commands=[ReadingCommand(name=c.name, command=c.command) for c in r.commands]
            )
            engine_data.readings.append(rd)

        return M.SuccessMessage()

    async def handle_TagsUpdatedMsg(self, msg: EM.TagsUpdatedMsg) -> M.SuccessMessage | M.ErrorMessage:
        engine_data = self.get_registered_engine_data(msg.engine_id)
        if engine_data is None:
            return M.ErrorMessage()

        logger.debug(f"Got tags update from client: {str(msg)}")
        for ti in msg.tags:
            engine_data.tags_info.upsert(ti.name, ti.value, ti.value_unit)
        return M.SuccessMessage()

    async def handle_RunLogMsg(self, msg: EM.RunLogMsg) -> M.SuccessMessage | M.ErrorMessage:
        engine_data = self.get_registered_engine_data(msg.engine_id)
        if engine_data is None:
            return M.ErrorMessage()

        engine_data.runlog = msg
        return M.SuccessMessage()

    async def handle_ControlStateMsg(self, msg: EM.ControlStateMsg) -> M.SuccessMessage | M.ErrorMessage:
        engine_data = self.get_registered_engine_data(msg.engine_id)
        if engine_data is None:
            return M.ErrorMessage()

        engine_data.control_state = msg
        return M.SuccessMessage()
