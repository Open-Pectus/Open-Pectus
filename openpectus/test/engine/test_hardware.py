from __future__ import annotations
import logging
import time
from typing import Any, Callable
import unittest

from openpectus.engine.hardware import (
    HardwareLayerBase,
    HardwareLayerException,
    Register,
    RegisterDirection,
)
from openpectus.engine.hardware_error import (
    ErrorRecoveryConfig,
    ErrorRecoveryDecorator,
    ErrorRecoveryState,
)
from openpectus.engine.models import ConnectionStatusEnum
from openpectus.test.engine.test_engine import TestHW, create_test_uod


FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format='%(asctime)-15s :: %(name)s :: %(levelname)-8s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', force=True)
#logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', force=True)
logger = logging.getLogger("openpectus.engine.hardware_error")
logger.setLevel(logging.DEBUG)



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


class TestHardwareErrorRecovery(unittest.TestCase):

    def create_hardware(
            self,
            connect_error_callback: Callable[[Exception], None] | None = None,
            error_callback:  Callable[[], None] | None = None,
            fail_callback:  Callable[[], None] | None = None,
            ) -> tuple[ErrorRecoveryDecorator, ErrorTestHardware]:

        def default_conn_cb(exception: Exception):
            pass

        def default_cb():
            pass

        connect_error_callback = connect_error_callback or default_conn_cb
        error_callback = error_callback or default_cb
        fail_callback = fail_callback or default_cb

        hwl = ErrorTestHardware()
        error_config = ErrorRecoveryConfig()
        #error_config.fail_timeout_seconds
        return ErrorRecoveryDecorator(hwl, error_config, connect_error_callback, error_callback, fail_callback), hwl


    def test_state_Disconnected_connect_ok_Connected(self):
        decorator, hwl = self.create_hardware()
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Disconnected)

        decorator.connect()

        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)
        self.assertEqual(decorator.get_connection_state(), ConnectionStatusEnum.Connected)
        # self.assertEqual(decorator.get_method_state_error(), False)

    def test_state_Disconnected_connect_error_Disconnected(self):
        decorator, hwl = self.create_hardware()
        hwl.connect_fail = True

        decorator.connect()
        self.assertEqual(decorator.get_connection_state(), ConnectionStatusEnum.Disconnected)
        # self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)
        # self.assertEqual(decorator.get_method_state_error(), False)

    def test_state_Disconnected_read_raises(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Disconnected
        reg_A = hwl.reg_A

        with self.assertRaises(HardwareLayerException):
            decorator.read(reg_A)
        with self.assertRaises(HardwareLayerException):
            decorator.read_batch([reg_A])

    def test_state_Failed_read_raises(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Failure
        reg_A = hwl.reg_A

        with self.assertRaises(HardwareLayerException):
            decorator.read(reg_A)
        with self.assertRaises(HardwareLayerException):
            decorator.read_batch([reg_A])

    def test_read_error_returns_last_known_good_value_masking_error(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()

        reg_A = hwl.reg_A
        hwl.reg_A_value = 3
        val_A = decorator.read(reg_A)
        self.assertEqual(val_A, 3)

        hwl.read_fail = True
        val_A_fail = decorator.read(reg_A)
        self.assertEqual(val_A_fail, 3)

    def test_read_error_in_state_OK_transitions_to_state_Issue(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)

        hwl.read_fail = True
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)

    def test_read_error_in_state_Issue_transitions_to_state_Error(self):
        decorator, hwl = self.create_hardware()
        decorator.config.error_timeout_seconds = 1
        decorator.config.fail_timeout_seconds = 2
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)

        time.sleep(1)

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Error)

    def test_read_error_in_state_Error_transitions_to_state_Failure(self):
        decorator, hwl = self.create_hardware()
        decorator.config.error_timeout_seconds = 1
        decorator.config.fail_timeout_seconds = 2
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        time.sleep(1)
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Error)

        time.sleep(1)

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Failure)

    def test_read_success_in_state_Issue_transitions_to_state_OK(self):
        decorator, hwl = self.create_hardware()
        decorator.config.error_timeout_seconds = 1
        decorator.config.fail_timeout_seconds = 2
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)

        hwl.read_fail = False
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)

    def test_read_success_in_state_Error_keeps_state_Error(self):
        decorator, hwl = self.create_hardware()
        decorator.config.error_timeout_seconds = 1
        decorator.config.fail_timeout_seconds = 2
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        time.sleep(1)
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Error)

        hwl.read_fail = False
        _ = decorator.read(hwl.reg_A)

        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Error)
    # Writes

    def test_state_Disconnected_write_raises(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Disconnected
        reg_B = hwl.reg_B

        with self.assertRaises(HardwareLayerException):
            decorator.write(3, reg_B)
        with self.assertRaises(HardwareLayerException):
            decorator.write_batch([4], [reg_B])

    def test_state_Failed_write_raises(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Failure
        reg_B = hwl.reg_B

        with self.assertRaises(HardwareLayerException):
            decorator.write(3, reg_B)
        with self.assertRaises(HardwareLayerException):
            decorator.write_batch([4], [reg_B])


    def test_failing_write_masks_error_and_adds_to_pending(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        decorator.state = ErrorRecoveryState.OK
        reg_B = hwl.reg_B
        hwl.reg_B_value = 2

        hwl.write_fail = True
        decorator.write(3, reg_B)  # error masked
        self.assertEqual(hwl.reg_B_value, 2)  # value not written
        self.assertEqual(decorator.pending_writes[reg_B], 3)  # value added to pending


    def test_write_ok_after_Issue_writes_pending_values(self):
        decorator, hwl = self.create_hardware()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Issue
        hwl.reg_B_value = 2
        decorator.pending_writes[hwl.reg_B] = 3

        # write succcesfully to another register
        decorator.write(7, hwl.reg_C)

        # applies the pending write to B
        self.assertEqual(hwl.reg_B_value, 3)

    def test_tag_HwErrorCount(self):
        pass


class ErrorTestHardware(HardwareLayerBase):
    """ A test hardware class that can fail its operations when so directed by the test"""
    def __init__(self) -> None:
        super().__init__()

        self.reg_A = self.registers["A"] = Register("A", RegisterDirection.Read)
        self.reg_B = self.registers["B"] = Register("B", RegisterDirection.Write)
        self.reg_C = self.registers["C"] = Register("C", RegisterDirection.Write)
        self.read_fail = False
        self.write_fail = False
        self.connect_fail = False
        self.disconnect_fail = False

        self.reg_A_value = 0
        self.reg_B_value = 0
        self.reg_C_value = 0

    def read(self, r: Register) -> Any:
        if self.read_fail:
            raise HardwareLayerException("Read failed as requested")
        if r.name == "A":
            return self.reg_A_value
        else:
            raise ValueError("Cannot read from register " + r.name)

    def write(self, value: Any, r: Register) -> None:
        if self.write_fail:
            raise HardwareLayerException("Write failed as requested")
        if r.name == "B":
            self.reg_B_value = value
        elif r.name == "C":
            self.reg_C_value = value
        else:
            raise ValueError("Cannot write to register " + r.name)

    def connect(self):
        if self.connect_fail:
            raise HardwareLayerException("Connect failed as requested")
        return super().connect()

    def disconnect(self):
        if self.disconnect_fail:
            raise HardwareLayerException("Disconnect failed as requested")
        return super().disconnect()


if __name__ == "__main__":
    unittest.main()
