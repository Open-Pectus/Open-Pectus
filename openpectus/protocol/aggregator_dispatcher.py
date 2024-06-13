import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import logging
from typing import Callable, Awaitable, Any, Literal

from fastapi import APIRouter, FastAPI, Request
from fastapi_websocket_rpc import RpcChannel, WebsocketRPCEndpoint
from fastapi_websocket_rpc.schemas import RpcResponse

from openpectus.lang.exec.timer import OneThreadTimer
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.protocol.dispatch_interface import AGGREGATOR_RPC_WS_PATH, AGGREGATOR_REST_PATH, EngineMessageType
from openpectus.protocol.exceptions import ProtocolException, ProtocolNetworkException
from openpectus.protocol.serialization import deserialize, serialize


logger = logging.getLogger(__name__)


RegisterHandler = Callable[[EM.RegisterEngineMsg], Awaitable[AM.RegisterEngineReplyMsg]]
""" Specific handler for register messages from engine """

AggregatorMessageHandler = Callable[[Any], Awaitable[M.MessageBase]]
""" Handler in aggregator that handles engine messages of a given type """


ConnectionFaultChangeCallback = Callable[[bool, str], None]
""" Callback that is called on changes to engine connection faults.

Arguments:
    bool:   Indicates whether connection is now faulty
    str:    Engine_id of the related engine
"""

@dataclass
class FaultInfo:
    faulty: bool
    last_updated: datetime


class AggregatorDispatcherBase():

    def __init__(self, connection_fault_timeout_seconds: float = 5) -> None:
        self._handlers: dict[type, AggregatorMessageHandler] = {}
        self._register_handler: RegisterHandler | None = None
        self.engine_connection_fault_map: dict[str, FaultInfo] = {}
        """ Map of known engines and their fault state. False for connection ok, True for connection fault. """

        self._connection_fault_change: ConnectionFaultChangeCallback | None = None        
        self.connection_fault_timeout_seconds = connection_fault_timeout_seconds
        self._tick_timer = OneThreadTimer(period_s=0.5, tick=self.tick)
        self._tick_timer.start()

    def tick(self):
        now = datetime.now(timezone.utc)
        for engine_id, fault_info in self.engine_connection_fault_map.items():
            if not fault_info.faulty:
                elapsed = now - fault_info.last_updated
                if elapsed.total_seconds() > self.connection_fault_timeout_seconds:
                    logger.warning(f"Timeout failure for engine: '{engine_id}")
                    logger.warning(f"elapsed: '{elapsed}, last updated: {fault_info.last_updated}")
                    self._set_connection_faulty(engine_id)

    async def rpc_call(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        """ Send message to engine. Handles hardware errors by marking engine connection faulty.

        Returns:
            Result message of the RPC call

        Raises:
            - ProtocolException - a logical protocol error occurred
            - ProtocolNetworkException - a physical network error occurred
        """
        try:
            response = await self.rpc_call_impl(engine_id, message)
            self._set_connection_ok(engine_id)
            return response
        except ProtocolNetworkException:
            self._set_connection_faulty(engine_id)
            return M.ProtocolErrorMessage(protocol_msg="Command failed. Engine connection is down.")
        except Exception:
            raise
        # TODO default handling of other exceptions?

    async def rpc_call_impl(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        """ Send message to engine. Abstract method. """
        raise NotImplementedError()

    def _set_connection_ok(self, engine_id: str):
        now = datetime.now(timezone.utc)
#        logger.warning(f"_set_connection_ok: {now}")
        current = self.engine_connection_fault_map.get(engine_id, None)
        if current is None:
            self.engine_connection_fault_map[engine_id] = FaultInfo(False, now)
        elif current.faulty:
            current.faulty = False
            current.last_updated = now
            # signal connection state change from faulty to ok
            if self._connection_fault_change is not None:
                self._connection_fault_change(False, engine_id)
        else:
            current.last_updated = now

#        logger.warning(f"_set_connection_ok end: {self.engine_connection_fault_map[engine_id]}")

    def _set_connection_faulty(self, engine_id: str):
        now = datetime.now(timezone.utc)
        current = self.engine_connection_fault_map.get(engine_id, None)
        if current is None:
            current = FaultInfo(False, now)
            self.engine_connection_fault_map[engine_id] = current
            # we should not be able to get a faulty connection without already having a
            # a non-faulty one
            logger.warning("_set_connection_faulty was called without a previous fault entry. This should not happen." +
                           f"Engine_id: '{engine_id}'")
            return

        if current.faulty:
            current.last_updated = now
        else:
            self.engine_connection_fault_map[engine_id] = FaultInfo(True, now)
            # signal connection state change from ok to faulty
            if self._connection_fault_change is not None:
                self._connection_fault_change(True, engine_id)

    def _set_connection_none(self, engine_id: str):
        if engine_id in self.engine_connection_fault_map.keys():
            del self.engine_connection_fault_map[engine_id]

    def has_connected_engine_id(self, engine_id: str) -> bool:
        """ Return a value indicating whether the engine_id is known. """
        return engine_id in self.engine_connection_fault_map.keys()

    async def dispatch_post(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        """ Dispatch incoming message to registered handler. """
        if isinstance(message, EM.RegisterEngineMsg):
            if self._register_handler is None:
                return M.ProtocolErrorMessage(protocol_msg="Missing handler for registering engine")
            response = await self._register_handler(message)
            assert isinstance(response, AM.RegisterEngineReplyMsg)
            assert isinstance(response.engine_id, str)
            assert response.engine_id != ""
            if response.success:
                self._set_connection_ok(engine_id=response.engine_id)
            else:
                self._set_connection_none(engine_id=response.engine_id)
            return response

        if message.engine_id == '':
            logger.warning("Failed to handle engine message as its engine_id was the empty string")
            return M.ProtocolErrorMessage(
                protocol_msg="Failed to handle engine message as its engine_id was the empty string")

        self._set_connection_ok(message.engine_id)

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

    def set_post_handler(self, message_type: type[EngineMessageType], handler: AggregatorMessageHandler):
        """ Set handler for message_type. """
        if message_type in self._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._handlers[message_type] = handler

    def set_register_handler(self, handler: RegisterHandler):
        self._register_handler = handler

    def set_connection_fault_callback(self, callback: ConnectionFaultChangeCallback):
        self._connection_fault_change = callback


class AggregatorDispatcher(AggregatorDispatcherBase):
    """
    Aggregator dispatcher for the Aggregator-Engine Protocol using REST + WebSocket RPC.
    Allows receiving message via HTTP POST and sending messages via JSON-RPC.
    """

    def __init__(self) -> None:
        super().__init__()

        self.router = APIRouter(tags=["aggregator"])
        self._engine_id_channel_map: dict[str, RpcChannel] = {}
        # WebsockeRPCEndpoint has wrong types for its on_connect and on_disconnect.
        # It should be List[Callable[[RpcChannel], Awaitable[Any]]] instead of List[Coroutine]
        # See https://github.com/permitio/fastapi_websocket_rpc/issues/30
        self.endpoint = WebsocketRPCEndpoint(
            on_connect=[self.on_client_connect],  # type: ignore
            on_disconnect=[self.on_client_disconnect])  # type: ignore
        self.endpoint.register_route(self.router, path=AGGREGATOR_RPC_WS_PATH)
        self._register_post_route(self.router)

    async def on_delayed_client_connect(self, channel: RpcChannel):
        """ We 'delay' our on_connect callback because the WebsocketRPCEndpoint calls on_connect callbacks before it starts
        listening to responses to rpc calls. When we use create_task(), in on_client_connect() below, to call this method,
        we ensure that WebsocketRPCEndpoint starts listening to responses before we call get_engine_id_async() over rpc.
        """
        try:
            response = await channel.other.get_engine_id_async()
        except Exception as ex:
            raise ProtocolNetworkException("Failed to invoke 'channel.other.get_engine_id_async()'") from ex

        try:
            assert isinstance(response, RpcResponse)
            engine_id = response.result
            assert isinstance(engine_id, str | None)
            if engine_id is None:
                logger.error("Engine tried connecting with no engine_id available. Closing connection.")
                try:
                    return await channel.close()
                except Exception as ex:
                    raise ProtocolNetworkException("Failed to invoke channel.close()") from ex
            if engine_id in self._engine_id_channel_map:
                logger.error("Engine tried connecting with engine_id that is already connected. Closing connection.")
                try:
                    return await channel.close()
                except Exception as ex:
                    raise ProtocolNetworkException("Failed to invoke channel.close()") from ex
            logger.info(f"Engine '{engine_id}' connected")
            self._engine_id_channel_map[engine_id] = channel
            self._set_connection_ok(engine_id)
        except Exception:
            logger.error("on_delayed_client_connect failed with exception", exc_info=True)
            return await channel.close()

    async def on_client_connect(self, channel: RpcChannel):
        asyncio.create_task(self.on_delayed_client_connect(channel))

    async def on_client_disconnect(self, channel: RpcChannel):
        engine_id: str | None = None
        for key, value in self._engine_id_channel_map.items():
            if value == channel:
                engine_id = key
                break
        if engine_id is not None:
            logger.info(f"Engine '{engine_id}' disconnected")
            del self._engine_id_channel_map[engine_id]
            self._set_connection_none(engine_id)
        else:
            logger.error("Unknown engine disconnected")

    async def rpc_call_impl(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        if engine_id not in self._engine_id_channel_map.keys():
            raise ProtocolException("Unknown engine: " + engine_id)

        channel = self._engine_id_channel_map[engine_id]
        message_json = serialize(message)

        try:
            response = await channel.other.dispatch_message_async(message_json=message_json)
            return response
        except Exception as ex:
            raise ProtocolNetworkException("Failed to invoke 'channel.other.dispatch_message_async()'") from ex

    def _register_post_route(self, router: APIRouter | FastAPI):
        @router.post(AGGREGATOR_REST_PATH)
        async def post(request: Request):
            request_json = await request.json()
            try:
                message = deserialize(request_json)
            except Exception:
                logger.error(f"Message deserialization failed, json:\n{request_json}\n", exc_info=True)
                raise ProtocolException("Deserialization error")

            if not isinstance(message, EM.RegisterEngineMsg) and not isinstance(message, EM.EngineMessage):
                raise ValueError(f"Invalid type of message sent from Engine: {type(message).__name__}")
            response_message = await self.dispatch_post(message)

            try:
                message_json = serialize(response_message)
            except Exception:
                logger.error(f"Message serialization failed, message type: {type(response_message).__name__}")
                raise ProtocolException("Serialization error")

            return message_json
