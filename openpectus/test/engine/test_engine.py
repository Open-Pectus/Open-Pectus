import logging
import threading
import time
from typing import Any, List
from typing_extensions import override
import unittest

import pint
from openpectus.lang.exec.runlog import RuntimeRecordStateEnum
from openpectus.lang.exec.timer import NullTimer

from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder
from openpectus.engine.eng import ExecutionEngine, EngineCommandEnum, SystemStateEnum
from openpectus.lang.exec import tags
from openpectus.lang.exec.uod import UodCommand
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger("Engine")
logger.setLevel(logging.DEBUG)

logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)

# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 sec")


def run_engine(engine: ExecutionEngine, pcode: str, max_ticks: int = -1):
    print("Interpretation started")
    ticks = 0
    max_ticks = max_ticks

    engine._running = True
    engine.set_program(pcode)
    engine.schedule_execution("Start")

    while engine.is_running():
        ticks += 1
        if max_ticks != -1 and ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            return

        time.sleep(0.1)
        engine.tick()


def continue_engine(engine: ExecutionEngine, max_ticks: int = -1):
    # This function (as well as run_engine) differs from just calling engine.tick() in that
    # it passes the time before calling tick(). Some functionality depends on this, such as
    # thresholds.

    # TODO consider adding a SystemClock abstraction to avoid the need for waiting
    # in tests
    print("Interpretation continuing")
    ticks = 0
    max_ticks = max_ticks

    engine._running = True

    while engine.is_running():
        ticks += 1
        if max_ticks != -1 and ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            return

        time.sleep(0.1)
        engine.tick()


def get_queue_items(q) -> list[tags.Tag]:
    items = []
    while not q.empty():
        items.append(q.get())
    return items


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
        .with_tag(tags.Tag("Danger", True, None, tags.TagDirection.OUTPUT, False))
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


def print_runlog(e: ExecutionEngine, description=""):
    runlog = e.interpreter.runtimeinfo.get_runlog()
    print(f"Runlog {runlog.id} records: ", description)
#    print("line | start | end   | name                 | states")
#    print("-----|-------|-------|----------------------|-------------------")
    for item in runlog.items:
        name = f"{str(item.name):<20}"
        prog = f"{item.progress:d2}" if item.progress else ""
        print(f"{name}   {item.state:<15}    {prog}")
#    print("-----|-------|-------|----------------------|-------------------")


def print_runtime_records(e: ExecutionEngine, description: str = ""):
    records = e.interpreter.runtimeinfo.records
    print("Runtime records: ", description)
    print("line | start | end   | name                 | states")
    print("-----|-------|-------|----------------------|-------------------")
    for r in records:
        name = f"{str(r.name):<20}" if r.name is not None else f"{str(r.node):<20}"
        line = f"{int(r.node.line):4d}" if r.node.line is not None else "   -"
        states = ", ".join([f"{st.state_name}: {st.state_tick}" for st in r.states])
        end = f"{r.visit_end_tick:5d}" if r.visit_end_tick != -1 else "    -"
        print(f"{line}   {r.visit_start_tick:5d}   {end}   {name}   {states}")
    print("-----|-------|-------|----------------------|-------------------")


def create_engine() -> ExecutionEngine:
    uod = create_test_uod()
    e = ExecutionEngine(uod)
    e._tick_timer = NullTimer()
    e._configure()
    return e


class TestEngineSetup(unittest.TestCase):

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


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine: ExecutionEngine = create_engine()

    def tearDown(self):
        self.engine.cleanup()

    def test_engine_start(self):
        e = self.engine

        t = threading.Thread(target=e.run)
        t.daemon = True
        t.start()

        time.sleep(1)
        e._running = False
        t.join()

    def test_engine_started_runs_scan_cycle(self):
        e = self.engine

        t = threading.Thread(target=e._run, daemon=True)  # dont configure twice
        t.start()

        # assert loop running
        time.sleep(0.5)
        self.assertTrue(e._running)

        time.sleep(0.5)
        e._running = False
        t.join()

    def test_read_process_image_marks_assigned_tags_dirty(self):
        e = self.engine

        hwl: TestHW = e.uod.hwl  # type: ignore
        self.assertIsInstance(hwl, TestHW)
        # set non-default values to trigger notification
        hwl.register_values["FT01"] = 1
        hwl.register_values["Reset"] = 1

        run_engine(e, "", 1)

        # assert tags marked dirty
        dirty_names = [t.name for t in get_queue_items(e.tag_updates)]
        self.assertTrue("FT01" in dirty_names)
        self.assertTrue("Reset" in dirty_names)

    def test_execute_command_marks_assigned_tags_dirty(self):
        e = self.engine

        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        run_engine(e, "Reset", 3)

        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        # assert tags marked dirty
        dirty_names = [t.name for t in get_queue_items(e.tag_updates)]
        self.assertTrue("Reset" in dirty_names)

    def test_read_process_image_sets_assigned_tag_values(self):
        e = self.engine

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
        e = self.engine
        t = e.uod.tags["FT01"]
        e._uod_listener.notify_change(t.name)

        e.notify_tag_updates()

        self.assertEqual(1, e.tag_updates.qsize())
        t_updated = e.tag_updates.get()
        self.assertEqual(t_updated.name, t.name)

    def test_write_process_values_writes_data_to_registers(self):
        e = self.engine

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
        e = self.engine
        run_engine(e, "", 3)
        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        e.inject_code("Reset")
        continue_engine(e, 1)

        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

    def test_uod_commands_multiple_iterations(self):
        e = self.engine

        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        run_engine(e, "Reset", 2)
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        # Reset takes 3 ticks to revert
        continue_engine(e, 3)
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        continue_engine(e, 1)
        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        continue_engine(e, 25)
        self.assertEqual("N/A", e.uod.tags["Reset"].get_value())

        print_runtime_records(e)
        print_runlog(e)

    def test_concurrent_uod_commands(self):
        e = self.engine
        run_engine(e, """
Reset
Reset
""", 5)

        records = e.interpreter.runtimeinfo.records

        print_runtime_records(e)

        r = records[2]
        self.assertEqual("Reset", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Cancelled))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        r = records[3]
        self.assertEqual("Reset", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Cancelled))        
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        continue_engine(e, 3)
        print_runtime_records(e)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Completed))

    def test_overlapping_uod_commands(self):
        e = self.engine
        run_engine(e, """
overlap1
overlap2
""", 5)

        rs = e.runtimeinfo.records

        print_runtime_records(e)

        r = rs[2]
        self.assertEqual("overlap1", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Cancelled))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Forced))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        continue_engine(e, 1)
        print_runtime_records(e)

        r = rs[3]
        self.assertEqual("overlap2", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Cancelled))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Forced))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        continue_engine(e, 1)
        print_runtime_records(e)

        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        print_runlog(e)

    def test_runlog_block(self):
        program = """
Block: A
    End Block
Mark: X
"""
        e = self.engine
        run_engine(e, program, 3)

        rs = e.runtimeinfo.records

        print_runtime_records(e)

        self.assertEqual(3, len(rs))
        self.assertEqual("Block: A", rs[2].name)
        self.assertFalse(rs[0].has_state(RuntimeRecordStateEnum.Started))

        continue_engine(e, 1)
        self.assertTrue(rs[2].has_state(RuntimeRecordStateEnum.Started))

        continue_engine(e, 1)
        self.assertTrue(rs[2].has_state(RuntimeRecordStateEnum.Completed))

        print_runtime_records(e)

    def test_runlog_watch(self):
        program = """
Watch: Block Time > 0.2s
    Mark: A
Mark: X
"""
        e = self.engine
        run_engine(e, program, 4)

        print_runtime_records(e)

        r = e.interpreter.runtimeinfo.records[2]
        self.assertEqual("Watch: Block Time > 0.2s", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.AwaitingInterrrupt))
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.AwaitingCondition))
        self.assertFalse(r.has_state(RuntimeRecordStateEnum.Started))

        continue_engine(e, 1)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))

        continue_engine(e, 1)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Completed))

        print_runtime_records(e)

    def test_runlog_uod_commands(self):
        e = self.engine
        run_engine(e, """
Reset
Reset
Reset
""", 10)
        
        print_runtime_records(e)

    @unittest.skip("Not implemented yet")
    def test_runlog_watch_forced(self):
        # TODO how do we represent the instruction we want to force?
        # user picks a runlog line to force
        # - how do we get to cmd or node from that?
        # - line number? or we assign uuids to entries?
        # - how about a modified program? should use version numbers
        #   to handle program modifications and runlog implications

        raise NotImplementedError()

    def test_internal_command_can_execute_valid_command(self):
        e = self.engine

        self.assertEqual(0, e._system_tags["Run Counter"].get_value())

        e.schedule_execution("Start")
        e.tick()

        e.schedule_execution("Increment run counter")
        e.tick()

        self.assertEqual(1, e._system_tags["Run Counter"].get_value())

        print_runlog(e)

    def test_clocks(self):
        e = self.engine

        self.assertTrue(e._system_tags.has("Clock"))

        # raise NotImplementedError()

    def test_set_and_run_program(self):
        program = """
Mark: A
Mark: B
Mark: C
"""
        e = self.engine
        run_engine(e, program, 10)

        self.assertEqual(['A', 'B', 'C'], e.interpreter.get_marks())

    def test_set_and_continue_program(self):
        program = """
Mark: A
"""
        e = self.engine
        run_engine(e, program, 10)
        self.assertEqual(['A', ], e.interpreter.get_marks())

        program = """
Mark: B
Mark: C
"""
        e.set_program(program)
        continue_engine(e, 10)

        self.assertEqual(['B', 'C'], e.interpreter.get_marks())

    @unittest.skip("not implemented, needs input")
    def test_get_status(self):
        # program progress
        # status that enable ProcessUnit:
        # name, state=ProcessUnitState (READY, IN_PROGRESS , NOT_ONLINE) , location="H21.5", runtime_msec=189309,
        raise NotImplementedError()

    def test_get_runlog(self):
        e = self.engine
        run_engine(e, "Reset", 3)

        print_runtime_records(e)

        items = e.get_runlog().items
        self.assertEqual(1, len(items))
        self.assertEqual("Reset", items[0].name)

        # assert has tags
        for item in items:
            start_values = item.start_values
            assert start_values is not None
            self.assertTrue(start_values.has("Base"))

    def test_runstate_start(self):
        e = self.engine

        e.schedule_execution("Start")
        e.tick()

        self.assertTrue(e._runstate_started)

    def test_clocks_start_stop(self):
        e = self.engine

        clock = e._system_tags.get(tags.DEFAULT_TAG_CLOCK)
        self.assertEqual(0.0, clock.as_number())

        e._runstate_started = True
        e.tick()

        clock_value = clock.as_number()
        self.assertGreater(clock_value, 0.0)

        e._runstate_started = False
        e.tick()


    def test_runstate_stop(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[tags.DEFAULT_TAG_SYSTEM_STATE]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

        e.schedule_execution("Stop")
        e.tick()
        self.assertFalse(e._runstate_started)

        self.assertEqual(SystemStateEnum.Stopped, system_state_tag.get_value())

    def test_runstate_pause(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[tags.DEFAULT_TAG_SYSTEM_STATE]
        process_time_tag = e._system_tags[tags.DEFAULT_TAG_PROCESS_TIME]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())
        pre_pause_process_time = process_time_tag.as_number()

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e.schedule_execution("Pause")
        e.tick()
        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_paused)
        self.assertEqual(SystemStateEnum.Paused, system_state_tag.get_value())

        # process time is now stopped
        self.assertEqual(pre_pause_process_time, process_time_tag.as_number())

        # Pause triggers safe-mode
        self.assertFalse(danger_tag.get_value())

    @unittest.skip("not implemented")
    def test_runstate_unpause(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[tags.DEFAULT_TAG_SYSTEM_STATE]
        process_time_tag = e._system_tags[tags.DEFAULT_TAG_PROCESS_TIME]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())
        pre_pause_process_time = process_time_tag.as_number()

        e.schedule_execution("PAUSE")
        e.tick()
        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_paused)
        self.assertEqual(SystemStateEnum.Paused, system_state_tag.get_value())

        # process time is now stopped
        self.assertEqual(pre_pause_process_time, process_time_tag.as_number())

        e.schedule_execution("Start")
        e.tick()
        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_paused)
        self.assertEqual(SystemStateEnum.Paused, system_state_tag.get_value())

        # process time is now stopped
        self.assertEqual(pre_pause_process_time, process_time_tag.as_number())

    def test_runstate_hold(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[tags.DEFAULT_TAG_SYSTEM_STATE]
        process_time_tag = e._system_tags[tags.DEFAULT_TAG_PROCESS_TIME]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())
        pre_hold_process_time = process_time_tag.as_number()

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e.schedule_execution("Hold")
        e.tick()
        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_holding)
        self.assertEqual(SystemStateEnum.Holding, system_state_tag.get_value())

        # process time is now stopped
        self.assertEqual(pre_hold_process_time, process_time_tag.as_number())

        # Hold does not trigger safe-mode
        self.assertTrue(danger_tag.get_value())

    @unittest.skip("not implemented")
    def test_runstate_unhold(self):
        raise NotImplementedError()

    def test_safe_values_apply(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e._apply_safe_state()

        self.assertFalse(danger_tag.get_value())

    @unittest.skip("not implemented")
    def test_safe_values_resume_load_values(self):
        raise NotImplementedError()

    def test_enum_has(self):
        self.assertTrue(EngineCommandEnum.has_value("Stop"))
        self.assertTrue(EngineCommandEnum.has_value("Increment run counter"))
        self.assertFalse(EngineCommandEnum.has_value("stop"))
        self.assertFalse(EngineCommandEnum.has_value("STOP"))

    def test_inject_command(self):
        program = """
Mark: A
Mark: B
Mark: C
"""
        e = self.engine
        run_engine(e, program, 3)
        self.assertEqual(['A'], e.interpreter.get_marks())

        e.inject_code("Mark: I")
        continue_engine(e, 1)
        self.assertEqual(['A', 'B', 'I'], e.interpreter.get_marks())

        continue_engine(e, 1)
        self.assertEqual(['A', 'B', 'I', 'C'], e.interpreter.get_marks())

    def test_inject_thresholds_1(self):
        program = """
Mark: A
0.25 Mark: B
Mark: C
"""
        e = self.engine
        run_engine(e, program, 3)

        self.assertEqual(['A'], e.interpreter.get_marks())

        e.inject_code("Mark: I")
        continue_engine(e, 1)
        self.assertEqual(['A', 'I'], e.interpreter.get_marks())

        continue_engine(e, 3)
        # print_runtime_records(e)
        self.assertEqual(['A', 'I', 'B', 'C'], e.interpreter.get_marks())

    def test_inject_thresholds_2(self):
        program = """
Mark: A
0.2 Mark: B
Mark: C
"""
        e = self.engine
        run_engine(e, program, 3)

        self.assertEqual(['A'], e.interpreter.get_marks())

        e.inject_code("0.3 Mark: I")
        continue_engine(e, 1)

        self.assertEqual(['A', 'B'], e.interpreter.get_marks())

        continue_engine(e, 3)
        self.assertEqual(['A', 'B', 'C', 'I'], e.interpreter.get_marks())


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


if __name__ == "__main__":
    unittest.main()
