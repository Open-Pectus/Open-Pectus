from fastapi_websocket_rpc.rpc_methods import RpcMethodsBase
from fastapi_websocket_rpc.websocket_rpc_endpoint import WebsocketRPCEndpoint
import asyncio

# Methods to expose to the clients
class ConcatServer(RpcMethodsBase):
    async def concat(self, a="", b=""):
        return a + b


async def on_connect(channel):
    asyncio.create_task(callConcat(channel))

async def callConcat(channel):
    await asyncio.sleep(1)
    result = await channel.other.concat(a='first', b='second')
    print(result)

# Create an endpoint and load it with the methods to expose
poc_endpoint = WebsocketRPCEndpoint(ConcatServer(), on_connect=[on_connect])
