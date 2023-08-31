import logging
import threading
import time
from typing import Any, List
from typing_extensions import override
import unittest

from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder
from openpectus.engine.eng import ExecutionEngine, CommandRequest, EngineInternalCommand, RunLogItemState
from openpectus.lang.exec import tags
from openpectus.lang.exec.uod import UodCommand
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger("Engine")
logger.setLevel(logging.DEBUG)


def create_test_uod() -> UnitOperationDefinitionBase:

    def reset(cmd: UodCommand, args: List[Any]) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset")
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A")
            cmd.set_complete()

    def overlap_exec(cmd: UodCommand, args: List[Any]) -> None:
        count = cmd.get_iteration_count()
        if count >= 9:
            cmd.set_complete()

    # TODO def exec_with_args()

    return (
        UodBuilder()
        .with_instrument("TestUod")
        .with_hardware(TestHW())
        .with_hardware_register(
            "FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
        .with_hardware_register(
            "Reset",
            RegisterDirection.Both,
            path="Objects;2:System;2:RESET",
            from_tag=lambda x: 1 if x == "Reset" else 0,
            to_tag=lambda x: "Reset" if x == 1 else "N/A",
        )
        # Readings
        .with_new_system_tags()
        .with_tag(tags.Reading("FT01", "L/h"))
        .with_tag(tags.Select("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_command(UodCommand.builder().with_name("overlap1").with_exec_fn(overlap_exec))
        .with_command(UodCommand.builder().with_name("overlap2").with_exec_fn(overlap_exec))
        .with_command_overlap(['overlap1', 'overlap2'])
        .build()
    )


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


def print_runlog(e: ExecutionEngine):
    print("Run Log:")
    for item in e.runlog.get_items():
        print(f" {item.start_tick}-{item.end_tick}  {item.command_req.name}  {', '.join(s.value for s in item.states)}")


def create_engine() -> ExecutionEngine:
    uod = create_test_uod()
    e = ExecutionEngine(uod)
    e._configure()
    return e


class TestEngine(unittest.TestCase):
    def test_create_engine(self):
        uod = create_test_uod()
        e = ExecutionEngine(uod)
        self.assertIsNotNone(e)

    def test_configure_uod(self):
        uod = create_test_uod()
        e = ExecutionEngine(uod)
        e._configure()

        self.assertTrue(len(uod.command_factories) > 0)
        self.assertTrue(len(uod.instrument) > 0)
        self.assertTrue(len(uod.tags) > 0)

    @unittest.skip("not implemented")
    def test_uod_reading_to_process_values(self):
        uod = create_test_uod()
        e = ExecutionEngine(uod)
        e._configure()

        # assert process values match the defined readings

    @unittest.skip("not implemented")
    def test_load_uod(self):
        pass

    def test_engine_start(self):
        e = create_engine()

        t = threading.Thread(target=e.run)
        t.daemon = True
        t.start()

        time.sleep(1)
        e._running = False
        t.join()

    def test_engine_started_runs_scan_cycle(self):
        e = create_engine()

        t = threading.Thread(target=e._run, daemon=True)  # dont configure twice
        t.start()

        # assert loop running
        time.sleep(0.5)
        self.assertTrue(e._running)

        time.sleep(0.5)
        e._running = False
        t.join()

    def test_read_process_image_marks_assigned_tags_dirty(self):
        e = create_engine()

        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        # set non-default values to trigger notification
        hwl.register_values["FT01"] = 1
        hwl.register_values["Reset"] = 1

        e.read_process_image()

        # assert tags marked dirty
        dirty_names = e._tag_names_dirty
        self.assertTrue("FT01" in dirty_names)
        self.assertTrue("Reset" in dirty_names)

    def test_execute_command_marks_assigned_tags_dirty(self):
        e = create_engine()

        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        req = CommandRequest("Reset", None)
        e.cmd_queue.put(req)
        e.execute_commands()

        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        # assert tags marked dirty
        dirty_names = e._tag_names_dirty
        self.assertTrue("Reset" in dirty_names)

    def test_read_process_image_sets_assigned_tag_values(self):
        e = create_engine()

        # set hw values
        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        hwl.register_values["FT01"] = 87
        hwl.register_values["Reset"] = 0

        # assert values read
        e.read_process_image()
        # numerical value is set
        self.assertEqual(87, e.uod.tags["FT01"].get_value())
        # mapped value is set
        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

    def test_notify_tag_updates_publishes_dirty_tag(self):
        e = create_engine()
        t = e.uod.tags["FT01"]
        e._uod_listener.notify_change(t.name)

        e.notify_tag_updates()

        self.assertEqual(1, e.tag_updates.qsize())
        t_updated = e.tag_updates.get()
        self.assertEqual(t_updated.name, t.name)

    def test_write_process_values_writed_data_to_registers(self):
        e = create_engine()

        # set hw values
        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        hwl.register_values["FT01"] = 87

        # assert values read
        e.read_process_image()
        self.assertEqual(87, e.uod.tags["FT01"].get_value())

        # modify tag values
        e.uod.tags["FT01"].set_value(22)
        e.uod.tags["Reset"].set_value("Reset")

        e.write_process_image()

        # assert values written to registers
        self.assertEqual(22, hwl.register_values["FT01"])
        self.assertEqual(1, hwl.register_values["Reset"])

    def test_uod_command_can_execute_valid_command(self):
        e = create_engine()

        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        req = CommandRequest("Reset", None)
        e._execute_command(req)

        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

    def test_uod_commands_multiple_iterations(self):
        e = create_engine()

        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        e.schedule_execution("Reset", "")

        e.tick()
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        e.tick()
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        e.tick()
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        e.tick()
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        e.tick()
        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        e.tick()
        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        print_runlog(e)

    def test_concurrent_uod_commands(self):
        e = create_engine()

        e.schedule_execution("Reset", "")
        e.tick()

        e.schedule_execution("Reset", "")
        e.tick()

        runlog = list(e.runlog.get_items())
        self.assertEqual(2, len(runlog))

        print_runlog(e)

        self.assertEqual("Reset", runlog[0].command_req.name)
        self.assertTrue(RunLogItemState.Started in runlog[0].states)
        self.assertTrue(RunLogItemState.Cancelled in runlog[0].states)
        self.assertTrue(RunLogItemState.Forced not in runlog[0].states)
        self.assertTrue(RunLogItemState.Completed not in runlog[0].states)

        self.assertEqual("Reset", runlog[1].command_req.name)
        self.assertTrue(RunLogItemState.Started in runlog[1].states)
        self.assertTrue(RunLogItemState.Completed not in runlog[1].states)
        self.assertTrue(RunLogItemState.Cancelled not in runlog[1].states)
        self.assertTrue(RunLogItemState.Forced not in runlog[1].states)

        for _ in range(10):
            e.tick()

        self.assertTrue(RunLogItemState.Completed in runlog[1].states)

        print_runlog(e)        

    def test_overlapping_uod_commands(self):
        e = create_engine()

        e.schedule_execution("overlap1", "")
        e.tick()

        e.schedule_execution("overlap2", "")
        e.tick()

        runlog = list(e.runlog.get_items())
        self.assertEqual(2, len(runlog))

        print_runlog(e)

        self.assertEqual("overlap1", runlog[0].command_req.name)
        self.assertTrue(RunLogItemState.Started in runlog[0].states)
        self.assertTrue(RunLogItemState.Cancelled in runlog[0].states)
        self.assertTrue(RunLogItemState.Forced not in runlog[0].states)
        self.assertTrue(RunLogItemState.Completed not in runlog[0].states)

        self.assertEqual("overlap2", runlog[1].command_req.name)
        self.assertTrue(RunLogItemState.Started in runlog[1].states)
        self.assertTrue(RunLogItemState.Completed not in runlog[1].states)
        self.assertTrue(RunLogItemState.Cancelled not in runlog[1].states)
        self.assertTrue(RunLogItemState.Forced not in runlog[1].states)

        for _ in range(10):
            e.tick()

        self.assertTrue(RunLogItemState.Completed in runlog[1].states)

        print_runlog(e)

    def test_internal_command_can_execute_valid_command(self):
        e = create_engine()

        self.assertEqual(0, e._system_tags["RUN COUNTER"].get_value())

        e.schedule_execution("INCREMENT RUN COUNTER", "")
        e.tick()

        self.assertEqual(1, e._system_tags["RUN COUNTER"].get_value())

        print_runlog(e)

    @unittest.skip("not implemented")
    def test_internal_commands_multiple_iterations(self):
        raise NotImplementedError()

    def test_clocks(self):
        e = create_engine()

        self.assertTrue(e._system_tags.has("Clock"))

        # raise NotImplementedError()

    @unittest.skip("not implemented")
    def test_set_program(self):
        raise NotImplementedError()

    @unittest.skip("not implemented, needs input")
    def test_get_status(self):
        # program progress
        # status that enable ProcessUnit:
        # name, state=ProcessUnitState (READY, IN_PROGRESS , NOT_ONLINE) , location="H21.5", runtime_msec=189309,
        raise NotImplementedError()

    def test_get_runlog(self):
        e = create_engine()

        e.cmd_queue.put(CommandRequest("START"))
        e.tick()

        self.assertEqual(1, len(e.runlog._items))

    def test_runstate_start(self):
        e = create_engine()

        e.cmd_queue.put(CommandRequest("START"))
        e.tick()

        self.assertTrue(e._runstate_started)

    def test_clocks_start_stop(self):
        e = create_engine()

        clock = e._system_tags.get(tags.DEFAULT_TAG_CLOCK)
        self.assertEqual(0.0, clock.as_number())

        e._runstate_started = True
        e.tick()

        clock_value = clock.as_number()
        self.assertGreater(clock_value, 0.0)

        e._runstate_started = False
        e.tick()

        self.assertEqual(clock_value, clock.as_number())

    def test_runstate_stop(self):
        e = create_engine()
        e.cmd_queue.put(CommandRequest("START"))
        e.tick()
        self.assertTrue(e._runstate_started)

        e.cmd_queue.put(CommandRequest("STOP"))
        e.tick()
        self.assertFalse(e._runstate_started)

    @unittest.skip("not implemented")
    def test_runstate_pause(self):
        raise NotImplementedError()

    @unittest.skip("not implemented")
    def test_runstate_unpause(self):
        raise NotImplementedError()

    @unittest.skip("not implemented")
    def test_runstate_hold(self):
        raise NotImplementedError()

    @unittest.skip("not implemented")
    def test_runstate_unhold(self):
        raise NotImplementedError()

    @unittest.skip("not implemented")
    def test_safe_values(self):
        raise NotImplementedError()

    def test_enum_has(self):
        self.assertTrue(EngineInternalCommand.has_value("STOP"))
        self.assertFalse(EngineInternalCommand.has_value("stop"))


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


# TODO remove once tests are green
# class TestUod(UnitOperationDefinitionBase):
#     def __init__(self) -> None:
#         super().__init__()

#         self.define_instrument("TestUod")
#         self.define_hardware_layer(TestHW())

#         self.define_register(
#             "FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01"
#         )
#         self.define_register(
#             "Reset",
#             RegisterDirection.Both,
#             path="Objects;2:System;2:RESET",
#             from_tag=lambda x: 1 if x == "Reset" else 0,
#             to_tag=lambda x: "Reset" if x == 1 else "N/A",
#         )

#         self.define_tag(tags.Reading("FT01", "L/h"))
#         self.define_tag(
#             tags.Select("Reset", value="N/A", unit=None, choices=["Reset", "N/A"])
#         )

#         # self.define_io('VA01', {'path': 'Objects;2:System;2:VA01', 'fn': self.valve_fn})
#         # self.define_io('VA02', {'path': 'Objects;2:System;2:VA02', 'fn': self.valve_fn})
#         # self.define_io('PU01', {'path': 'Objects;2:System;2:PU01', 'fn': self.pu_fn})
#         # self.define_io('FT01', {'path': 'Objects;2:System;2:FT01'})
#         # self.define_io('TT01', {'path': 'Objects;2:System;2:TT01'})
#         # self.define_io('Reset', {'path': 'Objects;2:System;2:RESET', 'fn': lambda x: 1 if x == 'Reset' else 0})

#         # self.define_command(UodCommand.builder()
#         #                     .with_name("Reset")
#         #                     .with_exec_fn(self.reset)
#         #                     .build())

#         #self.define_command(ResetCommand())

#         self.define_command(
#             UodCommand.builder().with_name("Foo").with_exec_fn(self.exec_foo).build()
#         )

#     def exec_foo(cmd: UodCommand, args: List[Any], uod: UnitOperationDefinitionBase):
#         cmd = uod.get_command("Foo")
#         if cmd is None:
#             raise ValueError("command Foo not found")

#         if cmd.iterations > 3:
#             cmd.is_complete = True
#             # cmd.reset()

#     # def valve_fn(self, x: int | float) -> bool:
#     #     return x > 0

#     # def pu_fn(self, x: int | float) -> float:
#     #     return min(max(x/100, 0), 1)

#     # def reset_fn(self, x: str) -> int:
#     #     return 1 if x == 'Reset' else 0

#     # def _va01(self, state, io): io.fields['VA01'].write(self.valve); self.progress = True
#     # def _va02(self, state, io): io.fields['VA02'].write(self.valve); self.progress = True
#     # def _pu01(self, state, io): io.fields['PU01'].write(self.speed); self.progress = True
#     # def reset(self, args, uod):
#     #     cmd = self.get_command('Reset')
#     #     assert isinstance(cmd, UodCommand)
#     #     if cmd.iterations == 0:
#     #         # io.fields['Reset'].write('Reset');
#     #         self.tags.get("Reset").set_value('Reset')
#     #     elif cmd.iterations == 5:
#     #         # io.fields['Reset'].write('N/A');
#     #         self.tags.get("Reset").set_value('N/A')
#     #         self.progress = True
#     #     for e in locals().copy():
#     #         if '_' in e:
#     #             setattr(self, e, locals()[e])


# class ResetCommand(UodCommand):
#     def __init__(self) -> None:
#         super().__init__()
#         self.name = "Reset"
#         self.is_complete = False

#     def execute(self, args: List[Any], uod: UnitOperationDefinitionBase) -> None:
#         if self.iterations == 0:
#             uod.tags.get("Reset").set_value("Reset")
#         elif self.iterations == 5:
#             uod.tags.get("Reset").set_value("N/A")
#             self.is_complete = True
#             self.iterations = 0


if __name__ == "__main__":
    unittest.main()
