import asyncio
from enum import StrEnum, auto

from fastapi.routing import APIRouter
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_pubsub.event_notifier import TopicList
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from fastapi_websocket_rpc.logger import logging_config, LoggingModes

logging_config.set_mode(LoggingModes.UVICORN)  # set RPC to log like UVICORN


class PubSubTopic(StrEnum):
    RUN_LOG = auto()
    METHOD = auto()
    CONTROL_STATE = auto()


class FrontendPublisher:
    class MethodsWithUnsubscribe(RpcEventServerMethods):
        """ We need to add our own unsubscribe method to support this for the frontend client.
            If/when I get this added to the library itself, we can remove this """

        async def unsubscribe(self, topics: TopicList = []) -> bool:
            await self.event_notifier.unsubscribe(self.channel.id, topics)
            return True

    def __init__(self):
        self.router = APIRouter(tags=["frontend_pubsub"], prefix='/api')
        self.router.add_api_route('/expose-pubsub-topics', endpoint=self.expose_pubsub_topics, methods=['POST'])
        self.router.add_api_route('/trigger-publish-msw', endpoint=self.trigger_publish_msw, methods=['POST'])
        self.pubsub_endpoint = PubSubEndpoint(methods_class=FrontendPublisher.MethodsWithUnsubscribe)
        self.pubsub_endpoint.register_route(self.router, path="/frontend-pubsub")

    async def publish_run_log_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.RUN_LOG}')

    async def publish_method_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.METHOD}')

    async def publish_control_state_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.CONTROL_STATE}')

    def expose_pubsub_topics(self, topic: PubSubTopic):
        """ This endpoint is just for exposing the topic enum to frontend via autogeneration """
        pass

    def trigger_publish_msw(self):
        """ Publish to all topics that start with 'MSW_' """
        topics_subscribed_to = list(self.pubsub_endpoint.notifier._topics.keys())
        msw_topics_subscribed_to = [topic for topic in topics_subscribed_to if topic.startswith('MSW_')]
        asyncio.create_task(self.pubsub_endpoint.publish(msw_topics_subscribed_to))
