from __future__ import annotations

import logging
import socket
from typing import Callable, Any, Awaitable
import json
import ssl
import platform

from fastapi_websocket_rpc import RpcMethodsBase, WebSocketRpcClient
from fastapi_websocket_rpc.rpc_methods import RpcResponse
from fastapi_websocket_rpc.rpc_channel import RpcChannelClosedException
from websockets.exceptions import ConnectionClosedError
import httpx
import tenacity

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolException, ProtocolNetworkException
import openpectus.protocol.messages as M
from openpectus import __version__, __name__ as client_name
from openpectus.protocol.dispatch_interface import (
    AGGREGATOR_REST_PATH, AGGREGATOR_RPC_WS_PATH, AGGREGATOR_HEALTH_PATH, AGGREGATOR_AUTH_CONFIG_PATH
)
from openpectus.protocol.serialization import serialize, deserialize
from openpectus.aggregator.routers.dto import AuthConfig

logger = logging.getLogger(__name__)

EngineMessageHandler = Callable[[AM.AggregatorMessage], Awaitable[M.MessageBase]]
""" Handler in engine that handles aggregator messages of a given type """

engine_headers = {"User-Agent": f"{client_name}/{__version__}"}

if platform.system() == "Windows":
    # Use system certificates on Windows instead
    # of Anaconda provided certificates.
    ssl_context = ssl.create_default_context()
    ssl_context.load_default_certs()
    # Disable strict mode for ZScaler to work with Python > 3.12
    # See https://community.zscaler.com/s/question/0D54u0000AfJDtECQW/
    ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT
else:
    # SSL library method load_default_certs only does
    # something useful on Windows. On other systems
    # the Anaconda certificate bundle will have to do.
    ssl_context = httpx.create_ssl_context()


class EngineDispatcher():
    """
    Engine dispatcher for the Aggregator-Engine Protocol.
    Allows sending messages via HTTP POST and JSON-RPC.
    """

    class EngineRpcMethods(RpcMethodsBase):
        def __init__(self, dispatcher: EngineDispatcher, engine_id: str):
            super().__init__()
            self.disp = dispatcher
            self.engine_id = engine_id

        # Note: this method cannot have a return type specified - this causes a RPC Reader task failed
        # which seems like a bug in pydantic
        # It should return a serialized M.MessageBase message as type str
        async def dispatch_message_async(self, message_json: dict[str, Any]):  # -> str:
            """ Handle RPC call from aggregator. Dispatch message to registered handler. """
            try:
                message = deserialize(message_json)
                assert isinstance(message, M.MessageBase)
            except Exception:
                msg = "Dispatch failed. Message deserialization failed."
                logger.error(msg, exc_info=True)
                return json.dumps(serialize(M.ErrorMessage(message=msg)))

            result = await self.disp.dispatch_message_async(message)
            logger.debug(f"Return type of dispatched message {type(message).__name__} was: {type(result).__name__}")
            return json.dumps(serialize(result))

        async def get_engine_id_async(self):
            # Note: Must be declared async to be usable by RPC
            return self.engine_id

    def __init__(self, aggregator_host: str, secure: bool, uod_options: dict[str, str], secret: str = "") -> None:
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
        self._secret = secret

        http_scheme = "https" if secure else "http"
        ws_scheme = "wss" if secure else "ws"
        self._ssl_context: ssl.SSLContext | bool = ssl_context if secure else False
        self._post_url = f"{http_scheme}://{aggregator_host}{AGGREGATOR_REST_PATH}"
        self._health_url = f"{http_scheme}://{self._aggregator_host}{AGGREGATOR_HEALTH_PATH}"
        self._rpc_url = f"{ws_scheme}://{self._aggregator_host}{AGGREGATOR_RPC_WS_PATH}"
        self._auth_config_url = f"{http_scheme}://{self._aggregator_host}{AGGREGATOR_AUTH_CONFIG_PATH}"
        logger.info(f"Connecting to aggregator using urls:\n{self._post_url}\n{self._rpc_url}")

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(_rpc_url="{self._rpc_url}", _engine_id="{self._engine_id}", ' +
                f'_sequence_number={self._sequence_number})')

    def check_aggregator_alive(self) -> bool:
        try:
            resp = httpx.get(self._health_url, headers=engine_headers, verify=self._ssl_context)
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

    def is_aggregator_authentication_enabled(self) -> bool:
        response = httpx.get(self._auth_config_url, headers=engine_headers, verify=self._ssl_context)
        auth_config = AuthConfig(**response.json())
        return auth_config.use_auth

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

        # invoke registration rest call that provides engine_id
        if self._engine_id is None:
            self._engine_id = await self._register_for_engine_id_async()
            if self._engine_id is None:
                logger.error("Failed to register because Aggregator refused the registration.")
                raise ProtocolNetworkException("Registration failed")

        rpc_methods = EngineDispatcher.EngineRpcMethods(self, self._engine_id)
        self._rpc_client = WebSocketRpcClient(
            uri=self._rpc_url,
            methods=rpc_methods,
            retry_config=retry_config,
            on_disconnect=[self.on_disconnect],
            user_agent_header=engine_headers,
            ssl=self._ssl_context if self._ssl_context else None,
        )
        try:
            await self._rpc_client.__aenter__()
        except Exception:
            raise ProtocolNetworkException("Error creating websocket connection")

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

    async def send_registration_msg_async(self, message: EM.RegisterEngineMsg) -> M.MessageBase:
        """ Send message registration message via post"""
        try:
            message_json = serialize(message)
        except Exception:
            logger.error("Message serialization failed", exc_info=True)
            return M.ErrorMessage(message="Message serialization failed")

        try:
            async with httpx.AsyncClient(verify=self._ssl_context) as client:
                response = await client.post(url=self._post_url, json=message_json, headers=engine_headers)
        except Exception as ex:
            logger.error(f"Post failed with  exception type {type(ex).__name__}")  # skip details,  exc_info=True)
            raise ProtocolNetworkException("Post failed with exception")

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
            raise ProtocolNetworkException(f"Post failed with non-success http status code: {response.status_code}" +
                                           " for input message type: {message_type}")

    async def send_async(self, message: EM.EngineMessage) -> M.MessageBase:
        """ Send message via websocket. """
        assert self._rpc_client is not None, "Cannot send when rpc_client is None"

        if self._engine_id is None:
            # this should never occur since engine_id is required to set up the websocket connection
            raise ProtocolException("Engine did not have engine_id yet")

        message.engine_id = self._engine_id
        self.assign_sequence_number(message)

        try:
            message_json = serialize(message)
        except Exception:
            logger.error("Message serialization failed", exc_info=True)
            return M.ErrorMessage(message="Message serialization failed")

        try:
            response = await self._rpc_client.other.dispatch_message_async(message_json=message_json)
            assert isinstance(response, RpcResponse)
            logger.debug(f"Sent message: {message.ident}")
        except (ConnectionClosedError, RpcChannelClosedException):
            raise ProtocolNetworkException("Connection closed")
        except Exception:
            logger.error(f"Unkown error sending message: {message.ident}", exc_info=True)
            return M.ErrorMessage(message=f"Unkown error sending message: {message.ident}")

        value_str = response.result
        try:
            assert isinstance(value_str, str)
            value = deserialize(json.loads(value_str))
            assert isinstance(value, M.MessageBase), f"Expected type M.MessageBase, not {type(value).__name__}"
            return value
        except Exception:
            err = f"Error deserializing response for message: {message.ident}"
            logger.error(err, exc_info=True)
            return M.ErrorMessage(message=err)


    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        """ Register handler for given message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    async def dispatch_message_async(self, message: M.MessageBase) -> M.MessageBase:
        """ Dispatch incoming message to registered handler. """
        message_type = type(message)
        try:
            result = await self._handlers[message_type](message)
            assert isinstance(result, M.MessageBase)
            return result
        except KeyError:
            msg = f"Dispatch failed for message type: {message_type}. No handler registered."
            logger.warning(msg)
            return M.ErrorMessage(message=msg)
        except Exception:
            msg = f"Dispatch failed for message type: {message_type}. A handler was registered, but failed somehow."
            logger.warning(msg, exc_info=True)
            return M.ErrorMessage(message=msg)

    async def _register_for_engine_id_async(self) -> str | None:
        logger.info("Registering for engine id")
        register_engine_msg = EM.RegisterEngineMsg(
            computer_name=socket.gethostname(),
            uod_name=self._uod_name,
            uod_author_name=self._uod_author_name,
            uod_author_email=self._uod_author_email,
            uod_filename=self._uod_filename,
            location=self._location,
            engine_version=__version__,
            secret=self._secret)
        register_response = await self.send_registration_msg_async(register_engine_msg)
        if not isinstance(register_response, AM.RegisterEngineReplyMsg) or not register_response.success:
            logger.warning("Aggregator refused registration")
            if isinstance(register_response, AM.RegisterEngineReplyMsg) and not register_response.secret_match:
                logger.error("Secret supplied by engine does not match aggregator secret")
            return None
        logger.debug(f"Aggregator accepted registration and issued engine_id: {register_response.engine_id}")
        return register_response.engine_id

    def assign_sequence_number(self, message: EM.EngineMessage | EM.RegisterEngineMsg):
        # only assign sequence number once (otherwise buffered messages would be reassigned)
        if message.sequence_number == -1:
            self._sequence_number += 1
            message.sequence_number = self._sequence_number
