import asyncio
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_rpc import RpcChannel, WebsocketRPCEndpoint, RpcMethodsBase, WebSocketRpcClient
from fastapi_websocket_rpc.logger import get_logger
from openpectus.protocol.dispatch_interface import AGGREGATOR_RPC_WS_PATH

logger = get_logger("Test")

PORT = 7990
ws_url = f"ws://localhost:{PORT}/{AGGREGATOR_RPC_WS_PATH}"
trigger_url = f"http://localhost:{PORT}/trigger"

mock_engine_id = 'mock engine id'


async def on_delayed_client_connect(channel: RpcChannel):
    engine_id = await channel.other.get_engine_id_async()
    # self.assertEqual(engine_id, mock_engine_id)
    logger.info(engine_id)


async def on_client_connect(channel: RpcChannel):
    asyncio.create_task(on_delayed_client_connect(channel))


class RpcMethods(RpcMethodsBase):
    async def get_engine_id_async(self):
        return mock_engine_id


def setup_server_endpoint():
    server = FastAPI()
    # WebsockeRPCEndpoint has wrong types for its on_connect and on_disconnect.
    # It should be List[Callable[[RpcChannel], Awaitable[Any]]] instead of List[Coroutine]
    server_endpoint = WebsocketRPCEndpoint(on_connect=[on_client_connect])  # type: ignore
    server_endpoint.register_route(server, path=AGGREGATOR_RPC_WS_PATH)
    uvicorn.run(server, port=PORT)


class TestRpc(IsolatedAsyncioTestCase):
    async def test_get_engine_id(self):
        proc = Process(target=setup_server_endpoint, daemon=True)
        proc.start()
        rpc_url = f"ws://127.0.0.1:{PORT}{AGGREGATOR_RPC_WS_PATH}"
        rpc_methods = RpcMethods()
        rpc_client = WebSocketRpcClient(uri=rpc_url, methods=rpc_methods)
        await rpc_client.__aenter__()
        proc.terminate()


if __name__ == "__main__":
    unittest.main()
