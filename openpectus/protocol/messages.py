from __future__ import annotations
import json
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel

import openpectus.protocol.messages as messages_namespace

# Topics

TOPIC_AGGREGATOR_ENGINE = "AGGREGATOR_ENGINE"


# Messages

class MessageBase(BaseModel):
    """ Base class for protocol messages for both REST and WebSocket communication.

    These inherit from pydantic BaseModel to support automatic (de-)serialization when sent over
    fastapi_websocket_pubsub. Additionally they support automatic openapi schema generation for
    use with REST.
      """
    pass


class SuccessMessage(MessageBase):
    """ Indicates operation success"""
    pass


class ErrorMessage(MessageBase):
    """ Returned whenever an error occurs"""
    message: str | None = None
    exception_message: str | None = None


class ProtocolErrorMessage(ErrorMessage):
    protocol_mgs: str


RpcErrorMessage = ErrorMessage | ProtocolErrorMessage
RpcStatusMessage = SuccessMessage | RpcErrorMessage
#RpcValueMessage = MessageBase | RpcErrorMessage


class RegisterEngineMsg(MessageBase):
    computer_name: str
    uod_name: str
    # uod file hash, file change date


class RegisterEngineReplyMsg(MessageBase):
    success: bool
    engine_id: str | None


class ReadingCommand(MessageBase):
    name: str
    command: str


class ReadingInfo(MessageBase):
    label: str
    tag_name: str
    valid_value_units: List[str] | None
    commands: List[ReadingCommand]


class UodInfoMsg(MessageBase):
    readings: List[ReadingInfo]


class TagsUpdatedMsg(MessageBase):
    tags: List[TagValueMsg] = []


TagValueType = str | int | float | None


class TagValueMsg(MessageBase):
    name: str = ""
    value: TagValueType = None
    value_unit: str | None


# Note: required for instantiation of TagsUpdatedMsg to work
TagsUpdatedMsg.update_forward_refs()


class InvokeCommandMsg(MessageBase):
    name: str = ""
    arguments: str | None = None


class InjectCodeMsg(MessageBase):
    pcode: str

# class UodSpecMsg(MessageBase):
#     name: str
#     tags: List[TagSpec] = []


class TagSpec(MessageBase):
    tag_name: str
    tag_unit: str | None


class RunLogMsg(MessageBase):
    id: str
    lines: List[RunLogLineMsg]

    @staticmethod
    def default() -> RunLogMsg:
        return RunLogMsg(id="", lines=[])


class RunLogLineMsg(MessageBase):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: List[TagValueMsg]
    end_values: List[TagValueMsg]


RunLogMsg.update_forward_refs()


class ControlStateMsg(MessageBase):
    is_running: bool
    is_holding: bool
    is_paused: bool

    @staticmethod
    def default() -> ControlStateMsg:
        return ControlStateMsg(is_running=False, is_holding=False, is_paused=False)


class MethodLineMsg(MessageBase):
    id: str
    content: str


class MethodMsg(MessageBase):
    lines: List[MethodLineMsg]
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]

    @staticmethod
    def default() -> MethodMsg:
        return MethodMsg(lines=[], started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


MethodMsg.update_forward_refs()


def serialize(msg: MessageBase) -> dict[str, Any]:
    json_dict = msg.dict()
    json_dict["_type"] = type(msg).__name__
    return json_dict


def deserialize(json_dict: dict[str, Any]) -> MessageBase:
    if "_type" not in json_dict.keys():
        raise ValueError("Deserialization error. Key '_type' missing.")
    message_type = json_dict["_type"]    
    cls = getattr(messages_namespace, message_type)
    msg = cls(**json_dict)
    assert isinstance(msg, MessageBase)
    return msg


# TODO remove these

def serialize_msg(msg: MessageBase) -> Tuple[str, Dict[str, Any]]:
    return type(msg).__name__, msg.dict()


def serialize_msg_to_json(msg: MessageBase) -> str:
    wrapper = {'t': type(msg).__name__, 'd': msg.dict()}
    return json.dumps(wrapper)


def deserialize_msg(msg_cls_name, init_dict: Dict[str, Any]) -> MessageBase:
    cls = getattr(messages_namespace, msg_cls_name)
    msg = cls(**init_dict)
    assert isinstance(msg, MessageBase)
    return msg


def deserialize_msg_from_json(val: str) -> MessageBase:
    wrapper = json.loads(val)
    return deserialize_msg(wrapper['t'], wrapper['d'])
