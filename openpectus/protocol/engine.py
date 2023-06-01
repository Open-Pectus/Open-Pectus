'''
The engine connects with the Aggregator
and registers itself.
After registration it will periodically
send data to the aggregator.
'''


# Adapted from this source:
#https://github.com/permitio/fastapi_websocket_pubsub/blob/master/examples/pubsub_client_example.py

import asyncio
import logging
from typing import Callable
from fastapi_websocket_rpc.schemas import RpcResponse
from fastapi_websocket_pubsub import PubSubClient
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventClientMethods
from fastapi_websocket_rpc import RpcChannel
from protocol.exceptions import ProtocolException
from protocol.clienthandler import ClientHandler, WsClientHandler
from protocol.messages import (
    deserialize_msg,
    MessageBase,
    RegisterEngineMsg
)


PORT = 9800


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO can we integration test aggregator+engine? Then we could step down on handlers and just test the functionality directly


class RpcClientHandler(RpcEventClientMethods):
    """ Represents the client's RPC interface """
    def __init__(self, client):
        super().__init__(client)
        self._send_callback: Callable[[str, MessageBase], None] | None = None

    def set_send_callback(self, callback: Callable[[str, MessageBase], None]):
        self._send_callback = callback


class Client():
    def __init__(self) -> None:
        self.rpc_handler: RpcClientHandler | None = None
        self.client_handler: ClientHandler | None = None
        self.connected_event = asyncio.Event()
        self.channel: RpcChannel | None = None

    def set_rpc_handler(self, handler: RpcClientHandler):
        self.rpc_handler = handler
        self.rpc_handler.set_send_callback(self.handle_message)

    def set_client_handler(self, handler: ClientHandler):
        self.client_handler = handler

    async def on_connect(self, ps_client: PubSubClient, channel: RpcChannel):  # registered as handler on RpcEndpoint
        logger.debug("connected on channel: " + channel.id)
        self.ps_client = ps_client
        self.channel = channel
        self.connected_event.set()

    @property
    def connected(self):
        return self.connected_event.is_set()

    async def wait_start_connect(self, ws_url: str, ps_client: PubSubClient):
        self.connected_event.clear()
        ps_client.start_client(ws_url)
        if self.connected:
            raise ProtocolException("Already connected")

        await ps_client.wait_until_ready()
        await asyncio.wait_for(self.connected_event.wait(), 5)

    async def register(self, on_register=None):
        if self.channel is None:
            raise ProtocolException("Cannot register when no channel is set")

        success = False
        try:
            # explicit register method - consider using handle_message instead
            resp = await self.channel.other.register(client_id="foo")
            success = resp.result
        except Exception as ex:
            logger.error("Failed to invoke server.register", exc_info=True)
            raise ProtocolException("Registration failed", ex)

        if success and on_register is not None:
            await on_register()

        return success

    async def handle_message(self, channel_id: str, msg: MessageBase):
        logger.debug(f"handle_message type {type(msg).__name__}: {msg.__repr__()}")
        handler_name = "handle_" + type(msg).__name__
        handler = getattr(self, handler_name, None)
        if handler is None:
            logger.error(f"Handler name {handler_name} is not defined")
        else:
            await handler(channel_id, msg)

    async def on_disconnect(self, channel: RpcChannel):  # registered as handler on RpcEndpoint
        logger.debug("disconnected channel: " + channel.id)
        self.connected_event.clear()

    # TODO on_error(self, Exception):


async def on_events(data, topic):
    print(f"got event on topic '{topic}' with data: '{data}'")


def create_client(on_connect_callback=None, on_disconnect_callback=None):
    client = Client()

    _on_conn = [client.on_connect]
    if on_connect_callback is not None:
        _on_conn.append(on_connect_callback)

    _on_disconnn = [client.on_disconnect]
    if on_disconnect_callback is not None:
        _on_disconnn.append(on_disconnect_callback)

    ps_client = PubSubClient(on_connect=_on_conn, on_disconnect=_on_disconnn)
#    client_handler = WsClientHandler(ps_client)

#    client.set_rpc_handler(ps_client._methods)  # type: ignore
#    client.set_client_handler(client_handler)
    return client, ps_client


async def main():
    # Create a client and subscribe to topics    
    ps_client = PubSubClient(["guns", "germs"], callback=on_events, methods_class=RpcClientHandler)
    client_handler = WsClientHandler(ps_client)
    client = Client()
    client.set_rpc_handler(ps_client._methods)  # type: ignore
    client.set_client_handler(client_handler)

    ps_client.start_client(f"ws://127.0.0.1:{PORT}/pubsub")


    msg = RegisterEngineMsg(engine_name="eng1", uod_name="uod1")
    #result = await client.client_handler.send(msg=msg)
    result = await client.rpc_handler

    # async def on_steel(data, topic):
    #     print("running callback steel!")
    #     print("Got data", data, " on topic ", topic)
    #     asyncio.create_task(ps_client.disconnect())

    # ps_client.subscribe("steel", on_steel)
    # ps_client.start_client(f"ws://127.0.0.1:{PORT}/pubsub")
    # logger.debug("client started")
    # await asyncio.sleep(1)
    # logger.debug("Registering...")
    # # Note: For RPC calls one MUST use argument name(s). Otherwise it fails with a weird error
    # # Also, there is not deserialization going on. Must be missing something (register returns a bool)    
    # # value : RpcResponse = await client._rpc_channel.other.register(client_id="foo")  # type: ignore
    # # assert isinstance(value.result, bool)
    # # if value.result:  # == str(True):  # Not much type help here
    # #     logger.debug("Registration successful")
    # # else:
    # #     logger.warning("Registration failed")

    # logger.debug("Sending RegisterEngineMsg")
    # msg = RegisterEngineMsg(engine_name="eng1", uod_name="uod1")
    # value = await ps_client._rpc_channel.other.send(msg_type=type(msg).__name__, msg_dict=msg.dict())
    # logger.debug(f"msg sent. result: {value}")

    await ps_client.wait_until_done()


if __name__ == "__main__":
    asyncio.run(main())
