import logging
from typing import Any, Dict, Iterable

from openpectus.engine.hardware import (
    HardwareLayerBase,
    Register,
    RegisterDirection,
    HardwareLayerException,
    HardwareConnectionStatus,
)

import asyncua
from asyncua.sync import Client as OPCUAClient

logger = logging.getLogger(__name__)

class OPCUA_Hardware(HardwareLayerBase):
    """ Represents OPCUA hardware layer. """
    def __init__(self, host: str) -> None:
        super().__init__()
        self._client = None
        self._node_ids: dict[Register, asyncua.common.node.Node] = dict()
        self.host: str = host
    
    def _registers_to_node_ids(self, registers: list[Register]) -> list[asyncua.common.node.Node]:
        node_ids = []
        for r in registers:
            path = r.options["path"]
            node_id = self._node_ids.get(r, None)
            if node_id is None:
                node_id = self._client.nodes.root.get_child(path)
                self._node_ids[r] = node_id
            node_ids.append(node_id)
        return node_ids
    
    def read(self, r: Register) -> Any:
        try:
            path = r.options['path']
            opcua_node = self._client.nodes.root.get_child(path)
            return opcua_node.read_value()
        except ConnectionError:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Not connected to {self.host}")

    def read_batch(self, registers: list[Register]) -> list[Any]:
        """ Read batch of register values."""
        try:
            registers = [r for r in registers if RegisterDirection.Read in r.direction]
            node_ids = self._registers_to_node_ids(registers)
            values = self._client.read_values(node_ids)
        except ConnectionError:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Not connected to {self.host}")
        return values

    def write(self, value: Any, r: Register):
        if RegisterDirection.Write not in r.direction:
            return
        try:
            path = r.options['path']
            opcua_node = self._client.nodes.root.get_child(path)
            opcua_node.set_value(value)
        except ConnectionError:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Not connected to {self.host}")

    def write_batch(self, values: Iterable[Any], registers: Iterable[Register]):
        """ Write batch of register values. Override to provide efficient implementation """
        try:
            node_ids = []
            registers = [r for r in registers if RegisterDirection.Write in r.direction]
            node_ids = self._registers_to_node_ids(registers)
            self._client.write_values(node_ids, values)
        except ConnectionError:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Not connected to {self.host}")

    def connect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        logger.info(f"Attempting to connect to {self.host}")
        self.connection_status.register_connection_attempt()
        if self._client:
            del self._client
        self._client = OPCUAClient(self.host)
        try:
            self._client.connect()
        except ConnectionRefusedError:
            logger.info(f"Unable to connect to {self.host}")
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Unable to connect to {self.host}")
        logger.info(f"Connected to {self.host}")
        self.connection_status.set_ok()

    def disconnect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        logger.info("Disconnecting from OPCUA...")
        if self._client:
            self._client.disconnect()
        self.connection_status.set_not_ok()
