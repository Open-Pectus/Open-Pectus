import logging

from openpectus.aggregator.models.models import EngineData
from openpectus.aggregator.aggregator import Aggregator
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
# from openpectus.protocol.messages import RegisterEngineMsg, UodInfoMsg, TagsUpdatedMsg, RunLogMsg, ControlStateMsg, SuccessMessage, ErrorMessage
import openpectus.protocol.messages as M

logger = logging.getLogger(__name__)


class MessageHandlers:
    def __init__(self, aggregator: Aggregator):
        self.aggregator = aggregator
        aggregator.dispatcher.set_post_handler(M.RegisterEngineMsg, self.handle_RegisterEngineMsg)
        aggregator.dispatcher.set_post_handler(M.UodInfoMsg, self.handle_UodInfoMsg)
        aggregator.dispatcher.set_post_handler(M.TagsUpdatedMsg, self.handle_TagsUpdatedMsg)
        aggregator.dispatcher.set_post_handler(M.RunLogMsg, self.handle_RunLogMsg)
        aggregator.dispatcher.set_post_handler(M.ControlStateMsg, self.handle_ControlStateMsg)

    async def handle_RegisterEngineMsg(self, register_engine_msg: M.RegisterEngineMsg) -> M.SuccessMessage | M.ErrorMessage:
        """ Registers engine """
        engine_id = Aggregator.create_engine_id(register_engine_msg)
        if engine_id in self.aggregator.dispatcher.engine_id_channel_map.keys():
            logger.error(
                f"""Registration failed for engine_id {engine_id}. An engine with that engine_id already has a websocket connection. """
            )
            return M.RegisterEngineReplyMsg(success=False)

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
        return M.RegisterEngineReplyMsg(success=True, engine_id=engine_id)

    async def handle_UodInfoMsg(self, channel_id: str, msg: M.UodInfoMsg) -> M.SuccessMessage | M.ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        logger.debug(f"Got UodInfo from client: {str(msg)}")
        client_data.readings = []
        for r in msg.readings:
            rd = ReadingDef(
                label=r.label,
                tag_name=r.tag_name,
                valid_value_units=r.valid_value_units,
                commands=[ReadingCommand(name=c.name, command=c.command) for c in r.commands]
            )
            client_data.readings.append(rd)

        return M.SuccessMessage()

    async def handle_TagsUpdatedMsg(self, channel_id: str, msg: M.TagsUpdatedMsg) -> M.SuccessMessage | M.ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        logger.debug(f"Got tags update from client: {str(msg)}")
        for ti in msg.tags:
            client_data.tags_info.upsert(ti.name, ti.value, ti.value_unit)
        return M.SuccessMessage()

    async def handle_RunLogMsg(self, channel_id: str, msg: M.RunLogMsg) -> M.SuccessMessage | M.ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        client_data.runlog = msg
        return M.SuccessMessage()

    async def handle_ControlStateMsg(self, channel_id: str, msg: M.ControlStateMsg) -> M.SuccessMessage | M.ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        client_data.control_state = msg
        return M.SuccessMessage()
