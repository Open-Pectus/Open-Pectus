import asyncio
from enum import StrEnum, auto
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi.routing import APIRouter
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from fastapi_websocket_pubsub.event_notifier import TopicList

# set RPC to log like UVICORN
from fastapi_websocket_rpc.logger import logging_config, LoggingModes
logging_config.set_mode(LoggingModes.UVICORN)

router = APIRouter(tags=["frontend_pubsub"])

class MethodsWithUnsubscribe(RpcEventServerMethods):
    """ We need to add our own unsubscribe method to support this for the frontend client """
    async def unsubscribe(self, topics: TopicList = []) -> bool:
        await self.event_notifier.unsubscribe(self.channel.id, topics)
        return True

pubsub_endpoint = PubSubEndpoint(methods_class=MethodsWithUnsubscribe)
pubsub_endpoint.register_route(router, path="/frontend-pubsub")


class PubSubTopic(StrEnum):
    RUN_LOG = auto()
    METHOD = auto()
    CONTROL_STATE = auto()


def publish_run_log_changed(unitId: str):
    return pubsub_endpoint.publish(f'${unitId}/${PubSubTopic.RUN_LOG}')

def publish_method_changed(unitId: str):
    return pubsub_endpoint.publish(f'${unitId}/${PubSubTopic.METHOD}')

def publish_control_state_changed(unitId: str):
    return pubsub_endpoint.publish(f'${unitId}/${PubSubTopic.CONTROL_STATE}')



@router.post('/expose-pusub-topics')
def expose_pubsub_topics(topic: PubSubTopic):
    """ This endpoint is just for exposing the topic enum to frontend via autogeneration """
    pass


async def triggerPublishMsw():
    topics_subscribed_to = list(pubsub_endpoint.notifier._topics.keys())
    msw_topics_subscribed_to = [topic for topic in topics_subscribed_to if topic.startswith('MSW_')]
    await pubsub_endpoint.publish(msw_topics_subscribed_to)

@router.get("/trigger-publish-msw")
async def trigger_publish_msw():
    """ Publish to all topics that start with 'MSW_' """
    asyncio.create_task(triggerPublishMsw())

