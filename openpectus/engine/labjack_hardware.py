import logging
import ctypes
import os
import sys
from typing import Any, Iterable
import labjack.ljm.ljm as ljm
import labjack.ljm.constants

from openpectus.engine.hardware import (
    HardwareLayerBase,
    Register,
    RegisterDirection,
    HardwareLayerException,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEVICE_TYPES = {
    labjack.ljm.constants.dtT4: "T4",
    labjack.ljm.constants.dtT7: "T7",
    labjack.ljm.constants.dtT8: "T8",
}

CONNECTION_TYPES = {
    labjack.ljm.constants.ctANY: "Any",
    labjack.ljm.constants.ctUSB: "USB",
    labjack.ljm.constants.ctTCP: "TCP",
    labjack.ljm.constants.ctETHERNET: "Ethernet",
    labjack.ljm.constants.ctWIFI: "Wifi",
    labjack.ljm.constants.ctNETWORK_UDP: "UDP",
    labjack.ljm.constants.ctETHERNET_UDP: "Ethernet UDP",
    labjack.ljm.constants.ctWIFI_UDP: "Wifi UDP",
    labjack.ljm.constants.ctNETWORK_ANY: "Network",
    labjack.ljm.constants.ctETHERNET_ANY: "Ethernet",
    labjack.ljm.constants.ctWIFI_ANY: "Wifi",
    labjack.ljm.constants.ctANY_UDP: "UDP",
}

# The Labjack DLL/so are not distributed with the python package.
# They are included here along with the obligatory LICENSE.
if sys.platform.startswith("win32"):
    ljm._staticLib = ctypes.WinDLL(os.path.dirname(os.path.abspath(__file__))+r'\LabJackM.dll')
elif sys.platform.startswith("linux"):
    ljm._staticLib = ctypes.CDLL(os.path.dirname(os.path.abspath(__file__))+r'/libLabJackM.so')


class Labjack_Hardware(HardwareLayerBase):
    """ Represents OPCUA hardware layer. """
    def __init__(self, serial_number: str = None) -> None:
        super().__init__()
        self.serial_number: str = serial_number if serial_number else "ANY"
        self._handle = None

    def validate_offline(self):
        for r in self.registers.values():
            if "port" not in r.options:
                raise HardwareLayerException((f"Labjack hardware layer requires specification of "
                                              f" port. Please specify port for register {r}."))
            # Check that the register port exists
            port = r.options["port"]
            try:
                address, data_type = ljm.nameToAddress(port)
            except ljm.LJMError as error:
                raise HardwareLayerException(f"Register {r} port '{port}' invalid. Labjack error: {error}.")

    def validate_online(self):
        for r in self.registers.values():
            self.read(r)

    def read(self, r: Register) -> Any:
        if RegisterDirection.Read not in r.direction:
            raise HardwareLayerException("Attempt to read unreadable register {r}.")
        try:
            return ljm.eReadName(self._handle, r.options["port"])
        except ljm.LJMError as error:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Unable to read {r}. Labjack error: {error}.")

    def read_batch(self, registers: Iterable[Register]) -> list[Any]:
        """ Read batch of register values with a single OPC-UA call. """
        for r in registers:
            if RegisterDirection.Read not in r.direction:
                raise HardwareLayerException("Attempt to read unreadable register {r}.")
        try:
            return ljm.eReadNames(self._handle, len(registers), [r.options["port"] for r in registers])
        except ljm.LJMError as error:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Unable to read registers {registers}. Labjack error: {error}.")

    def write(self, value: Any, r: Register):
        if RegisterDirection.Write not in r.direction:
            raise HardwareLayerException("Attempt to write unwritable register {r}.")
        try:
            return ljm.eWriteName(self._handle, r.options["port"], value)
        except ljm.LJMError as error:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Unable to write '{value}' to {r}. Labjack error: {error}.")

    def write_batch(self, values: Iterable[Any], registers: Iterable[Register]):
        """ Write batch of register values with a single OPC-UA call. """
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise HardwareLayerException("Attempt to write unwritable register {r}.")
        try:
            ljm.eWriteNames(self._handle, len(registers), [r.options["port"] for r in registers], values)
        except ljm.LJMError as error:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Unable to write registers {registers}. Labjack error: {error}.")

    def setup(self):
        """ Method to call after successful connect. """
        pass

    def _reconnect(self, handle):
        logger.info(f"Reconnected to Labjack with serial number {self.serial_number}")
        self.connection_status.register_connection_attempt()
        self.connection_status.set_ok()

    def connect(self):
        """ Connect to Labjack. """
        logger.info(f"Attempting to connect to Labjack with serial number {self.serial_number}")
        self.connection_status.register_connection_attempt()
        if self._handle:
            self.disconnect()
        try:
            self._handle = ljm.openS("ANY",  # Device (T4, T7, T8)
                                     "ANY",  # Connection (USB, ETHERNET)
                                     self.serial_number)  # Identifier (Serial number)
        except ljm.LJMError:
            logger.info(f"Unable to connect to Labjack with serial number {self.serial_number}")
            # Look for devices
            n, device_types, connection_types, serial_numbers, ip_addresses = ljm.listAllS("ANY", "ANY")
            if n > 0:
                logger.info(f"Found {n} Labjack device(s):")
                logger.info(" Type    Connection      Serial Number      IP")
                for (device_type,
                     connection_type,
                     serial_number,
                     ip_addresse) in zip(device_types,
                                         connection_types,
                                         serial_numbers,
                                         ip_addresses):
                    logger.info((f"  {DEVICE_TYPES[device_type]:<10} "
                                 f"{CONNECTION_TYPES[connection_type]:<12}  "
                                 f"{serial_number:<10}       "
                                 f"{ip_addresse:<15}"))
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Unable to connect to Labjack with serial number {self.serial_number}")
        logger.info(f"Connected to {self.serial_number}")
        self.connection_status.set_ok()
        self.setup()
        ljm.registerDeviceReconnectCallback(self._handle, self._reconnect)

    def disconnect(self):
        """ Disconnect hardware. """
        logger.info(f"Disconnecting from Labjack with serial number {self.serial_number}")
        if self._handle:
            ljm.close(self._handle)
            self._handle = None
        self.connection_status.set_not_ok()

    def __str__(self):
        return f"Labjack_Hardware(serial_number={self.serial_number})"
