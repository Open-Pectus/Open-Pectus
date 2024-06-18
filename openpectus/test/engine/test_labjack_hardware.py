import logging
import unittest
from openpectus.engine.hardware import Register, RegisterDirection, HardwareLayerException
from openpectus.engine.labjack_hardware import Labjack_Hardware
import labjack.ljm.constants

logging.basicConfig(format=" %(name)s :: %(levelname)-8s :: %(message)s")
logger = logging.getLogger("openpectus.engine.labjack_hardware.Labjack_Hardware")
logger.setLevel(logging.DEBUG)


SN = labjack.ljm.constants.DEMO_MODE


class TestLabjackHardware(unittest.TestCase):
    def test_can_connect(self):
        hwl = Labjack_Hardware(serial_number=SN)
        try:
            hwl.connect()
            hwl.disconnect()
        except HardwareLayerException:
            self.fail()

    def test_can_read_register(self):
        FT01 = Register("FT01", RegisterDirection.Read, port="AIN1")
        registers = {"FT01": FT01}

        hwl = Labjack_Hardware(serial_number=SN)
        hwl._registers = registers
        with hwl:
            value = hwl.read(FT01)
        self.assertEqual(value, 0.0)

    def test_can_write_register(self):
        PU01 = Register("PU01", RegisterDirection.Both, port="DAC0")
        registers = {"PU01": PU01}

        hwl = Labjack_Hardware(serial_number=SN)
        hwl._registers = registers
        with hwl:
            hwl.write(10.2, PU01)

    def test_can_read_multiple_registers(self):
        registers = {f"Readable {i:02d}": Register(f"{i:02d}",
                                                   RegisterDirection.Read,
                                                   port=f"AIN{i}") for i in range(5)}

        hwl = Labjack_Hardware(serial_number=SN)
        hwl._registers = registers
        hwl.validate_offline()
        with hwl:
            values = hwl.read_batch(list(registers.values()))
        for value in values:
            self.assertEqual(0.0, value)

    def test_can_write_multiple_registers(self):
        registers = {f"Writable {i:02d}": Register(f"{i:02d}",
                     RegisterDirection.Both,
                     port=f"USER_RAM{i}_U16") for i in range(8)}
        values_to_write = [float(i) for i in range(len(registers))]

        hwl = Labjack_Hardware(serial_number=SN)
        hwl._registers = registers
        hwl.validate_offline()
        with hwl:
            hwl.write_batch(values_to_write, list(registers.values()))


if __name__ == "__main__":
    unittest.main()
