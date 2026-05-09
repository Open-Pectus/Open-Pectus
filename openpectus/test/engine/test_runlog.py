import time
from typing import Any
import unittest

from openpectus.aggregator.models import RunLog, RunLogLine
from openpectus.engine.engine import Engine
from openpectus.engine.hardware import RegisterDirection
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.runlog import (
    RunLogItem, RuntimeInfo, RuntimeRecord, RuntimeRecordStateEnum,
    assert_Runtime_HasRecord,
    assert_Runtime_HasRecord_Completed, assert_Runtime_HasRecord_Started,
    assert_Runlog_HasItem, assert_Runlog_HasNoItem,
    assert_Runlog_HasItem_Completed, assert_Runlog_HasItem_Started, rjust,
)
from openpectus.lang.exec.tags import Tag, TagDirection
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder, UodCommand
import openpectus.lang.model.ast as p
from openpectus.test.engine.test_engine import create_engine

from openpectus.test.engine.test_helpers import TestHW
from openpectus.test.engine.utility_methods import (
    EngineTestInstance,
    EngineTestRunner,
    continue_engine, run_engine, print_runlog, print_runtime_records,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)

configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()

start_ticks = 3


def create_test_uod_local() -> UnitOperationDefinitionBase:  # noqa C901
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

    builder = (
        UodBuilder()
        .with_instrument("TestUod")
        .with_author("Test Author", "test@openpectus.org")
        .with_filename(__file__)
        .with_hardware(TestHW(connected=True))
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
        .with_command(name="Reset", exec_fn=reset)
    )
    uod = builder.build()
    uod.hwl.connect()
    return uod

class TestRunlog(unittest.TestCase):

    def set_test_instance(self, instance: EngineTestInstance):
        self._instance = instance

    @property
    def test_instance(self) -> EngineTestInstance:
        if self._instance is None:
            raise RuntimeError("test instance has not been set")
        return self._instance

    @property
    def rti(self) -> RuntimeInfo:
        return self.test_instance.runtimeinfo

    def assert_Runlog_HasItem(self, name: str):
        assert_Runlog_HasItem(self.rti, name)

    def assert_Runlog_HasNoItem(self, name: str):
        assert_Runlog_HasNoItem(self.rti, name)

    def assert_Runlog_HasItem_Started(self, name: str):
        assert_Runlog_HasItem_Started(self.rti, name)

    def assert_Runlog_HasItem_Completed(self, name: str, min_times=1):
        assert_Runlog_HasItem_Completed(self.rti, name, min_times)

    def assert_Runtime_HasRecord(self, name: str):
        assert_Runtime_HasRecord(self.rti, name)

    def assert_Runtime_HasRecord_Started(self, name: str):
        assert_Runtime_HasRecord_Started(self.rti, name)

    def assert_Runtime_HasRecord_Completed(self, name: str):
        assert_Runtime_HasRecord_Completed(self.rti, name)

    def test_start_complete_UodCommand(self):
        
        runner = EngineTestRunner(create_test_uod_local, "Reset")
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_command("Reset", increment_index=False)

            self.assert_Runlog_HasItem_Started("Reset")

            instance.run_until_command("Reset", state="completed")

            self.assert_Runlog_HasItem_Completed("Reset")

            self.assert_Runtime_HasRecord_Started("Reset")
            self.assert_Runtime_HasRecord_Completed("Reset")

    def test_start_complete_InstructionUodCommand(self):
        
        runner = EngineTestRunner(create_test_uod_local, "Mark: A")
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Mark", state="completed")

            self.assert_Runtime_HasRecord_Started("Mark: A")
            self.assert_Runtime_HasRecord_Completed("Mark: A")

            self.assert_Runlog_HasItem_Completed("Mark: A")

    def test_start_complete_EngineInternalCommand(self):
        cmd = "Increment run counter"

        
        runner = EngineTestRunner(create_test_uod_local, cmd)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Increment run counter", state="completed")

            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)

            self.assert_Runlog_HasItem_Completed(cmd)

    def test_Watch(self):
        program = """
Mark: a
Watch: Run Counter > -1
    Mark: b
Mark: c"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Mark", state="completed", arguments="b")

            cmd = "Mark: b"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd)

    def test_Alarm_invocations(self):
        program = """
Alarm: Run Counter < 5
    Mark: b
    Increment run counter
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Mark", state="completed")

            cmd = "Mark: b"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)

            instance.run_until_condition(lambda: instance.marks == ["b", "b", "b", "b", "b"])
            self.assert_Runlog_HasItem_Completed(cmd, 5)

    def test_Macro_no_invocation(self):
        program = """
Macro: A
    Mark: b
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_event("method_end")

            cmd = "Macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem(cmd)
            # is completed after definition. once it's called, the states start over
            self.assert_Runlog_HasItem_Completed(cmd, 1)

    def test_Macro_single_invocation(self):
        program = """
Macro: A
    Mark: b
Call macro: A
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_event("method_end")

            cmd = "Macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd)
            cmd = "Mark: b"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Call macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)

    def test_Macro_multiple_invocations(self):
        program = """
Macro: A
    Mark: b
Call macro: A
Call macro: A
Call macro: A
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_event("method_end")

            cmd = "Macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Mark: b"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 3)
            cmd = "Call macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 3)

    def test_Macro_restart(self):
        program = """\
Macro: M
    Mark: M1
Call macro: M
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_event("method_end")

            cmd = "Macro: M"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Mark: M1"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Call macro: M"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)

            instance.restart_and_run_until_started()
            instance.run_until_event("method_end")

            cmd = "Macro: M"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Mark: M1"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Call macro: M"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)

    def test_Macro_followed_by_blank(self):
        program = """
Macro: A
    Mark: b

Call macro: A
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_event("method_end")

            cmd = "Macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd)
            cmd = "Mark: b"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)
            cmd = "Call macro: A"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd, 1)

    def test_runlog_cancel_interpretercommand_watch(self):
        program = """
Watch: Block Time > .3s
    Mark: Foo
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_instruction("Watch")

            item_name = "Watch: Block Time > .3s"
            self.assert_Runlog_HasItem(item_name)

            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)
            instance_id = item.id

            # verify that its runlog item is cancelable
            self.assertEqual(item.cancellable, True)
            self.assertEqual(item.cancelled, False)
            # instance.print_runtime_table("pre-cancel")

            # cancel it. interpreter needs a tick to process it
            instance.engine.cancel_instruction(instance_id)
            # instance.run_until_event("method_end")

            instance.print_runtime_table("post-cancel")

            # fetch the updated (rebuilt from runtime records) runlog
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name(item_name)
            assert isinstance(item, RunLogItem)

            # verify it was cancelled
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.cancelled, True)
            self.assertEqual([], instance.marks)

            # needs end to be set or the frontend won't know the state is an end state
            self.assertIsNotNone(item.end)

    def test_runlog_force_interpretercommand_watch(self):
        program = """
Watch: Block Time > 3s
    Mark: Foo
"""
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_instruction("Watch")

            # instance.print_runtime_table("watch")
            # instance.print_runlog("watch")

            item_name = "Watch: Block Time > 3s"
            self.assert_Runlog_HasItem(item_name)

            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)

            # verify that its runlog item is forcible
            self.assertEqual(item.forcible, True)
            self.assertEqual(item.forced, False)

            # instance.print_runtime_table("pre-force")
            # instance.print_runlog("pre-force")

            # force it. interpreter needs a tick to process it
            instance.engine.force_instruction(instance_id=item.id)
            instance.run_ticks(1)

            # fetch the updated (rebuilt from runtime records) runlog
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)

            # verify it was forced
            # instance.print_runtime_table("post-force")
            # instance.print_runlog("post-force")

            self.assertEqual(item.forcible, False)
            self.assertEqual(item.forced, True)

            instance.run_until_instruction("Mark", state="completed")

            self.assertEqual(instance.marks, ['Foo'])

    def test_iteration_modification(self):
        # test iteration_modification as used in engine._execute_uod_command
        # doesn't seem to be a problem. little weird that the condition is not
        # reevaluated during iteration.
        foos = ['foo', 'bar', 'baz']
        bazs = []
        result = []
        for x in [f for f in foos if f not in bazs]:
            if x == "bar":
                bazs.append('baz')
            result.append(x)
        self.assertEqual(['foo', 'bar', 'baz'], result)

    def test_runlog_cancel_uod_command_Reset(self):
        
        runner = EngineTestRunner(create_test_uod_local, "Reset")
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_command("Reset")
            instance.run_ticks(1)  # needed for non-empty progress

            self.assert_Runlog_HasItem_Started("Reset")

            runlog = instance.runtimeinfo.get_runlog()
            self.assertEqual(1, len([i for i in runlog.items if i.name == "Reset"]))
            item = runlog.get_item_by_name_or_fail("Reset")
            instance_id = item.id

            # verify that its runlog item is cancelable
            instance.print_runtime_table("pre-cancel")
            instance.print_runlog("pre-cancel")
            self.assertEqual(item.cancellable, True)
            self.assertEqual(item.cancelled, False)

            assert item.progress is not None
            self.assertEqual(item.progress > 0.0, True)

            # cancel it. engine needs a tick to process it
            instance.engine.cancel_instruction(instance_id)
            instance.run_ticks(2)

            # fetch the updated (rebuilt from runtime records) runlog
            runlog = instance.runtimeinfo.get_runlog()
            self.assertEqual(1, len([i for i in runlog.items if i.name == "Reset"]))
            item = runlog.get_item_by_name_or_fail("Reset")

            # verify it was cancelled
            instance.print_runlog("post-cancel")
            instance.print_runtime_table("post-cancel")

            # verify record state
            record = instance.runtimeinfo.get_record_by_instance(instance_id)
            assert record is not None
            any_cancelled = False
            for st in record.states:
                if st.cancelled:
                    any_cancelled = True
            self.assertEqual(any_cancelled, True)

            # verify runlog state
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.cancelled, True)

            # assert we only have one item
            self.assertEqual(1, len([i for i in runlog.items if i.name == "Reset"]))

    def test_runlog_force_interpretercommand_Wait(self):
        program = """\
Mark: A
Wait: 5s
Mark: B
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()

            instance.run_until_instruction("Wait", state="started")
            item_name = "Wait: 5s"
            self.assert_Runlog_HasItem(item_name)
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)

            # verify that its runlog item is cancellable
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.cancelled, False)
            self.assertEqual(item.forcible, True)
            self.assertEqual(item.forced, False)

            instance_id = item.id
            instance.engine.force_instruction(instance_id)
            record = instance.runtimeinfo.get_record_by_instance_or_fail(instance_id)

            instance.run_until_condition(lambda: record.has_state(RuntimeRecordStateEnum.Forced))

            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)

            self.assertEqual(item.forcible, False)
            self.assertEqual(item.forced, True)

    def test_runlog_force_alarm(self):
        program = """
Alarm: Block Time > 3s
    Mark: Foo
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Alarm")
            #run_engine(e, program, 3)
            item_name = "Alarm: Block Time > 3s"
            self.assert_Runlog_HasItem(item_name)

            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)

            # verify that its runlog item is forcible
            self.assertEqual(item.forcible, True)
            self.assertEqual(item.forced, False)

            # force it
            instance.engine.force_instruction(instance_id=item.id)

            # fetch the updated (rebuilt from runtime records) runlog
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)

            # verify it was forced
            self.assertEqual(item.forced, True)
            self.assertEqual(item.forcible, False)

    def test_runlog_watch_in_alarm_body_runs_in_each_alarm_instance(self):
        program = """
Alarm: Block Time > 0s
    Watch: Block Time > 0.5s
        Mark: A
    Wait: 0.5s
"""
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Watch")

            alarm_item_name = "Alarm: Block Time > 0s"
            watch_item_name = "Watch: Block Time > 0.5s"

            self.assert_Runlog_HasItem(alarm_item_name)
            self.assert_Runlog_HasItem(watch_item_name)

            instance.index_step_back(3)
            instance.run_until_instruction("Watch", state="completed")
            self.assertEqual(instance.marks, ['A'])

            instance.run_until_condition(lambda: instance.marks == ["A", "A", "A"])

            self.assert_Runlog_HasItem_Completed(alarm_item_name, 2)  # verify we waited long enough

    def test_runlog_watch_states(self):
        program = """\
01 Watch: Block Time > 0.2s
02     Mark: A
03 Mark: X
"""
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Watch", state="awaiting_condition", increment_index=False)

            instance.print_runtime_table("Awaiting condition")

            r = instance.runtimeinfo.get_record_by_node("01")
            assert r is not None

            self.assertEqual("Watch: Block Time > 0.2s", r.name)
            self.assertTrue(r.has_state(RuntimeRecordStateEnum.AwaitingCondition))

            instance.run_until_instruction("Watch", state="started", increment_index=False)

            self.assertTrue(r.has_state(RuntimeRecordStateEnum.Started))

            instance.run_until_instruction("Watch", state="completed", increment_index=False)
            self.assertTrue(r.has_state(RuntimeRecordStateEnum.Completed))

            instance.print_runtime_table("Watch completed")


    def test_runlog_uod_commands(self):
        program = """
Reset
Reset
Reset
"""

        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_ticks(10)

            instance.print_runtime_table()
            instance.print_runlog()



    def test_runlog_item_awaiting_threshold_is_not_rendered(self):
        program = """
2 Mark: A
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Mark")

            mark_name = "Mark: A"
            self.assert_Runlog_HasNoItem(mark_name) # no runlog item

            instance.print_runtime_table()
            mark = instance.method_manager.program.get_first_child_or_fail(p.MarkNode)
            record = instance.runtimeinfo.get_record_by_node(mark.id)
            assert record is not None
            self.assertEqual(record.name, "Mark: A")
            self.assertTrue(record.has_state(RuntimeRecordStateEnum.AwaitingThreshold)) # but a record awaiting threshold

    def test_runlog_force_Mark_without_threshold_is_not_forcible(self):
        program = """
Mark: A
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Mark")

            mark_name = "Mark: A"
            self.assert_Runlog_HasItem(mark_name)
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(mark_name)

            self.assertEqual(item.forcible, False)
            self.assertEqual(item.forced, False)

    def test_wait_progress_InterpreterCommand(self):
        cmd = "Wait: 0.5s"
        item_name = cmd

        
        runner = EngineTestRunner(create_test_uod_local, cmd)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Wait", state="started")
            instance.run_ticks(1)  # ensure progress > 0

            instance.print_runlog()

            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runlog_HasItem(item_name)

            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)
            assert item.progress is not None
            self.assertAlmostEqual(item.progress, 0.2, delta=0.1)
            self.assertEqual(item.forcible, True)
            self.assertEqual(item.cancellable, False)

            instance.run_ticks(1)

            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(item_name)
            assert item.progress is not None
            self.assertAlmostEqual(item.progress, 0.5, delta=0.1)

            instance.run_until_event("method_end")
            self.assert_Runlog_HasItem_Completed(cmd)

    def test_runlog_Wait_is_forcible(self):
        program = """
Wait: 0.5s
"""
        
        runner = EngineTestRunner(create_test_uod_local, program)
        with runner.run() as instance:
            self.set_test_instance(instance)  # QND workaround to make test base class know to use instance for runlog asserts
            instance.start_run()
            instance.run_until_instruction("Wait")

            cmd_name = "Wait: 0.5s"
            self.assert_Runlog_HasItem(cmd_name)
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(cmd_name)

            self.assertEqual(item.forcible, True)
            self.assertEqual(item.forced, False)

            instance.engine.force_instruction(instance_id=item.id)
            # in effect immediately because its an enginecommand

            # get updated runlog
            runlog = instance.runtimeinfo.get_runlog()
            item = runlog.get_item_by_name_or_fail(cmd_name)

            self.assertEqual(item.forcible, False)
            self.assertEqual(item.forced, True)

    def test_runlog_aggregator_eq(self):
        l1 = RunLogLine(id="id", command_name="c", start=1, end=None, progress=None,
                        start_values=[], end_values=[],
                        forcible=False, forced=False, cancellable=False, cancelled=False)

        l2 = RunLogLine(id="id", command_name="c", start=1, end=None, progress=None,
                        start_values=[], end_values=[],
                        forcible=False, forced=False, cancellable=False, cancelled=False)

        l3 = RunLogLine(id="id2", command_name="c", start=1, end=None, progress=None,
                        start_values=[], end_values=[],
                        forcible=False, forced=False, cancellable=False, cancelled=False)

        l4 = RunLogLine(id="id", command_name="c", start=1, end=None, progress=0.2,
                        start_values=[], end_values=[],
                        forcible=False, forced=False, cancellable=False, cancelled=False)

        self.assertTrue(l1 == l2)
        self.assertTrue(l1 != l3)
        self.assertTrue(l1 != l4)

        rl1 = RunLog(lines=[l1])
        rl2 = RunLog(lines=[l2])
        rl3 = RunLog(lines=[l3])
        rl4 = RunLog(lines=[l4])

        self.assertTrue(rl1 == rl2)
        self.assertTrue(rl1 != rl3)
        self.assertTrue(rl1 != rl4)


    def test_Watch(self):
        cmd = """
Mark: a
Watch: Run Counter > -1
    Mark: b
Mark: c"""

        runner = EngineTestRunner(create_test_uod_local, method=cmd)
        with runner.run() as instance:
            self.set_test_instance(instance)
            instance.start_run()
            instance.run_until_instruction("Mark", "completed", arguments="b")

            cmd = "Mark: b"
            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runtime_HasRecord_Completed(cmd)
            self.assert_Runlog_HasItem_Completed(cmd)

    def test_Hold_w_argument_is_cancellable_and_not_forcible(self):
        method = """
Hold: 5s
Mark: A
"""
        cmd = "Hold: 5s"
        runner = EngineTestRunner(create_test_uod_local, method=method)
        with runner.run() as instance:
            self.set_test_instance(instance)
            instance.start_run()
            instance.run_until_instruction("Hold", "started")

            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runlog_HasItem_Started(cmd)
            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, True)
            self.assertEqual(item.forcible, False)

            instance.engine.cancel_instruction(item.id)

            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.cancelled, True)
            self.assertEqual(item.forcible, False)

            ticks = instance.run_until_instruction("Mark", "completed")
            self.assertLess(ticks, 4)

    def test_Hold_wo_argument_is_not_cancellable_and_not_forcible(self):
        cmd = "Hold"
        runner = EngineTestRunner(create_test_uod_local, method=cmd)
        with runner.run() as instance:
            self.set_test_instance(instance)
            instance.start_run()
            instance.run_until_instruction("Hold", state="started")

            self.assert_Runtime_HasRecord_Started(cmd)
            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.forcible, False)

    def test_Pause_w_argument_is_cancellable_and_not_forcible(self):
        method = """
Pause: 5s
Mark: A
"""
        cmd = "Pause: 5s"
        runner = EngineTestRunner(create_test_uod_local, method=method)
        with runner.run() as instance:
            self.set_test_instance(instance)
            instance.start_run()
            instance.run_until_instruction("Pause", "started")

            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runlog_HasItem_Started(cmd)
            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, True)
            self.assertEqual(item.forcible, False)

            instance.engine.cancel_instruction(item.id)

            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.cancelled, True)
            self.assertEqual(item.forcible, False)

            ticks = instance.run_until_instruction("Mark", "completed")
            self.assertLess(ticks, 4)

    def test_Pause_wo_argument_is_not_cancellable_and_not_forcible(self):
        cmd = "Pause"
        runner = EngineTestRunner(create_test_uod_local, method=cmd)
        with runner.run() as instance:
            self.set_test_instance(instance)
            instance.start_run()
            instance.run_until_instruction("Pause", state="started")

            self.assert_Runtime_HasRecord_Started(cmd)
            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.forcible, False)

    def test_priority_command_Stop_interrupts_pause(self):
        cmd = "Pause: 2s"
        runner = EngineTestRunner(create_test_uod_local, method=cmd)
        with runner.run() as instance:
            self.set_test_instance(instance)
            instance.start_run()
            instance.run_until_instruction("Pause", "started")

            self.assert_Runtime_HasRecord_Started(cmd)
            self.assert_Runlog_HasItem_Started(cmd)
            # item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)

            instance.engine.schedule_execution(EngineCommandEnum.STOP)

            ticks = instance.run_until_event("stop")
            self.assertLess(ticks, 4)


    def test_state_split(self):
        rti = RuntimeInfo()
        watch = p.WatchNode(id="1")
        record = RuntimeRecord.from_node(watch)
        rti._add_record(record)
        record._add_state("inst1", RuntimeRecordStateEnum.Started, 1, 1, None, watch)
        record._add_state("inst1", RuntimeRecordStateEnum.Cancelled, 2, 2, None, watch)
        record._add_state("inst2", RuntimeRecordStateEnum.Started, 4, 4, None, watch)
        record._add_state("inst2", RuntimeRecordStateEnum.Completed, 5, 5, None, watch)
        states_list = rti._split_states_by_instance_id(record)
        self.assertEqual(2, len(states_list))
        self.assertEqual(2, len(states_list[0]))
        self.assertEqual(2, len(states_list[1]))

    def test_formatting_str(self):
        x_short = "a"
        x_formatted = "         a"
        x_long = x_formatted + "x"
        self.assertEqual(rjust(x_short, 10), x_formatted)
        self.assertEqual(rjust(x_long, 10), x_formatted)

        self.assertEqual(rjust(" ", 4), "    ")
        self.assertEqual(rjust("", 4), "    ")

    def test_formatting_int(self):
        self.assertEqual(rjust(23, 4), "  23")
        self.assertEqual(rjust(12345, 4), "12345")  # don't crop ints


if __name__ == "__main__":
    unittest.main()
