import logging
import unittest
from typing import Any, Iterable
from openpectus.engine.hardware import (
    HardwareLayerBase,
    Register,
    RegisterDirection,
    HardwareLayerException,
)
from openpectus.engine.composite_hardware import Composite_Hardware

logging.basicConfig(format=" %(name)s :: %(levelname)-8s :: %(message)s")
logger = logging.getLogger("openpectus.engine.composite_hardware.Composite_Hardware")
logger.setLevel(logging.DEBUG)


global_list = []


class Test_Hardware(HardwareLayerBase):
    __test__ = False

    """ Test hardware class which logs all interactions to a global list """
    def __init__(self, identity: int) -> None:
        super().__init__()
        self.identity = identity

    def validate_offline(self):
        global global_list
        for r in self.registers.values():
            global_list.append(("VALIDATE_OFFLINE", str(self), str(r),))

    def validate_online(self):
        global global_list
        for r in self.registers.values():
            global_list.append(("VALIDATE_ONLINE", str(self), str(r),))

    def read(self, r: Register) -> Any:
        global global_list
        global_list.append(("READ", str(self), str(r),))
        return r.options["value"]

    def read_batch(self, registers: Iterable[Register]) -> list[Any]:
        global global_list
        global_list.append(("READ", str(self), str(registers),))
        return [r.options["value"] for r in registers]

    def write(self, value: Any, r: Register):
        global global_list
        global_list.append(("WRITE", str(self), str(r), value,))

    def write_batch(self, values: Iterable[Any], registers: Iterable[Register]):
        global global_list
        global_list.append(("WRITE", str(self), str(registers), str(values),))

    def connect(self):
        global global_list
        global_list.append(("CONNECT", str(self),))

    def disconnect(self):
        global global_list
        global_list.append(("DISCONNECT", str(self),))

    def __str__(self):
        return f"Test_Hardware({self.identity})"

    def __repr__(self):
        return str(self)


def setup_composite_hardware(i0=0):
    hardwares = [Test_Hardware(i0+i) for i in range(3)]

    composite_hardware = Composite_Hardware()
    registers = dict()
    for j, hardware in enumerate(hardwares):
        for i in range(2):
            registers[f"Reg {j}_{i}"] = Register(f"Reg {j}_{i}", RegisterDirection.Both, hardware=hardware, value=i+j*10)

    composite_hardware._registers = registers
    return composite_hardware


class TestCompositeHardware(unittest.TestCase):
    def test_connect(self):
        global global_list
        global_list = []
        composite_hardware = setup_composite_hardware()

        with composite_hardware:
            pass

        self.assertListEqual(global_list, [
            ("CONNECT", "Test_Hardware(0)"),
            ("CONNECT", "Test_Hardware(1)"),
            ("CONNECT", "Test_Hardware(2)"),
            ("DISCONNECT", "Test_Hardware(0)"),
            ("DISCONNECT", "Test_Hardware(1)"),
            ("DISCONNECT", "Test_Hardware(2)")
        ])

    def test_read_register(self):
        global global_list
        global_list = []
        composite_hardware = setup_composite_hardware()
        registers = composite_hardware.registers

        with composite_hardware:
            read = composite_hardware.read(registers["Reg 1_0"])

        self.assertEqual(read, 10)
        self.assertListEqual(global_list, [
            ("CONNECT", "Test_Hardware(0)"),
            ("CONNECT", "Test_Hardware(1)"),
            ("CONNECT", "Test_Hardware(2)"),
            ("READ", "Test_Hardware(1)", 'Register(name="Reg 1_0", direction=RegisterDirection.Both)'),
            ("DISCONNECT", "Test_Hardware(0)"),
            ("DISCONNECT", "Test_Hardware(1)"),
            ("DISCONNECT", "Test_Hardware(2)")
        ])

    def test_write_register(self):
        global global_list
        global_list = []
        composite_hardware = setup_composite_hardware()
        registers = composite_hardware.registers

        with composite_hardware:
            composite_hardware.write(10.1, registers["Reg 2_1"])

        self.assertListEqual(global_list, [
            ("CONNECT", "Test_Hardware(0)"),
            ("CONNECT", "Test_Hardware(1)"),
            ("CONNECT", "Test_Hardware(2)"),
            ("WRITE", "Test_Hardware(2)", 'Register(name="Reg 2_1", direction=RegisterDirection.Both)', 10.1),
            ("DISCONNECT", "Test_Hardware(0)"),
            ("DISCONNECT", "Test_Hardware(1)"),
            ("DISCONNECT", "Test_Hardware(2)")
        ])

    def test_read_multiple_registers(self):
        global global_list
        global_list = []
        composite_hardware = setup_composite_hardware()
        registers = composite_hardware.registers

        with composite_hardware:
            read = composite_hardware.read_batch([registers[name] for name in ["Reg 2_1",
                                                                               "Reg 0_0",
                                                                               "Reg 0_1",
                                                                               "Reg 2_0",
                                                                               "Reg 1_1"]])

        self.assertListEqual(read, [21, 0, 1, 20, 11])
        self.assertListEqual(global_list, [
            ("CONNECT", "Test_Hardware(0)"),
            ("CONNECT", "Test_Hardware(1)"),
            ("CONNECT", "Test_Hardware(2)"),
            ("READ", "Test_Hardware(2)",
                '[Register(name="Reg 2_1", direction=RegisterDirection.Both), ' +
                'Register(name="Reg 2_0", direction=RegisterDirection.Both)]'),
            ("READ", "Test_Hardware(0)",
                '[Register(name="Reg 0_0", direction=RegisterDirection.Both), ' +
                'Register(name="Reg 0_1", direction=RegisterDirection.Both)]'),
            ("READ", "Test_Hardware(1)",
                '[Register(name="Reg 1_1", direction=RegisterDirection.Both)]'),
            ("DISCONNECT", "Test_Hardware(0)"),
            ("DISCONNECT", "Test_Hardware(1)"),
            ("DISCONNECT", "Test_Hardware(2)")
        ])

    def test_write_multiple_registers(self):
        global global_list
        global_list = []
        composite_hardware = setup_composite_hardware()
        registers = composite_hardware.registers

        with composite_hardware:
            regs = [registers[name] for name in ["Reg 2_1",
                                                 "Reg 0_0",
                                                 "Reg 0_1",
                                                 "Reg 2_0",
                                                 "Reg 1_1"]]
            vals = [1, 2, 3, 4, 5,]
            composite_hardware.write_batch(vals, regs)

        self.assertListEqual(global_list, [
            ("CONNECT", "Test_Hardware(0)"),
            ("CONNECT", "Test_Hardware(1)"),
            ("CONNECT", "Test_Hardware(2)"),
            ("WRITE", "Test_Hardware(2)",
                '[Register(name="Reg 2_1", direction=RegisterDirection.Both), ' +
                'Register(name="Reg 2_0", direction=RegisterDirection.Both)]', "[1, 4]"),
            ("WRITE", "Test_Hardware(0)",
                '[Register(name="Reg 0_0", direction=RegisterDirection.Both), ' +
                'Register(name="Reg 0_1", direction=RegisterDirection.Both)]', "[2, 3]"),
            ("WRITE", "Test_Hardware(1)",
                '[Register(name="Reg 1_1", direction=RegisterDirection.Both)]', "[5]"),
            ("DISCONNECT", "Test_Hardware(0)"),
            ("DISCONNECT", "Test_Hardware(1)"),
            ("DISCONNECT", "Test_Hardware(2)")
        ])

    def test_missing_hardware_layer(self):
        global global_list
        global_list = []
        composite_hardware = setup_composite_hardware()
        del composite_hardware.registers["Reg 0_1"].options["hardware"]

        with self.assertRaises(HardwareLayerException) as context:
            composite_hardware.validate_offline()
        self.assertEqual(
            'HardwareLayerException(message="Hardware layer undefined for register ' +
            'Register(name="Reg 0_1", direction=RegisterDirection.Both).")',
            str(context.exception)
        )

    def test_hardware_layer_is_itself_composite(self):
        global global_list
        global_list = []
        composite_hardware_A = setup_composite_hardware()
        composite_hardware_B = setup_composite_hardware(i0=10)
        composite_hardware_A.registers["Reg 0_1"].options["hardware"] = composite_hardware_B

        with self.assertRaises(HardwareLayerException) as context:
            composite_hardware_A.validate_offline()
        self.assertEqual(
            (
                'HardwareLayerException(message="Hardware layer Composite_Hardware(hardwares=[Test_Hardware(10), '
                'Test_Hardware(11), Test_Hardware(12)]) specified for register '
                'Register(name="Reg 0_1", direction=RegisterDirection.Both) is itself a composite hardware layer. '
                'This is not allowed.")'
            ),
            str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
