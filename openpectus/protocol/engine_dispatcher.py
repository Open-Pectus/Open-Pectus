import logging
from typing import Dict

import openpectus.protocol.messages as M
import requests
from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient
from openpectus.protocol.dispatch_interface import AGGREGATOR_POST_PATH, AGGREGATOR_RPC_WS_PATH, MessageHandler

logger = logging.getLogger(__name__)

class EngineDispatcher():
    """
    Engine dispatcher for the Aggregator-Engine Protocol.
    Allows sending messages via HTTP POST and receiving messages via JSON-RPC.
    """

    class EngineRpcMethods(RpcMethodsBase):
        def __init__(self, disp: 'EngineDispatcher'):
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

        rpc_methods = EngineDispatcher.EngineRpcMethods(self)
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
