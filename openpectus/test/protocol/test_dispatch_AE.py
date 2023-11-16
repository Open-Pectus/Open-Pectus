import asyncio
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase

import uvicorn
from fastapi import FastAPI, Request
from fastapi_websocket_rpc import WebsocketRPCEndpoint
from fastapi_websocket_rpc.logger import get_logger

from openpectus.protocol.dispatch import AE_AggregatorDispatcher_Impl, AE_EngineDispatcher_Impl
import openpectus.protocol.messages as M


logger = get_logger("Test")

# rpc_logger.logging_config.set_mode(rpc_logger.LoggingModes.UVICORN, rpc_logger.logging.DEBUG)

PORT = 7994
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
    app = FastAPI()

    # dispatcher sets up websocket endpoint
    aggregator_disp = AE_AggregatorDispatcher_Impl(app)

    async def handle_register(msg: M.MessageBase) -> M.MessageBase:
        assert isinstance(msg, M.RegisterEngineMsg)
        return M.RegisterEngineReplyMsg(success=True, engine_id="1234")

    aggregator_disp.set_post_handler(M.RegisterEngineMsg, handle_register)

    # endpoint = WebsocketRPCEndpoint(methods=server_proxy)
    # endpoint.register_route(app, path="/test-rpc")
    uvicorn.run(app, port=PORT)


def server():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


class TestAE_EngineDispatcher_Impl(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        next(server())

    def test_post(self):
        disp = AE_EngineDispatcher_Impl(aggregator_host)
        msg = M.RegisterEngineMsg(uod_name="uod1", computer_name="pc1")
        result = disp.post(msg)
        assert isinstance(result, M.RegisterEngineReplyMsg), f"Got type {type(result)}"
        self.assertEqual(result.success, True)
        self.assertEqual(result.engine_id, "1234")

    async def test_rpc_handler(self):

        finish = asyncio.Event()

        async def handler(message: M.MessageBase) -> M.MessageBase:
            finish.set()
            return M.MessageBase()

        disp = AE_EngineDispatcher_Impl(aggregator_host)
        disp.set_rpc_handler(M.InvokeCommandMsg, handler)

        # dispatch unrelated message
        await disp._dispatch_message(M.MessageBase())

        await asyncio.sleep(2)
        self.assertTrue(not finish.is_set())

        # dispatch handled message
        await disp._dispatch_message(M.InvokeCommandMsg(name="foo"))

        await asyncio.wait_for(finish.wait(), 5)
        self.assertTrue(finish.is_set())


class TestAE_AggregatorDispatcher_Impl(IsolatedAsyncioTestCase):
    pass


if __name__ == "__main__":
    unittest.main()
