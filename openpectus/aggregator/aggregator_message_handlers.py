import logging

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.aggregator.models as Mdl
from openpectus.aggregator.aggregator import Aggregator

logger = logging.getLogger(__name__)


class AggregatorMessageHandlers:
    def __init__(self, aggregator: Aggregator):
        self.aggregator = aggregator
        aggregator.dispatcher.set_register_handler(self.handle_RegisterEngineMsg)
        aggregator.dispatcher.set_post_handler(EM.UodInfoMsg, self.handle_UodInfoMsg)
        aggregator.dispatcher.set_post_handler(EM.TagsUpdatedMsg, self.handle_TagsUpdatedMsg)
        aggregator.dispatcher.set_post_handler(EM.RunLogMsg, self.handle_RunLogMsg)
        aggregator.dispatcher.set_post_handler(EM.ControlStateMsg, self.handle_ControlStateMsg)
        aggregator.dispatcher.set_post_handler(EM.MethodStateMsg, self.handle_MethodStateMsg)

    async def handle_RegisterEngineMsg(self, register_engine_msg: EM.RegisterEngineMsg) -> AM.RegisterEngineReplyMsg:
        """ Registers engine """
        engine_id = self.aggregator.create_engine_id(register_engine_msg)
        if self.aggregator.dispatcher.has_engine_id(engine_id):
            logger.error(
                f"""Registration failed for engine_id {engine_id}. An engine with that engine_id already
                has a websocket connection. """
            )
            return AM.RegisterEngineReplyMsg(success=False)

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - engine_id reused with "same uod" should take over session, else fail as misconfigured client
        # - add machine name + uod secret

        # initialize client data
        if not self.aggregator.has_registered_engine_id(engine_id):
            self.aggregator.from_engine.register_engine_data(Mdl.EngineData(
                engine_id=engine_id,
                computer_name=register_engine_msg.computer_name,
                uod_name=register_engine_msg.uod_name,
                location=register_engine_msg.location
            ))

        logger.debug(f"Registration successful of client {engine_id}")
        return AM.RegisterEngineReplyMsg(success=True, engine_id=engine_id)

    def validate_msg(self, msg: EM.EngineMessage):
        if not self.aggregator.has_registered_engine_id(msg.engine_id):
            return AM.ErrorMessage(message=f'No engine registered under id {msg.engine_id}')
        # possibly more validations...
        return None

    async def handle_UodInfoMsg(self, msg: EM.UodInfoMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        logger.debug(f"Got UodInfo from client: {str(msg)}")
        self.aggregator.from_engine.readings_changed(msg.engine_id, msg.readings)
        self.aggregator.from_engine.plot_configuration_changed(msg.engine_id, msg.plot_configuration)
        return AM.SuccessMessage()

    async def handle_TagsUpdatedMsg(self, msg: EM.TagsUpdatedMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        logger.debug(f"Got tags update from client: {str(msg)}")
        self.aggregator.from_engine.tag_values_changed(msg.engine_id, msg.tags)
        return AM.SuccessMessage()

    async def handle_RunLogMsg(self, msg: EM.RunLogMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        logger.debug(f"Got run log from client: {str(msg)}")
        self.aggregator.from_engine.runlog_changed(msg.engine_id, msg.runlog)
        return AM.SuccessMessage()

    async def handle_ControlStateMsg(self, msg: EM.ControlStateMsg) -> AM.SuccessMessage | AM.ErrorMessage:
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        logger.debug(f"Got control state from client: {str(msg)}")
        self.aggregator.from_engine.control_state_changed(msg.engine_id, msg.control_state)
        return AM.SuccessMessage()

    async def handle_MethodStateMsg(self, msg: EM.MethodStateMsg):
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        logger.debug(f"Got method state from client: {str(msg)}")
        self.aggregator.from_engine.method_state_changed(msg.engine_id, msg.method_state)
        return AM.SuccessMessage()
