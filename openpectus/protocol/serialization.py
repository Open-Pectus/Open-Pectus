import json
from types import NoneType
from typing import Any, Tuple, Dict, Callable

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M


def serialize(msg: M.MessageBase) -> dict[str, Any]:
    json_dict = msg.dict()
    json_dict["_type"] = type(msg).__name__
    return json_dict


def deserialize(json_dict: dict[str, Any]) -> M.MessageBase:
    if "_type" not in json_dict.keys():
        raise ValueError("Deserialization error. Key '_type' missing.")
    message_type = json_dict["_type"]
    cls = getattr(EM, message_type, getattr(AM, message_type, getattr(M, message_type, None)))
    assert not isinstance(cls, NoneType)
    msg = cls(**json_dict)
    assert isinstance(msg, M.MessageBase)
    return msg


# TODO remove these

def serialize_msg(msg: M.MessageBase) -> Tuple[str, Dict[str, Any]]:
    return type(msg).__name__, msg.dict()


def serialize_msg_to_json(msg: M.MessageBase) -> str:
    wrapper = {'t': type(msg).__name__, 'd': msg.dict()}
    return json.dumps(wrapper)


def deserialize_msg(msg_cls_name, init_dict: Dict[str, Any]) -> M.MessageBase:
    cls = getattr(EM, msg_cls_name, getattr(AM, msg_cls_name, getattr(M, msg_cls_name, None)))
    msg = cls(**init_dict)
    assert isinstance(msg, M.MessageBase)
    return msg


def deserialize_msg_from_json(val: str) -> M.MessageBase:
    wrapper = json.loads(val)
    return deserialize_msg(wrapper['t'], wrapper['d'])
