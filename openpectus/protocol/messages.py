from __future__ import annotations
import json
from typing import List, Tuple
from pydantic import BaseModel

import openpectus.protocol.messages as messages_namescape

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
    tags: List[TagValue] = []


class TagValue(MessageBase):
    name: str = ""
    value: str | int | float | None = None
    value_unit: str | None


# Note: required for instantiation of TagsUpdatedMsg to work
TagsUpdatedMsg.update_forward_refs()


class InvokeCommandMsg(MessageBase):
    name: str = ""
    arguments: str | None = None


# class UodSpecMsg(MessageBase):
#     name: str
#     tags: List[TagSpec] = []


class TagSpec(MessageBase):
    tag_name: str
    tag_unit: str | None


def serialize_msg(msg: MessageBase) -> Tuple[str, dict]:
    return type(msg).__name__, msg.dict()


def serialize_msg_to_json(msg: MessageBase) -> str:
    wrapper = {'t': type(msg).__name__, 'd': msg.dict()}
    return json.dumps(wrapper)


def deserialize_msg(msg_cls_name, init_dict: dict) -> MessageBase:
    cls = getattr(messages_namescape, msg_cls_name)
    msg = cls(**init_dict)
    assert isinstance(msg, MessageBase)
    return msg


def deserialize_msg_from_json(val: str) -> MessageBase:
    wrapper = json.loads(val)
    return deserialize_msg(wrapper['t'], wrapper['d'])
