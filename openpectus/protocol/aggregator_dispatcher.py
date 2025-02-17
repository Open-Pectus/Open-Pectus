import asyncio
import json
import logging
from typing import Callable, Awaitable, Any

from fastapi import APIRouter, FastAPI, Request
from fastapi_websocket_rpc import RpcMethodsBase, RpcChannel, WebsocketRPCEndpoint
from fastapi_websocket_rpc.schemas import RpcResponse

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.protocol.dispatch_interface import AGGREGATOR_REST_PATH, AGGREGATOR_RPC_WS_PATH, EngineMessageType
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

WEBSOCKET_RPC_TIMEOUT_SECS: float | None = 2.0


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
        self._on_client_connect_tasks = set()
        # WebsockeRPCEndpoint has wrong types for its on_connect and on_disconnect.
        # It should be List[Callable[[RpcChannel], Awaitable[Any]]] instead of List[Coroutine]
        # See https://github.com/permitio/fastapi_websocket_rpc/issues/30

        class AggregatorRpcMethods(RpcMethodsBase):
            def __init__(self, dispatcher: AggregatorDispatcher):
                super().__init__()
                self.disp = dispatcher

            # Why does this work with return type?? In engine_dispatcher
            # it fails if we do this. At least we know how to fix it, should it should fail.
            async def dispatch_message_async(self, message_json: dict[str, Any]) -> str:
                """ Handle RCP call from engine. Dispatch message to registered handler. """
                try:
                    message = deserialize(message_json)
                    assert isinstance(message, EM.EngineMessage)  # only allow EngineMessage, Register is via rest
                except Exception:
                    logger.error("Dispatch failed. Message deserialization failed.", exc_info=True)
                    return json.dumps(serialize(M.ProtocolErrorMessage(protocol_msg="Message deserialization failed")))

                result = await self.disp.dispatch_message(message)
                return json.dumps(serialize(result))

        self.endpoint = WebsocketRPCEndpoint(AggregatorRpcMethods(self),
                                             on_connect=[self.on_client_connect],  # type: ignore
                                             on_disconnect=[self.on_client_disconnect])  # type: ignore
        self.endpoint.register_route(self.router, path=AGGREGATOR_RPC_WS_PATH)
        self._register_post_route(self.router)

    def __str__(self):
        engines = [str(engine_id) for engine_id in self._engine_id_channel_map.keys()]
        return f'{self.__class__.__name__}(connected_engines={engines})'

    def _register_post_route(self, router: APIRouter | FastAPI):
        """
        Set up post route to handle RegisterEngineMsg which must be handled before websocket can be established
        """
        @router.post(AGGREGATOR_REST_PATH, response_model_exclude_none=True)
        async def post(request: Request):
            request_json = await request.json()
            try:
                message = deserialize(request_json)
                assert isinstance(message, EM.RegisterEngineMsg), "type must be RegisterEngineMsg"
            except Exception:
                logger.error(f"Message deserialization failed, json:\n{request_json}\n", exc_info=True)
                raise ProtocolException("Deserialization error")

            if self._register_handler is None:
                logger.error("Missing handler for registering engine")
                return M.ProtocolErrorMessage(protocol_msg="Missing handler for registering engine")

            response_message = await self._register_handler(message)
            if response_message is None:
                logger.error(f"Invalid response (None) returned from handler for message type {type(message).__name__}")
                response_message = M.ProtocolErrorMessage(protocol_msg="Invalid response from handler")

            try:
                message_json = serialize(response_message)
            except Exception:
                logger.error(f"Message serialization failed, message type: {type(response_message).__name__}")
                raise ProtocolException("Serialization error")

            return message_json

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

            logger.info(f"Engine connected: '{engine_id}'")
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
        channel.default_response_timeout = WEBSOCKET_RPC_TIMEOUT_SECS
        task = asyncio.create_task(self._on_delayed_client_connect(channel))
        self._on_client_connect_tasks.add(task)
        task.add_done_callback(self._on_client_connect_tasks.discard)

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
        logger.info(f"Invoke rpc, engine: {engine_id}, msg-type: {type(message).__name__}")
        logger.debug(f"{message}")
        if engine_id not in self._engine_id_channel_map.keys():
            logger.error(f"Cannot invoke rpc call to unknown engine: {engine_id}")
            return M.ErrorMessage(message=f"Cannot invoke rpc call to unknown engine: {engine_id}")

        channel = self._engine_id_channel_map[engine_id]

        try:
            message_json = serialize(message)
        except Exception:
            msg = f"Failed to seralize message: {type(message).__name__}"
            logger.error(msg, exc_info=True)
            return M.ErrorMessage(message=msg)

        try:
            response = await channel.other.dispatch_message_async(message_json=message_json)
            assert isinstance(response, RpcResponse)
            assert isinstance(response.result, str)
        except Exception:
            logger.error("Error during rpc call", exc_info=True)
            await channel.close()
            # this causes connection to fail and then reconnect
            raise ProtocolException("Error in rpc call")

        try:
            result_json = json.loads(response.result)
            result_message = deserialize(result_json)
            return result_message
        except Exception:
            logger.error("Failed to deserialize rpc result", exc_info=True)
            return M.ErrorMessage(message="Failed to deserialize rpc result")

    async def dispatch_message(self, message: EM.EngineMessage) -> M.MessageBase:
        """ Dispatch incoming message to registered handler. """
        logger.debug(f"Incoming message: {message.ident}")

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

    def set_message_handler(self, message_type: type[EngineMessageType], handler: AggregatorMessageHandler):
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
