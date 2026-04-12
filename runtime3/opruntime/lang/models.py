from __future__ import annotations
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
import difflib
import logging

from opruntime.lang.parser import Method
import opruntime.lang.program as p

logger = logging.getLogger(__name__)


def serialize(obj) -> str:
    """ Serialize data for debugging """
    import json
    from collections import abc

    def serialize_dict_values(obj):
        if isinstance(obj, abc.ValuesView):
            return list(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Method):
            return obj.as_json()
        elif is_dataclass(obj):
            return asdict(obj)
        raise TypeError("Type %s is not serializable" % type(obj))

    return json.dumps(obj, default=serialize_dict_values, indent=4)


@dataclass
class SePath:
    """ Represents a structural execution path, a representation of the active
    instruction during interpretation, of either the main visitor or that of an
    interrupt visitor.

    The prefixed number is the line_id/node_id. Empty for root. The name is the
    instruction name. The postfixed number is an index of the active child node
    or invocation.

    The extra 'child.N' is used when traversing child nodes. Other extras are used
    in specific Node types, e.g. 'invocation.N' for macro and alarm invocations.

    #### Examples:
    Path in main visitor
    - root > root.child.0 > 01.Mark
    - root > root.child.0 > 01.Block > 01.Block.child.1 > 03.End block
    - root > root.child.1 > 05.Call macro > 01.Macro.invocation.0 > 01.Macro.child.0 -> 03.Mark

    Path in interrupt visitor
    - 02.Alarm.interrupt > 02.Alarm > 02.Alarm.invocation.0
    """

    @dataclass
    class Item:
        node_id: str
        name: str
        extra: str = ""

        @staticmethod
        def from_node(node: p.Node, extra: str = "") -> SePath.Item:
            return SePath.Item(node_id=node.id, name=node.name, extra=extra)

        @property
        def key(self):
            s = self.node_id
            if self.node_id != "root":
                s += "." + self.name
            if self.extra != "":
                s += "." + self.extra
            return s

        def __str__(self):
            return self.key

        def clone(self) -> SePath.Item:
            return SePath.Item(node_id=self.node_id, name=self.name, extra=self.extra)

    def __init__(self):
        self._items: list[SePath.Item] = []

    def push(self, node: p.Node, extra: str = ""):
        item = SePath.Item.from_node(node, extra)
        # if any(self._items) and extra != "":
        #     last = self.peek()
        #     if node.id != last.node_id:
        #         raise ValueError(f"Cannot push item '{item.key}' onto path '{self.path}'")
        self._items.append(item)
        logger.debug("Sep: " + str(self))

    def pop(self) -> SePath.Item:
        if not any(self._items):
            raise ValueError("SePath pop() stack underrun")
        item = self._items.pop()
        #logger.debug("Sep - popped " + item.key + " | remaining path: " + str(self))
        return item

    def peek(self) -> SePath.Item:
        if not any(self._items):
            raise ValueError("SePath peek() stack underrun")
        return self._items[-1]

    @property
    def path(self) -> str:
        """ Returns the canonical string representation of the path. """
        elms = [r.key for r in self._items]
        return " > ".join(elms)

    def __eq__(self, value):
        if value is None:
            return False
        if isinstance(value, SePath):
            return self.path == value.path
        if isinstance(value, str):
            return self.path == value
        return False

    def has_node_id(self, node_id: str) -> bool:
        """ Determines whether node_id is (anywhere) in the path. """
        for item in self._items:
            if item.node_id == node_id:
                return True
        return False

    def has_node_key(self, node_key: str, raise_on_id_only_match=True) -> bool:
        """ Determines whether node_key is (anywhere) in the path. By default, a partial match on node id only
        raises a ValueError. """
        if "." not in node_key:
            raise ValueError(f"{node_key} is not a valid node key. Node keys have the form '<node_id>.<node_name>'")
        node_id = node_key.split(".")[0]
        node_name = node_key[len(node_id) + 1:]
        for item in self._items:
            if item.node_id == node_id:
                if item.name != node_name:
                    logger.warning(
                        f"SePath.has_node_key() found a node_id match for key '{node_key}' " +
                        f"but the name '{node_name}' does not match the item name '{item.name}'")
                    if raise_on_id_only_match:
                        raise ValueError(
                            f"SePath.has_node_key() found a node_id match for key '{node_key}' " +
                            f"but the name '{node_name}' does not match the item name '{item.name}'")
                else:
                    return True
        return False

    def ends_with_node_id(self, node_id: str) -> bool:
        if len(self._items) > 2:
            return self._items[-1].node_id == node_id
        return False

    def matches(self, path: str) -> bool:
        return path == self.path

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def clone(self) -> SePath:
        instance = SePath()
        instance._items = [item.clone() for item in self._items]
        return instance


@dataclass
class InterruptState:
    node_id: str
#    sep: Sep


@dataclass
class InterpreterState:
    export_date: datetime
    method: Method
    tree_state: dict[str, p.NodeState]
    main_sep: SePath
    interrupt_states: list[InterruptState]
    macros_registered: list[str]

    @staticmethod
    def compare(a: InterpreterState, b: InterpreterState, include_export_date=False) -> list[str]:
        """ Compare states a and b and return differences as string list. Result is empty if the states are identical.
        Otherwise unified diffs are returned. """
        result_lines: list[str] = []
        if include_export_date:
            result_lines.extend(
                difflib.unified_diff(
                    a=a.export_date.isoformat(),
                    b=b.export_date.isoformat(),
                    n=0
                ))

        result_lines.extend(Method.compare(a.method, b.method))
        a_lines = serialize(a.tree_state).splitlines()
        b_lines = serialize(b.tree_state).splitlines()
        result_lines.extend(difflib.unified_diff(a=a_lines, b=b_lines, n=8, lineterm=""))
        return list(result_lines)

    @staticmethod
    def write_htmldiff(a: InterpreterState, b: InterpreterState, test_id: str, out_filepath: str):
        a_lines = serialize(a.tree_state).splitlines()
        b_lines = serialize(b.tree_state).splitlines()
        differ = difflib.HtmlDiff()
        html = differ.make_file(
            fromlines=a_lines,
            tolines=b_lines,
            fromdesc="test_id: " + test_id + " @ ",
            todesc="time: " + datetime.now().isoformat(timespec="seconds"),
            context=False)
        with open(out_filepath, 'w') as f:
            f.write(html)


    # try difflib for this

    # could spend lots of time doing this - is it worth it?
    # @staticmethod
    # def compare_states(a: InterpreterState, b: InterpreterState) -> dict[str, Any]:
    #     if a is None or b is None:
    #         raise ValueError("One of the states are None")
    #     result = {}
    #     if a.export_date == b.export_date:
    #         result["export_date"] = f"Identical {a.export_date.isoformat()}"
    #     else:
    #         result["export_date"] = f"Different {a.export_date.isoformat()} vs {b.export_date.isoformat()}"
    #     return result
