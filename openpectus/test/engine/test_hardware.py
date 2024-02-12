import unittest

from openpectus.engine.hardware import HardwareLayerBase
from openpectus.test.engine.test_engine import TestHW, create_test_uod


class TestHardwareLayer(unittest.TestCase):
    def test_can_read_register(self):
        uod = create_test_uod()
        hwl: TestHW = uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        self.assertIsInstance(hwl, HardwareLayerBase)

        rFT01 = hwl.registers["FT01"]

        self.assertEqual(None, hwl.read(rFT01))
        hwl.register_values["FT01"] = 78

        self.assertEqual(78, hwl.read(rFT01))

    def test_can_write_register(self):
        uod = create_test_uod()
        hwl: TestHW = uod.hwl  # type: ignore

        rFT01 = hwl.registers["FT01"]

        hwl.write("foo", rFT01)

        self.assertEqual("foo", hwl.register_values["FT01"])


if __name__ == "__main__":
    unittest.main()
