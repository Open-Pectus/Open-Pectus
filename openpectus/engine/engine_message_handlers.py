from openpectus.engine.engine import Engine
from openpectus.protocol.engine_dispatcher import EngineDispatcher
import openpectus.protocol.messages as M
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM


class EngineMessageHandlers():
    def __init__(self, engine: Engine, dispatcher: EngineDispatcher) -> None:
        self.engine = engine
        dispatcher.set_rpc_handler(AM.InvokeCommandMsg, self.handle_invokeCommandMsg)
        dispatcher.set_rpc_handler(AM.InjectCodeMsg, self.handle_injectCodeMsg)
        dispatcher.set_rpc_handler(AM.MethodMsg, self.handle_methodMsg)

    async def handle_methodMsg(self, method_msg: AM.MethodMsg) -> M.RpcStatusMessage:
        pcode = '\n'.join(line.content for line in method_msg.lines)
        try:
            self.engine.set_program(pcode)
            proxy_logger.info("New method set")
            return M.SuccessMessage()
        except Exception as ex:
            proxy_logger.error("Failed to set method")
            return M.ErrorMessage(message="Failed to set method", exception_message=str(ex))

    async def handle_invokeCommandMsg(self, msg: AM.InvokeCommandMsg) -> M.MessageBase:
        assert isinstance(msg, AM.InvokeCommandMsg)

        # as side effect, start engine on first START command
        # TODO verify this is intended behavior
        # TODO - move this into ExecutionEngine
        if not self.engine.is_running() and msg.name.upper() == "START":
            logger.info("Starting engine on first start command")
            self.engine.run()

        self.engine.schedule_execution(name=msg.name, args=msg.arguments)
        return M.SuccessMessage()

    async def handle_injectCodeMsg(self, msg: AM.InjectCodeMsg) -> M.MessageBase:
        assert isinstance(msg, AM.InjectCodeMsg)
        self.engine.inject_code(msg.pcode)
        return M.SuccessMessage()
