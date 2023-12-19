import asyncio
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
import uvicorn
from fastapi import FastAPI
from fastapi_websocket_rpc.logger import get_logger
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from openpectus.protocol.engine_dispatcher import EngineDispatcher

logger = get_logger("Test")

# rpc_logger.logging_config.set_mode(rpc_logger.LoggingModes.UVICORN, rpc_logger.logging.DEBUG)


# PORT = random.randint(7000, 10000)
PORT = 7795
aggregator_host = f"localhost:{PORT}"
trigger_url = f"http://localhost:{PORT}/trigger"


# def setup_server_rest_route(app, endpoint: WebsocketRPCEndpoint):
#     @app.get("/trigger")
#     async def trigger_rpc_send():
#         logger.info("Triggered via HTTP route - publishing event")
#         # Publish an event named 'steel'
#         # Since we are calling back (RPC) to the client- this would deadlock if we wait on it
#         asyncio.create_task(endpoint.publish([EVENT_TOPIC_A], data=DATA))
#         return "triggered"


def setup_server():
    # dispatcher sets up websocket endpoint
    aggregator_disp = AggregatorDispatcher()

    async def handle_register(msg: EM.RegisterEngineMsg) -> AM.RegisterEngineReplyMsg:
        assert isinstance(msg, EM.RegisterEngineMsg)
        return AM.RegisterEngineReplyMsg(success=True, engine_id="1234")

    aggregator_disp.set_register_handler(handle_register)

    # endpoint = WebsocketRPCEndpoint(methods=server_proxy)
    # endpoint.register_route(app, path="/test-rpc")
    app = FastAPI()
    app.include_router(aggregator_disp.router)
    uvicorn.run(app, port=PORT)


def server():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


@unittest.skip("TODO Fix on CI server")
class TestAE_EngineDispatcher_Impl(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        next(server())

    def test_post(self):
        disp = EngineDispatcher(aggregator_host, "uod1")
        # msg = M.RegisterEngineMsg(uod_name="uod1", computer_name="pc1")
        # result = disp.post(msg)
        # assert isinstance(result, M.RegisterEngineReplyMsg), f"Got type {type(result)}"
        # self.assertEqual(result.success, True)
        # self.assertEqual(result.engine_id, "1234")

    async def test_rpc_handler(self):
        finish = asyncio.Event()

        async def handler(message: M.MessageBase) -> M.MessageBase:
            finish.set()
            return M.MessageBase()

        disp = EngineDispatcher(aggregator_host, "uod1")
        disp.set_rpc_handler(AM.InvokeCommandMsg, handler)

        # dispatch unrelated message
        await disp._dispatch_message_async(M.MessageBase())

        await asyncio.sleep(2)
        self.assertTrue(not finish.is_set())

        # dispatch handled message
        await disp._dispatch_message_async(AM.InvokeCommandMsg(name="foo"))

        await asyncio.wait_for(finish.wait(), 5)
        self.assertTrue(finish.is_set())


class TestAE_AggregatorDispatcher_Impl(IsolatedAsyncioTestCase):
    pass


if __name__ == "__main__":
    unittest.main()
