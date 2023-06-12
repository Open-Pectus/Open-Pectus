import asyncio
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Awaitable, Callable, Dict
from fastapi_websocket_pubsub.event_notifier import EventNotifier
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_rpc import RpcChannel
from fastapi_websocket_rpc.schemas import RpcResponse
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from protocol.exceptions import ProtocolException
from protocol.messages import (
    deserialize_msg,
    deserialize_msg_from_json,
    serialize_msg,
    serialize_msg_to_json,
    ProtocolErrorMessage,
    MessageBase,
    SuccessMessage,
    ErrorMessage,
    RegisterEngineMsg,
    InvokeCommandMsg,
)
import logging


app = FastAPI()
router = APIRouter()


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PORT = 9800


@app.get("/health")
def health():
    return "healthy"


@app.get("/debug")
async def show_debug_info():
    print("Server channel map (channel, ch. closed, client_id, status):")
    for x in server.channel_map.values():
        print(f"{x.channel.id}\t{x.channel.isClosed}\t{x.client_id}\t{x.status}")


class RpcServerHandler(RpcEventServerMethods):
    """Represents the server's RPC interface"""

    def __init__(
        self, event_notifier: EventNotifier, rpc_channel_get_remote_id: bool = False
    ):
        super().__init__(event_notifier, rpc_channel_get_remote_id)
        # self._callback: Callable[[str, str], bool] | None = None
        self._message_handler: Callable[
            [str, MessageBase], Awaitable[MessageBase]
        ] | None = None
        logger.debug("RpcServerHandler init")

    # def set_callback(self, callback: Callable[[str, str], bool]):
    #     self._callback = callback

    def set_message_handler(
        self, handler: Callable[[str, MessageBase], Awaitable[MessageBase]]
    ):
        self._message_handler = handler

    async def on_client_message(self, msg_type: str, msg_dict: dict):
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
    channel: RpcChannel
    status: ChannelStatusEnum = ChannelStatusEnum.Unknown


class Server:
    def __init__(self) -> None:
        self.channel_map: Dict[str, ChannelInfo] = {}
        logger.debug("Server init")

    def set_rpc_handler(self, handler: RpcServerHandler):
        handler.set_message_handler(self.handle_message)

    async def on_connect(
        self, channel: RpcChannel
    ):  # registered as handler on RpcEndpoint
        self.channel_map[channel.id] = ChannelInfo(
            client_id=None, channel=channel, status=ChannelStatusEnum.Connected
        )
        logger.debug("Client connected on channel: " + channel.id)

    async def handle_message(self, channel_id: str, msg: MessageBase) -> MessageBase:
        logger.debug(f"handle_message type {type(msg).__name__}: {msg.__repr__()}")
        handler_name = "handle_" + type(msg).__name__
        handler = getattr(self, handler_name, None)
        if handler is None:
            err = f"Handler name {handler_name} is not defined"
            logger.error(err)
            return ProtocolErrorMessage(protocol_mgs=err)
        else:
            try:
                result = await handler(channel_id, msg)
            except Exception:
                err = f"Handler '{handler_name}' raised exception"
                logger.error(err, exc_info=True)
                return ErrorMessage(exception_message=err)
            if not isinstance(result, MessageBase):
                err = f"Handler returned an invalid result type '{type(result).__name__}', should be MessageBase"
                logger.error(err)
                return ProtocolErrorMessage(protocol_mgs=err)
            return result

    @staticmethod
    def get_client_id(msg: RegisterEngineMsg):
        return msg.engine_name + "_" + msg.uod_name

    async def handle_RegisterEngineMsg(
        self, channel_id, msg: RegisterEngineMsg
    ) -> SuccessMessage | ErrorMessage:
        logger.debug("handle_RegisterEngineMsg")

        client_id = Server.get_client_id(msg)
        if channel_id not in self.channel_map.keys():
            logger.error(
                f"Registration failed for client_id {client_id} and channel_id {channel_id}. Channel not found"
            )
            return ErrorMessage(message="Registration failed")
        channelInfo = self.channel_map[channel_id]
        if channelInfo.client_id is not None:
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Channel already in use by client_id {channelInfo.client_id}"""
            )
            # TODO if channelInfo.client_id == client_id we can make this idempotent and not fail
            return ErrorMessage(message="Registration failed")

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - client_id reused with "same uod" should take over session, else fail as misconfigured client
        registrations = list(
            [x for x in self.channel_map.values() if x.client_id == client_id]
        )
        if (
            len(registrations) > 0
            and registrations[0].status != ChannelStatusEnum.Disconnected
        ):
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Client has other channel"""
            )
            return ErrorMessage(message="Registration failed")

        # we're not being async here...
        # if False:
        #     await False

        channelInfo.client_id = client_id
        channelInfo.status = ChannelStatusEnum.Registered
        logger.debug(
            f"Registration successful of client {client_id} on channel {channel_id}"
        )
        return SuccessMessage()

    async def handle_TagsUpdatedMsg(
        self, channel_id, msg: RegisterEngineMsg
    ) -> SuccessMessage | ErrorMessage:
        if channel_id not in self.channel_map.keys():
            logger.error(f"Channel '{channel_id}' not found")
            return ErrorMessage(message="Registration error")

        logger.info(f"Got update from client: {str(msg)}")
        # TODO update internal state

        return SuccessMessage()

    async def on_disconnect(
        self, channel: RpcChannel
    ):  # registered as handler on RpcEndpoint
        logger.debug("disconnected channel: " + channel.id)
        if channel.id in self.channel_map.keys():
            self.channel_map[channel.id].status = ChannelStatusEnum.Disconnected

    def get_client_channel(self, client_id: str) -> ChannelInfo | None:
        for ci in self.channel_map.values():
            if ci.client_id == client_id:
                return ci
        return None

    async def send_to_client(
        self,
        client_id: str,
        msg: MessageBase
    ) -> MessageBase:

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


server = Server()

# fix this instantiation order nonsense with DI
endpoint = PubSubEndpoint(  # cannot mutate these handlers later
    on_connect=[server.on_connect],  # type: ignore
    on_disconnect=[server.on_disconnect],  # type: ignore
    methods_class=RpcServerHandler,
)
server.set_rpc_handler(endpoint.methods)  # type: ignore

endpoint.register_route(router, path="/pubsub")
app.include_router(router)


# TODO consider if this can be implemented in the test
class SimpleCommandToClient(MessageBase):
    client_id: str
    cmd_name: str


@app.post("/trigger_send")
async def trigger_send_command(cmd: SimpleCommandToClient):
    if cmd.client_id is None or cmd.client_id == "" or cmd.cmd_name is None or cmd.cmd_name == "":
        return "Bad message", 400
    logger.debug("trigger_send command: " + cmd.cmd_name)

    # can't await this call or the test would deadlock
    asyncio.create_task(
        server.send_to_client(cmd.client_id, InvokeCommandMsg(name=cmd.cmd_name))
    )
    return "OK"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
