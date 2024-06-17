import logging

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.messages as M
from openpectus.engine.engine import Engine
from openpectus.protocol.engine_dispatcher import EngineDispatcher


logger = logging.getLogger(__name__)


class EngineMessageHandlers():
    def __init__(self, engine: Engine, dispatcher: EngineDispatcher) -> None:
        self.engine = engine
        dispatcher.set_rpc_handler(AM.InvokeCommandMsg, self.handle_invokeCommandMsg)
        dispatcher.set_rpc_handler(AM.InjectCodeMsg, self.handle_injectCodeMsg)
        dispatcher.set_rpc_handler(AM.MethodMsg, self.handle_methodMsg)

    async def handle_methodMsg(self, msg: AM.AggregatorMessage):
        assert isinstance(msg, AM.MethodMsg)

        try:
            self.engine.set_method(msg.method)
            return AM.SuccessMessage()
        except Exception as ex:
            logger.error("Failed to set method", exc_info=True)
            return AM.ErrorMessage(message="Failed to set method", exception_message=str(ex))

    async def handle_invokeCommandMsg(self, msg: AM.AggregatorMessage) -> M.MessageBase:
        assert isinstance(msg, AM.InvokeCommandMsg)

        # as side effect, start engine on first Start command
        # TODO verify this is intended behavior
        # TODO - move this into ExecutionEngine
        # TODO this is now handled elsewhere. Verify this and remove
        if not self.engine.is_running() and msg.name.upper() == "START":
            logger.error("This should no longer be necessary - Starting engine on first start command")
            self.engine.run()

        self.engine.schedule_execution_user(name=msg.name, args=msg.arguments)
        return AM.SuccessMessage()

    async def handle_injectCodeMsg(self, msg: AM.AggregatorMessage) -> M.MessageBase:
        assert isinstance(msg, AM.InjectCodeMsg)
        self.engine.inject_code(msg.pcode)
        return AM.SuccessMessage()
