import asyncio
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_rpc import WebsocketRPCEndpoint
from fastapi_websocket_rpc.rpc_methods import RpcMethodsBase
from fastapi_websocket_rpc.logger import get_logger

from openpectus.protocol.dispatch import AE_EngineDispatcher_Impl
import openpectus.protocol.messages as M


logger = get_logger("Test")

# rpc_logger.logging_config.set_mode(rpc_logger.LoggingModes.UVICORN, rpc_logger.logging.DEBUG)

PORT = 7994
ws_url = f"ws://localhost:{PORT}/test-rpc"
trigger_url = f"http://localhost:{PORT}/trigger"
post_url = f"http://localhost:{PORT}/post"


class ServerProxyInterface(RpcMethodsBase):
    def __init__(self):
        """
        endpoint (WebsocketRPCEndpoint): the endpoint these methods are loaded into
        """
        super().__init__()

    async def upper(self, a: str) -> str:
        return a.upper()
  

def setup_server_rest_route(app):
    @app.post("/post")
    async def post(message: M.MessageBase):
        # -> MessageBase NOOOOOOO!! adding return type breaks the response, leaving it empty?!?
        # That is absolutely horrible. Hopefully it is fixed with the new pydantic version

        message_type = type(message)
        print(f"Post received message type: {message_type}")
        #retval = M.ErrorMessage(message="foo error", exception_message="no ex msg")
        retval = M.RegisterEngineReplyMsg(success=True, client_id="1234")
        message_json = M.serialize(retval)
        return message_json


def setup_server():
    app = FastAPI()
    server_proxy = ServerProxyInterface()
    endpoint = WebsocketRPCEndpoint(methods=server_proxy)
    endpoint.register_route(app, path="/test-rpc")
    setup_server_rest_route(app)
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
        disp = AE_EngineDispatcher_Impl(post_url, ws_url)
        msg = M.RegisterEngineMsg(uod_name="uod1", computer_name="pc1")
        result = disp.post(msg)
        assert isinstance(result, M.RegisterEngineReplyMsg), f"Got type {type(result)}"
        self.assertEqual(result.success, True)
        self.assertEqual(result.client_id, "1234")

    async def test_rpc_handler(self):

        finish = asyncio.Event()

        async def handler(message: M.MessageBase) -> M.MessageBase:
            finish.set()
            return M.MessageBase()

        disp = AE_EngineDispatcher_Impl(post_url, ws_url)
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
