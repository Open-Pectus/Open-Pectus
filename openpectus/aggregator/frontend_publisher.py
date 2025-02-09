from enum import StrEnum, auto

from fastapi.routing import APIRouter
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_pubsub.event_notifier import TopicList
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods


class PubSubTopic(StrEnum):
    RUN_LOG = auto()
    METHOD = auto()
    CONTROL_STATE = auto()
    ERROR_LOG = auto()
    PROCESS_UNITS = auto()


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
        self.pubsub_endpoint = PubSubEndpoint(methods_class=FrontendPublisher.MethodsWithUnsubscribe)
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
        # for now we use PubSubTopic.METHOD for both Method and MethodState changes
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.METHOD}')

    async def publish_control_state_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.CONTROL_STATE}')

    async def publish_error_log_changed(self, unitId: str):
        await self.pubsub_endpoint.publish(f'{unitId}/{PubSubTopic.ERROR_LOG}')

    def expose_pubsub_topics(self, topic: PubSubTopic):
        """ This endpoint is just for exposing the topic enum to frontend via autogeneration """
        pass

    async def trigger_publish_msw(self):
        """ Publish to all topics that start with 'MSW_' """
        topics_subscribed_to = list(self.pubsub_endpoint.notifier._topics.keys())
        msw_topics_subscribed_to = [topic for topic in topics_subscribed_to if topic.startswith('MSW_')]
        await self.pubsub_endpoint.publish(msw_topics_subscribed_to)
