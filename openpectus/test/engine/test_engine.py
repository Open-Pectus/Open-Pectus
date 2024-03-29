from contextlib import contextmanager
import logging
import threading
import time
import unittest
from typing import Any, Generator, List
from openpectus.lang.exec.tag_lifetime import TagContext
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag

import openpectus.protocol.models as Mdl
import pint
from openpectus.engine.engine import Engine
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection
from openpectus.engine.models import EngineCommandEnum, MethodStatusEnum, SystemStateEnum, SystemTagName
from openpectus.lang.exec.runlog import RuntimeRecordStateEnum
from openpectus.lang.exec.tags import Tag, TagDirection
from openpectus.lang.exec.timer import NullTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder, UodCommand
from openpectus.test.engine.utility_methods import (
    continue_engine, run_engine,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging,
    print_runlog, print_runtime_records
)
from typing_extensions import override


configure_test_logger()
set_engine_debug_logging()


logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)

# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 sec")


def get_queue_items(q) -> list[Tag]:
    items = []
    while not q.empty():
        items.append(q.get())
    return items


def create_test_uod() -> UnitOperationDefinitionBase:
    def reset(cmd: UodCommand, args: List[Any]) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time.time())
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A", time.time())
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
        .with_location("Test location")
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
        .with_tag(ReadingTag("FT01", "L/h"))
        .with_tag(SelectTag("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.OUTPUT, safe_value=False))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_command(UodCommand.builder().with_name("overlap1").with_exec_fn(overlap_exec))
        .with_command(UodCommand.builder().with_name("overlap2").with_exec_fn(overlap_exec))
        .with_command_overlap(['overlap1', 'overlap2'])
        .build()
    )


def create_engine() -> Engine:
    uod = create_test_uod()
    e = Engine(uod)
    e._tick_timer = NullTimer()
    e._configure()
    return e


@contextmanager
def create_engine_context(uod: UnitOperationDefinitionBase) -> Generator[Engine, Any, None]:
    e = Engine(uod)
    e._tick_timer = NullTimer()
    e._configure()
    try:
        yield e
    finally:
        e.cleanup()


class TestEngineSetup(unittest.TestCase):

    def test_create_engine(self):
        uod = create_test_uod()
        e = Engine(uod)
        self.assertIsNotNone(e)
        e.cleanup()

    def test_configure_uod(self):
        uod = create_test_uod()
        e = Engine(uod)
        e._configure()

        self.assertTrue(len(uod.command_factories) > 0)
        self.assertTrue(len(uod.instrument) > 0)
        self.assertTrue(len(uod.tags) > 0)

        e.cleanup()

    @unittest.skip("not implemented")
    def test_uod_reading_to_process_values(self):
        uod = create_test_uod()
        e = Engine(uod)
        e._configure()
        e.cleanup()

        # assert process values match the defined readings

    @unittest.skip("not implemented")
    def test_load_uod(self):
        pass


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine: Engine = create_engine()

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
        time.sleep(0.1)

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
        e.uod.tags["FT01"].set_value(22, e._tick_time)
        e.uod.tags["Reset"].set_value("Reset", e._tick_time)

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
        #self.assertFalse(r.has_state(RuntimeRecordStateEnum.Started))

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

        e.inject_code("Increment run counter")
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
        e.set_method(Mdl.Method.from_pcode(pcode=program))
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
            self.assertTrue(start_values.has("Reset"))

    def test_clocks_start_stop(self):
        e = self.engine

        clock = e._system_tags.get(SystemTagName.CLOCK)
        self.assertEqual(0.0, clock.as_number())

        e._runstate_started = True
        e.tick()

        clock_value = clock.as_number()
        self.assertGreater(clock_value, 0.0)

        e._runstate_started = False
        e.tick()


    # --- RunState ---


    def test_runstate_start(self):
        e = self.engine

        e.schedule_execution("Start")
        e.tick()

        self.assertTrue(e._runstate_started)

    def test_runstate_stop(self):
        set_engine_debug_logging()

        e = self.engine
        e.schedule_execution("Start")

        e.tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

        e.schedule_execution("Stop")
        e.tick()

        self.assertFalse(e._runstate_started)

        self.assertEqual(SystemStateEnum.Stopped, system_state_tag.get_value())

    def test_runstate_pause(self):
        e = self.engine

        def tick():
            e.tick()
            time.sleep(0.1)

        e.schedule_execution("Start")
        tick()

        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]
        process_time_tag = e._system_tags[SystemTagName.PROCESS_TIME]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())        

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e.schedule_execution("Pause")
        tick()

        # now paused so we can get the paused value
        pause_process_time = process_time_tag.as_number()

        # run a few ticks while paused
        tick()
        tick()

        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_paused)
        self.assertEqual(SystemStateEnum.Paused, system_state_tag.get_value())

        # process time is stopped
        self.assertEqual(pause_process_time, process_time_tag.as_number())

        # Pause has triggered safe-mode
        self.assertFalse(danger_tag.get_value())

    def test_runstate_unpause(self):
        e = self.engine

        def tick():
            e.tick()
            time.sleep(0.1)

        # apply start and pause
        e.schedule_execution("Start")
        tick()

        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]
        process_time_tag = e._system_tags[SystemTagName.PROCESS_TIME]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e.schedule_execution("Pause")
        tick()

        pause_process_time = process_time_tag.as_number()

        e.schedule_execution("Unpause")
        tick()

        self.assertEqual(e._runstate_started, True)
        self.assertEqual(e._runstate_paused, False)
        self.assertEqual(system_state_tag.get_value(), SystemStateEnum.Running)

        # Unpause applies pre-pause values
        self.assertEqual(danger_tag.get_value(), True)

        # needs an additional tick in system state Running before process time resumes
        tick()

        # process time is resumed
        process_time_increment = process_time_tag.as_number() - pause_process_time
        self.assertTrue(process_time_increment > 0.0)

    def test_runstate_hold(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e.schedule_execution("Hold")
        e.tick()

        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_holding)
        self.assertEqual(SystemStateEnum.Holding, system_state_tag.get_value())

        # Hold does not trigger safe-mode so danger is still True
        self.assertTrue(danger_tag.get_value())

    @unittest.skip("not implemented")
    def test_runstate_unhold(self):
        raise NotImplementedError()


    # --- Safe values ---


    def test_safe_values_apply(self):
        e = self.engine
        e.schedule_execution("Start")

        e.tick()

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e._apply_safe_state()

        self.assertFalse(danger_tag.get_value())

    def test_restart_can_stop(self):
        set_engine_debug_logging()
        set_interpreter_debug_logging()
        program = """
Mark: A
Restart
"""
        e = self.engine
        run_engine(e, program, 4)

        # when no commands need to be stopped, restart immediately moves to Stopped
        system_state = e.tags[SystemTagName.SYSTEM_STATE]
        self.assertEqual(system_state.get_value(), SystemStateEnum.Restarting)


    # --- Totalizers ---


    def test_totalizer_base_units_no_accumulator(self):
        e = self.engine

        with self.subTest("allows_time_unit"):
            run_engine(e, "Base: s\n0.1 Mark: A", 5)
            self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

        with self.subTest("disallows_volume_unit"):
            run_engine(e, "Base: L\n0.1 Mark: A", 5)
            self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.ERROR)

    def test_totalizer_base_units_with_accumulator_volume(self):        
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("Meter", "L"))
               .with_accumulated_volume(totalizer_tag_name="Meter")
               .build())

        with self.subTest("allows_time_unit"):
            with create_engine_context(uod) as e:
                run_engine(e, "Base: s\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

        with self.subTest("allows_volume_unit"):
            with create_engine_context(uod) as e:
                run_engine(e, "Base: L\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

        with self.subTest("disallows_cv_unit"):
            with create_engine_context(uod) as e:
                run_engine(e, "Base: CV\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.ERROR)

    def test_totalizer_base_units_with_accumulator_cv(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("Meter", "L"))
               .with_tag(ReadingTag("CV", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="Meter")
               .build())

        uod.tags["CV"].set_value(1.0, 0)

        with self.subTest("allows_time_unit"):
            with create_engine_context(uod) as e:
                run_engine(e, "Base: s\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

        with self.subTest("disallows_volume_unit"):
            with create_engine_context(uod) as e:
                run_engine(e, "Base: L\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.ERROR)

        with self.subTest("allows_cv_unit"):
            with create_engine_context(uod) as e:
                run_engine(e, "Base: CV\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)


    def test_accumulated_volume(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_volume(totalizer_tag_name="calc")
               .build())

        program = """
Base: s
1 Mark: A
        """
        with create_engine_context(uod) as e:
            acc_vol = e.tags[SystemTagName.ACCUMULATED_VOLUME]
            run_engine(e, program, 1)

            self.assertEqual(acc_vol.as_float(), 0.0)
            self.assertEqual(acc_vol.unit, "L")

            t0 = time.time()
            continue_engine(e, 10)
            t1 = time.time()

            self.assertAlmostEqual(t1 - t0, 1, delta=0.1)
            self.assertAlmostEqual(acc_vol.as_float(), 1, delta=0.1)

    def test_accumulated_block_volume(self):
        self.engine.cleanup()  # dispose the test default engine

        set_interpreter_debug_logging()

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_volume(totalizer_tag_name="calc")
               .build())

        program = """
Base: s
Block: A
    0.5 End block
0.5 Mark: A
        """
        with create_engine_context(uod) as e:
            acc_vol = e.tags[SystemTagName.ACCUMULATED_VOLUME]
            block_vol = e.tags[SystemTagName.BLOCK_VOLUME]

            run_engine(e, program, 1)
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), None)

            self.assertEqual(acc_vol.as_float(), 0.0)
            self.assertEqual(acc_vol.unit, "L")
            self.assertEqual(block_vol.as_float(), 0.0)
            self.assertEqual(block_vol.unit, "L")

            continue_engine(e, 2)  # Blank + Base
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), None)
            self.assertAlmostEqual(acc_vol.as_float(), 0.2, delta=0.1)
            self.assertAlmostEqual(block_vol.as_float(), 0.2, delta=0.1)

            continue_engine(e, 1)  # Block
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), "A")
            self.assertAlmostEqual(acc_vol.as_float(), 0.3, delta=0.1)
            self.assertAlmostEqual(block_vol.as_float(), 0.1, delta=0.1)

            continue_engine(e, 5)
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), "A")
            self.assertAlmostEqual(acc_vol.as_float(), 0.8, delta=0.1)
            self.assertAlmostEqual(block_vol.as_float(), 0.6, delta=0.1)

            continue_engine(e, 1)
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), None)
            # acc_vol keeps counting
            self.assertAlmostEqual(acc_vol.as_float(), 0.9, delta=0.1)
            # block_vol is reset to value before block A - so it matches acc_vol again
            self.assertAlmostEqual(block_vol.as_float(), 0.9, delta=0.1)

    def test_accumulated_column_volume(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """
Base: s
1 Mark: A
"""
        with create_engine_context(uod) as e:
            cv = e.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = e.tags[SystemTagName.ACCUMULATED_CV]
            run_engine(e, program, 1)

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")

            t0 = time.time()
            continue_engine(e, 10)
            t1 = time.time()

            self.assertAlmostEqual(t1 - t0, 1, delta=0.1)
            self.assertAlmostEqual(acc_cv.as_float(), 1/2, delta=0.1)


    def test_accumulated_column_block_volume(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """
Base: s
Block: A
    0.5 End block
0.5 Mark: A
        """
        with create_engine_context(uod) as e:
            cv = e.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = e.tags[SystemTagName.ACCUMULATED_CV]
            block_cv = e.tags[SystemTagName.BLOCK_CV]
            run_engine(e, program, 1)

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")
            self.assertEqual(block_cv.as_float(), 0.0)
            self.assertEqual(block_cv.unit, "CV")

            continue_engine(e, 2)  # Blank + Base
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), None)
            self.assertAlmostEqual(acc_cv.as_float(), 0.2/2, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), 0.2/2, delta=0.1)

            continue_engine(e, 1)  # Block
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), "A")
            self.assertAlmostEqual(acc_cv.as_float(), 0.3/2, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), 0.1/2, delta=0.1)

            continue_engine(e, 5)
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), "A")
            self.assertAlmostEqual(acc_cv.as_float(), 0.8/2, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), 0.6/2, delta=0.1)

            continue_engine(e, 1)
            self.assertEqual(e.tags[SystemTagName.BLOCK].get_value(), None)
            # acc_vol keeps counting
            self.assertAlmostEqual(acc_cv.as_float(), 0.9/2, delta=0.1)
            # block_vol is reset to value before block A - so it matches acc_vol again
            self.assertAlmostEqual(block_cv.as_float(), 0.9/2, delta=0.1)

    # --- Restart ---


    def test_restart_can_restart(self):
        set_engine_debug_logging()
        set_interpreter_debug_logging()
        program = """
Mark: A
Increment run counter
Restart
"""
        e = self.engine
        self.assertEqual(0, e.tags[SystemTagName.RUN_COUNTER].as_number())

        run_engine(e, program, 5)

        run_id_1 = e.tags[SystemTagName.RUN_ID].get_value()
        self.assertEqual(e.tags[SystemTagName.SYSTEM_STATE].get_value(), SystemStateEnum.Restarting)
        self.assertEqual(1, e.tags[SystemTagName.RUN_COUNTER].as_number())

        self.assertEqual(e.interpreter.get_marks(), ["A"])

        continue_engine(e, 1)

        self.assertEqual(e.tags[SystemTagName.SYSTEM_STATE].get_value(), SystemStateEnum.Stopped)
        self.assertIsNone(e.tags[SystemTagName.RUN_ID].get_value())
        self.assertEqual(e.interpreter.get_marks(), [])
        self.assertEqual(1, e.tags[SystemTagName.RUN_COUNTER].as_number())

        continue_engine(e, 1)

        run_id2 = e.tags[SystemTagName.RUN_ID].get_value()
        self.assertEqual(e.tags[SystemTagName.SYSTEM_STATE].get_value(), SystemStateEnum.Running)
        self.assertNotEqual(run_id_1, run_id2)
        self.assertEqual(e.interpreter.get_marks(), [])
        self.assertEqual(1, e.tags[SystemTagName.RUN_COUNTER].as_number())

        continue_engine(e, 3)

        self.assertEqual(e.interpreter.get_marks(), ["A"])
        self.assertEqual(2, e.tags[SystemTagName.RUN_COUNTER].as_number())

    def test_restart_stop_ticking_interpreter(self):

        set_interpreter_debug_logging()
        program = """
Mark: A
Restart
Mark: X
"""
        e = self.engine
        run_engine(e, program, 1)

        for _ in range(30):
            continue_engine(e, 1)
            self.assertTrue("X" not in e.interpreter.get_marks())

    def test_restart_cancels_running_commands(self):
        program = """
Reset
Restart
"""
        e = self.engine
        run_engine(e, program, 4)

        # TODO look into logs - something is not right

        system_state = e.tags[SystemTagName.SYSTEM_STATE]
        self.assertEqual(system_state.get_value(), SystemStateEnum.Restarting)

    def test_EngineCommandEnum_has(self):
        self.assertTrue(EngineCommandEnum.has_value("Stop"))
        self.assertFalse(EngineCommandEnum.has_value("stop"))
        self.assertFalse(EngineCommandEnum.has_value("STOP"))


    # --- Inject ---


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
        e.tags[SystemTagName.BASE].set_value("s", e._tick_time)
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
        e.tags[SystemTagName.BASE].set_value("s", e._tick_time)
        run_engine(e, program, 3)

        self.assertEqual(['A'], e.interpreter.get_marks())

        e.inject_code("0.3 Mark: I")
        continue_engine(e, 1)

        self.assertEqual(['A', 'B'], e.interpreter.get_marks())

        continue_engine(e, 3)
        # self.assertEqual(['A', 'B', 'C', 'I'], e.interpreter.get_marks())
        self.assertTrue(['A', 'B', 'C', 'I'] == e.interpreter.get_marks() 
                        or ['A', 'B', 'I', 'C'] == e.interpreter.get_marks())

    def test_engine_error_causes_Paused_state(self):
        e = self.engine
        run_engine(e, "foo bar", 3)

        self.assertTrue(e._runstate_paused)

    def test_interpreter_error_causes_Paused_state(self):
        e = self.engine
        run_engine(e, """WATCH x > 2""", 3)

        self.assertTrue(e._runstate_paused)


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


class CalculatedLinearTag(Tag):
    """ Test tag that is used to simulate a value that is linear function of time. """
    def __init__(self, name: str, unit: str | None, slope: float = 1.0) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.NA)
        self.slope = slope

    def on_start(self, context: TagContext):
        self.value = time.time() * self.slope

    def on_tick(self):
        self.value = time.time() * self.slope


if __name__ == "__main__":
    unittest.main()
