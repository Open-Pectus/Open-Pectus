import asyncio
import logging

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.aggregator.models as Mdl
from openpectus.aggregator.aggregator import Aggregator
from openpectus.lsp.lsp_analysis import create_analysis_input

logger = logging.getLogger(__name__)


class AggregatorMessageHandlers:
    def __init__(self, aggregator: Aggregator):
        self.aggregator = aggregator
        aggregator.dispatcher.set_register_handler(self.handle_RegisterEngineMsg)
        aggregator.dispatcher.set_disconnect_handler(self.handle_EngineDisconnected)
        aggregator.dispatcher.set_connect_handler(self.handle_EngineConnected)
        aggregator.dispatcher.set_message_handler(EM.UodInfoMsg, self.handle_UodInfoMsg)
        aggregator.dispatcher.set_message_handler(EM.TagsUpdatedMsg, self.handle_TagsUpdatedMsg)
        aggregator.dispatcher.set_message_handler(EM.RunLogMsg, self.handle_RunLogMsg)
        aggregator.dispatcher.set_message_handler(EM.ControlStateMsg, self.handle_ControlStateMsg)
        aggregator.dispatcher.set_message_handler(EM.MethodStateMsg, self.handle_MethodStateMsg)
        aggregator.dispatcher.set_message_handler(EM.ErrorLogMsg, self.handle_ErrorLogMsg)
        aggregator.dispatcher.set_message_handler(EM.RunStartedMsg, self.handle_RunStartedMsg)
        aggregator.dispatcher.set_message_handler(EM.RunStoppedMsg, self.handle_RunStoppedMsg)
        aggregator.dispatcher.set_message_handler(EM.MethodMsg, self.handle_MethodMsg)
        aggregator.dispatcher.set_message_handler(EM.WebPushNotificationMsg, self.handle_WebPushNotificationMsg)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(aggregator={self.aggregator})'

    async def handle_RegisterEngineMsg(self, register_engine_msg: EM.RegisterEngineMsg) -> AM.RegisterEngineReplyMsg:
        """ Registers engine """
        if register_engine_msg.secret != self.aggregator.secret:
            logger.info(
                f'Engine registration message {register_engine_msg} received ' +
                "but secret does not match aggregator secret"
            )
            return AM.RegisterEngineReplyMsg(success=False, secret_match=False)
        engine_id = self.aggregator.create_engine_id(register_engine_msg)
        if self.aggregator.dispatcher.has_connected_engine_id(engine_id):
            logger.error(
                f"""Registration failed for engine_id {engine_id}. An engine with that engine_id already
                has a websocket connection. """
            )
            return AM.RegisterEngineReplyMsg(success=False, engine_id=engine_id, secret_match=True)

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - engine_id reused with "same uod" should take over session, else fail as misconfigured client
        # - add machine name + uod secret

        # initialize client data
        if not self.aggregator.has_registered_engine_id(engine_id):
            self.aggregator.from_engine.register_engine_data(
                Mdl.EngineData(
                    engine_id=engine_id,
                    computer_name=register_engine_msg.computer_name,
                    uod_name=register_engine_msg.uod_name,
                    uod_author_name=register_engine_msg.uod_author_name,
                    uod_author_email=register_engine_msg.uod_author_email,
                    uod_filename=register_engine_msg.uod_filename,
                    location=register_engine_msg.location,
                    engine_version=register_engine_msg.engine_version,
                )
            )

        logger.info(f"Registration of engine {engine_id} successful")
        # Clear LSP analysis cache to ensure that any UOD changes will be applied
        # This fits better in aggregator, but it cannot be there because it would incur
        # a circular import.
        create_analysis_input.cache_clear()
        return AM.RegisterEngineReplyMsg(success=True, engine_id=engine_id, secret_match=True)

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
        self.aggregator.from_engine.uod_info_changed(
            msg.engine_id, msg.readings,
            msg.commands, msg.uod_definition,
            msg.plot_configuration,
            msg.hardware_str, msg.required_roles,
            msg.data_log_interval_seconds)
        return AM.SuccessMessage()

    async def handle_EngineConnected(self, engine_id: str):
        self.aggregator.from_engine.engine_connected(engine_id)

    async def handle_EngineDisconnected(self, engine_id: str):
        self.aggregator.from_engine.engine_disconnected(engine_id)

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
        self.aggregator.from_engine.runlog_changed(msg.engine_id, msg.run_id, msg.runlog)
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

    async def handle_ErrorLogMsg(self, msg: EM.ErrorLogMsg):
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        logger.debug(f'error log message from engine: {msg.log}')
        self.aggregator.from_engine.error_log_changed(msg.engine_id, msg.log)
        return AM.SuccessMessage()

    async def handle_RunStartedMsg(self, msg: EM.RunStartedMsg):
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        self.aggregator.from_engine.run_started(msg)
        return AM.SuccessMessage()

    async def handle_RunStoppedMsg(self, msg: EM.RunStoppedMsg):
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors

        self.aggregator.from_engine.run_stopped(msg)
        return AM.SuccessMessage()

    async def handle_MethodMsg(self, msg: EM.MethodMsg):
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors
        
        if msg.method.lines is None or len(msg.method.lines) == 0:
            return AM.ErrorMessage(message="Invalid method. Method was empty but should always contain at least one line")
        if msg.method.lines[-1].content != "":
            return AM.ErrorMessage(message="Invalid method. Method should always end in a blank line")
        
        self.aggregator._engine_data_map[msg.engine_id].method.lines = msg.method.lines
        asyncio.create_task(self.aggregator.from_engine.publisher.publish_method_changed(msg.engine_id))
        return AM.SuccessMessage()

    async def handle_WebPushNotificationMsg(self, msg: EM.WebPushNotificationMsg):
        validation_errors = self.validate_msg(msg)
        if validation_errors is not None:
            return validation_errors
        
        if msg.notification.data is None:
            msg.notification.data = Mdl.WebPushData(
                process_unit_id=msg.engine_id
            )
            msg.notification.actions = [
                Mdl.WebPushAction(
                    action="navigate",
                    title="Go to process unit"
                )
            ]
        asyncio.create_task(self.aggregator.webpush_publisher.publish_message(
            notification=msg.notification,
            topic=msg.topic,
            process_unit=self.aggregator._engine_data_map[msg.engine_id],
        ))
        return AM.SuccessMessage()