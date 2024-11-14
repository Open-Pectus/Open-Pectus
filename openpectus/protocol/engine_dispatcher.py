from __future__ import annotations

import logging
import socket
from typing import Callable, Any, Awaitable

import httpx
import json
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolNetworkException
import openpectus.protocol.messages as M
from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient
import tenacity
from openpectus import __version__, __name__
from openpectus.protocol.dispatch_interface import AGGREGATOR_REST_PATH, AGGREGATOR_RPC_WS_PATH, AGGREGATOR_HEALTH_PATH
from openpectus.protocol.serialization import serialize, deserialize

logger = logging.getLogger(__name__)

EngineMessageHandler = Callable[[AM.AggregatorMessage], Awaitable[M.MessageBase]]
""" Handler in engine that handles aggregator messages of a given type """

engine_headers = {"User-Agent": f"{__name__}/{__version__}"}

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

        async def dispatch_message_async(self, message_json: dict[str, Any]):
            """ Dispath message to registered handler. """
            try:
                message = deserialize(message_json)
                assert isinstance(message, M.MessageBase)
            except Exception:
                logger.error("Dispatch failed. Message deserialization failed.", exc_info=True)
                return

            return await self.disp.dispatch_message_async(message)

        async def get_engine_id_async(self):
            # Note: Must be declared async to be usable by RPC
            return self.engine_id

    def __init__(self, aggregator_host: str, secure: bool, uod_options: dict[str, str]) -> None:
        super().__init__()
        self._aggregator_host = aggregator_host
        self._uod_name = uod_options.pop("uod_name")
        self._uod_author_name = uod_options.pop("uod_author_name")
        self._uod_author_email = uod_options.pop("uod_author_email")
        self._uod_filename = uod_options.pop("uod_filename")
        self._location = uod_options.pop("location")
        self._rpc_client: WebSocketRpcClient | None = None
        self._handlers: dict[type, Callable[[Any], Awaitable[M.MessageBase]]] = {}
        self._engine_id = None
        self._sequence_number = 1

        http_scheme = "https" if secure else "http"
        ws_scheme = "wss" if secure else "ws"
        self._post_url = f"{http_scheme}://{aggregator_host}{AGGREGATOR_REST_PATH}"
        self._health_url = f"{http_scheme}://{self._aggregator_host}{AGGREGATOR_HEALTH_PATH}"
        self._rpc_url = f"{ws_scheme}://{self._aggregator_host}{AGGREGATOR_RPC_WS_PATH}"
        logger.info(f"Connecting to aggregator using urls:\n{self._post_url}\n{self._rpc_url}")

    def check_aggregator_alive(self) -> bool:
        try:
            resp = httpx.get(self._health_url, headers=engine_headers)
        except httpx.ConnectError as ex:
            logger.error(f"Connection to Aggregator health end point {self._health_url} failed.")
            logger.info("Connection to Aggregator health end point failed.")
            logger.info(f"Status url: {self._health_url}")
            logger.info(f"Error: {ex}")
            return False

        if resp.is_error:
            logger.error(
                f"Aggregator health end point {self._health_url} returned an unsuccessful result: {resp.status_code}.",
                exc_info=True)
            logger.info("Aggregator health end point returned an unsuccessful result.")
            logger.info(f"Status url: {self._health_url}")
            logger.info(f"HTTP status code returned: {resp.status_code}")
            return False

        logger.debug(f"Aggregator health url {self._health_url} responded succesfully")
        return True

    async def connect_async(self):
        def logerror(retry_state: tenacity.RetryCallState):
            if retry_state and retry_state.outcome:
                ex = retry_state.outcome.exception()
                if ex:
                    logger.exception(ex)
        retry_config = {  # use no retry because we use our own reconnect mechanism
            'wait': tenacity.wait.wait_none,
            'retry': tenacity.retry_never,
            'reraise': True,
            "retry_error_callback": logerror
        }
        rpc_methods = EngineDispatcher.EngineRpcMethods(self, self._engine_id)
        self._rpc_client = WebSocketRpcClient(
            uri=self._rpc_url, methods=rpc_methods, retry_config=retry_config, on_disconnect=[self.on_disconnect]
        )
        try:
            await self._rpc_client.__aenter__()
        except Exception:
            raise ProtocolNetworkException("Error creating websocket connection")

        if self._engine_id is None:
            self._engine_id = await self._register_for_engine_id_async()
            if self._engine_id is None:
                logger.error("Failed to register because Aggregator refused the registration.")
                raise ProtocolNetworkException("Registration failed")


        logger.info("Websocket connected")

    async def on_disconnect(self, channel):
        # Hooking up this handler with an INFO message seems to mostly avoid the reconnect
        # hang issue that sometimes occur when aggregator is down very briefly. Not all the
        # issues though. The offending call is WebSocketRpcClient.close() which logs this message:
        # INFO:fastapi_ws_rpc.RPC_CLIENT:Closing RPC client
        logger.info("on_websocket_disconnect")
        # asyncio.create_task(self.disconnect_async()) # this does not help - it must be one of the
        # calls in WebSocketRpcClient.close()

    async def disconnect_async(self):
        logger.info("Websocket disconnected")
        if self._rpc_client is not None:
            await self._rpc_client.__aexit__()
            self._rpc_client = None

    async def post_async(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Send message via HTTP POST. """
        if not isinstance(message, EM.RegisterEngineMsg):  # Special case for registering
            if self._engine_id is None:
                logger.error("Engine did not have engine_id yet")
                return M.ErrorMessage(message="Engine did not have engine_id yet")
            message.engine_id = self._engine_id

        self.assign_sequence_number(message)

        try:
            message_json = serialize(message)
            _message = json.dumps(message_json)
        except Exception:
            logger.error("Message serialization failed", exc_info=True)
            return M.ErrorMessage(message="Message serialization failed")

        try:
            result = await self._rpc_client.other.dispatch_message_async(message=_message)
        except Exception as ex:
            logger.debug(f"Message not sent: {message.ident}")
            raise ProtocolNetworkException("Websocket rpc call failed with exception") from ex

        try:
            value = deserialize(json.loads(result.result))
            return value
        except Exception:
            logger.error("Message deserialization failed", exc_info=True)
            return M.ErrorMessage(message="WebSocket request succeeded but result deserialization failed")
# =======
#             response = httpx.post(url=self._post_url, json=message_json, headers=engine_headers)
#             # logger.debug(f"Sent message: {message.ident}")
#         except Exception as ex:
#             logger.debug(f"Message not sent: {message.ident}")
#             raise ProtocolNetworkException("Post failed with exception") from ex

#         if response.status_code == 200:
#             response_json = response.json()
#             try:
#                 value = deserialize(response_json)
#                 return value
#             except Exception:
#                 logger.error("Message deserialization failed", exc_info=True)
#                 return M.ErrorMessage(message="Post succeeded but result deserialization failed")
#         else:
#             message_type = type(message)
#             logger.error(f"Non-success http status code: {response.status_code} for input message type: {message_type}")
#             raise ProtocolNetworkException(f"Post failed with non-success http status code: {response.status_code}" +
#                                            " for input message type: {message_type}")
# >>>>>>> main

    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        """ Register handler for given message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    async def dispatch_message_async(self, message: M.MessageBase):
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

    async def _register_for_engine_id_async(self) -> str | None:
        logger.info("Registering for engine id")
        register_engine_msg = EM.RegisterEngineMsg(
            computer_name=socket.gethostname(),
            uod_name=self._uod_name,
            uod_author_name=self._uod_author_name,
            uod_author_email=self._uod_author_email,
            uod_filename=self._uod_filename,
            location=self._location,
            engine_version=__version__)
        register_response = await self.post_async(register_engine_msg)
        if not isinstance(register_response, AM.RegisterEngineReplyMsg) or not register_response.success:
            return None
        return register_response.engine_id

    def assign_sequence_number(self, message: EM.EngineMessage | EM.RegisterEngineMsg):
        # only assign sequence number once (otherwise buffered messages would be reassigned)
        if message.sequence_number == -1:
            self._sequence_number += 1
            message.sequence_number = self._sequence_number
