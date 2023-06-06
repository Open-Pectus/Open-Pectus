from __future__ import annotations
from dataclasses import dataclass
import json
from typing import List, Tuple, Optional
from pydantic import BaseModel
import protocol.messages

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


class TagsUpdatedMsg(MessageBase):
    tags: List[TagValue] = []


class TagValue(MessageBase):
    name: str = ""
    value: str | int | float | None = None


# Note: required for instantiation of TagsUpdatedMsg to work
TagsUpdatedMsg.update_forward_refs()


class UodSpecMsg(MessageBase):
    name: str
    tags: List[TagSpec] = []


class TagSpec(MessageBase):
    tag_name: str
    tag_unit: str | None


def serialize_msg(msg: MessageBase) -> Tuple[str, dict]:
    return type(msg).__name__, msg.dict()


def serialize_msg_to_json(msg: MessageBase) -> str:
    wrapper = {'t': type(msg).__name__, 'd': msg.dict()}
    return json.dumps(wrapper)


def deserialize_msg(msg_cls_name, init_dict: dict) -> MessageBase:
    cls = getattr(protocol.messages, msg_cls_name)
    msg = cls(**init_dict)
    return msg


def deserialize_msg_from_json(val: str) -> MessageBase:
    wrapper = json.loads(val)
    return deserialize_msg(wrapper['t'], wrapper['d'])
