from __future__ import annotations

import asyncio
import atexit
import logging
import socket
from typing import Callable, Any, Awaitable

import httpx
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolNetworkException
import openpectus.protocol.messages as M
import requests
from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient
from openpectus import __version__
from openpectus.protocol.dispatch_interface import AGGREGATOR_REST_PATH, AGGREGATOR_RPC_WS_PATH, AGGREGATOR_HEALTH_PATH
from openpectus.protocol.serialization import serialize, deserialize

logger = logging.getLogger(__name__)

EngineMessageHandler = Callable[[AM.AggregatorMessage], Awaitable[M.MessageBase]]
""" Handler in engine that handles aggregator messages of a given type """

class EngineDispatcherBase():
    def __init__(self) -> None:
        self._handlers: dict[type, Callable[[Any], Awaitable[M.MessageBase]]] = {}
        self._engine_id = None

    async def connect_async(self):
        raise NotImplementedError()

    async def disconnect_async(self):
        raise NotImplementedError()

    async def _reconnect(self):
        while True:
            logger.info("Reconnecting")
            await asyncio.sleep(3)
            try:
                await self.disconnect_async()
            except Exception as ex:
                logger.error("Reconnect - disconnect failed: " + str(ex))

            await asyncio.sleep(3)
            try:
                await self.connect_async()
                logger.info("Reconnect successful")
                return
            except Exception as ex:
                logger.error("Reconnect - connect failed: " + str(ex))


    async def post_async(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Post message to Aggregator """
        try:
            result = await self.post_async_impl(message)
            return result
        except ProtocolNetworkException:
            while True:
                try:
                    await self._reconnect()
                    result = await self.post_async_impl(message)
                    return result
                except ProtocolNetworkException:
                    pass
                except Exception:
                    logger.critical("Post error - unexpected exception", exc_info=True)
                    pass

    async def post_async_impl(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Post message to Aggregator. Abstract method """
        raise NotImplementedError()

    async def _dispatch_message_async(self, message: M.MessageBase):
        """ Dispath incoming message to registered handler. """
        message_type = type(message)
        try:
            await self._handlers[message_type](message)
        except KeyError:
            logger.warning(f"Dispatch failed for message type: {message_type}. No handler registered.")
        except Exception:
            logger.warning(
                f"Dispatch failed for message type: {message_type}. A handler was registered, but failed somehow.",
                exc_info=True)

    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        """ Register handler for given message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    def unset_rpc_handler(self, message_type: type):
        """ Unset handler for message_type. """
        if message_type in self._handlers.keys():
            del self._handlers[message_type]


class EngineDispatcher(EngineDispatcherBase):
    """
    Engine dispatcher for the Aggregator-Engine Protocol.
    Allows sending messages via HTTP POST and receiving messages via JSON-RPC.
    """

    class EngineRpcMethods(RpcMethodsBase):
        def __init__(self, dispatcher: EngineDispatcher, engine_id: str):
            super().__init__()
            self.disp = dispatcher
            self.engine_id = engine_id

        async def dispatch_message_async(self, message_json: dict[str, Any]):
            """ Dispath message to registered handler. """
            try:
                message = deserialize(message_json)
                assert isinstance(message, M.MessageBase)
            except Exception:
                logger.error("Dispatch failed. Message deserialization failed.", exc_info=True)
                return

            return await self.disp._dispatch_message_async(message)

        async def get_engine_id_async(self):
            # Note: Must be async since it is invoked by RPC
            return self.engine_id

    def __init__(self, aggregator_host: str, uod_name: str, location: str) -> None:
        super().__init__()
        self._aggregator_host = aggregator_host
        self._uod_name = uod_name
        self._location = location

        # TODO consider https/wss
        self.post_url = f"http://{aggregator_host}{AGGREGATOR_REST_PATH}"

    async def register_for_engine_id_async(self, uod_name: str, location: str) -> str | None:
        register_engine_msg = EM.RegisterEngineMsg(computer_name=socket.gethostname(), uod_name=uod_name, location=location,
                                                   engine_version=__version__)
        register_response = await self.post_async(register_engine_msg)
        logger.info("Registering for engine id")
        if not isinstance(register_response, AM.RegisterEngineReplyMsg) or not register_response.success:
            print("Failed to Register")
            return
        return register_response.engine_id

    def check_aggregator_alive_or_exit(self, aggregator_host: str):
        aggregator_health_url = f"http://{aggregator_host}{AGGREGATOR_HEALTH_PATH}"
        try:
            resp = httpx.get(aggregator_health_url)
        except httpx.ConnectError as ex:
            logger.fatal(f"Connection to Aggregator health end point {aggregator_health_url} failed.", exc_info=True)
            print("Connection to Aggregator health end point failed.")
            print(f"Status url: {aggregator_health_url}")
            print(f"Error: {ex}")
            print("OpenPectus Engine cannot start.")
            exit(1)
        if resp.is_error:
            logger.fatal(
                f"Aggregator health end point {aggregator_health_url} returned an unsuccessful result: {resp.status_code}.",
                exc_info=True)
            print("Aggregator health end point returned an unsuccessful result.")
            print(f"Status url: {aggregator_health_url}")
            print(f"HTTP status code returned: {resp.status_code}")
            print("OpenPectus Engine cannot start.")
            exit(1)

    async def connect_async(self):
        # TODO move this check into main - is ok to check on startup but will break retry
        #self.check_aggregator_alive_or_exit(self._aggregator_host)

        # TODO now we have a recurtsive loop where connect depends on itself

        if self._engine_id is None:
            logger.info("Registering for engine_id")
            self._engine_id = await self.register_for_engine_id_async(self._uod_name, self._location)
            if self._engine_id is None:
                logger.error("Failed to register. Aggregator refused registration. Exiting.")
                exit(2)  # TODO hmm this is not great

        rpc_url = f"ws://{self._aggregator_host}{AGGREGATOR_RPC_WS_PATH}"
        rpc_methods = EngineDispatcher.EngineRpcMethods(self, self._engine_id)
        self.rpc_client = WebSocketRpcClient(uri=rpc_url, methods=rpc_methods)
        atexit.register(self.disconnect_async)
        await self.rpc_client.__aenter__()
        logger.info("Websocket connected")

    async def disconnect_async(self):
        logger.info("Websocket disconnected")
        #await self.rpc_client.__aexit__()

    async def post_async_impl(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Send message via HTTP POST. """
        if (not isinstance(message, EM.RegisterEngineMsg)):  # Special case for registering
            if (self._engine_id is None):
                logger.error("Engine did not have engine_id yet")
                return M.ErrorMessage(message="Engine did not have engine_id yet")
            message.engine_id = self._engine_id

        try:
            message_json = serialize(message)
        except Exception:
            logger.error("Message serialization failed", exc_info=True)
            return M.ErrorMessage(message="Post failed")

        try:
            response = requests.post(url=self.post_url, json=message_json)
        except Exception as ex:
            raise ProtocolNetworkException("Post failed with exception") from ex
        
        if response.status_code == 200:
            response_json = response.json()
            try:
                value = deserialize(response_json)
                return value
            except Exception:
                logger.error("Message deserialization failed", exc_info=True)
                return M.ErrorMessage(message="Post succeeded but result deserialization failed")
        else:
            message_type = type(message)
            logger.error(f"Non-success http status code: {response.status_code} for input message type: {message_type}")
            raise ProtocolNetworkException(f"Post failed with non-success http status code: {response.status_code} for input message type: {message_type}")
