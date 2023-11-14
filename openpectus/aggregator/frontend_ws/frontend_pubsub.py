import asyncio
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi.routing import APIRouter


from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from fastapi_websocket_pubsub.event_notifier import TopicList

# set RPC to log like UVICORN
from fastapi_websocket_rpc.logger import logging_config, LoggingModes
logging_config.set_mode(LoggingModes.UVICORN)

router = APIRouter(tags=["frontend_pubsub"])


# class ConcatServer(RpcMethodsBase):
#     async def concat(self, a="", b=""):
#         return a + b

# async def on_rpc_connect(channel):
#     asyncio.create_task(callConcat(channel))

# async def callConcat(channel):
#     await asyncio.sleep(1)
#     result = await channel.other.concat(a='first', b='second')
#     print(result)

# rpc_endpoint = WebsocketRPCEndpoint(ConcatServer(), on_connect=[on_rpc_connect])
# rpc_endpoint.register_route(router)


class MethodsWithUnsubscribe(RpcEventServerMethods):
    """ We need to add our own unsubscribe method to support this for the frontend client """
    async def unsubscribe(self, topics: TopicList = []) -> bool:
        await self.event_notifier.unsubscribe(self.channel.id, topics)
        return True


pubsub_endpoint = PubSubEndpoint(methods_class=MethodsWithUnsubscribe)
pubsub_endpoint.register_route(router, path="/frontend-pubsub")

async def publishPubSub():
    topics_subscribed_to = list(pubsub_endpoint.notifier._topics.keys())
    msw_topics_subscribed_to = [topic for topic in topics_subscribed_to if topic.startswith('MSW_')]
    await pubsub_endpoint.publish(msw_topics_subscribed_to)

@router.get("/trigger-pubsub")
async def trigger_pubsub():
    asyncio.create_task(publishPubSub())

