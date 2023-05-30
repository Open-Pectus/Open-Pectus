import threading
import time
from typing import Any, List
from typing_extensions import override
import unittest

from lang.exec.uod import UnitOperationDefinitionBase
from engine.engine import Engine, EngineCommand
from lang.exec import tags
from lang.exec.uod import UodCommand
from engine.hardware import HardwareLayerBase, Register, RegisterDirection


class TestHardwareLayer(unittest.TestCase):
    def test_can_read_register(self):
        uod = TestUod()
        uod.define()
        hwl: TestHW = uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        self.assertIsInstance(hwl, HardwareLayerBase)

        rFT01 = hwl.registers['FT01']

        self.assertEqual(None, hwl.read(rFT01))
        hwl.register_values['FT01'] = 78

        self.assertEqual(78, hwl.read(rFT01))

    def test_can_write_register(self):
        uod = TestUod()
        uod.define()
        hwl: TestHW = uod.hwl  # type: ignore

        rFT01 = hwl.registers['FT01']

        hwl.write('foo', rFT01)

        self.assertEqual('foo', hwl.register_values['FT01'])


def create_engine() -> Engine:
    uod = TestUod()
    e = Engine(uod)
    e._configure()
    return e


class TestEngine(unittest.TestCase):
    def test_create_engine(self):
        uod = TestUod()
        e = Engine(uod)
        self.assertIsNotNone(e)

    def test_configure_uod(self):
        uod = TestUod()
        e = Engine(uod)
        e._configure()

        self.assertEqual(1, len(uod.commands))
        self.assertTrue(len(uod.instrument) > 0)
        self.assertTrue(len(uod.tags) > 0)

    @unittest.skip("not implemented")
    def test_load_uod(self):
        pass

    def test_engine_start(self):
        e = create_engine()

        t = threading.Thread(target=e.run)
        t.setDaemon(True)
        t.start()

        time.sleep(1)
        e.started = False
        t.join()

    def test_read_process_image_marks_assigned_tags_dirty(self):
        e = create_engine()

        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        # set non-default values to trigger notification
        hwl.register_values['FT01'] = 1
        hwl.register_values['Reset'] = 1

        e.read_process_image()

        # assert tags marked dirty
        dirty_names = e._tag_names_dirty
        self.assertTrue("FT01" in dirty_names)
        self.assertTrue("Reset" in dirty_names)

    def test_execute_command_marks_assigned_tags_dirty(self):
        e = create_engine()

        self.assertEqual("N/A", e.uod.tags['Reset'].get_value())

        req = EngineCommand("Reset", None)
        e.cmd_queue.put(req)
        e.execute_commands()

        self.assertEqual("Reset", e.uod.tags['Reset'].get_value())

        # assert tags marked dirty
        dirty_names = e._tag_names_dirty
        self.assertTrue("Reset" in dirty_names)

    def test_read_process_image_sets_assigned_tag_values(self):
        e = create_engine()

        # set hw values
        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        hwl.register_values['FT01'] = 87
        hwl.register_values['Reset'] = 0

        # assert values read
        e.read_process_image()
        # numerical value is set
        self.assertEqual(87, e.uod.tags['FT01'].get_value())
        # mapped value is set
        self.assertEqual("N/A", e.uod.tags['Reset'].get_value())

    def test_notify_tag_updates_publishes_dirty_tag(self):
        e = create_engine()
        t = e.uod.tags['FT01']
        e._tag_names_dirty.append(t.name)

        e.notify_tag_updates()

        self.assertEqual(1, e.tag_updates.qsize())
        t_updated = e.tag_updates.get()
        self.assertEqual(t_updated.name, t.name)

    def test_write_process_values_writed_data_to_registers(self):
        e = create_engine()

        # set hw values
        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        hwl.register_values['FT01'] = 87

        # assert values read
        e.read_process_image()
        self.assertEqual(87, e.uod.tags['FT01'].get_value())

        # modify tag values
        e.uod.tags['FT01'].set_value(22)
        e.uod.tags['Reset'].set_value("Reset")

        e.write_process_image()

        # assert values written to registers
        self.assertEqual(22, hwl.register_values['FT01'])
        self.assertEqual(1, hwl.register_values['Reset'])

    def test_uod_command_can_execute_valid_command(self):
        e = create_engine()

        self.assertEqual("N/A", e.uod.tags['Reset'].get_value())

        req = EngineCommand("Reset", None)
        e._execute_command(req)

        self.assertEqual("Reset", e.uod.tags['Reset'].get_value())

    @unittest.skip("not implemented")
    def test_uod_commands_multiple_iterations(self):
        pass

    @unittest.skip("not implemented")
    def test_overlapping_uod_commands(self):
        pass

    @unittest.skip("not implemented")
    def test_internal_command_can_execute_valid_command(self):
        e = create_engine()

        req = EngineCommand("INCREMENT RUN COUNTER", None)
        e._execute_command(req)

    @unittest.skip("not implemented")
    def test_internal_commands_multiple_iterations(self):
        pass

    @unittest.skip("not implemented")
    def test_clocks(self):
        pass

    @unittest.skip("not implemented")
    def test_set_program(self):
        pass

    @unittest.skip("not implemented, needs input")
    def test_get_status(self):
        # program progress
        # status that enable ProcessUnit:
        # name, state=ProcessUnitState (READY, IN_PROGRESS , NOT_ONLINE) , location="H21.5", runtime_msec=189309,
        pass

    @unittest.skip("not implemented")
    def test_get_runlog(self):
        pass

    @unittest.skip("not implemented")
    def test_runstate_stop(self):
        pass

    @unittest.skip("not implemented")
    def test_runstate_start(self):
        pass

    @unittest.skip("not implemented")
    def test_runstate_pause(self):
        pass

    @unittest.skip("not implemented")
    def test_runstate_unpause(self):
        pass

    @unittest.skip("not implemented")
    def test_runstate_hold(self):
        pass

    @unittest.skip("not implemented")
    def test_runstate_unhold(self):
        pass


# Test helpers


class TestHW(HardwareLayerBase):
    def __init__(self) -> None:
        super().__init__()
        self.register_values = {}

    @override
    def read(self, r: Register) -> Any:
        if r.name in self.registers.keys() and r.name in self.register_values.keys():
            return self.register_values[r.name]
        return None

    @override
    def write(self, value: Any, r: Register):
        if r.name in self.registers.keys():
            self.register_values[r.name] = value


# TODO define a builder pattern for this
# Consider using https://peps.python.org/pep-0544/#callback-protocols for the callbacks


class TestUod(UnitOperationDefinitionBase):
    def define(self):
        self.define_instrument("TestUod")
        self.define_hardware_layer(TestHW())

        self.define_register("FT01", RegisterDirection.Both, path='Objects;2:System;2:FT01')
        self.define_register("Reset", RegisterDirection.Both, path='Objects;2:System;2:RESET',
                             from_tag=lambda x: 1 if x == 'Reset' else 0,
                             to_tag=lambda x: "Reset" if x == 1 else "N/A")

        self.define_tag(tags.Reading("FT01", "L/h"))
        self.define_tag(tags.Select("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))

        # self.define_io('VA01', {'path': 'Objects;2:System;2:VA01', 'fn': self.valve_fn})
        # self.define_io('VA02', {'path': 'Objects;2:System;2:VA02', 'fn': self.valve_fn})
        # self.define_io('PU01', {'path': 'Objects;2:System;2:PU01', 'fn': self.pu_fn})
        # self.define_io('FT01', {'path': 'Objects;2:System;2:FT01'})
        # self.define_io('TT01', {'path': 'Objects;2:System;2:TT01'})
        # self.define_io('Reset', {'path': 'Objects;2:System;2:RESET', 'fn': lambda x: 1 if x == 'Reset' else 0})

        # self.define_command(UodCommand.builder()
        #                     .with_name("Reset")
        #                     .with_exec_fn(self.reset)
        #                     .build())

        self.define_command(ResetCommand())

    # def valve_fn(self, x: int | float) -> bool:
    #     return x > 0

    # def pu_fn(self, x: int | float) -> float:
    #     return min(max(x/100, 0), 1)

    # def reset_fn(self, x: str) -> int:
    #     return 1 if x == 'Reset' else 0

    # def _va01(self, state, io): io.fields['VA01'].write(self.valve); self.progress = True
    # def _va02(self, state, io): io.fields['VA02'].write(self.valve); self.progress = True
    # def _pu01(self, state, io): io.fields['PU01'].write(self.speed); self.progress = True
    # def reset(self, args, uod):
    #     cmd = self.get_command('Reset')
    #     assert isinstance(cmd, UodCommand)
    #     if cmd.iterations == 0:
    #         # io.fields['Reset'].write('Reset');
    #         self.tags.get("Reset").set_value('Reset')
    #     elif cmd.iterations == 5:
    #         # io.fields['Reset'].write('N/A');
    #         self.tags.get("Reset").set_value('N/A')
    #         self.progress = True
    #     for e in locals().copy():
    #         if '_' in e:
    #             setattr(self, e, locals()[e])


class ResetCommand(UodCommand):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Reset"
        self.is_complete = False

    def execute(self, args: List[Any], uod: UnitOperationDefinitionBase) -> None:
        if self.iterations == 0:
            uod.tags.get("Reset").set_value("Reset")
        elif self.iterations == 5:
            uod.tags.get("Reset").set_value("N/A")
            self.is_complete = True
            self.iterations = 0


if __name__ == "__main__":
    unittest.main()
