from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import Any, Awaitable, Callable, Dict, List
from fastapi_websocket_pubsub.event_notifier import EventNotifier
from pydantic import BaseModel
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_rpc import RpcChannel
from fastapi_websocket_rpc.schemas import RpcResponse
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
import logging

from openpectus.protocol.exceptions import ProtocolException
from openpectus.protocol.messages import (
    ControlStateMsg,
    RunLogMsg,
    UodInfoMsg,
    deserialize_msg,
    deserialize_msg_from_json,
    serialize_msg,
    serialize_msg_to_json,
    ProtocolErrorMessage,
    MessageBase,
    SuccessMessage,
    ErrorMessage,
    RegisterEngineMsg,
    TagsUpdatedMsg,
    MethodMsg
)

logger = logging.getLogger(__name__)

ServerMessageHandler = Callable[[str, MessageBase], Awaitable[MessageBase]]
""" Represents the type of callbacks that handle incoming messages from clients """


class RpcServerHandler(RpcEventServerMethods):
    """Represents the aggregator server's RPC interface"""

    def __init__(self, event_notifier: EventNotifier, rpc_channel_get_remote_id: bool = False):
        super().__init__(event_notifier, rpc_channel_get_remote_id)
        self._message_handler: ServerMessageHandler | None = None

    def set_message_handler(self, handler: ServerMessageHandler):
        self._message_handler = handler

    async def on_client_message(self, msg_type: str, msg_dict: Dict[str, Any]):
        """Implements the server proxy's method. Is invoked by a client by its server proxy."""
        logger.debug(f"on_client_message was called with msg_type: {msg_type}, msg_dict: {msg_dict}")
        assert isinstance(self.channel, RpcChannel)
        if self._message_handler is not None:
            try:
                msg = deserialize_msg(msg_type, msg_dict)
            except Exception:
                logger.error("Deserialization failed", exc_info=True)
                return ProtocolErrorMessage(protocol_mgs="Deserialization failed")
            try:
                result = await self._message_handler(self.channel.id, msg)
                return serialize_msg_to_json(result)
            except Exception:
                logger.error("Send failed", exc_info=True)
                return ProtocolErrorMessage(protocol_mgs="Send _message_handler failed")

        logger.error("No _message_handler registered", exc_info=True)
        return ProtocolErrorMessage(protocol_mgs="Internal error")


class ChannelStatusEnum(StrEnum):
    Unknown = auto()
    Connected = auto()
    Registered = auto()
    Disconnected = auto()


@dataclass
class ChannelInfo:
    client_id: str | None
    engine_name: str
    uod_name: str
    channel: RpcChannel
    status: ChannelStatusEnum = ChannelStatusEnum.Unknown


TagValueType = int | float | str | None
""" Represents the possible types of a tag value"""


class TagInfo(BaseModel):
    name: str
    value: TagValueType
    value_unit: str | None
    updated: datetime


class TagsInfo(BaseModel):
    map: Dict[str, TagInfo]

    def get(self, tag_name: str):
        return self.map.get(tag_name)

    def upsert(self, name: str, value: TagValueType, unit: str | None):
        current = self.map.get(name)
        now = datetime.now()
        if current is None:
            current = TagInfo(name=name, value=value, value_unit=unit, updated=now)
            self.map[name] = current
        else:
            if current.value != value:
                current.value = value
                current.updated = now

            if current.value_unit != unit:
                logger.warning(f"Tag '{name}' changed unit from '{current.value_unit}' to '{unit}'. This is unexpected")


TagsInfo.update_forward_refs()


class ReadingCommand(BaseModel):
    name: str
    command: str


class ReadingDef(BaseModel):
    label: str
    tag_name: str
    valid_value_units: List[str] | None
    commands: List[ReadingCommand]


ReadingDef.update_forward_refs()


class ClientData(BaseModel):
    client_id: str
    readings: List[ReadingDef] = []
    tags_info: TagsInfo = TagsInfo(map={})
    runlog: RunLogMsg = RunLogMsg.default()
    control_state: ControlStateMsg = ControlStateMsg.default()
    method: MethodMsg = MethodMsg.default()


ClientData.update_forward_refs()


# class AggregatorApi():
#     """ Represents the Aggregator Rest API service interface """

#     def get_method(self, client_id: str) -> MethodMsg | None:
#         raise NotImplementedError()

#     async def set_method(self, client_id: str, method: MethodMsg) -> RpcStatusMessage:
#         raise NotImplementedError()


# class AggregatorApiAdapter(AggregatorApi):
#     def __init__(self, agg: Aggregator) -> None:
#         super().__init__()
#         self.agg = agg

#     def get_method(self, client_id: str) -> MethodMsg | None:
#         raise NotImplementedError()

#     async def set_method(self, client_id: str, method: MethodMsg) -> RpcStatusMessage:
#         raise NotImplementedError()


class Aggregator():
    def __init__(self) -> None:
        logger.debug("Server init")
        self.channel_map: Dict[str, ChannelInfo] = {}
        """ channel data, indexed by channel_id"""
        self.client_data_map: Dict[str, ClientData] = {}
        """ all client data except channels, indexed by client_id"""
        self.endpoint: PubSubEndpoint | None = None

    def set_endpoint(self, endpoint: PubSubEndpoint):
        self.endpoint = endpoint
        assert isinstance(endpoint.methods, RpcServerHandler)
        endpoint.methods.set_message_handler(self.handle_message)

    async def on_connect(self, channel: RpcChannel):
        self.channel_map[channel.id] = ChannelInfo(
            client_id=None,
            engine_name="(Unregistered)",
            uod_name="(Unregistered)",
            channel=channel,
            status=ChannelStatusEnum.Connected
        )
        logger.debug("Client connected on channel: " + channel.id)

    async def handle_message(self, channel_id: str, msg: MessageBase) -> MessageBase:
        """ Handle message from Engine by invoking the designated handler method """
        logger.debug(f"handle_message type {type(msg).__name__}: {msg.__repr__()}")
        handler_name = "handle_" + type(msg).__name__
        handler = getattr(self, handler_name, None)
        if handler is None:
            err = f"Handler method name {handler_name} is not defined"
            logger.error(err)
            return ProtocolErrorMessage(protocol_mgs=err)
        else:
            try:
                result = await handler(channel_id, msg)
            except Exception:
                err = f"Handler method '{handler_name}' raised exception"
                logger.error(err, exc_info=True)
                return ErrorMessage(exception_message=err)
            if not isinstance(result, MessageBase):
                err = f"Handler method returned an invalid result type '{type(result).__name__}', should be MessageBase"
                logger.error(err)
                return ProtocolErrorMessage(protocol_mgs=err)
            return result

    @staticmethod
    def create_client_id(register_engine_msg: RegisterEngineMsg):
        """ Defines the generation of the client_id that is uniquely assigned to each engine client.

        TODO: Considerations:
            - engine name should be machine name
            - uod hash should probably be included

        Implications of the registration process
        - historical data; we should not corrupt historical data by accidentially reusing client_id
        - number of cards shown; we should not show many irrelevant cards in frontend of superseeded client_ids
        """
        return register_engine_msg.computer_name + "_" + register_engine_msg.uod_name

    def get_registered_client_data_or_error(self, channel_id: str) -> ClientData | ErrorMessage:
        ci = self.get_channel(channel_id)
        if ci is None:
            logger.error(f"Channel '{channel_id}' not found")
            return ErrorMessage(message="Client unknown")
        if ci.client_id is None or ci.status != ChannelStatusEnum.Registered:
            logger.error(f"Channel '{channel_id}' has invalid status {ci.status} for this operation")
            return ErrorMessage(message="Client not registered")
        client_data = self.client_data_map.get(ci.client_id)
        if client_data is None:
            return ErrorMessage(message="Client data not initialized")
        return client_data

    async def handle_RegisterEngineMsg(self, channel_id, register_engine_msg: RegisterEngineMsg) \
            -> SuccessMessage | ErrorMessage:

        """ Registers engine """
        client_id = Aggregator.create_client_id(register_engine_msg)
        if channel_id not in self.channel_map.keys():
            logger.error(
                f"Registration failed for client_id {client_id} and channel_id {channel_id}. Channel not found"
            )
            return ErrorMessage(message="Registration failed")

        channel_info = self.channel_map[channel_id]
        if channel_info.client_id is not None and channel_info.client_id != client_id:
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Channel already in use by client_id {channel_info.client_id}"""
            )
            return ErrorMessage(message="Registration failed")

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - client_id reused with "same uod" should take over session, else fail as misconfigured client
        # - add machine name + uod secret
        existing_registrations = [x for x in self.channel_map.values() if x.client_id == client_id]
        if (
                len(existing_registrations) > 0 and
                any(existing_registration.status != ChannelStatusEnum.Disconnected for
                    existing_registration in existing_registrations)
        ):
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Client has other channel"""
            )
            return ErrorMessage(message="Registration failed")

        channel_info.client_id = client_id
        channel_info.engine_name = register_engine_msg.computer_name
        channel_info.uod_name = register_engine_msg.uod_name
        channel_info.status = ChannelStatusEnum.Registered
        logger.debug(f"Registration successful of client {client_id} on channel {channel_id}")

        # initialize client data
        if client_id not in self.client_data_map.keys():
            self.client_data_map[client_id] = ClientData(client_id=client_id)

        return SuccessMessage()

    async def handle_UodInfoMsg(self, channel_id: str, msg: UodInfoMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        logger.debug(f"Got UodInfo from client: {str(msg)}")
        client_data.readings = []
        for r in msg.readings:
            rd = ReadingDef(
                label=r.label,
                tag_name=r.tag_name,
                valid_value_units=r.valid_value_units,
                commands=[ReadingCommand(name=c.name, command=c.command) for c in r.commands]
            )
            client_data.readings.append(rd)

        return SuccessMessage()

    async def handle_TagsUpdatedMsg(self, channel_id, msg: TagsUpdatedMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        logger.debug(f"Got tags update from client: {str(msg)}")
        for ti in msg.tags:
            client_data.tags_info.upsert(ti.name, ti.value, ti.value_unit)
        return SuccessMessage()

    async def handle_RunLogMsg(self, channel_id, msg: RunLogMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        client_data.runlog = msg
        return SuccessMessage()

    async def handle_ControlStateMsg(self, channel_id, msg: ControlStateMsg) -> SuccessMessage | ErrorMessage:
        client_data = self.get_registered_client_data_or_error(channel_id)
        if isinstance(client_data, ErrorMessage):
            return client_data

        client_data.control_state = msg
        return SuccessMessage()

    async def on_disconnect(self, channel: RpcChannel):  # registered as handler on RpcEndpoint
        logger.debug("disconnected channel: " + channel.id)
        if channel.id in self.channel_map.keys():
            self.channel_map[channel.id].status = ChannelStatusEnum.Disconnected

    def get_channel(self, channel_id: str) -> ChannelInfo | None:
        return self.channel_map.get(channel_id)

    def get_client_channel(self, client_id: str) -> ChannelInfo | None:
        for ci in self.channel_map.values():
            if ci.client_id == client_id:
                return ci
        return None

    async def send_to_client(self, client_id: str, msg: MessageBase) -> MessageBase:
        logger.debug("send_to_client begin")
        ci = self.get_client_channel(client_id)
        if ci is None:
            logger.warning(f"Cannot send message to unknown client {client_id}")
            return ErrorMessage(message="Client unknown")
        elif ci.status != ChannelStatusEnum.Registered:
            logger.warning(f"Cannot send message to unregistered client {client_id}")
            return ErrorMessage(message="Client unregistered")

        try:
            msg_type, msg_dict = serialize_msg(msg)
            logger.debug(f"Sending message of type {msg_type} to client")
            resp = await ci.channel.other.on_server_message(msg_type=msg_type, msg_dict=msg_dict)
            logger.debug(f"Send success. Got response of type {type(resp).__name__} with value {str(resp)}")
            if not isinstance(resp, RpcResponse):
                err = f"Result from client proxy should be of type RpcResponse, not '{type(resp).__name__}'"
                raise ProtocolException(err)
            if not isinstance(resp.result, str):
                err = f"RpcResponse result property should be of type str, not '{type(resp.result).__name__}'"
                raise ProtocolException(err)
            try:
                result = deserialize_msg_from_json(resp.result)
            except Exception as ex:
                raise ProtocolException("Deserialization failed: " + str(ex))
            return result
        except ProtocolException:
            err = "Protocol server error"
            logger.error(err, exc_info=True)
            return ProtocolErrorMessage(protocol_mgs=err)
        except Exception:
            err = "Unhandled server error"
            logger.error(err, exc_info=True)
            return ErrorMessage(exception_message=err)

    # AggregatorApi interface implementation
    def get_method(self, client_id: str) -> MethodMsg | None:
        client_data = self.client_data_map.get(client_id)
        if client_data is None:
            return None

        logger.info(f"Returned local method with {len(client_data.method.lines)} lines")
        return client_data.method

    async def set_method(self, client_id: str, method: MethodMsg) -> bool:
        try:
            response = await self.send_to_client(client_id=client_id, msg=method)
            if isinstance(response, ErrorMessage):
                logger.error(f"Failed to set method. Engine response: {response.message}")
                return False
        except Exception:
            logger.error("Failed to set method", exc_info=True)
            return False

        # update local method state
        client_data = self.client_data_map.get(client_id)
        if client_data is not None:
            client_data.method = method

        return True


_server: Aggregator | None = None


# singleton instance


def _get_aggregator() -> Aggregator:
    if _server is None:
        raise Exception("DI configuration error. Aggregator has not been initialized")
    return _server


def _create_aggregator(router) -> Aggregator:
    global _server
    if _server is not None:
        return _server
    else:
        _server = Aggregator()
        print("GLOBAL: Creating aggregator server")

    endpoint = PubSubEndpoint(  # cannot mutate these handlers later
        on_connect=[_server.on_connect],  # type: ignore
        on_disconnect=[_server.on_disconnect],  # type: ignore
        methods_class=RpcServerHandler,
    )
    _server.set_endpoint(endpoint)
    endpoint.register_route(router, path="/engine-pubsub")
    return _server
