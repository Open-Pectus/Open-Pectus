
from types import NoneType
from typing import Any

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M


def serialize(msg: M.MessageBase) -> dict[str, Any]:
    """ Serialize a protocol message in a round-trippable fashion. """
    json_dict = msg.dict()
    json_dict["_type"] = type(msg).__name__
    return json_dict


def deserialize(json_dict: dict[str, Any]) -> M.MessageBase:
    """ Deserializes a protocol message to the proper concrete MessageBase subtype.

    Supports messages serialized to dict by the serialize() function.
    """
    if "_type" not in json_dict.keys():
        raise ValueError("Deserialization error. Key '_type' missing.")
    message_type = json_dict["_type"]
    cls = getattr(EM, message_type, getattr(AM, message_type, getattr(M, message_type, None)))
    assert not isinstance(cls, NoneType), f"Class name {cls} is not defined in any of the protocol message namespaces."
    msg = cls(**json_dict)
    assert isinstance(msg, M.MessageBase)
    return msg
