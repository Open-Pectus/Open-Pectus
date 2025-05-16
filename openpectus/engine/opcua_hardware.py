import logging
import functools
import itertools
from typing import Any, Sequence
import asyncua
import asyncua.ua
import asyncua.sync
import asyncua.client.ua_client

from openpectus.engine.hardware import (
    HardwareLayerBase,
    Register,
    RegisterDirection,
    HardwareLayerException,
)

logger = logging.getLogger(__name__)

OPCUA_Types = asyncua.ua.VariantType


def _opcua_parent_path(path):
    """ Returns the parent path for an OPC-UA path.

    > path = "Objects/2:FT01/2:Totalizer/2:Total 1"
    > self._parent_path(path)
    "Objects/2:FT01/2:Totalizer"
    """
    if '/' in path:
        return path.rsplit('/', 1)[0]
    else:
        return path


def batched(iterable: Sequence[Any], n: int):
    """ Batch data into tuples of length n. The last batch may be shorter.
    Sourced from https://docs.python.org/3.11/library/itertools.html#itertools.batched.
    In Python 3.12 this will become a part of the itertools package
    and this function can be replaced by 'from itertools import batched'."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


#  Monkeypatch asyncua library
# The asyncua OPC-UA client launches a thread class called
# ThreadLoop which is unfortunately not configured to be daemonic.
# This can cause a python instance to hang if the client
# connection is not deliberately disconnected.
# A PR to asyncua petitioning them to set it daemonic in the
# first place has been submitted, see
# https://github.com/FreeOpcUa/opcua-asyncio/pull/1555.
asyncua.sync.ThreadLoop.daemon = True


class OPCUA_Hardware(HardwareLayerBase):
    """ Represents OPCUA hardware layer. """
    def __init__(self, host: str) -> None:
        super().__init__()
        self.host: str = host
        self._client: asyncua.sync.Client = asyncua.sync.Client(self.host)
        # Siemens default maximum values
        self._max_nodes_per_read: int = 1000
        self._max_nodes_per_write: int = 1000

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(is_connected={self.is_connected}, host="{self.host}")'

    def _browse_opcua_name_space_depth_first_until_path_is_valid(
            self, path: str) -> tuple[str, list[asyncua.ua.uatypes.QualifiedName]]:
        """ Given a path to a node that does not exist, find the closest
        parent that does.

        > path_to_nonexistant_node = "Objects/2:FT01/2:Totalizer/2:Totaal 1"
        > # User made a spelling mistake at the final node above. Oh dear...
        > # Suppose that "Objects/2:FT01/2:Totalizer" does exist though
        > self._browse_opcua_name_space_depth_first_until_path_is_valid(
        > path_to_nonexistant_node)
        [QualifiedName(NamespaceIndex=2, Name='Total 1'),
        QualifiedName(NamespaceIndex=2, Name='Total 2'),
        QualifiedName(NamespaceIndex=2, Name='Total 3')]
        """
        while True:
            path = _opcua_parent_path(path)
            if '/' in path:  # We are still not at the "Objects" node
                try:
                    children = self._client.nodes.root.get_child(path).get_children()
                    break
                except asyncua.ua.uaerrors._auto.BadNoMatch:
                    pass
            else:  # We've reached the "Objects" node
                children = self._client.get_objects_node().get_children()
                break
        children = [child.read_browse_name() for child in children]
        return (path, children,)

    def _query_server_operation_limits(self):
        """ Ask the server about it's operational capabilities. """
        registers = [
            Register("max_nodes_per_read",
                     RegisterDirection.Read,
                     path="Objects/0:Server/0:ServerCapabilities/0:OperationLimits/0:MaxNodesPerRead"),
            Register("max_nodes_per_write",
                     RegisterDirection.Read,
                     path="Objects/0:Server/0:ServerCapabilities/0:OperationLimits/0:MaxNodesPerWrite"),
        ]
        self._max_nodes_per_read, self._max_nodes_per_write = self.read_batch(registers)

    def validate_offline(self):
        for r in self.registers.values():
            # Check that path is specified
            if "path" not in r.options:
                raise HardwareLayerException((f"OPC-UA hardware layer requires specification "
                                              f"of a path to the register value. Please "
                                              f"specify path for register {r}."))
            # Check that path is sensible
            if "/" not in r.options["path"]:
                if not r.options["path"] == "Objects":
                    raise HardwareLayerException(f"Invalid OPC-UA node path '{r.options['path']}' for register {r}.")
            else:
                for browse_name in r.options["path"].split("/")[1:]:
                    if not browse_name.count(":") == 1:
                        raise HardwareLayerException((f"Invalid OPC-UA node path '{r.options['path']}' "
                                                      f"for register {r}. Node browse name "
                                                      f"'{browse_name}' specifically is not valid."))
            # If a type is specified, check that it is sensible
            if "type" in r.options and not isinstance(r.options["type"], asyncua.ua.VariantType):
                raise HardwareLayerException((f"Invalid type '{r.options['type']}' "
                                              f"specified for register {r}. Type must "
                                              f"be an asyncua.ua.VariantType."))

    def validate_online(self):
        for r in self.registers.values():
            # Get the node
            node = self._register_to_node(r)
            # Read the type of the node
            opcua_type = node.read_data_type_as_variant_type()
            # Verify that register type and actual OPC-UA type match
            if 'type' in r.options:
                register_type = r.options["type"]
                if register_type is not opcua_type:
                    raise HardwareLayerException((f"Disparity between type '{OPCUA_Types(register_type).name}' "
                                                  f"for register {r} and actual OPC-UA type "
                                                  f"'{OPCUA_Types(opcua_type).name}'."))
            else:
                # Use type specified in OPC-UA
                r.options["type"] = opcua_type

            # Verify access level
            access_level = node.get_access_level()
            if (
               RegisterDirection.Read in r.direction and
               asyncua.ua.AccessLevel.CurrentRead not in access_level
               ) or (
               RegisterDirection.Write in r.direction and
               asyncua.ua.AccessLevel.CurrentWrite not in access_level
               ):
                raise HardwareLayerException((f"Disparity between register direction '{r.direction}' "
                                              f"for register {r} and OPC-UA access level "
                                              f"'{access_level}."))

    @functools.cache
    def _register_to_node(self, r: Register) -> asyncua.sync.SyncNode:
        """ Resolving a NodeId from a path requires an OPC-UA call.
        The NodeId's are fixed so it makes sense to resolve them once
        and cache the result for future use. """
        path = r.options["path"]
        try:
            node_id = self._client.nodes.root.get_child(path)
        except asyncua.ua.uaerrors._auto.BadNoMatch:
            # If the node cannot be found then we try to help the
            # person writing the UOD debug by browsing the OPC-UA
            # namespace for them.
            valid_path, children = self._browse_opcua_name_space_depth_first_until_path_is_valid(path)
            children_string = ", ".join([f"{child.NamespaceIndex}:{child.Name}" for child in children])
            raise HardwareLayerException((f"Node at register {r} path {path} "
                                          f"cannot be found. The closest parent "
                                          f"node is '{valid_path}' with children: {children_string}"))
        except asyncua.sync.ThreadLoopNotRunning:
            raise HardwareLayerException("OPC-UA client is closed.")
        return node_id

    def _registers_to_nodes(self, registers: Sequence[Register]) -> list[asyncua.sync.SyncNode]:
        node_ids = []
        for r in registers:
            node_ids.append(self._register_to_node(r))
        return node_ids

    def read(self, r: Register) -> Any:
        if RegisterDirection.Read not in r.direction:
            raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        try:
            opcua_node = self._register_to_node(r)
            return opcua_node.read_value()
        except ConnectionError:
            raise HardwareLayerException(f"Not connected to {self.host}")
        except asyncua.sync.ThreadLoopNotRunning:
            logger.error("Thread loop not running", exc_info=True)
            raise HardwareLayerException("OPC-UA client is closed.")

    def read_batch(self, registers: Sequence[Register]) -> list[Any]:
        """ Read batch of register values with a single OPC-UA call. """
        for r in registers:
            if RegisterDirection.Read not in r.direction:
                raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        values = []
        try:
            for register_batch in batched(registers, self._max_nodes_per_read):
                nodes = self._registers_to_nodes(register_batch)
                values += self._client.read_values(nodes)
        except ConnectionError:
            raise HardwareLayerException(f"Not connected to {self.host}")
        except asyncua.sync.ThreadLoopNotRunning:
            logger.error("Thread loop not running", exc_info=True)
            raise HardwareLayerException("OPC-UA client is closed.")
        return values

    def _coerce_value_to_proper_type(self, value: Any, r: Register) -> Any:
        if "type" not in r.options:
            return value

        coercion_mapping = {
            OPCUA_Types.Boolean: lambda x: bool(x),
            OPCUA_Types.Byte: lambda x: int(x),
            OPCUA_Types.Int16: lambda x: int(x),
            OPCUA_Types.UInt16: lambda x: 0 if x < 0 else int(x),
            OPCUA_Types.Int32: lambda x: int(x),
            OPCUA_Types.UInt32: lambda x: 0 if x < 0 else int(x),
            OPCUA_Types.Int64: lambda x: int(x),
            OPCUA_Types.UInt64: lambda x: 0 if x < 0 else int(x),
            OPCUA_Types.Float: lambda x: float(x),
            OPCUA_Types.Double: lambda x: float(x),
        }

        limits_check_mapping = {
            OPCUA_Types.Boolean: lambda x: x in [True, False],
            OPCUA_Types.Byte: lambda x: x >= 0 and x < 256,
            OPCUA_Types.Int16: lambda x: x >= -(2**15-1) and x < (2**15-1),
            OPCUA_Types.UInt16: lambda x: x >= 0 and x < (2**16-1),
            OPCUA_Types.Int32: lambda x: x >= -(2**31-1) and x < (2**31-1),
            OPCUA_Types.UInt32: lambda x: x >= 0 and x < (2**32-1),
            OPCUA_Types.Int64: lambda x: x >= -(2**63-1) and x < (2**63-1),
            OPCUA_Types.UInt64: lambda x: x >= 0 and x < (2**64-1),
        }

        coercion_function = coercion_mapping.get(r.options["type"], None)
        limits_check_function = limits_check_mapping.get(r.options["type"], None)

        coerced_value = value
        if coercion_function:
            try:
                coerced_value = coercion_function(value)
            except Exception:
                raise HardwareLayerException((f"Value '{value}' could not be coerced to type '{r.options['type']}' "
                                              f"when writing register {r}."))
            if coerced_value is not value:
                logger.warning((f"Value '{value}' was coerced to '{coerced_value}' "
                                f"when writing register {r}."))

        if limits_check_function:
            if not limits_check_function(coerced_value):
                raise HardwareLayerException((f"Value '{coerced_value}' does not satisfy the limits that its "
                                              f"type '{r.options['type']}' imposes when writing register {r}."))

        return coerced_value

    def write(self, value: Any, r: Register):
        return self.write_batch([value], [r])

    def write_batch(self, values: Sequence[Any], registers: Sequence[Register]):
        """ Write batch of register values with a single OPC-UA call. """
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        try:
            node_ids = []
            nodes = self._registers_to_nodes(registers)
            node_ids = [node.nodeid for node in nodes]
            data_values = []
            for r, value in zip(registers, values):
                value = self._coerce_value_to_proper_type(value, r)
                if 'type' in r.options:
                    value = asyncua.ua.Variant(value, r.options['type'])
                data_values.append(asyncua.ua.DataValue(value))
            # This is quite convoluted because asyncua.sync does not offer a convenience method.
            # The approach taken to get a synchronous "write_attributes" method is documented
            # in opcua-asyncua asyncua/sync.py source code:
            # https://github.com/FreeOpcUa/opcua-asyncio/blob/master/asyncua/sync.py
            write_attributes = asyncua.sync.sync_uaclient_method(
                               asyncua.client.ua_client.UaClient.write_attributes)(self._client)
            write_status_codes = []
            for node_id_batch, data_value_batch in zip(batched(node_ids, self._max_nodes_per_write),
                                                       batched(data_values, self._max_nodes_per_write)):
                result = write_attributes(node_id_batch, data_value_batch, asyncua.ua.AttributeIds.Value)
                assert isinstance(result, list)
                write_status_codes.extend(result)
            for register, value, status_code in  zip(registers, values, write_status_codes):
                if status_code.value != 0:
                    raise HardwareLayerException(f'Write of value "{value}" to register {register} failed with status code {asyncua.ua.status_codes.get_name_and_doc(status_code.value)}.')
        except ConnectionError:
            raise HardwareLayerException(f"Not connected to {self.host}")
        except asyncua.sync.ThreadLoopNotRunning:
            logger.error("Thread loop not running", exc_info=True)
            raise HardwareLayerException("OPC-UA client is closed.")

    def connect(self):
        """ Connect to OPC-UA server. """
        logger.info(f"Attempting to connect to {self.host}")
        if self._client:
            # catching these exceptions make reconnect able to just try
            # again which seems to work
            try:
                self._client.disconnect()
            except asyncua.sync.ThreadLoopNotRunning:
                pass
            except RuntimeError:
                pass
            # Remove potential stale references to nodes on re-connect
            self._register_to_node.cache_clear()
            del self._client
        self._client = asyncua.sync.Client(self.host)
        try:
            self._client.connect()
        except ConnectionRefusedError:
            logger.error(f"Unable to connect to {self.host}")
            raise HardwareLayerException(f"Unable to connect to {self.host}")
        logger.info(f"Connected to {self.host}")
        self._query_server_operation_limits()
        super().connect()

    def disconnect(self):
        """ Disconnect hardware. """
        logger.info(f"Disconnecting from {self.host}")
        if self._client:
            self._client.disconnect()
        super().disconnect()
