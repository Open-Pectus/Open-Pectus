import logging
from typing import Any, Iterable, Dict

from openpectus.engine.hardware import (
    HardwareLayerBase,
    HardwareLayerException,
    Register,
)

logger = logging.getLogger(__name__)


class Composite_Hardware(HardwareLayerBase):
    """ Combine multiple hardware layers into one by
        assigning the hardware layer on a per-register basis.

        Example pseudo-code:
        hwl_A = Hardware_1()
        hwl_B = Hardware_2()
        registers = dict()
        registers["Reg 1"] = Register("Reg 1", RegisterDirection.Both, hardware=hwl_A)
        registers["Reg 2"] = Register("Reg 2", RegisterDirection.Both, hardware=hwl_B)
        hwl = Composite_Hardware()
        hwl.registers = registers
        with hwl:
            hwl.read(registers["Reg 1"])"""
    def _underlying_hardwares(self) -> list[HardwareLayerBase]:
        """ Construct list of unique hardwares from list of registers """
        return list(dict.fromkeys(r.options["hardware"] for r in self.registers.values()))

    def validate_offline(self):
        for r in self.registers.values():
            if "hardware" not in r.options:
                raise HardwareLayerException(f"Hardware layer undefined for register {r}.")
            if not issubclass(type(r.options["hardware"]), HardwareLayerBase):
                raise HardwareLayerException((f"Hardware layer {r.options['hardware']} "
                                              f"specified for register {r} is not a valid "
                                              f"hardware layer."))
            if isinstance(r.options["hardware"], type(self)):
                raise HardwareLayerException((f"Hardware layer {r.options['hardware']} "
                                              f"specified for register {r} is itself a "
                                              f"composite hardware layer. This is not allowed."))
        for hardware in self._underlying_hardwares():
            hardware.validate_online()

    def validate_online(self):
        for hardware in self._underlying_hardwares():
            hardware.validate_online()

    def read(self, r: Register) -> Any:
        return r.options["hardware"].read(r)

    def read_batch(self, registers: Iterable[Register]) -> list[Any]:
        """ Divide list of registers by the hardware they belong to,
        perform the batch read, gather the results and order them
        like the list of registers. """
        registers_by_hardware: Dict[HardwareLayerBase, list[Register]] = dict()
        read_by_register: Dict[Register, Any] = dict()
        for r in registers:
            if r.options["hardware"] not in registers_by_hardware:
                registers_by_hardware[r.options["hardware"]] = [r]
            else:
                registers_by_hardware[r.options["hardware"]].append(r)
        for hardware, registers_belonging_to_hardware in registers_by_hardware.items():
            reads = hardware.read_batch(registers_belonging_to_hardware)
            for register, read in zip(registers_belonging_to_hardware, reads):
                read_by_register[register] = read
        return [read_by_register[register] for register in registers]

    def write(self, value: Any, r: Register):
        r.options["hardware"].write(value, r)

    def write_batch(self, values: Iterable[Any], registers: Iterable[Register]):
        """ Divide list of registers by the hardware they belong to,
        perform the batch write with values in same order as the registers. """
        registers_by_hardware: Dict[HardwareLayerBase, list[Register]] = dict()
        write_value_by_register: Dict[Register, Any] = dict()
        for v, r in zip(values, registers):
            if r.options["hardware"] not in registers_by_hardware:
                registers_by_hardware[r.options["hardware"]] = [r]
            else:
                registers_by_hardware[r.options["hardware"]].append(r)
            write_value_by_register[r] = v
        for hardware, registers_belonging_to_hardware in registers_by_hardware.items():
            values_to_hardware = [write_value_by_register[r] for r in registers_belonging_to_hardware]
            hardware.write_batch(values_to_hardware, registers_belonging_to_hardware)

    def connect(self):
        for hardware in self._underlying_hardwares():
            hardware.connect()
        super().connect()

    def disconnect(self):
        for hardware in self._underlying_hardwares():
            hardware.disconnect()
        super().disconnect()

    def __str__(self):
        return f"Composite_Hardware(hardwares={self._underlying_hardwares()})"
