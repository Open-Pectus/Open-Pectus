from fastapi_websocket_rpc.rpc_methods import RpcMethodsBase
from fastapi_websocket_rpc.websocket_rpc_endpoint import WebsocketRPCEndpoint

# Methods to expose to the clients
class ConcatServer(RpcMethodsBase):
    async def concat(self, a="", b=""):
        return a + b

# Create an endpoint and load it with the methods to expose
poc_endpoint = WebsocketRPCEndpoint(ConcatServer())
