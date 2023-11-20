import asyncio
import time
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase
import requests

import uvicorn
from fastapi import FastAPI, Request
from fastapi_websocket_rpc import WebsocketRPCEndpoint
from fastapi_websocket_rpc.logger import get_logger

from openpectus.protocol.dispatch import AE_AggregatorDispatcher_Impl, AE_EngineDispatcher_Impl
import openpectus.protocol.messages as M


logger = get_logger("Test")
# rpc_logger.logging_config.set_mode(rpc_logger.LoggingModes.UVICORN, rpc_logger.logging.DEBUG)


PORT = 7795
aggregator_host = f"localhost:{PORT}"
trigger_url = f"http://localhost:{PORT}/trigger"
health_url = f"http://{aggregator_host}/health"

# def setup_server_rest_route(app, endpoint: WebsocketRPCEndpoint):
#     @app.get("/trigger")
#     async def trigger_rpc_send():
#         logger.info("Triggered via HTTP route - publishing event")
#         # Publish an event named 'steel'
#         # Since we are calling back (RPC) to the client- this would deadlock if we wait on it
#         asyncio.create_task(endpoint.publish([EVENT_TOPIC_A], data=DATA))
#         return "triggered"


def setup_server_health(app):
    @app.get("/health")
    def health():
        logger.info("Health endpoint hit")
        return "OK"


def setup_server():
    app = FastAPI()

    setup_server_health(app)

    # dispatcher sets up websocket endpoint
    aggregator_disp = AE_AggregatorDispatcher_Impl(app)

    async def handle_register(msg: M.MessageBase) -> M.MessageBase:
        assert isinstance(msg, M.RegisterEngineMsg)
        return M.RegisterEngineReplyMsg(success=True, engine_id="1234")

    aggregator_disp.set_post_handler(M.RegisterEngineMsg, handle_register)

    # endpoint = WebsocketRPCEndpoint(methods=server_proxy)
    # endpoint.register_route(app, path="/test-rpc")
    print(f"*** Starting uvicorn on port {PORT}", flush=True)
    uvicorn.run(app, port=PORT)


def server():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


def wait_for_url_ok(url: str, timeout_seconds=5):
    start_time = time.time()
    while time.time() < start_time + timeout_seconds:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return
        except Exception:
            time.sleep(0.1)
    raise TimeoutError(f"Url {url} did respond in time")


class FastAPIAsyncTestCase(IsolatedAsyncioTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.DEBUG = True
        self.server_process: Process | None = None

    async def asyncSetUp(self):
        if self.DEBUG:
            print("** SetUp", flush=True)
        self.server_process = Process(target=setup_server, args=(), daemon=True)
        self.server_process.start()
        if self.DEBUG:
            print("*** Server process initiated", flush=True)

        wait_for_url_ok(health_url, 5)

        print("*** Server app started", flush=True)

    async def asyncTearDown(self):
        if self.DEBUG:
            print("** TearDown", flush=True)
        if self.server_process is not None:
            if self.server_process.is_alive():
                if self.DEBUG:
                    print("*** Killing process", flush=True)
                self.server_process.kill()


class TestAE_EngineDispatcher_Impl(FastAPIAsyncTestCase):

    def test_post(self):
        print("*** test_post: start", flush=True)
        disp = AE_EngineDispatcher_Impl(aggregator_host)
        msg = M.RegisterEngineMsg(uod_name="uod1", computer_name="pc1")
        print("*** test_post: post", flush=True)
        result = disp.post(msg)
        print("*** test_post: post successful", flush=True)
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
