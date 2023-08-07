from __future__ import annotations
from typing import Callable
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_rpc import RpcChannel
from openpectus.protocol.messages import MessageBase


class ServerHandler():
    """ Handler for server, i.e. Aggregator """

    async def connect(self):
        """ A client is connecting"""
        pass

    async def register(self, client_id: str):
        """ A connected client registers its client_id. Note: Is invoked using a special rpc method."""
        pass

    async def disconnect(self):
        """ A client is disconnecting"""
        pass

    async def publish(self, topic: str, msg: MessageBase):
        """ Publish a message on a topic """
        pass

    async def subscribe(self, topic: str):
        """ Subscribe to a topic """
        pass

    async def send(self, channel: RpcChannel, msg: MessageBase):
        """ Send a direct message to a connected registered client """
        pass

    def register_direct_handler(self, handler: Callable[[MessageBase], None]):
        pass

    async def on_direct_message(self, client_id: str, msg: MessageBase):
        """ A message was received directly from a client. This may be a response to
        a sent message (via send()) or a message sent by the client on its own accord.
        """
        pass

    def register_topic_handler(self, topic: str, handler: Callable[[MessageBase], None]):
        pass

    async def on_topic_message(self, topic: str, msg: MessageBase):
        """ A message was received on a subscribed topic """
        pass


class WsServerHandler(ServerHandler):
    def __init__(self, ps_endpoint: PubSubEndpoint) -> None:
        super().__init__()

        self.ps_endpoint = ps_endpoint
        self.topic_handlers = {}
        self.direct_handler: Callable[[MessageBase], None] | None = None

    async def publish(self, topic: str, msg: MessageBase):
        await self.ps_endpoint.publish([topic], msg)

    async def subscribe(self, topic: str):
        async def on_msg(topics , data, _):
            topic = topics[0]
            await self.on_topic_message(topic, data)

        await self.ps_endpoint.subscribe([topic], on_msg)

    async def send(self, channel: RpcChannel, msg: MessageBase):
        await channel.other.send(msg=msg)

    def register_direct_handler(self, handler: Callable[[MessageBase], None]):
        self.direct_handler = handler

    async def on_direct_message(self, msg: MessageBase):
        if self.direct_handler is not None:
            self.direct_handler(msg)

    def register_topic_handler(self, topic: str, handler: Callable[[MessageBase], None]):
        self.topic_handlers[topic] = handler

    async def on_topic_message(self, topic: str, msg: MessageBase):
        if topic in self.topic_handlers.keys():
            handler = self.topic_handlers[topic]
            await handler(msg)
