import logging
from typing import Protocol
from uuid import UUID

import openpectus.sentry as sentry
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.messages as M
from openpectus.engine.engine import Engine
from openpectus.protocol.engine_dispatcher import EngineMessageHandler


logger = logging.getLogger(__name__)


class EngineDispatcherRpcHandler(Protocol):
    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        raise NotImplementedError


class EngineMessageHandlers():
    def __init__(self, engine: Engine, dispatcher: EngineDispatcherRpcHandler) -> None:
        self.engine = engine
        dispatcher.set_rpc_handler(AM.InvokeCommandMsg, self.handle_invokeCommandMsg)
        dispatcher.set_rpc_handler(AM.InjectCodeMsg, self.handle_injectCodeMsg)
        dispatcher.set_rpc_handler(AM.MethodMsg, self.handle_methodMsg)
        dispatcher.set_rpc_handler(AM.CancelMsg, self.handle_cancelMsg)
        dispatcher.set_rpc_handler(AM.ForceMsg, self.handle_forceMsg)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine={self.engine})'

    async def handle_methodMsg(self, msg: AM.AggregatorMessage):
        assert isinstance(msg, AM.MethodMsg)
        logger.info("Incomming set_method command from aggregator")
        try:
            self.engine.set_method(msg.method)
            sentry.engine_method_set(msg.method.as_pcode())
            return AM.SuccessMessage()
        except Exception as ex:
            logger.error("Failed to set method")
            return AM.ErrorMessage(message="Failed to set method", exception_message=str(ex))

    async def handle_invokeCommandMsg(self, msg: AM.AggregatorMessage) -> M.MessageBase:
        assert isinstance(msg, AM.InvokeCommandMsg)
        logger.info(f"Incomming command from aggregator: {msg.name}")
        try:
            self.engine.schedule_execution_user(name=msg.name, args=msg.arguments)
            return AM.SuccessMessage()
        except Exception:
            logger.error(f"The command '{msg.name}' could not be scheduled")
            return AM.ErrorMessage(message=f"The command '{msg.name}' could not be scheduled")

    async def handle_injectCodeMsg(self, msg: AM.AggregatorMessage) -> M.MessageBase:
        assert isinstance(msg, AM.InjectCodeMsg)
        logger.info(f"Incomming inject code command from aggregator: '{msg.pcode}'")
        try:
            self.engine.inject_code(msg.pcode)
            return AM.SuccessMessage()
        except Exception:
            logger.error("Code injection failed")
            return AM.ErrorMessage(message="The code could not be injected")

    async def handle_cancelMsg(self, msg: AM.AggregatorMessage) -> M.MessageBase:
        assert isinstance(msg, AM.CancelMsg)
        logger.info(f"Incomming cancel request {msg.exec_id}")
        try:
            exec_id = UUID(msg.exec_id)
            self.engine.cancel_instruction(exec_id)
            return AM.SuccessMessage()
        except Exception:
            logger.error("Cancel failed", exc_info=True)
            return AM.ErrorMessage(message="The engine failed to cancel the instruction")

    async def handle_forceMsg(self, msg: AM.AggregatorMessage) -> M.MessageBase:
        assert isinstance(msg, AM.ForceMsg)
        logger.info(f"Incomming force request {msg.exec_id}")
        try:
            exec_id = UUID(msg.exec_id)
            self.engine.force_instruction(exec_id)
            return AM.SuccessMessage()
        except Exception:
            logger.error("Force failed", exc_info=True)
            return AM.ErrorMessage(message="The engine failed to force the instruction")
