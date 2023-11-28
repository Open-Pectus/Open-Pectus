from __future__ import annotations

import asyncio
import atexit
import logging
import socket
from typing import Dict, TypeVar, Callable, Any, Awaitable

import httpx
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
import requests
from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient
from openpectus.protocol.dispatch_interface import AGGREGATOR_REST_PATH, AGGREGATOR_RPC_WS_PATH, AGGREGATOR_HEALTH_PATH
from openpectus.protocol.serialization import serialize, deserialize

logger = logging.getLogger(__name__)


class EngineDispatcher():
    """
    Engine dispatcher for the Aggregator-Engine Protocol.
    Allows sending messages via HTTP POST and receiving messages via JSON-RPC.
    """

    class EngineRpcMethods(RpcMethodsBase):
        def __init__(self, dispatcher: EngineDispatcher, engine_id: str):
            super().__init__()
            self.disp = dispatcher
            self.engine_id = engine_id

        async def _dispatch_message(self, message: M.MessageBase):
            """ Dispath message to registered handler. """
            return await self.disp._dispatch_message(message)

        async def get_engine_id(self):
            return self.engine_id

    async def register_for_engine_id(self, uod_name: str):
        register_engine_msg = EM.RegisterEngineMsg(computer_name=socket.gethostname(), uod_name=uod_name)
        register_response = self.post(register_engine_msg)
        if not isinstance(register_response, AM.RegisterEngineReplyMsg) or not register_response.success:
            print("Failed to Register")
            return
        return register_response.engine_id

    def check_aggregator_alive(self, aggregator_host: str):
        aggregator_health_url = f"http://{aggregator_host}{AGGREGATOR_HEALTH_PATH}"
        try:
            resp = httpx.get(aggregator_health_url)
        except httpx.ConnectError as ex:
            print("Connection to Aggregator health end point failed.")
            print(f"Status url: {aggregator_health_url}")
            print(f"Error: {ex}")
            print("OpenPectus Engine cannot start.")
            exit(1)
        if resp.is_error:
            print("Aggregator health end point returned an unsuccessful result.")
            print(f"Status url: {aggregator_health_url}")
            print(f"HTTP status code returned: {resp.status_code}")
            print("OpenPectus Engine cannot start.")
            exit(1)

    def __init__(self, aggregator_host: str, uod_name: str) -> None:
        super().__init__()
        self._handlers: Dict[type, Callable[[Any], Awaitable[M.MessageBase]]] = {}
        self._engine_id = None

        # TODO consider https/wss
        self.post_url = f"http://{aggregator_host}{AGGREGATOR_REST_PATH}"
        asyncio.create_task(self.setup_websocket(aggregator_host, uod_name))

    async def setup_websocket(self, aggregator_host: str, uod_name: str):
        self.check_aggregator_alive(aggregator_host)
        while self._engine_id is None:
            self._engine_id = await self.register_for_engine_id(uod_name)

        rpc_url = f"ws://{aggregator_host}{AGGREGATOR_RPC_WS_PATH}"
        rpc_methods = EngineDispatcher.EngineRpcMethods(self, self._engine_id)
        self.rpc_client = WebSocketRpcClient(uri=rpc_url, methods=rpc_methods)
        atexit.register(self.disconnect)
        await self.rpc_client.__aenter__()

    async def disconnect(self):
        await self.rpc_client.__aexit__()

    def post(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Send message via HTTP POST. """
        if (not isinstance(message, EM.RegisterEngineMsg)):  # Special case for registering
            if (self._engine_id is None): return M.ErrorMessage(message="Engine did not have engine_id yet")
            message.engine_id = self._engine_id
        message_json = serialize(message)
        response = requests.post(url=self.post_url, json=message_json)
        if response.status_code == 200:
            response_json = response.json()
            value = deserialize(response_json)
            return value
        else:
            message_type = type(message)
            logger.error(f"Non-success http status code: {response.status_code} for input message type: {message_type}")
            return M.ErrorMessage(message=f"Post failed with message {message_type}")

    async def _dispatch_message(self, message: M.MessageBase):
        """ Dispath message to registered handler. """
        message_type = type(message)
        if message_type in self._handlers.keys():
            try:
                await self._handlers[message_type](message)
            except Exception:
                logger.warning(f"Dispatch failed for message type: {message_type}. No handler registered.")

    MessageToHandle = TypeVar("MessageToHandle", bound=M.MessageBase)

    def set_rpc_handler(self, message_type: type[MessageToHandle], handler: Callable[[MessageToHandle], Awaitable[M.MessageBase]]):
        """ Set handler for message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    def unset_rpc_handler(self, message_type: type):
        """ Unset handler for message_type. """
        if message_type in self._handlers.keys():
            del self._handlers[message_type]
