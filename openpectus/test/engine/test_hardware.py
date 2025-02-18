from __future__ import annotations
import logging
import time
from typing import Any
import unittest

from openpectus.engine.hardware import (
    HardwareLayerBase,
    HardwareLayerException,
    Register,
    RegisterDirection,
)
from openpectus.engine.hardware_recovery import (
    ErrorRecoveryConfig,
    ErrorRecoveryDecorator,
    ErrorRecoveryState,
)
from openpectus.engine.models import ConnectionStatusEnum
from openpectus.lang.exec.tags import SystemTagName, create_system_tags
from openpectus.test.engine.test_engine import TestHW, create_test_uod


FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format='%(asctime)-15s :: %(name)s :: %(levelname)-8s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    force=True)
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

    def create_hardwares(self) -> tuple[ErrorRecoveryDecorator, ErrorTestHardware]:
        hwl = ErrorTestHardware()
        error_config = ErrorRecoveryConfig()
        system_tags = create_system_tags()
        connection_status_tag = system_tags[SystemTagName.CONNECTION_STATUS]
        return ErrorRecoveryDecorator(hwl, error_config, connection_status_tag), hwl

    def test_initial_state_Disconnected(self):
        decorator, hwl = self.create_hardwares()
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Disconnected)
        self.assertEqual(decorator.connection_status_tag.get_value(), ConnectionStatusEnum.Disconnected)

    def test_state_Disconnected_connect_ok_Connected(self):
        decorator, hwl = self.create_hardwares()
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Disconnected)

        decorator.connect()

        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)
        self.assertEqual(decorator.connection_status_tag.get_value(), ConnectionStatusEnum.Connected)

    def test_initialize_with_connected_hwl(self):
        hwl = ErrorTestHardware()
        hwl._is_connected = True
        error_config = ErrorRecoveryConfig()
        system_tags = create_system_tags()
        connection_status_tag = system_tags[SystemTagName.CONNECTION_STATUS]
        decorator = ErrorRecoveryDecorator(hwl, error_config, connection_status_tag)

        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)
        self.assertEqual(decorator.is_connected, True)

    def test_state_Disconnected_connect_error_Disconnected(self):
        decorator, hwl = self.create_hardwares()
        hwl.connect_fail = True

        with self.assertRaises(HardwareLayerException):
            decorator.connect()

        self.assertEqual(decorator.connection_status_tag.get_value(), ConnectionStatusEnum.Disconnected)

    def test_state_Disconnected_read_raises(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Disconnected
        reg_A = hwl.reg_A

        with self.assertRaises(HardwareLayerException):
            decorator.read(reg_A)
        with self.assertRaises(HardwareLayerException):
            decorator.read_batch([reg_A])

    def test_state_Error_read_raises(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Error
        reg_A = hwl.reg_A

        with self.assertRaises(HardwareLayerException):
            decorator.read(reg_A)
        with self.assertRaises(HardwareLayerException):
            decorator.read_batch([reg_A])

    def test_read_error_returns_last_known_good_value_masking_error(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()

        reg_A = hwl.reg_A
        hwl.reg_A_value = 3
        val_A = decorator.read(reg_A)
        self.assertEqual(val_A, 3)

        hwl.read_fail = True
        val_A_fail = decorator.read(reg_A)
        self.assertEqual(val_A_fail, 3)

    def test_read_error_in_state_OK_transitions_to_state_Issue(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)

        hwl.read_fail = True
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)

    def test_read_error_in_state_Issue_transitions_to_state_Reconnect(self):
        decorator, hwl = self.create_hardwares()
        decorator.config.reconnect_timeout_seconds = 1
        decorator.config.error_timeout_seconds = 2
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)

        time.sleep(1)

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Reconnect)
        self.assertEqual(decorator.connection_status_tag.get_value(), ConnectionStatusEnum.Connected)

    def test_read_in_state_Reconnect_transitions_to_state_Error_after_timeout(self):
        decorator, hwl = self.create_hardwares()
        decorator.config.reconnect_timeout_seconds = 1
        decorator.config.error_timeout_seconds = 1
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        time.sleep(1)
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Reconnect)

        time.sleep(1)

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Error)

    def test_read_success_in_state_Issue_transitions_to_state_OK(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Issue)

        hwl.read_fail = False
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.OK)

    def test_read_success_in_state_Reconnect_keeps_state_Reconnect(self):
        decorator, hwl = self.create_hardwares()
        decorator.config.reconnect_timeout_seconds = 1
        decorator.config.error_timeout_seconds = 1
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        _ = decorator.read(hwl.reg_A)
        time.sleep(1)
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Reconnect)

        hwl.read_fail = False
        _ = decorator.read(hwl.reg_A)

        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Reconnect)

    # Writes

    def test_state_Disconnected_write_raises(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Disconnected
        reg_B = hwl.reg_B

        with self.assertRaises(HardwareLayerException):
            decorator.write(3, reg_B)
        with self.assertRaises(HardwareLayerException):
            decorator.write_batch([4], [reg_B])

    def test_state_Error_write_raises(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Error
        reg_B = hwl.reg_B

        with self.assertRaises(HardwareLayerException):
            decorator.write(3, reg_B)
        with self.assertRaises(HardwareLayerException):
            decorator.write_batch([4], [reg_B])


    def test_failing_write_masks_error_and_adds_to_pending(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.OK
        reg_B = hwl.reg_B
        hwl.reg_B_value = 2

        hwl.write_fail = True
        decorator.write(3, reg_B)  # error masked
        self.assertEqual(hwl.reg_B_value, 2)  # value not written
        self.assertEqual(decorator.pending_writes[reg_B], 3)  # value added to pending


    def test_write_ok_in_state_Issue_writes_pending_values(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Issue
        hwl.reg_B_value = 2
        decorator.pending_writes[hwl.reg_B] = 3

        # write succcesfully to another register
        decorator.write(7, hwl.reg_C)

        # applies the pending write to B
        self.assertEqual(hwl.reg_B_value, 3)

    # Reconnect

    def test_reconnect_is_correctly_backed_off(self):
        decorator, hwl = self.create_hardwares()
        decorator.connect()
        decorator.state = ErrorRecoveryState.Reconnect

        # collect the ticks for which reconnect is called
        hwl.connect_fail = True  # make all reconnects fail
        reconnected_ticks = []
        decorator.reconnecting_callback = lambda : reconnected_ticks.append(decorator.reconnect_tick)

        largest = decorator.reconnect_backoff_ticks[-1]
        for _ in range(0, 2 * (largest + 1)):
            decorator.tick()

        expected_ticks = decorator.reconnect_backoff_ticks + [2 * largest]

        # because all reconnects fail, we collected all the backoff ticks
        self.assertEqual(reconnected_ticks, expected_ticks)

    def test_in_state_Reconnect_reconnect_is_automatically_performed_on_tick(self):
        decorator, hwl = self.create_hardwares()
        decorator.config.reconnect_timeout_seconds = 1
        decorator.config.error_timeout_seconds = 5
        decorator.connect()
        _ = decorator.read(hwl.reg_A)  # make last_known_good value available
        hwl.read_fail = True

        is_reconnecting = False

        def on_reconnecting():
            nonlocal is_reconnecting
            is_reconnecting = True
        decorator.on_reconnecting = on_reconnecting

        _ = decorator.read(hwl.reg_A)
        time.sleep(1)
        _ = decorator.read(hwl.reg_A)
        self.assertEqual(decorator.get_recovery_state(), ErrorRecoveryState.Reconnect)

        self.assertEqual(is_reconnecting, False)

        for _ in range(1 + decorator.reconnect_backoff_ticks[0]):
            decorator.tick()

        self.assertEqual(is_reconnecting, True)

    def test_registers_are_delegated(self):
        decorator, hwl = self.create_hardwares()
        self.assertEqual(hwl.reg_A, decorator.registers["A"])
        self.assertEqual(len(hwl.registers), len(decorator.registers))

    def test_methods_are_delegated(self):
        decorator, hwl = self.create_hardwares()
        # Since test hardware has this method, it should also be callable on the decorator. This is done using
        # method forwarding, implemented in ErrorRecoveryDecorator._setup_base_method_forwards()
        decorator.test_cmd()  # type: ignore

class ErrorTestHardware(HardwareLayerBase):
    __test__ = False
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

    def test_cmd(self):
        print("Test Cmd executed")

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
        self._is_connected = True

    def disconnect(self):
        # The order here is tricky. If it fails, we cannot reasonably know
        # whether self._is_connected is set and to what value. But when
        # we are using the decorator we don't use this value because the
        # decorator knows better.
        self._is_connected = False
        if self.disconnect_fail:
            raise HardwareLayerException("Disconnect failed as requested")


if __name__ == "__main__":
    unittest.main()
