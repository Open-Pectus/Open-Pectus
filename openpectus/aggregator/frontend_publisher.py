import asyncio
from enum import StrEnum, auto
from typing import Awaitable, Callable, Coroutine

from fastapi.routing import APIRouter
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_pubsub.event_notifier import TopicList
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from fastapi_websocket_rpc.rpc_channel import OnDisconnectCallback, RpcChannel


class PubSubTopic(StrEnum):
    RUN_LOG = auto()
    METHOD = auto()
    METHOD_STATE = auto()
    CONTROL_STATE = auto()
    ERROR_LOG = auto()
    PROCESS_UNITS = auto()
    ACTIVE_USERS = auto()
    DEAD_MAN_SWITCH = auto()


class FrontendPublisher:
    class MethodsWithUnsubscribe(RpcEventServerMethods):
        """ We need to add our own unsubscribe method to support this for the frontend client.
            If/when I get this added to the library itself, we can remove this """

        async def unsubscribe(self, topics: TopicList = []) -> bool:
            channel_id = await self._get_channel_id_()
            await self.event_notifier.unsubscribe(channel_id, topics)
            return True

    def __init__(self):
        self.router = APIRouter(tags=["frontend_pubsub"], prefix='/api')
        self.router.add_api_route('/expose-pubsub-topics', endpoint=self.expose_pubsub_topics, methods=['POST'])
        self.router.add_api_route('/trigger-publish-msw', endpoint=self.trigger_publish_msw, methods=['POST'])
        self.on_disconnect_callbacks: list[Callable[[str], Awaitable[None]]] = []
        self.pubsub_endpoint = PubSubEndpoint(methods_class=FrontendPublisher.MethodsWithUnsubscribe, on_disconnect=[self.on_disconnect]) # type: ignore
        self.pubsub_endpoint.register_route(self.router, path="/frontend-pubsub")

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    async def publish_process_units_changed(self):
        await self.pubsub_endpoint.publish(PubSubTopic.PROCESS_UNITS)

    async def publish_run_log_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.RUN_LOG}')

    async def publish_method_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.METHOD}')

    async def publish_method_state_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.METHOD_STATE}')

    async def publish_control_state_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.CONTROL_STATE}')

    async def publish_error_log_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.ERROR_LOG}')

    async def publish_active_users_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.ACTIVE_USERS}')

    def expose_pubsub_topics(self, topic: PubSubTopic):
        """ This endpoint is just for exposing the topic enum to frontend via automatic type generation """
        pass

    async def trigger_publish_msw(self):
        """ Publish to all topics that start with 'MSW_' """
        topics_subscribed_to = list(self.pubsub_endpoint.notifier._topics.keys())
        msw_topics_subscribed_to = [topic for topic in topics_subscribed_to if topic.startswith('MSW_')]
        await self.pubsub_endpoint.publish(msw_topics_subscribed_to)

    async def on_disconnect(self, rpc_channel: RpcChannel):
        await asyncio.gather(*(callback(rpc_channel.id) for callback in self.on_disconnect_callbacks))

    def register_on_disconnect(self, on_disconnect: Callable[[str], Awaitable[None]]):
        self.on_disconnect_callbacks.append(on_disconnect)
