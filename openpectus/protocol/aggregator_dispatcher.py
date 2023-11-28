import asyncio
import logging
from typing import Dict, TypeVar, Callable, Awaitable, Any

import openpectus.protocol.messages as M
from fastapi import APIRouter, FastAPI, Request
from fastapi_websocket_rpc import RpcChannel, WebsocketRPCEndpoint
from fastapi_websocket_rpc.schemas import RpcResponse
from openpectus.protocol.dispatch_interface import AGGREGATOR_RPC_WS_PATH, AGGREGATOR_REST_PATH
from openpectus.protocol.exceptions import ProtocolException
from openpectus.protocol.serialization import deserialize, serialize

logger = logging.getLogger(__name__)


class AggregatorDispatcher():
    """
    Aggregator dispatcher for the Aggregator-Engine Protocol using REST + WebSocket RPC.
    Allows receiving message via HTTP POST and sending messages via JSON-RPC.
    """
    def __init__(self) -> None:
        super().__init__()

        self.router = APIRouter(tags=["aggregator"])
        self._engine_id_channel_map: Dict[str, RpcChannel] = {}
        self._handlers: Dict[type, Callable[[Any], Awaitable[M.MessageBase]]] = {}
        # WebsockeRPCEndpoint has wrong types for its on_connect and on_disconnect. It should be List[Callable[[RpcChannel], Awaitable[Any]]] instead of List[Coroutine]
        # See https://github.com/permitio/fastapi_websocket_rpc/issues/30
        self.endpoint = WebsocketRPCEndpoint(on_connect=[self.on_client_connect], on_disconnect=[self.on_client_disconnect]) # type: ignore
        self.endpoint.register_route(self.router, path=AGGREGATOR_RPC_WS_PATH)
        self.register_post_route(self.router)

    def has_engine_id(self, engine_id: str) -> bool:
        return engine_id in self._engine_id_channel_map.keys()

    async def on_delayed_client_connect(self, channel: RpcChannel):
        """ We 'delay' our on_connect callback because the WebsocketRPCEndpoint calls on_connect callbacks before it starts listening to responses to rpc calls.
         When we use create_task(), in on_client_connect() below, to call this method, we ensure that WebsocketRPCEndpoint starts listening to responses before we call get_engine_id() over rpc. """
        try:
            response = await channel.other.get_engine_id()
            assert isinstance(response, RpcResponse)
            engine_id = response.result
            assert isinstance(engine_id, str | None)
            if engine_id is None:
                logger.error("Engine tried connecting with no engine_id available. Closing connection.")
                return await channel.close()
            if engine_id in self._engine_id_channel_map:
                logger.error("Engine tried connecting with engine_id that is already connected. Closing connection.")
                return await channel.close()
            logger.info(f"Engine connected with engine_id: {engine_id}")
            self._engine_id_channel_map[engine_id] = channel
        except:
            logger.error("on_client_connect failed with exception", exc_info=True)
            return await channel.close()

    async def on_client_connect(self, channel: RpcChannel):
        asyncio.create_task(self.on_delayed_client_connect(channel))

    async def on_client_disconnect(self, channel: RpcChannel):
        self._engine_id_channel_map = {key:value for key, value in self._engine_id_channel_map.items() if value != channel}

    async def rpc_call(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        if engine_id not in self._engine_id_channel_map.keys():
            raise ProtocolException("Unknown engine: " + engine_id)

        channel = self._engine_id_channel_map[engine_id]
        response = await channel.other._dispatch_message(message=message)
        return response

    def register_post_route(self, router: APIRouter | FastAPI):
        @router.post(AGGREGATOR_REST_PATH)
        async def post(request: Request):
            request_json = await request.json()
            message = deserialize(request_json)

            response_message = await self._dispatch_post(message)

            message_json = serialize(response_message)
            return message_json

    async def _dispatch_post(self, message: M.MessageBase) -> M.MessageBase:
        """ Dispath message to registered handler. """
        message_type = type(message)
        if message_type in self._handlers.keys():
            try:
                response = await self._handlers[message_type](message)
                return response
            except Exception:
                logger.error(f"Dispatch failed for message type: {message_type}. Handler raised exception.", exc_info=True)
                return M.ProtocolErrorMessage(protocol_mgs="Dispatch failed. Handler raised exception.")
        else:
            logger.warning(f"Dispatch failed for message type: {message_type}. No handler registered.")
            return M.ProtocolErrorMessage(protocol_mgs="Dispatch failed. No handler registered.")

    MessageToHandle = TypeVar("MessageToHandle", bound=M.MessageBase)

    def set_post_handler(self, message_type: type[MessageToHandle], handler: Callable[[MessageToHandle], Awaitable[M.MessageBase]]):
        """ Set handler for message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    def unset_post_handler(self, message_type: type):
        """ Unset handler for message_type. """
        if message_type in self._handlers.keys():
            del self._handlers[message_type]
