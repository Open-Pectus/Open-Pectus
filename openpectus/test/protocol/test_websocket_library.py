import asyncio
import time
import unittest
from multiprocessing import Process
from typing import List, Coroutine
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods, RpcEventClientMethods
from fastapi_websocket_rpc import RpcChannel, WebsocketRPCEndpoint, RpcMethodsBase, WebSocketRpcClient
from fastapi_websocket_rpc.logger import get_logger
from openpectus.protocol.dispatch_interface import AGGREGATOR_RPC_WS_PATH

logger = get_logger("Test")

PORT = 7990
ws_url = f"ws://localhost:{PORT}/{AGGREGATOR_RPC_WS_PATH}"
trigger_url = f"http://localhost:{PORT}/trigger"

DATA = "MAGIC"
EVENT_TOPIC = "event/has-happened"


def setup_server_rest_route(app, endpoint: WebsocketRPCEndpoint):
    @app.get("/get_engine_id")
    async def get_engine_id():
        asyncio.create_task(endpoint.other.get_engine_id())


class TestServerRpcMethods(RpcEventServerMethods):
    async def to_upper(self, x: str) -> str:
        await asyncio.sleep(0.1)
        return x.upper()


class TestClientRpcMethods(RpcEventClientMethods):
    async def to_upper(self, x: str) -> str:
        await asyncio.sleep(0.1)
        return x.upper()



def setup_server():
    app = FastAPI()
    mock = Mock()
    endpoint = WebsocketRPCEndpoint()
    endpoint.register_route(app, path=AGGREGATOR_RPC_WS_PATH)
    setup_server_rest_route(app, endpoint)
    uvicorn.run(app, port=PORT)


def server():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test





mock_engine_id = 'fdsa'

async def on_delayed_client_connect(channel: RpcChannel):
    engine_id = await channel.other.get_engine_id()
    # self.assertEqual(engine_id, mock_engine_id)
    logger.info(engine_id)
    print(engine_id, flush=True)

async def on_client_connect(channel: RpcChannel):
    asyncio.create_task(on_delayed_client_connect(channel))


class RpcMethods(RpcMethodsBase):
    async def get_engine_id(self):
        return mock_engine_id


def setup_server_endpoint():
    server = FastAPI()
    server_endpoint = WebsocketRPCEndpoint(on_connect=[on_client_connect])
    server_endpoint.register_route(server, path=AGGREGATOR_RPC_WS_PATH)
    uvicorn.run(server, port=PORT)


class TestRpc(IsolatedAsyncioTestCase):
    async def test_get_engine_id(self):
        proc = Process(target=setup_server_endpoint, daemon=True)
        proc.start()
        logger.info('fdsafdsa')
        rpc_url = f"ws://127.0.0.1:{PORT}{AGGREGATOR_RPC_WS_PATH}"
        rpc_methods = RpcMethods()
        rpc_client = WebSocketRpcClient(uri=rpc_url, methods=rpc_methods)
        await rpc_client.__connect__()
        proc.terminate()

if __name__ == "__main__":
    unittest.main()
