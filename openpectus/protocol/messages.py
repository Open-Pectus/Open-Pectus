from __future__ import annotations
from typing import List
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


class RegisterEngineMsg(MessageBase):
    engine_name: str
    uod_name: str
    # uod file hash, file change date


class TagsUpdatedMsg(MessageBase):
    tags: List[TagValue] = []


class TagValue(MessageBase):
    name: str = ""
    value: str | int | float | None = None


class UodSpecMsg(MessageBase):
    name: str
    tags: List[TagSpec] = []


class TagSpec(MessageBase):
    tag_name: str
    tag_unit: str | None


def serialize_msg(msg: MessageBase) -> dict:
    return msg.dict()


def deserialize_msg(msg_cls_name, init_dict: dict) -> MessageBase:
    cls = getattr(protocol.messages, msg_cls_name)
    msg = cls(**init_dict)
    return msg
