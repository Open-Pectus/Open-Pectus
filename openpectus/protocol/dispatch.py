from __future__ import annotations
import logging
from typing import Awaitable, Callable, Dict
import requests
import httpx

from fastapi_websocket_rpc.websocket_rpc_endpoint import WebsocketRPCEndpoint
from fastapi_websocket_rpc.websocket_rpc_client import WebSocketRpcClient, RpcMethodsBase

import openpectus.protocol.messages as M


logger = logging.getLogger(__name__)


# --------- Dispatch interfaces ------------

MessageHandler = Callable[[M.MessageBase], Awaitable[M.MessageBase]]


class AE_EngineDispatcher():
    """ Protocol dispatcher for Engine.

    Allows sending sync message via HTTP POST and receiving async messages via JSON-RPC.
    """

    def post(self, message: M.MessageBase) -> M.MessageBase:
        raise NotImplementedError()

    def set_rpc_handler(self, message_type: type, handler: MessageHandler):
        raise NotImplementedError()

    def unset_rpc_handler(self, message_type: type):
        raise NotImplementedError()


class AE_AggregatorDispatcher():

    async def rpc_call(self, message: M.MessageBase) -> M.MessageBase:
        raise NotImplementedError()

    def set_post_handler(self, message_type: type, handler: MessageHandler):
        raise NotImplementedError()

    def unset_post_handler(self, message_type: type, handler: MessageHandler):
        raise NotImplementedError()


class AF_AggregatorDispatcher():

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

    def __init__(self, post_url: str, ws_url: str) -> None:
        super().__init__()

        self.post_url = post_url

        rpc_methods = AE_EngineDispatcher_Impl.EngineRpcMethods(self)
        self.rpc_client = WebSocketRpcClient(uri=ws_url, methods=rpc_methods)

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
    def __init__(self) -> None:
        super().__init__()

        self.endpoint = WebsocketRPCEndpoint()
        self._handlers: Dict[str, MessageHandler] = {}

    async def rpc_call(self, message: M.MessageBase) -> M.MessageBase:
        response = await self.endpoint.other._dispatch_message(message=message)
        return response

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
        raise NotImplementedError()

    def unset_post_handler(self, message_type: type, handler: MessageHandler):
        raise NotImplementedError()
