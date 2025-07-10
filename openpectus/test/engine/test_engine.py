from contextlib import contextmanager
import logging
import threading
import time
import unittest
from typing import Any, Generator
from openpectus.lang.exec.errors import EngineError, UodValidationError
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag

import pint
from openpectus.engine.engine import Engine
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection
from openpectus.engine.models import EngineCommandEnum, MethodStatusEnum, SystemStateEnum, SystemTagName
from openpectus.lang.exec.runlog import RuntimeRecordStateEnum
from openpectus.lang.exec.tags import Tag, TagDirection
from openpectus.lang.exec.uod import (
    UnitOperationDefinitionBase,
    UodCommand,
    UodBuilder,
    RegexNamedArgumentParser
)
from openpectus.test.engine.utility_methods import (
    continue_engine, run_engine,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging,
    print_runlog, print_runtime_records
)
from typing_extensions import override

# the number of ticks to run befpre the first command (not including a blank first line)
start_ticks = 1


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


def create_test_uod() -> UnitOperationDefinitionBase:  # noqa C901
    def reset(cmd: UodCommand, **kvargs) -> None:
        count = cmd.get_iteration_count()
        max_ticks = 5
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time.time())
        elif count > max_ticks:
            cmd.context.tags.get("Reset").set_value("N/A", time.time())
            cmd.set_complete()
        else:
            progress = count/max_ticks
            cmd.set_progress(progress)

    def cmd_with_args(cmd: UodCommand, **kvargs) -> None:
        print("arguments: " + str(kvargs))
        cmd.set_complete()

    def cmd_arg_parse(args: str) -> dict[str, Any] | None:
        if args is None or args == "" or args == "FAIL":
            return None
        result = {}
        for i, item in enumerate(args.split(",")):
            result[f"item{i}"] = item.strip()
        return result

    def cmd_regex(cmd: UodCommand, number, number_unit) -> None:
        cmd.context.tags["CmdWithRegex_Area"].set_value(number + number_unit, time.monotonic())
        cmd.set_complete()

    def overlap_exec(cmd: UodCommand, **kvargs) -> None:
        count = cmd.get_iteration_count()
        if count >= 9:
            cmd.set_complete()

    builder = (
        UodBuilder()
        .with_instrument("TestUod")
        .with_author("Test Author", "test@openpectus.org")
        .with_filename(__file__)
        .with_hardware(TestHW())
        .with_location("Test location")
        .with_hardware_register("FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
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
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.Output, safe_value=False))
        .with_command(name="Reset", exec_fn=reset)
        .with_command(name="CmdWithArgs", exec_fn=cmd_with_args, arg_parse_fn=cmd_arg_parse)
        .with_command(name="overlap1", exec_fn=overlap_exec)
        .with_command(name="overlap2", exec_fn=overlap_exec)
        .with_command_overlap(['overlap1', 'overlap2'])
        .with_tag(Tag("CmdWithRegex_Area", value=""))
        .with_command_regex_arguments(
            name="CmdWithRegexArgs",
            arg_parse_regex=RegexNumber(units=['m2']),
            exec_fn=cmd_regex)
    )
    uod = builder.build()
    uod.hwl.connect()
    print(uod)
    print(uod.tags)
    return uod


def create_engine(uod: UnitOperationDefinitionBase | None = None) -> Engine:
    if uod is None:
        uod = create_test_uod()
    e = Engine(uod)
    return e


@contextmanager
def create_engine_context(uod: UnitOperationDefinitionBase) -> Generator[Engine, Any, None]:
    e = create_engine(uod)
    try:
        yield e
    finally:
        e.cleanup()


class TestEngineSetup(unittest.TestCase):

    def test_create_engine(self):
        e = create_engine()
        self.assertIsNotNone(e)
        e.cleanup()

    def test_configure_uod(self):
        uod = create_test_uod()
        e = Engine(uod)

        self.assertTrue(len(uod.command_factories) > 0)
        self.assertTrue(len(uod.instrument) > 0)
        self.assertTrue(len(uod.tags) > 0)

        e.cleanup()


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine: Engine = create_engine()

    def tearDown(self):
        self.engine.cleanup()

    @unittest.skip("Potentially affects other tests.")
    def test_engine_start(self):
        e = self.engine

        t = threading.Thread(target=e.run)
        t.daemon = True
        t.start()

        time.sleep(1)
        e._running = False
        t.join()

    @unittest.skip("Potentially affects other tests.")
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
        reset_tag = e.uod.tags["Reset"]

        self.assertEqual("N/A", reset_tag.get_value())

        run_engine(e, "Reset", start_ticks + 1)
        self.assertEqual("Reset", reset_tag.get_value())

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

        run_engine(e, "", start_ticks)
        time.sleep(0.1)

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

    def test_engine_start_writes_safe_values_to_hw(self):
        e = self.engine

        # get Dange tag which has an initial value of True
        danger_tag = e.tags["Danger"]
        self.assertEqual(True, danger_tag.value)

        # trigger startup to write safe values
        e._run()

        # safe value has now been set
        self.assertEqual(False, danger_tag.value)

    def test_uod_command_w_arguments(self):
        e = self.engine
        program = "CmdWithArgs: a, b,c ,  d"
        run_engine(e, program, 10)

        self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

    def test_uod_command_w_arguments_fail(self):
        e = self.engine
        program = "CmdWithArgs: FAIL"
        with self.assertRaises(EngineError):
            run_engine(e, program, 10)
        self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.ERROR)

    def test_uod_command_w_regex_arguments(self):
        e = self.engine
        program = "CmdWithRegexArgs: 3.14 m2"
        run_engine(e, program, 10)

        self.assertEqual("3.14m2", e.tags["CmdWithRegex_Area"].get_value())

    def test_RegexNamedArgumentParser_parse(self):
        regex = r"(?P<value>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+) ?(?P<unit>m2)"
        parser = RegexNamedArgumentParser(regex)
        result = parser.parse("3.14m2")

        assert result is not None
        self.assertEqual(2, len(result))
        self.assertEqual("3.14", result["value"])
        self.assertEqual("m2", result["unit"])

    def test_RegexNamedArgumentParser_get_named_groups(self):
        regex = r"(?P<value>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+) ?(?P<unit>m2)"
        parser = RegexNamedArgumentParser(regex)
        self.assertEqual(['value', 'unit'], parser.get_named_groups())

    def test_uod_verify_command_signatures_regex(self):

        def no_args(cmd: UodCommand):
            pass

        def kvargs(cmd: UodCommand, **kvargs):
            pass

        def two_args(cmd: UodCommand, value, unit):
            pass

        def two_args_bad_names(cmd: UodCommand, one, two):
            pass

        def two_args_def(cmd: UodCommand, value, unit=None):
            pass

        exec_functions = {
            'no_args': no_args,
            'kvargs': kvargs,
            'two_args': two_args,
            'two_args_bad_names': two_args_bad_names,
            'two_args_def': two_args_def,
        }
        regexes = {
            'two_parms': "(?P<value>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+) ?(?P<unit>m2)",
            'one_parms': "(?P<value>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+) ?",
            'no_parms': "",
        }

        def test(exec_name, regex_name, expect_success: bool = True):
            with self.subTest(exec_name + ", " + regex_name + ", " + ("success" if expect_success else "fail")):
                exec_fn = exec_functions[exec_name]
                regex = regexes[regex_name]
                uod = (
                    UodBuilder()
                    .with_instrument("foo")
                    .with_author("Test Author", "test@openpectus.org")
                    .with_filename(__file__)
                    .with_hardware_none()
                    .with_command_regex_arguments("bar", regex, exec_fn)
                    .build()
                )

                if expect_success:
                    uod.validate_command_signatures()
                else:
                    self.assertRaises(UodValidationError, uod.validate_command_signatures)

        test('kvargs', "two_parms")
        test('no_args', "no_parms")
        test('two_args', "two_parms")
        test('two_args_def', "one_parms")

        test('no_args', "two_parms", False)
        test('two_args_bad_names', "two_parms", False)
        test('two_args', "one_parms", False)

    def test_uod_verify_command_signatures_default(self):

        def no_args(cmd: UodCommand):
            pass

        def kvargs(cmd: UodCommand, **kvargs):
            pass

        def value_arg(cmd: UodCommand, value):
            pass

        def value_arg_default(cmd: UodCommand, value=None):
            pass

        exec_functions = {
            'no_args': no_args,
            'kvargs': kvargs,
            'value_arg': value_arg,
            'value_arg_default': value_arg_default,
        }

        def test(exec_name, expect_success: bool = True):
            with self.subTest(exec_name + ", " + ("success" if expect_success else "fail")):
                uod = (
                    UodBuilder()
                    .with_instrument("foo")
                    .with_author("Test Author", "test@openpectus.org")
                    .with_filename(__file__)
                    .with_hardware_none()
                    .with_command("bar", exec_fn=exec_functions[exec_name])
                    .build()
                )

                if expect_success:
                    uod.validate_command_signatures()
                else:
                    self.assertRaises(UodValidationError, uod.validate_command_signatures)

        test('kvargs')
        test('value_arg')
        test("value_arg_default")

        test('no_args', False)

    def test_uod_invoke_command_signatures(self):  # noqa C901

        def no_args(cmd: UodCommand):
            pass

        def kvargs(cmd: UodCommand, **kvargs):
            pass

        def value_arg(cmd: UodCommand, value):
            pass

        def value_arg_default(cmd: UodCommand, value=None):
            pass

        exec_functions = {
            'no_args': no_args,
            'kvargs': kvargs,
            'value_arg': value_arg,
            'value_arg_default': value_arg_default,
        }

        def test(exec_name, parsed_args: dict[str, Any], expect_success: bool = True):
            with self.subTest(exec_name + ", " + str(parsed_args) + ", " + ("success" if expect_success else "fail")):
                exec_fn = exec_functions[exec_name]
                try:
                    exec_fn(cmd=None, **parsed_args)
                    if not expect_success:
                        raise AssertionError("Expected execution error but none occurred")
                except TypeError:
                    if expect_success:
                        raise AssertionError("Expected no execution error but one occurred")
                except Exception as ex:
                    raise AssertionError("Did not expect exception") from ex

        test('no_args', {})
        test('kvargs', {'bar': 1})
        test('kvargs', {})
        test('value_arg', {'value': 23})
        test("value_arg_default", {})
        test("value_arg_default", {'value': 34})

        test('no_args', {'bar': 1}, False)
        test('value_arg', {}, False)
        test('value_arg', {'foo': 34}, False)
        test('value_arg', {'value': 1, 'foo': 34}, False)
        test("value_arg_default", {'foo': 34}, False)

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

        run_engine(e, "Reset", start_ticks + 1)
        self.assertEqual("Reset", e.uod.tags["Reset"].get_value())

        # Reset takes 5 ticks to revert
        continue_engine(e, 5)
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

        r = records[1]
        self.assertEqual("Reset", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Cancelled))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        r = records[2]
        self.assertEqual("Reset", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Cancelled))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        continue_engine(e, 5)
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

        r = rs[1]
        self.assertEqual("overlap1", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.Cancelled))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Forced))
        self.assertTrue(not r.has_state(RuntimeRecordStateEnum.Completed))

        continue_engine(e, 1)
        print_runtime_records(e)

        r = rs[2]
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
    End block
Mark: X
"""
        e = self.engine
        run_engine(e, program, 3)

        rs = e.runtimeinfo.records

        print_runtime_records(e)

        self.assertEqual("Block: A", rs[1].name)
        self.assertFalse(rs[0].has_state(RuntimeRecordStateEnum.Started))

        continue_engine(e, 1)
        self.assertTrue(rs[1].has_state(RuntimeRecordStateEnum.Started))

        continue_engine(e, 2)
        self.assertTrue(rs[1].has_state(RuntimeRecordStateEnum.Completed))

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

        r = e.interpreter.runtimeinfo.records[1]
        self.assertEqual("Watch: Block Time > 0.2s", r.name)
        self.assertTrue(r.has_state(RuntimeRecordStateEnum.AwaitingCondition))
        # self.assertFalse(r.has_state(RuntimeRecordStateEnum.Started))

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
        e.tick(0, 0)

        e.inject_code("Increment run counter")
        e.tick(0, 0)
        e.tick(0, 0)

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
        code = "Mark: A\nMark: B\nMark: C"
        e = self.engine
        run_engine(e, code, 2)
        # run_engine(e, code, start_ticks)
        self.assertEqual(['A'], e.interpreter.get_marks())
        continue_engine(e, 10)

        self.assertEqual(['A', 'B', 'C'], e.interpreter.get_marks())

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
        e.tick(1, 1)

        clock_value = clock.as_number()
        self.assertGreater(clock_value, 0.0)

        e._runstate_started = False
        e.tick(2, 1)

        self.assertEqual(clock_value, clock.as_number())


    # --- RunState ---


    def test_runstate_start(self):
        e = self.engine

        e.schedule_execution("Start")
        e.tick(1, 1)

        self.assertTrue(e._runstate_started)

    def test_runstate_stop(self):
        set_engine_debug_logging()

        e = self.engine
        e.schedule_execution("Start")

        e.tick(1, 1)
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

        e.schedule_execution("Stop")
        e.tick(1, 1)
        e.tick(1, 1)

        self.assertFalse(e._runstate_started)
        self.assertEqual(SystemStateEnum.Stopped, system_state_tag.get_value())

    def test_runstate_pause(self):
        e = self.engine

        def tick():
            tick_time = time.time()
            e.tick(tick_time, 0.1)
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
            tick_time = time.time()
            e.tick(tick_time, 0.1)
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
        def tick():
            tick_time = time.time()
            e.tick(tick_time, 0.1)
            time.sleep(0.1)

        e = self.engine
        e.schedule_execution("Start")

        tick()
        self.assertTrue(e._runstate_started)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]
        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e.schedule_execution("Hold")
        tick()

        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_holding)
        self.assertEqual(SystemStateEnum.Holding, system_state_tag.get_value())

        # Hold does not trigger safe-mode so danger is still True
        self.assertTrue(danger_tag.get_value())

    @unittest.skip("not implemented")
    def test_runstate_unhold(self):
        raise NotImplementedError()


    def test_pause_w_duration(self):
        e = self.engine
        program = """
Mark: a
Pause: .5s
Mark: b
"""
        run_engine(e, program, 5)
        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_paused)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]

        self.assertEqual(SystemStateEnum.Paused, system_state_tag.get_value())

        continue_engine(e, 5)

        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

    def test_hold_w_duration(self):
        e = self.engine
        program = """
Mark: a
Hold: .5s
Mark: b
"""
        run_engine(e, program, 7)
        self.assertTrue(e._runstate_started)
        self.assertTrue(e._runstate_holding)
        system_state_tag = e._system_tags[SystemTagName.SYSTEM_STATE]

        self.assertEqual(SystemStateEnum.Holding, system_state_tag.get_value())

        continue_engine(e, 5)

        self.assertEqual(SystemStateEnum.Running, system_state_tag.get_value())

    def test_wait(self):
        e = self.engine
        program = """
Mark: a
Wait: .5s
Mark: b
"""
        run_engine(e, program, 2)
        #run_engine(e, program, start_ticks)
        self.assertEqual([], e.interpreter.get_marks())

        continue_engine(e, 1)
        self.assertEqual(['a'], e.interpreter.get_marks())

        continue_engine(e, 5)
        self.assertEqual(['a'], e.interpreter.get_marks())

        continue_engine(e, 3)
        self.assertEqual(['a', 'b'], e.interpreter.get_marks())

    # --- Safe values ---


    def test_safe_values_apply(self):

        def tick():
            tick_time = time.time()
            e.tick(tick_time, 0.1)
            time.sleep(0.1)

        e = self.engine
        e.schedule_execution("Start")

        tick()

        danger_tag = e.uod.tags["Danger"]
        self.assertTrue(danger_tag.get_value())

        e._apply_safe_state()

        self.assertFalse(danger_tag.get_value())


    # --- Totalizers ---


    def test_totalizer_base_units_no_accumulator_allows_time_unit(self):
        e = self.engine

        run_engine(e, "Base: s\n0.1 Mark: A", 5)
        self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

    def test_totalizer_base_units_no_accumulator_disallows_volume_unit(self):
        e = self.engine
        with self.assertRaises(EngineError):
            run_engine(e, "Base: L\n0.1 Mark: A", 5)
        self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.ERROR)

    def test_totalizer_base_units_with_accumulator_volume(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
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
                with self.assertRaises(EngineError):
                    run_engine(e, "Base: CV\n0.1 Mark: A", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.ERROR)

    def test_totalizer_base_units_with_accumulator_cv(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
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
                with self.assertRaises(EngineError):
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
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
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

            t0 = e._clock.get_time()
            continue_engine(e, 10)
            t1 = e._clock.get_time()

            self.assertAlmostEqual(t1 - t0, 1, delta=0.1)
            self.assertAlmostEqual(acc_vol.as_float(), 1, delta=0.1)

    def test_accumulated_block_volume(self):
        self.engine.cleanup()  # dispose the test default engine
        delta = 0.15
        set_interpreter_debug_logging()

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_volume(totalizer_tag_name="calc")
               .build())

        program = """\
Base: s
Wait: 0.45s
Block: A
    0.85 End block
0.45 Mark: A
        """
        with create_engine_context(uod) as e:
            acc_vol = e.tags[SystemTagName.ACCUMULATED_VOLUME]
            block_vol = e.tags[SystemTagName.BLOCK_VOLUME]
            block = e.tags[SystemTagName.BLOCK]

            run_engine(e, program, 1)
            self.assertEqual(block.get_value(), None)

            self.assertEqual(acc_vol.as_float(), 0.0)
            self.assertEqual(acc_vol.unit, "L")
            self.assertEqual(block_vol.as_float(), 0.0)
            self.assertEqual(block_vol.unit, "L")

            continue_engine(e, 1)  # Base
            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_vol.as_float(), 0.1, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), 0.1, delta=delta)

            continue_engine(e, 5)  # Wait
            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_vol.as_float(), 0.7, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), 0.7, delta=delta)

            continue_engine(e, 1)  # Block
            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_vol.as_float(), 0.8, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), 0.1, delta=delta)

            continue_engine(e, 8)
            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_vol.as_float(), 1.6, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), 0.9, delta=delta)

            continue_engine(e, 1)
            self.assertEqual(block.get_value(), None)
            # acc_vol keeps counting
            self.assertAlmostEqual(acc_vol.as_float(), 1.7, delta=delta)
            # block_vol is reset to value before block A - so it matches acc_vol again
            self.assertAlmostEqual(block_vol.as_float(), 1.7, delta=delta)

    def test_accumulated_column_volume(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
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

            t0 = e._clock.get_time()
            continue_engine(e, 10)
            t1 = e._clock.get_time()

            self.assertAlmostEqual(t1 - t0, 1, delta=0.1)
            self.assertAlmostEqual(acc_cv.as_float(), 1/2, delta=0.1)

    def test_accumulated_column_volume_base(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """
Base: CV
0.5 Mark: A
"""
        with create_engine_context(uod) as e:
            cv = e.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = e.tags[SystemTagName.ACCUMULATED_CV]
            run_engine(e, program, 1)

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")

            continue_engine(e, 4)
            self.assertAlmostEqual(acc_cv.as_float(), 0.2, delta=0.1)
            self.assertEqual([], e.interpreter.get_marks())

            continue_engine(e, 4)
            self.assertAlmostEqual(acc_cv.as_float(), 0.4, delta=0.1)
            self.assertEqual([], e.interpreter.get_marks())

            continue_engine(e, 4)
            self.assertAlmostEqual(acc_cv.as_float(), 0.6, delta=0.1)
            self.assertEqual(['A'], e.interpreter.get_marks())

    def test_accumulated_column_block_volume(self):
        # TODO flaky - even in dev
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """\
Base: s
Block: A
    0.45 End block
0.45 Mark: A
        """
        with create_engine_context(uod) as e:
            cv = e.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = e.tags[SystemTagName.ACCUMULATED_CV]
            block_cv = e.tags[SystemTagName.BLOCK_CV]
            block = e.tags[SystemTagName.BLOCK]
            run_engine(e, program, 1)

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")
            self.assertEqual(block_cv.as_float(), 0.0)
            self.assertEqual(block_cv.unit, "CV")

            continue_engine(e, 1)  # Base
            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_cv.as_float(), 0.2/2, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), 0.2/2, delta=0.1)

            continue_engine(e, 2)  # Block
            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_cv.as_float(), 0.3/2, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), 0.1/2, delta=0.1)

            continue_engine(e, 3)
            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_cv.as_float(), 0.7/2, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), 0.5/2, delta=0.1)

            continue_engine(e, 1)
            self.assertEqual(block.get_value(), None)
            # acc_vol keeps counting
            self.assertAlmostEqual(acc_cv.as_float(), 0.8/2, delta=0.1)
            # block_vol is reset to value before block A - so it matches acc_vol again
            self.assertAlmostEqual(block_cv.as_float(), 0.8/2, delta=0.1)


    # --- Units ---


    def test_units(self):
        self.engine.cleanup()  # dispose the test default engine

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW())
               .with_location("Test location")
               .with_tag(ReadingTag("X1", "L"))
               .with_tag(ReadingTag("X2", "g"))
               .with_tag(ReadingTag("X3", "%"))
               .build())

        with self.subTest("test units"):
            with create_engine_context(uod) as e:
                run_engine(e, "", 5)
                self.assertEqual(e.tags[SystemTagName.METHOD_STATUS].get_value(), MethodStatusEnum.OK)

                percent_tag = uod.tags["X3"]
                self.assertEqual(percent_tag.unit, "%")

    def test_EngineCommandEnum_has(self):
        self.assertTrue(EngineCommandEnum.has_value("Stop"))
        self.assertFalse(EngineCommandEnum.has_value("stop"))
        self.assertFalse(EngineCommandEnum.has_value("STOP"))


# ----------- Engine Error -------------

    def test_engine_error_causes_Paused_state(self):
        e = self.engine
        with self.assertRaises(EngineError):
            run_engine(e, "foo bar", 3)
        self.assertTrue(e.has_error_state())

    def test_interpreter_error_causes_Paused_state(self):
        e = self.engine
        with self.assertRaises(EngineError):
            run_engine(e, """WATCH x > 2""", 3)
        self.assertTrue(e._runstate_paused)


# Test helpers


class TestHW(HardwareLayerBase):
    __test__ = False

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

    @override
    def connect(self):
        self._is_connected = True

    @override
    def disconnect(self):
        self._is_connected = False


class CalculatedLinearTag(Tag):
    """ Test tag that is used to simulate a value that is a linear function of time. """
    def __init__(self, name: str, unit: str | None, slope: float = 1.0) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.NA)
        self.slope = slope

    def on_start(self, run_id: str):
        self.value = time.time() * self.slope

    def on_tick(self, tick_time: float, increment_time: float):
        self.value = time.time() * self.slope


if __name__ == "__main__":
    unittest.main()
