from types import NoneType
from typing import Any

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
from openpectus.protocol.exceptions import ProtocolDeserializationException

_message_namespaces = [AM, EM, M]
_message_namespace_names = [ns.__name__ for ns in _message_namespaces]


def serialize(msg: M.MessageBase) -> dict[str, Any]:
    """ Serialize a protocol message in a round-trippable fashion. """
    json_dict = msg.model_dump()
    json_dict["_type"] = type(msg).__qualname__
    json_dict["_ns"] = msg.__module__
    return json_dict


def deserialize(json_dict: dict[str, Any]) -> M.MessageBase:
    """ Deserializes a protocol message to the proper concrete MessageBase subtype.

    Supports messages serialized to dict by the serialize() function.
    """
    try:
        if "_type" not in json_dict.keys() or "_ns" not in json_dict.keys():
            raise ValueError("Deserialization error. Key '_type' or '_ns' missing.")
        message_type, module_name = json_dict["_type"], json_dict["_ns"]
        if module_name not in _message_namespace_names:
            raise ValueError(f"Message module name '{module_name}' is not a valid protocol message namespace.")
        ns = _message_namespaces[_message_namespace_names.index(module_name)]
        cls = getattr(ns, message_type, None)
        assert not isinstance(cls, NoneType), f"Class name {cls} is not defined in namespace '{module_name}'."
        msg = cls(**json_dict)
        assert isinstance(msg, M.MessageBase)
        return msg
    except Exception as ex:
        raise ProtocolDeserializationException(f"Deserialization protocol error: {ex}")
