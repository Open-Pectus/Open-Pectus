from __future__ import annotations
from typing import Callable
from fastapi_websocket_pubsub import PubSubClient
from openpectus.protocol.messages import MessageBase


class ClientHandler():
    """ Handler interface to be used for protocol clients, e.i. Engine and UI """

    def get_client_id(self) -> str:
        raise NotImplementedError()

    async def connect(self, config):
        """ Connect clint to web socket """
        pass

    async def publish(self, topic: str, msg: MessageBase):
        """ Publish a message on a topic """
        pass

    async def subscribe(self, topic: str):
        """ Subscribe to a topic """
        pass

    async def send(self, msg: MessageBase):
        """ Send a direct message to server """
        pass

    async def on_direct_message(self, msg: MessageBase):
        """ A message was received directly from server. This may be a response to
        a sent message (via send()) or a message sent by the server on its own accord.
        """
        pass

    def register_direct_handler(self, handler: Callable[[MessageBase], None]):
        pass

    async def on_topic_message(self, topic: str, msg: MessageBase):
        """ A message was received on a subscribed topic """
        pass

    def register_topic_handler(self, topic: str, handler: Callable[[MessageBase], None]):
        pass


class WsClientHandler(ClientHandler):
    """ Implementation of ClientHandler using a PubSubClient """
    def __init__(self, ps_client: PubSubClient) -> None:
        self.ps_client = ps_client
        self.topic_handlers = {}
        self.direct_handler: Callable[[MessageBase], None] | None = None
        super().__init__()

    async def publish(self, topic: str, msg: MessageBase):
        await self.ps_client.publish([topic], msg)

    async def subscribe(self, topic: str):
        async def on_msg(topics , data, _):
            topic = topics[0]
            await self.on_topic_message(topic, data)

        self.ps_client.subscribe(topic, on_msg)  # type: ignore

    async def send(self, msg: MessageBase):
        rpc_caller = self.ps_client._rpc_channel.other  # type: ignore
        await rpc_caller.on_direct_message(msg=msg)

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
            handler(msg)
