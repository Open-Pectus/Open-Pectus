from __future__ import annotations
import logging
from typing import Awaitable, Callable, Dict
from fastapi import APIRouter, FastAPI, Request
import requests

from fastapi_websocket_rpc.websocket_rpc_endpoint import WebsocketRPCEndpoint, RpcChannel
from fastapi_websocket_rpc.websocket_rpc_client import WebSocketRpcClient, RpcMethodsBase
from openpectus.protocol.exceptions import ProtocolException

import openpectus.protocol.messages as M

AGGREGATOR_RPC_WS_PATH = "/AE_rpc"
AGGREGATOR_POST_PATH = "/AE_post"

logger = logging.getLogger(__name__)


# --------- Dispatch interfaces ------------

MessageHandler = Callable[[M.MessageBase], Awaitable[M.MessageBase]]


class AE_EngineDispatcher():
    """ Engine dispatcher for the Aggregator-Engine Protocol.

    Allows sending messages via HTTP POST and receiving messages via JSON-RPC.
    """

    def post(self, message: M.MessageBase) -> M.MessageBase:
        raise NotImplementedError()

    def set_rpc_handler(self, message_type: type, handler: MessageHandler):
        raise NotImplementedError()

    def unset_rpc_handler(self, message_type: type):
        raise NotImplementedError()


class AE_AggregatorDispatcher():
    """ Aggregator dispatcher for the Aggregator-Engine Protocol.

    Allows receiving message via HTTP POST and sending messages via JSON-RPC.
    """
    async def rpc_call(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        raise NotImplementedError()

    def set_post_handler(self, message_type: type, handler: MessageHandler):
        raise NotImplementedError()

    def unset_post_handler(self, message_type: type):
        raise NotImplementedError()


class AF_AggregatorDispatcher():
    """ Aggregator dispatcher for the Aggregator-Frontend Protocol.

    Allows sending messages via JSON-PubSub.
    """
    async def publish_msg1(self, message: M.MessageBase):
        raise NotImplementedError()

    async def publish_msg2(self, message: M.MessageBase):
        raise NotImplementedError()

# engine should post Register (which returns client_id), then register handlers, then post Ready


# ---------- Implementations -----------


class AE_EngineDispatcher_Impl(AE_EngineDispatcher):

    class EngineRpcMethods(RpcMethodsBase):
        def __init__(self, disp: AE_EngineDispatcher_Impl):
            super().__init__()
            self.disp = disp

        async def _dispatch_message(self, message: M.MessageBase):
            """ Dispath message to registered handler. """
            return await self.disp._dispatch_message(message)

    def __init__(self, aggregator_host: str) -> None:
        super().__init__()

        # TODO consider https/wss
        self.post_url = f"http://{aggregator_host}{AGGREGATOR_POST_PATH}"
        rpc_url = f"ws://{aggregator_host}{AGGREGATOR_RPC_WS_PATH}"

        rpc_methods = AE_EngineDispatcher_Impl.EngineRpcMethods(self)
        self.rpc_client = WebSocketRpcClient(uri=rpc_url, methods=rpc_methods)

        self._handlers: Dict[str, MessageHandler] = {}

    def post(self, message: M.MessageBase) -> M.MessageBase:
        """ Send message via HTTP POST. """
        message_json = M.serialize(message)
        response = requests.post(url=self.post_url, json=message_json)
        if response.status_code == 200:
            response_json = response.json()
            value = M.deserialize(response_json)
            return value
        else:
            message_type = type(message)
            logger.error(f"Non-success http status code: {response.status_code} for input message type: {message_type}")
            return M.ErrorMessage(message=f"Post failed with message {message_type}")

    async def _dispatch_message(self, message: M.MessageBase):
        """ Dispath message to registered handler. """
        message_type = type(message).__name__
        if message_type in self._handlers.keys():
            try:
                await self._handlers[message_type](message)
            except Exception:
                logger.warning(f"Dispatch failed for message type: {message_type}. No handler registered.")

    def set_rpc_handler(self, message_type: type, handler: MessageHandler):
        """ Set handler for message_type. """
        if message_type.__name__ in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type.__name__] = handler

    def unset_rpc_handler(self, message_type: type):
        """ Unset handler for message_type. """
        if message_type.__name__ in self._handlers.keys():
            del self._handlers[message_type.__name__]


class AE_AggregatorDispatcher_Impl(AE_AggregatorDispatcher):
    """ Aggregator dispatcher for the Aggregator-Engine Protocol using REST + WebSocket RPC.

    """
    def __init__(self, router: APIRouter | FastAPI) -> None:
        super().__init__()

        self.engine_map: Dict[str, RpcChannel] = {}
        self.endpoint = WebsocketRPCEndpoint()
        self.endpoint.register_route(router, path=AGGREGATOR_RPC_WS_PATH)
        self._handlers: Dict[str, MessageHandler] = {}
        self.register_post_route(router)

    # TODO handle client_id/engine_id => channel map
    # async def on_client_connect(self, channel: RpcChannel, _):
    #     pass

    # async def on_client_disconnect(self, channel: RpcChannel, _):
    #     pass

    async def rpc_call(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        if engine_id not in self.engine_map.keys():
            raise ProtocolException("Unknown engine: " + engine_id)

        channel = self.engine_map[engine_id]
        response = await channel.other._dispatch_message(message=message)  # type: ignore
        return response

    def register_post_route(self, router: APIRouter | FastAPI):
        @router.post(AGGREGATOR_POST_PATH)
        async def post(request: Request):
            request_json = await request.json()
            message = M.deserialize(request_json)

            response_message = await self._dispatch_post(message)

            message_json = M.serialize(response_message)
            return message_json

    async def _dispatch_post(self, message: M.MessageBase) -> M.MessageBase:
        """ Dispath message to registered handler. """
        message_type = type(message).__name__
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

    def set_post_handler(self, message_type: type, handler: MessageHandler):
        """ Set handler for message_type. """
        if message_type.__name__ in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type.__name__] = handler

    def unset_post_handler(self, message_type: type):
        """ Unset handler for message_type. """
        if message_type.__name__ in self._handlers.keys():
            del self._handlers[message_type.__name__]
