import logging
from typing import Protocol

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.messages as M
from openpectus.engine.engine import Engine
from openpectus.protocol.engine_dispatcher import EngineMessageHandler


logger = logging.getLogger(__name__)


class EngineDispatcherRpcHandler(Protocol):
    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        ...


class EngineMessageHandlers():
    def __init__(self, engine: Engine, dispatcher: EngineDispatcherRpcHandler) -> None:
        self.engine = engine
        dispatcher.set_rpc_handler(AM.InvokeCommandMsg, self.handle_invokeCommandMsg)
        dispatcher.set_rpc_handler(AM.InjectCodeMsg, self.handle_injectCodeMsg)
        dispatcher.set_rpc_handler(AM.MethodMsg, self.handle_methodMsg)

    async def handle_methodMsg(self, msg: AM.AggregatorMessage):
        assert isinstance(msg, AM.MethodMsg)
        logger.info("Incomming set_method command from aggregator")
        try:
            self.engine.set_method(msg.method)
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
