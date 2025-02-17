import logging
import ctypes
import os
import sys
import json
import functools
import re
from typing import Any, Sequence, Optional, Dict

from openpectus.engine.hardware import (
    HardwareLayerBase,
    Register,
    RegisterDirection,
    HardwareLayerException,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SuppressPrint:
    """ Supress print
    Source: https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print """
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


# The LabJack library executes code on import and this cannot be hindered.
# The code attempts to load the LabJack DLL but fails if it is not installed.
# This is not a problem, because the DLL is shipped with this sofware.
# However, the error message is still printed and this may confuse the user.
with SuppressPrint():
    import labjack.ljm.ljm as ljm
    import labjack.ljm.constants


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
    ljm._staticLib = ctypes.CDLL(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "labjack",
            "LabJackM.dll"))
elif sys.platform.startswith("linux"):
    ljm._staticLib = ctypes.CDLL(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "labjack",
            "libLabJackM.so"))

constants_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "labjack",
    "ljm_constants.json")
ljm.loadConstantsFromFile(constants_file)


class Labjack_Hardware(HardwareLayerBase):
    """ Represents LabJack hardware layer. """
    def __init__(self, serial_number: Optional[str] = None) -> None:
        super().__init__()
        self.serial_number: str = serial_number if serial_number else "ANY"
        self._handle = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(is_connected={self.is_connected}, serial_number="{self.serial_number}")'

    @functools.cached_property
    def port_directions(self):
        # Load ljm_constants.json
        with open(constants_file, "r") as f:
            ljm_constants = json.load(f)
        # Prepare regex and result dict
        regex = re.compile(r"#\((?P<start>\d+):(?P<end>\d+)\)")
        ljm_register_directions: Dict[str, RegisterDirection] = dict()
        direction_to_register_direction = {"R": RegisterDirection.Read,
                                           "W": RegisterDirection.Write,
                                           "RW": RegisterDirection.Both}
        # Note the port direction for each register
        for register in ljm_constants["registers"]:
            name = register["name"]
            # Some register names cover ranges of registers.
            # Example: "AIN#(0:254)"
            match = re.search(regex, name)
            if match:
                match_dict = match.groupdict()
                start, end = int(match_dict["start"]), int(match_dict["end"])
                base_name = name.replace(match.group(0), "{i}")
                names = [base_name.format(i=i) for i in range(start, end+1)]
            else:
                names = [name]
            for name in names:
                ljm_register_directions[name] = direction_to_register_direction[register["readwrite"]]
        return ljm_register_directions

    def validate_offline(self):
        for r in self.registers.values():
            if "port" not in r.options:
                raise HardwareLayerException((f"Labjack hardware layer requires specification of "
                                              f"port for register {r}."))
            # Check that the register port exists
            port = r.options["port"]
            try:
                address, data_type = ljm.nameToAddress(port)
            except ljm.LJMError as error:
                raise HardwareLayerException(f"Register {r} port '{port}' invalid. Labjack error: {error}.")
            # Check the direction
            labjack_port_direction = self.port_directions[port]
            if (
               RegisterDirection.Read in r.direction and
               RegisterDirection.Read not in labjack_port_direction
               ) or (
               RegisterDirection.Write in r.direction and
               RegisterDirection.Write not in labjack_port_direction
               ):
                raise HardwareLayerException((f"Disparity between register direction '{r.direction}' "
                                              f"for register {r} and Labjack port direction "
                                              f"'{labjack_port_direction}."))

    def read(self, r: Register) -> Any:
        if RegisterDirection.Read not in r.direction:
            raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        try:
            return ljm.eReadName(self._handle, r.options["port"])
        except ljm.LJMError as error:
            logger.error(f"Unable to read {r}", exc_info=True)
            raise HardwareLayerException(f"Unable to read {r}. Labjack error: {error}.")

    def read_batch(self, registers: Sequence[Register]) -> list[Any]:
        """ Read batch of register values with a single OPC-UA call. """
        for r in registers:
            if RegisterDirection.Read not in r.direction:
                raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        try:
            return ljm.eReadNames(self._handle, len(registers), [r.options["port"] for r in registers])
        except ljm.LJMError as error:
            logger.error(f"Unable to read registers {registers}", exc_info=True)
            raise HardwareLayerException(f"Unable to read registers {registers}. Labjack error: {error}.")

    def write(self, value: Any, r: Register):
        if RegisterDirection.Write not in r.direction:
            raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        try:
            return ljm.eWriteName(self._handle, r.options["port"], value)
        except ljm.LJMError as error:
            logger.error(f"Unable to write '{value}' to {r}", exc_info=True)
            raise HardwareLayerException(f"Unable to write '{value}' to {r}. Labjack error: {error}.")

    def write_batch(self, values: Sequence[Any], registers: Sequence[Register]):
        """ Write batch of register values with a single OPC-UA call. """
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        try:
            ljm.eWriteNames(self._handle, len(registers), [r.options["port"] for r in registers], values)
        except ljm.LJMError as error:
            logger.error("Unable to write batch", exc_info=True)
            raise HardwareLayerException(f"Unable to write registers {registers}. Labjack error: {error}.")

    def setup(self):
        """ Method to call after successful connect. """
        pass

    def _reconnect(self, handle):
        logger.info(f"Reconnected to Labjack with serial number {self.serial_number}")

    def connect(self):
        """ Connect to Labjack. """
        logger.info(f"Attempting to connect to Labjack with serial number {self.serial_number}")
        if self._handle:
            self.disconnect()
        try:
            self._handle = ljm.openS("ANY",  # Device (T4, T7, T8)
                                     "ANY",  # Connection (USB, ETHERNET)
                                     self.serial_number)  # Identifier (Serial number)
        except ljm.LJMError as labjack_error:
            logger.error(f"Unable to connect to Labjack with serial number {self.serial_number}")
            logger.error(labjack_error)
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
            raise HardwareLayerException(f"Unable to connect to Labjack with serial number {self.serial_number}")
        logger.info(f"Connected to {self.serial_number}")
        self.setup()
        ljm.registerDeviceReconnectCallback(self._handle, self._reconnect)
        super().connect()

    def disconnect(self):
        """ Disconnect hardware. """
        logger.info(f"Disconnecting from Labjack with serial number {self.serial_number}")
        if self._handle:
            ljm.close(self._handle)
            self._handle = None
        super().disconnect()
