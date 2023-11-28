import logging

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.aggregator.models as Mdl
from openpectus.aggregator.aggregator import Aggregator

logger = logging.getLogger(__name__)


class AggregatorMessageHandlers:
    def __init__(self, aggregator: Aggregator):
        self.aggregator = aggregator
        aggregator.dispatcher.set_post_handler(EM.RegisterEngineMsg, self.handle_RegisterEngineMsg)
        aggregator.dispatcher.set_post_handler(EM.UodInfoMsg, self.handle_UodInfoMsg)
        aggregator.dispatcher.set_post_handler(EM.TagsUpdatedMsg, self.handle_TagsUpdatedMsg)
        aggregator.dispatcher.set_post_handler(EM.RunLogMsg, self.handle_RunLogMsg)
        aggregator.dispatcher.set_post_handler(EM.ControlStateMsg, self.handle_ControlStateMsg)

    async def handle_RegisterEngineMsg(self, register_engine_msg: EM.RegisterEngineMsg) -> AM.RegisterEngineReplyMsg:
        """ Registers engine """
        engine_id = self.aggregator.create_engine_id(register_engine_msg)
        if self.aggregator.dispatcher.has_engine_id(engine_id):
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
        if not self.aggregator.has_registered_engine_id(engine_id):
            self.aggregator.register_engine_data(Mdl.EngineData(
                engine_id=engine_id,
                computer_name=register_engine_msg.computer_name,
                uod_name=register_engine_msg.uod_name
            ))

        logger.debug(f"Registration successful of client {engine_id}")
        return AM.RegisterEngineReplyMsg(success=True, engine_id=engine_id)

    # def check_engine_id(self, engine_id: str | None):
    #     if not isinstance(engine_id, str): return AM.ErrorMessage(message='engine_id on message was not a string.')
    #     assert isinstance(engine_id, str)
    #     if not self.aggregator.has_registered_engine_id(engine_id): return AM.ErrorMessage(message=f'No engine registered under id {engine_id}')
    #
    #     return None

    async def handle_UodInfoMsg(self, msg: EM.UodInfoMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        if not isinstance(msg.engine_id, str): return AM.ErrorMessage(message='engine_id on message was not a string.')
        if not self.aggregator.has_registered_engine_id(msg.engine_id): return AM.ErrorMessage(message=f'No engine registered under id {msg.engine_id}')

        logger.debug(f"Got UodInfo from client: {str(msg)}")
        self.aggregator.set_readings(msg.engine_id, msg.readings)
        return AM.SuccessMessage()

    async def handle_TagsUpdatedMsg(self, msg: EM.TagsUpdatedMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        if not isinstance(msg.engine_id, str): return AM.ErrorMessage(message='engine_id on message was not a string.')
        if not self.aggregator.has_registered_engine_id(msg.engine_id): return AM.ErrorMessage(message=f'No engine registered under id {msg.engine_id}')

        logger.debug(f"Got tags update from client: {str(msg)}")
        self.aggregator.upsert_tag_values(msg.engine_id, msg.tags)
        return AM.SuccessMessage()

    async def handle_RunLogMsg(self, msg: EM.RunLogMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        if not isinstance(msg.engine_id, str): return AM.ErrorMessage(message='engine_id on message was not a string.')
        if not self.aggregator.has_registered_engine_id(msg.engine_id): return AM.ErrorMessage(message=f'No engine registered under id {msg.engine_id}')

        logger.debug(f"Got run log from client: {str(msg)}")
        self.aggregator.set_runlog(msg.engine_id, msg.runlog)
        return AM.SuccessMessage()

    async def handle_ControlStateMsg(self, msg: EM.ControlStateMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        if not isinstance(msg.engine_id, str): return AM.ErrorMessage(message='engine_id on message was not a string.')
        if not self.aggregator.has_registered_engine_id(msg.engine_id): return AM.ErrorMessage(message=f'No engine registered under id {msg.engine_id}')

        logger.debug(f"Got control state from client: {str(msg)}")
        self.aggregator.set_control_state(msg.engine_id, msg.control_state)
        return AM.SuccessMessage()
