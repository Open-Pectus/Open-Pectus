from types import NoneType
from typing import Any

import openpectus.aggregator.routers.dto as namespace
from pydantic import BaseModel

namespace_name = namespace.__name__
namespace_types = dir(namespace)


def serialize(msg: BaseModel) -> dict[str, Any]:
    """ Serialize a dto message in a round-trippable fashion. """
    json_dict = msg.model_dump()
    t = type(msg)
    qualified_type_name = t.__qualname__
    assert t.__module__ == namespace_name, \
        f"Cannot serialize type '{qualified_type_name}' which is not defined in namespace {namespace_name}"
    json_dict["_type"] = qualified_type_name
    return json_dict


def deserialize(json_dict: dict[str, Any]) -> BaseModel:
    """ Deserializes a dto message to the proper concrete BaseModel subtype.

    Supports messages serialized to dict by the serialize() function.
    """
    if "_type" not in json_dict.keys():
        raise ValueError("Deserialization error. Key '_type' missing.")
    message_type = json_dict["_type"]

    cls = try_get_ctor_from_namespace(message_type, namespace=namespace)

    assert not isinstance(cls, NoneType), \
        f"Class name '{cls}' cannot be deserialized since it is not defined in namespace '{namespace_name}'."
    try:
        msg = cls(**json_dict)
        assert isinstance(msg, BaseModel)
        return msg
    except Exception:
        raise


def try_get_ctor_from_namespace(type_name: str, namespace):
    if "." in type_name:  # Nested type
        outer_name, inner_name = type_name.split(".")[0:2]
        if "." in inner_name:
            raise NotImplementedError("Nested inner type not supported")
        if outer_name not in namespace_types:
            ValueError(f"Nested type '{type_name}' cannot be deserialized because the outer type {outer_name} is not " +
                       f"defined in namespace {namespace_name}")
        outer_type = getattr(namespace, outer_name, None)
        if outer_type is None:
            raise ValueError(f"Failed to get outer class {outer_name} of nested type {type_name}")
        return getattr(outer_type, inner_name, None)
    else:
        return getattr(namespace, type_name, None)
