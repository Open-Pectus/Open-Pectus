import asyncio
import logging
from typing import Callable, Awaitable, Any

from fastapi import APIRouter, FastAPI, Request
from fastapi_websocket_rpc import RpcChannel, WebsocketRPCEndpoint
from fastapi_websocket_rpc.schemas import RpcResponse

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.protocol.dispatch_interface import AGGREGATOR_RPC_WS_PATH, AGGREGATOR_REST_PATH, EngineMessageType
from openpectus.protocol.exceptions import ProtocolException
from openpectus.protocol.serialization import deserialize, serialize


logger = logging.getLogger(__name__)


RegisterHandler = Callable[[EM.RegisterEngineMsg], Awaitable[AM.RegisterEngineReplyMsg]]
""" Specific handler for register messages from engine """

EngineConnectHandler = Callable[[str], Awaitable[None]]
""" Specific handler for engine disconnect notifications from dispatcher """

EngineDisconnectHandler = Callable[[str], Awaitable[None]]
""" Specific handler for engine disconnect notifications from dispatcher """

AggregatorMessageHandler = Callable[[Any], Awaitable[M.MessageBase]]
""" Handler in aggregator that handles engine messages of a given type """


class AggregatorDispatcher():
    """
    Aggregator dispatcher for the Aggregator-Engine Protocol using REST + WebSocket RPC.
    Allows receiving message via HTTP POST and sending messages via JSON-RPC.
    """

    def __init__(self) -> None:
        self._handlers: dict[type, AggregatorMessageHandler] = {}
        self._register_handler: RegisterHandler | None = None
        self._connect_handler: EngineConnectHandler | None = None
        self._disconnect_handler: EngineDisconnectHandler | None = None
        self.router = APIRouter(tags=["aggregator"])
        self._engine_id_channel_map: dict[str, RpcChannel] = {}
        # WebsockeRPCEndpoint has wrong types for its on_connect and on_disconnect.
        # It should be List[Callable[[RpcChannel], Awaitable[Any]]] instead of List[Coroutine]
        # See https://github.com/permitio/fastapi_websocket_rpc/issues/30
        self.endpoint = WebsocketRPCEndpoint(
            on_connect=[self.on_client_connect],  # type: ignore
            on_disconnect=[self.on_client_disconnect])  # type: ignore
        self.endpoint.register_route(self.router, path=AGGREGATOR_RPC_WS_PATH)
        self._register_post_route(self.router)

    async def _on_delayed_client_connect(self, channel: RpcChannel):
        """ We 'delay' our on_connect callback because the WebsocketRPCEndpoint calls on_connect callbacks before it starts
        listening to responses to rpc calls. When we use create_task(), in on_client_connect() below, to call this method,
        we ensure that WebsocketRPCEndpoint starts listening to responses before we call get_engine_id_async() over rpc.
        """
        try:
            response = await channel.other.get_engine_id_async()
        except Exception:
            logger.error("Failed to invoke 'channel.other.get_engine_id_async()'", exc_info=True)
            return

        try:
            assert isinstance(response, RpcResponse)
            engine_id = response.result
            assert isinstance(engine_id, str | None)
            if engine_id is None:
                logger.error("Engine tried connecting with no engine_id available. Closing connection.")
                await channel.close()
                return

            if engine_id in self._engine_id_channel_map:
                logger.warning("Engine tried connecting with engine_id that is already connected. Closing connection.")
                await channel.close()
                return

            logger.info(f"Engine '{engine_id}' connected")
            self._engine_id_channel_map[engine_id] = channel

            if self._connect_handler is not None:
                await self._connect_handler(engine_id)
        except Exception:
            logger.error("on_delayed_client_connect failed with exception", exc_info=True)
            try:
                await channel.close()
            except Exception:
                logger.warning("Failed to invoke channel.close()", exc_info=True)


    async def on_client_connect(self, channel: RpcChannel):
        asyncio.create_task(self._on_delayed_client_connect(channel))

    async def on_client_disconnect(self, channel: RpcChannel):
        engine_id: str | None = None
        for key, value in self._engine_id_channel_map.items():
            if value == channel:
                engine_id = key
                break
        if engine_id is not None:
            logger.info(f"Engine '{engine_id}' disconnected")
            del self._engine_id_channel_map[engine_id]
            # Notify aggregator that engine disconnected so that it
            # can save what is necessary and remove engine_data
            if self._disconnect_handler is not None:
                await self._disconnect_handler(engine_id)
        else:
            logger.error("Unknown engine disconnected")

    def has_connected_engine_id(self, engine_id: str) -> bool:
        """ Return a value indicating whether the engine_id is known. Abstract method. """
        return engine_id in self._engine_id_channel_map.keys()

    async def rpc_call(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        logger.info(f"Trying to invoke rpc, engine: {engine_id}, msg-type: {type(message).__name__}")
        if engine_id not in self._engine_id_channel_map.keys():
            logger.error(f"Cannot invoke rpc call to unknown engine: {engine_id}")
            raise ProtocolException("Unknown engine: " + engine_id)

        channel = self._engine_id_channel_map[engine_id]
        message_json = serialize(message)

        try:
            response = await channel.other.dispatch_message_async(message_json=message_json)
            return response
        except Exception:
            logger.error("Error during rpc call", exc_info=True)
            await channel.close()
            raise ProtocolException("Error in rpc call")

    def _register_post_route(self, router: APIRouter | FastAPI):
        @router.post(AGGREGATOR_REST_PATH)
        async def post(request: Request):
            request_json = await request.json()
            try:
                message = deserialize(request_json)
            except Exception:
                logger.error(f"Message deserialization failed, json:\n{request_json}\n", exc_info=True)
                raise ProtocolException("Deserialization error")

            if not isinstance(message, EM.RegisterEngineMsg) and not isinstance(message, EM.EngineMessage):
                raise ValueError(f"Invalid type of message sent from Engine: {type(message).__name__}")
            response_message = await self.dispatch_post(message)

            try:
                message_json = serialize(response_message)
            except Exception:
                logger.error(f"Message serialization failed, message type: {type(response_message).__name__}")
                raise ProtocolException("Serialization error")

            return message_json

    async def dispatch_post(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Dispatch incoming message to registered handler. """
        logger.debug(f"Incoming message: {message.ident}")
        if isinstance(message, EM.RegisterEngineMsg):
            if self._register_handler is None:
                return M.ProtocolErrorMessage(protocol_msg="Missing handler for registering engine")
            response = await self._register_handler(message)
            assert isinstance(response, AM.RegisterEngineReplyMsg)
            assert isinstance(response.engine_id, str)
            assert response.engine_id != ""
            return response

        if message.engine_id == '':
            logger.warning("Failed to handle engine message as its engine_id was the empty string")
            return M.ProtocolErrorMessage(
                protocol_msg="Failed to handle engine message as its engine_id was the empty string")

        message_type = type(message)
        if message_type in self._handlers.keys():
            try:
                return await self._handlers[message_type](message)
            except Exception:
                logger.error(f"Dispatch failed for message type: {message_type}. Handler raised exception.", exc_info=True)
                return M.ProtocolErrorMessage(protocol_msg="Dispatch failed. Handler raised exception.")
        else:
            logger.warning(f"Dispatch failed for message type: {message_type}. No handler registered.")
            return M.ProtocolErrorMessage(protocol_msg="Dispatch failed. No handler registered.")

    def set_post_handler(self, message_type: type[EngineMessageType], handler: AggregatorMessageHandler):
        """ Set handler for message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    def set_register_handler(self, handler: RegisterHandler):
        self._register_handler = handler

    def set_connect_handler(self, handler: EngineConnectHandler):
        self._connect_handler = handler

    def set_disconnect_handler(self, handler: EngineDisconnectHandler):
        self._disconnect_handler = handler

    async def shutdown(self):
        logger.info("shutdown started")
        self._handlers.clear()
        for _, channel in self._engine_id_channel_map.items():
            await channel.close()
        self._disconnect_handler = None
        logger.info("shutdown completed")
