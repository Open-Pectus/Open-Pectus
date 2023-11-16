from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

import tenacity
from fastapi_websocket_pubsub import PubSubClient
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventClientMethods
from fastapi_websocket_rpc import RpcChannel
from fastapi_websocket_rpc.schemas import RpcResponse
from openpectus.protocol.exceptions import ProtocolException
from openpectus.protocol.messages import (
    MessageBase,
    # RegisterEngineMsg,
    # ErrorMessage,
    ProtocolErrorMessage,
    # SuccessMessage,
    # InvokeCommandMsg,
    deserialize_msg,
    deserialize_msg_from_json,
    serialize_msg,
    serialize_msg_to_json
)

PORT = 9800


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO consider improving type hinting
# https://stackoverflow.com/questions/49360480/python-type-hinting-for-async-function-as-function-argument
# or even https://peps.python.org/pep-0544/#callback-protocols


ClientMessageHandler = Callable[[MessageBase], Awaitable[MessageBase]]

MsgDict = Dict[str, Any]


class RpcClientHandler(RpcEventClientMethods):
    """Represents the client's RPC interface"""

    def __init__(self, client):
        super().__init__(client)
        self._send_callback: Callable[[str, MessageBase], Awaitable[None]] | None = None
        self._client: Client | None = None

    def set_client(self, client: Client):
        self._client = client

    async def on_server_message(self, msg_type: str, msg_dict: MsgDict):
        """ Implements client's proxy method. Is invoked by the server using its client proxy. """
        logger.debug(f"on_server_message was called with msg_type: {msg_type}, msg_dict: {msg_dict}")
        assert isinstance(self.channel, RpcChannel)
        if self._client is None:
            raise ValueError("Client must be set on initialization")

        try:
            msg = deserialize_msg(msg_type, msg_dict)
        except Exception:
            logger.error("Deserialization failed", exc_info=True)
            return ProtocolErrorMessage(protocol_mgs="Deserialization failed")
        try:
            result = await self._client.handle_message(self.channel.id, msg)
            return serialize_msg_to_json(result)
        except Exception:
            logger.error("Send failed", exc_info=True)
            return ProtocolErrorMessage(protocol_mgs="on_server_message _send_callback failed")


class Client:
    def __init__(self) -> None:
        # self.client_handler: ClientHandler | None = None
        self.connected_event = asyncio.Event()
        self.channel: RpcChannel | None = None
        self.message_handlers: Dict[str, ClientMessageHandler] = {}
        self.ps_client: PubSubClient | None = None

    def set_ps_client(self, ps_client: PubSubClient):
        self.ps_client = ps_client
        assert isinstance(ps_client._methods, RpcClientHandler)
        ps_client._methods.set_client(self)

    def set_message_handler(self, message_type: type, handler: ClientMessageHandler):
        self.message_handlers[message_type.__name__] = handler

    async def disconnect_wait_async(self):
        if self.ps_client is not None:
            await self.ps_client.disconnect()
            await self.ps_client.wait_until_done()

    # def set_client_handler(self, handler: ClientHandler):
    #     self.client_handler = handler

    async def on_connect(
        self, ps_client: PubSubClient, channel: RpcChannel
    ):  # registered as handler on RpcEndpoint
        logger.debug("connected on channel: " + channel.id)
        self.ps_client = ps_client
        self.channel = channel
        self.connected_event.set()

    @property
    def connected(self):
        return self.connected_event.is_set()

    async def start_connect_wait_async(self, ws_url: str):
        logger.info(f"Opening WS connection to aggregator @ {ws_url}")
        self.connected_event.clear()
        if self.ps_client is None:
            raise ValueError("ps_client not set")
        self.ps_client.start_client(ws_url)
        if self.connected:
            raise ProtocolException("Already connected")

        await self.ps_client.wait_until_ready()
        await asyncio.wait_for(self.connected_event.wait(), 5)
        logger.info("Connected to aggregator")

    async def handle_message(self, channel_id: str, msg: MessageBase) -> MessageBase:
        msg_type = type(msg).__name__
        logger.debug(f"handle_message type {msg_type} on channel {channel_id}")
        handler = self.message_handlers.get(msg_type)
        if handler is None:
            err = f"No message handler registered for message type {msg_type}"
            logger.error(err)
            return ProtocolErrorMessage(protocol_mgs=err)
        else:
            return await handler(msg)

    async def on_disconnect(
        self, channel: RpcChannel
    ):  # registered as handler on RpcEndpoint
        logger.debug("disconnected channel: " + channel.id)
        self.connected_event.clear()

    async def send_to_server(
        self,
        msg: MessageBase,
        on_success: Callable[[], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> MessageBase:
        """Send message to server"""

        if self.channel is None:
            raise ProtocolException("Cannot send when no channel is set")

        try:
            msg_type, msg_dict = serialize_msg(msg)
            logger.debug(f"Sending message of type {msg_type} to server")
            resp = await self.channel.other.on_client_message(msg_type=msg_type, msg_dict=msg_dict)
            logger.debug(
                f"Send success. Got response of type {type(resp).__name__} with value {str(resp)}"
            )
            if not isinstance(resp, RpcResponse):
                err = f"Result from server proxy should be of type RpcResponse, not '{type(resp).__name__}'"
                logger.error(err)
                raise ProtocolException(err)

            if not isinstance(resp.result, str):
                err = f"RpcResponse result property should be of type str, not '{type(resp.result).__name__}'"
                logger.error(err)
                raise ProtocolException(err)

            result = deserialize_msg_from_json(resp.result)
        except Exception as ex:
            logger.error("Failed to invoke server.send", exc_info=True)
            if on_error is not None:
                on_error(ex)
            raise ProtocolException("Send failed")

        if on_success is not None:
            on_success()

        return result


async def on_events(data, topic):
    print(f"got event on topic '{topic}' with data: '{data}'")


def create_client(on_connect_callback=None, on_disconnect_callback=None) -> Client:
    client = Client()

    _on_conn = [client.on_connect]
    if on_connect_callback is not None:
        _on_conn.append(on_connect_callback)

    _on_disconnn = [client.on_disconnect]
    if on_disconnect_callback is not None:
        _on_disconnn.append(on_disconnect_callback)

    # Tenacity (https://tenacity.readthedocs.io/) retry kwargs. Defaults to  {'wait': wait.wait_random_exponential(max=45)}
    # reraise=True, stop=stop_after_attempt(1)

    def logerror(retry_state: tenacity.RetryCallState):
        logger.exception(retry_state.outcome.exception())  # type: ignore

    def create_retry_config():
        # from tenacity import retry, wait
        # from tenacity.retry import retry_if_exception
        from tenacity.retry import retry_never
        from tenacity.stop import stop_after_attempt

        # DEFAULT_RETRY_CONFIG = {
        #     'wait': wait.wait_random_exponential(min=0.1, max=120),
        #     'retry': retry_if_exception(isNotForbbiden),
        #     'reraise': True,
        #     "retry_error_callback": logerror
        # }
        cfg = {'retry': retry_never, "retry_error_callback": logerror, "stop": stop_after_attempt(1)}
        return cfg

    retry_config = create_retry_config()
    # Note: Instantiation order issue. handlers for connect/disconnest must be set in PubSubClient ctor.
    # For that reason we need these weird backwards assignments. Fix with DI
    ps_client = PubSubClient(
        on_connect=_on_conn,
        on_disconnect=_on_disconnn,
        methods_class=RpcClientHandler,  # type: ignore # RpcClientHandler
        retry_config=retry_config)
    client.set_ps_client(ps_client)

    return client
