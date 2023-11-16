import logging
from typing import Dict

import openpectus.protocol.messages as M
from fastapi import APIRouter, FastAPI, Request
from fastapi_websocket_rpc import RpcChannel, WebsocketRPCEndpoint
from openpectus.protocol.dispatch_interface import AGGREGATOR_RPC_WS_PATH, AGGREGATOR_POST_PATH, MessageHandler
from openpectus.protocol.exceptions import ProtocolException

logger = logging.getLogger(__name__)


class AE_AggregatorDispatcher():
    """
    Aggregator dispatcher for the Aggregator-Engine Protocol using REST + WebSocket RPC.
    Allows receiving message via HTTP POST and sending messages via JSON-RPC.
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
