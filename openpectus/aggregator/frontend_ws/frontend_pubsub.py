import asyncio
from fastapi_websocket_rpc.rpc_methods import RpcMethodsBase
from fastapi_websocket_rpc.websocket_rpc_endpoint import WebsocketRPCEndpoint
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi.routing import APIRouter


from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from fastapi_websocket_pubsub.websocket_rpc_event_notifier import WebSocketRpcEventNotifier
from fastapi_websocket_pubsub.event_notifier import TopicList

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


class MethodsWithUnsubscribe(RpcEventServerMethods):
    """ We need to add our own unsubscribe method to support this for the frontend client """
    async def unsubscribe(self, topics: TopicList = []) -> bool:
        await self.event_notifier.unsubscribe(self.channel.id, topics)
        return True


pubsub_endpoint = PubSubEndpoint(methods_class=MethodsWithUnsubscribe)



async def publishPubSub():
    await asyncio.sleep(1)
    await pubsub_endpoint.publish(["guns", "germs"])
    await asyncio.sleep(1)
    await pubsub_endpoint.publish(["germs"])
    await asyncio.sleep(1)
    await pubsub_endpoint.publish(["steel"], data={"author": "Jared Diamond"})
    await asyncio.sleep(1)
    await pubsub_endpoint.publish(["germs"])


rpc_endpoint.register_route(router)
pubsub_endpoint.register_route(router, path="/frontend-pubsub")


@router.get("/trigger-pubsub")
async def trigger_pubsub():
    asyncio.create_task(publishPubSub())

