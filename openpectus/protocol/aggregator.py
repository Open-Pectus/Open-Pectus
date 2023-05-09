from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Callable, Dict
from fastapi_websocket_pubsub.event_notifier import EventNotifier
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi_websocket_pubsub import PubSubEndpoint
from fastapi_websocket_rpc import RpcChannel
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
from protocol.serverhandler import ServerHandler, WsServerHandler
from protocol.messages import (
    deserialize_msg,
    MessageBase,
    RegisterEngineMsg
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
    return 'healthy'


@app.get("/debug")
async def show_debug_info():
    print("Server channel map (channel, ch. closed, client_id, status):")
    for x in server.channel_map.values():
        print(f"{x.channel.id}\t{x.channel.isClosed}\t{x.client_id}\t{x.status}")


class RpcServerHandler(RpcEventServerMethods):
    """ Represents the server's RPC interface """
    def __init__(self, event_notifier: EventNotifier, rpc_channel_get_remote_id: bool = False):
        super().__init__(event_notifier, rpc_channel_get_remote_id)
        self._callback: Callable[[str, str], bool] | None = None
        self._send_callback: Callable[[str, MessageBase], bool] | None = None        
        logger.debug("RpcServerHandler init")

    def set_callback(self, callback: Callable[[str, str], bool]):
        self._callback = callback

    def set_send_callback(self, callback: Callable[[str, MessageBase], bool]):
        self._send_callback = callback

    # TODO remove - just use send instead
    async def register(self, client_id: str) -> bool:
        logger.debug("Register with client_id: " + client_id)
        assert isinstance(self.channel, RpcChannel)
        logger.debug("Channel id is: " + self.channel.id)
        if self._callback is not None:
            val = self._callback(self.channel.id, client_id)
            return val
            # return SuccessMessage() if val else ErrorMessage(message="Registration failed")
        # return ErrorMessage(message="No callback was registered")
        return False

    #async def on_direct_message(self, msg_type: str, msg_dict: dict):
    async def send(self, msg_type: str, msg_dict: dict):
        logger.debug(f"Send was called with msg_type: {msg_type}, msg_dict: {msg_dict}")
        assert isinstance(self.channel, RpcChannel)
        if self._send_callback is not None:
            msg = deserialize_msg(msg_type, msg_dict)
            try:
                result = await self._send_callback(self.channel.id, msg)  # type: ignore # we just checked for None
                return result
            except Exception:
                logger.error("Send failed", exc_info=True)
            # return SuccessMessage() if val else ErrorMessage(message="Registration failed")
        # return ErrorMessage(message="No callback was registered")


class ChannelStatusEnum(StrEnum):
    Unknown = auto()
    Connected = auto()
    Registered = auto()
    Disconnected = auto()


@dataclass
class ChannelInfo():
    client_id: str | None
    channel: RpcChannel
    status: ChannelStatusEnum = ChannelStatusEnum.Unknown


class Server():
    def __init__(self) -> None:
        self.channel_map: Dict[str, ChannelInfo] = {}
        self.rpc_handler: RpcServerHandler | None = None
        self.server_handler: ServerHandler | None = None        
        logger.debug("Server init")

    def set_rpc_handler(self, handler: RpcServerHandler):
        self.rpc_handler = handler
        self.rpc_handler.set_callback(self.register)
        self.rpc_handler.set_send_callback(self.handle_message)

    def set_server_handler(self, handler: ServerHandler):
        self.server_handler = handler

    async def on_connect(self, channel: RpcChannel):  # registered as handler on RpcEndpoint
        self.channel_map[channel.id] = ChannelInfo(client_id=None, channel=channel, status=ChannelStatusEnum.Connected)
        logger.debug("connected on channel: " + channel.id)

    async def handle_message(self, channel_id: str, msg: MessageBase) -> bool:
        logger.debug(f"handle_message type {type(msg).__name__}: {msg.__repr__()}")
        handler_name = "handle_" + type(msg).__name__
        handler = getattr(self, handler_name, None)
        if handler is None:
            logger.error(f"Handler name {handler_name} is not defined")
            return False
        else:
            await handler(channel_id, msg)

    async def handle_RegisterEngineMsg(self, channel_id, msg: RegisterEngineMsg) -> bool:
        logger.debug("handle_RegisterEngineMsg")

        client_id = msg.engine_name + "_" + msg.uod_name
        if channel_id not in self.channel_map.keys():
            logger.error(f"Registration failed for client_id {client_id} and channel_id {channel_id}. Channel not found")
            return False
        channelInfo = self.channel_map[channel_id]
        if channelInfo.client_id is not None:
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Channel already in use by client_id {channelInfo.client_id}""")
            return False

        # TODO consider how to handle registrations
        # - disconnect/reconnect should work
        # - client kill/reconnect should work
        # - client_id reused with "same uod" should take over session, else fail as misconfigured client
        registrations = list([x for x in self.channel_map.values() if x.client_id == client_id])
        if len(registrations) > 0 and registrations[0].status != ChannelStatusEnum.Disconnected:
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Client has other channel""")
            return False

        # we're not being async here...
        # if False:
        #     await False

        channelInfo.client_id = client_id
        channelInfo.status = ChannelStatusEnum.Registered
        logger.debug(f"Registration successful of client {client_id} on channel {channel_id}")
        return True

    # TODO remove
    def register(self, channel_id: str, client_id: str) -> bool:  # registered as handler on RpcServerHandler
        if channel_id not in self.channel_map.keys():
            logger.error(f"Registration failed for client_id {client_id} and channel_id {channel_id}. Channel not found")
            return False
        channelInfo = self.channel_map[channel_id]
        if channelInfo.client_id is not None:
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Channel already in use by client_id {channelInfo.client_id}""")
            return False

        if len([x for x in self.channel_map.values() if x.client_id == client_id]) > 0:
            logger.error(
                f"""Registration failed for client_id {client_id} and channel_id {channel_id}.
                    Client has other channel""")
            return False

        channelInfo.client_id = client_id
        logger.debug("Registration successful")
        return True

    async def on_disconnect(self, channel: RpcChannel): # registered as handler on RpcEndpoint
        logger.debug("disconnected channel: " + channel.id)
        if channel.id in self.channel_map.keys():
            self.channel_map[channel.id].status = ChannelStatusEnum.Disconnected


server = Server()

# fix this order nonsense with DI
endpoint = PubSubEndpoint(  # cannot mutate these handlers later
    on_connect=[server.on_connect],         # type: ignore
    on_disconnect=[server.on_disconnect],   # type: ignore
    methods_class=RpcServerHandler)
server.set_rpc_handler(endpoint.methods)  # type: ignore
server.set_server_handler(WsServerHandler(endpoint))

endpoint.register_route(router, path="/pubsub")
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
