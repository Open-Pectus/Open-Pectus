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


class RegisterEngineMsg(MessageBase):
    engine_name: str
    uod_name: str
    # uod file hash, file change date


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
    id: str  # figure this out - should refer some persistent entity
    lines: List[RunLogLineMsg]


class RunLogLineMsg(MessageBase):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: List[TagValueMsg]
    end_values: List[TagValueMsg]


RunLogMsg.update_forward_refs()


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
