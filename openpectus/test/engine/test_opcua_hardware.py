import logging
import unittest
from openpectus.engine.hardware import Register, RegisterDirection
from openpectus.engine.opcua_hardware import OPCUA_Hardware


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger("openpectus.engine.opcua_hardware.OPCUA_Hardware")
logger.setLevel(logging.DEBUG)


class TestOPCUAHardware(unittest.TestCase):
    def test_can_connect(self):
        hw = OPCUA_Hardware()
        hw.connect()
        # TODO somehow manually verify that the hardware was connected

    def test_can_read_register(self):
        hwl = OPCUA_Hardware()
        ft01 = Register("FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
        hwl.registers[ft01.name] = ft01

        # TODO verify that value can be read
        self.assertEqual(87, hwl.read(ft01))

    def test_can_write_register(self):
        hwl = OPCUA_Hardware()
        ft01 = Register("FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
        hwl.registers[ft01.name] = ft01

        # TODO write some value to hardware
        # hwl.write("some string", ft01)
        # hwl.write(87, ft01)

        # TODO somehow manually verify that the hardware received the value

        # NOTE: to run a single test from the command line, use
        # python -m unittest -k TestOPCUAHardware.test_can_write_register


if __name__ == "__main__":
    unittest.main()
