import asyncio
from fastapi_websocket_rpc.rpc_methods import RpcMethodsBase
from fastapi_websocket_rpc.websocket_rpc_endpoint import WebsocketRPCEndpoint
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi.routing import APIRouter

# set RPC to log like UVICORN
from fastapi_websocket_rpc.logger import logging_config, LoggingModes
logging_config.set_mode(LoggingModes.UVICORN)

router = APIRouter()


class ConcatServer(RpcMethodsBase):
    async def concat(self, a="", b=""):
        return a + b

async def on_rpc_connect(channel):
    asyncio.create_task(callConcat(channel))

async def callConcat(channel):
    await asyncio.sleep(1)
    result = await channel.other.concat(a='first', b='second')
    print(result)

rpc_endpoint = WebsocketRPCEndpoint(ConcatServer(), on_connect=[on_rpc_connect])
pubsub_endpoint = PubSubEndpoint()



async def publishPubSub():
    await asyncio.sleep(1)
    # Publish multiple topics (without data)
    await pubsub_endpoint.publish(["guns", "germs"])
    await asyncio.sleep(1)
    # Publish single topic (without data)
    await pubsub_endpoint.publish(["germs"])
    await asyncio.sleep(1)
    # Publish single topic (with data)
    await pubsub_endpoint.publish(["steel"], data={"author": "Jared Diamond"})


rpc_endpoint.register_route(router)
pubsub_endpoint.register_route(router, path="/frontend-pubsub")


@router.get("/trigger-pubsub")
async def trigger_pubsub():
    asyncio.create_task(publishPubSub())

