import unittest

from openpectus.aggregator.models import RunLog, RunLogLine
from openpectus.engine.engine import Engine
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.runlog import (
    RunLogItem, RuntimeInfo, RuntimeRecord, RuntimeRecordStateEnum,
    assert_Runtime_HasRecord,
    assert_Runtime_HasRecord_Completed, assert_Runtime_HasRecord_Started,
    assert_Runlog_HasItem, assert_Runlog_HasNoItem,
    assert_Runlog_HasItem_Completed, assert_Runlog_HasItem_Started, rjust,
)
from openpectus.lang.model.pprogramformatter import print_program
import openpectus.lang.model.ast as p
from openpectus.test.engine.test_engine import create_engine, create_test_uod

from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    continue_engine, run_engine, print_runlog, print_runtime_records,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)

configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()

start_ticks = 3

class TestRunlog(unittest.TestCase):
    def setUp(self):
        self.engine: Engine = create_engine()

    def tearDown(self):
        self.engine.cleanup()

    def assert_Runlog_HasItem(self, name: str):
        assert_Runlog_HasItem(self.engine.interpreter.runtimeinfo, name)

    def assert_Runlog_HasNoItem(self, name: str):
        assert_Runlog_HasNoItem(self.engine.interpreter.runtimeinfo, name)

    def assert_Runlog_HasItem_Started(self, name: str):
        assert_Runlog_HasItem_Started(self.engine.interpreter.runtimeinfo, name)

    def assert_Runlog_HasItem_Completed(self, name: str, min_times=1):
        assert_Runlog_HasItem_Completed(self.engine.interpreter.runtimeinfo, name, min_times)

    def assert_Runtime_HasRecord(self, name: str):
        assert_Runtime_HasRecord(self.engine.interpreter.runtimeinfo, name)

    def assert_Runtime_HasRecord_Started(self, name: str):
        assert_Runtime_HasRecord_Started(self.engine.interpreter.runtimeinfo, name)

    def assert_Runtime_HasRecord_Completed(self, name: str):
        assert_Runtime_HasRecord_Completed(self.engine.interpreter.runtimeinfo, name)

    def test_start_complete_UodCommand(self):
        e = self.engine

        run_engine(e, "Reset", start_ticks + 1)
        self.assert_Runlog_HasItem_Started("Reset")

        continue_engine(e, 5)

        print_runtime_records(e)
        print_runlog(e)

        self.assert_Runlog_HasItem_Completed("Reset")

        self.assert_Runtime_HasRecord_Started("Reset")
        self.assert_Runtime_HasRecord_Completed("Reset")

    def test_start_complete_InstructionUodCommand(self):
        e = self.engine

        run_engine(e, "Mark: A", start_ticks + 1)

        self.assert_Runtime_HasRecord_Started("Mark: A")
        self.assert_Runtime_HasRecord_Completed("Mark: A")

        self.assert_Runlog_HasItem_Completed("Mark: A")

    def test_start_complete_EngineInternalCommand(self):
        e = self.engine

        cmd = "Increment run counter"
        run_engine(e, cmd, start_ticks + 3)

        print_runtime_records(e)

        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)

        self.assert_Runlog_HasItem_Completed(cmd)

    def test_Watch(self):
        e = self.engine

        cmd = """
Mark: a
Watch: Run Counter > -1
    Mark: b
Mark: c"""
        run_engine(e, cmd, 10)

        cmd = "Mark: b"
        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)
        self.assert_Runlog_HasItem_Completed(cmd)

    def test_Alarm_single_invocation(self):
        e = self.engine

        cmd = """
Alarm: Run Counter < 5
    Mark: b
    Increment run counter
"""
        run_engine(e, cmd, 6)

        cmd = "Mark: b"
        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)
        self.assert_Runlog_HasItem_Completed(cmd, 1)

    def test_Alarm_multiple_invocations(self):
        e = self.engine

        cmd = """
Alarm: Run Counter < 3
    Mark: b
    Increment run counter
"""
        run_engine(e, cmd, 25)

        # print_runtime_records(e)
        # print_runlog(e)

        cmd = "Mark: b"

        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)
        self.assert_Runlog_HasItem_Completed(cmd, 3)

        # print_runtime_records(e)

    def test_Macro_no_invocation(self):
        e = self.engine

        cmd = """
Macro: A
    Mark: b
"""
        run_engine(e, cmd, 5)
        cmd = "Macro: A"
        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)
        self.assert_Runlog_HasItem(cmd)
        # is completed after definition. once it's called, the states start over
        self.assert_Runlog_HasItem_Completed(cmd, 1)

    def test_Macro_single_invocation(self):
        e = self.engine

        program = """
Macro: A
    Mark: b
Call macro: A
"""
        run_engine(e, program, 8)
        print_program(e.method_manager.program, show_blanks=True)
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
        e = self.engine

        cmd = """
Macro: A
    Mark: b
Call macro: A
Call macro: A
Call macro: A
"""
        run_engine(e, cmd, 12)
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
        e = self.engine

        cmd = """\
Macro: M
    Mark: M1
Call macro: M
"""
        run_engine(e, cmd, 10)
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

        e.schedule_execution(EngineCommandEnum.RESTART)
        continue_engine(e, 15)

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
        e = self.engine

        program = """
Macro: A
    Mark: b

Call macro: A
"""
        run_engine(e, program, 8)
        print_program(e.method_manager.program, show_blanks=True)
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
        e = self.engine
        program = """
Watch: Block Time > .3s
    Mark: Foo
"""
        run_engine(e, program, 3)
        item_name = "Watch: Block Time > .3s"
        self.assert_Runlog_HasItem(item_name)

        runlog = e.tracking.get_runlog()
        item = runlog.get_item_by_name(item_name)
        assert isinstance(item, RunLogItem)
        instance_id = item.id

        # verify that its runlog item is cancelable
        self.assertEqual(item.cancellable, True)
        self.assertEqual(item.cancelled, False)
        print_runtime_records(e)
        #print_runlog(e, "pre-cancel")

        # cancel it. interpreter needs a tick to process it
        e.cancel_instruction(instance_id)
        continue_engine(e, 5)

        # print_runtime_records(e, "post-cancel")

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify it was cancelled
        # print_runtime_records(e, "post-cancel")
        # print_runlog(e, "post-cancel")

        self.assertEqual(item.cancellable, False)
        self.assertEqual(item.cancelled, True)
        self.assertEqual([], e.interpreter.get_marks())

        # needs end to be set or the frontend won't know the state is an end state
        self.assertIsNotNone(item.end)

    def test_runlog_force_interpretercommand_watch(self):
        e = self.engine
        program = """
Watch: Block Time > 3s
    Mark: Foo
"""
        run_engine(e, program, 3)
        item_name = "Watch: Block Time > 3s"
        self.assert_Runlog_HasItem(item_name)

        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify that its runlog item is forcible
        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)
        # print_runtime_records(e)
        # print_runlog(e, "pre-force")

        # force it. interpreter needs a tick to process it
        e.force_instruction(instance_id=item.id)
        continue_engine(e, 1)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify it was forced
        # print_runtime_records(e, "post-force")
        # print_runlog(e, "post-force")

        self.assertEqual(item.forcible, False)
        self.assertEqual(item.forced, True)

        continue_engine(e, 2)
        self.assertEqual(['Foo'], e.interpreter.get_marks())

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
        e = self.engine
        # start uod command
        run_engine(e, "Reset", start_ticks + 1)
        self.assert_Runlog_HasItem_Started("Reset")

        runlog = e.tracking.get_runlog()
        self.assertEqual(1, len([i for i in runlog.items if i.name == "Reset"]))
        item = next((i for i in runlog.items if i.name == "Reset"), None)
        assert isinstance(item, RunLogItem)
        instance_id = item.id

        # verify that its runlog item is cancelable
        print_runlog(e)
        self.assertEqual(item.cancellable, True)
        self.assertEqual(item.cancelled, False)

        print_runtime_records(e)
        assert item.progress is not None
        self.assertEqual(item.progress > 0.0, True)

        # cancel it. engine needs a tick to process it
        e.cancel_instruction(instance_id)
        continue_engine(e, 1)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == "Reset"), None)
        assert isinstance(item, RunLogItem)

        # verify it was cancelled
        print_runlog(e)
        print_runtime_records(e, "post-cancel")

        # verify record state
        record = e.tracking.records[0]
        any_cancelled = False
        for st in record.states:
            if st.cancelled:
                any_cancelled = True
        self.assertEqual(any_cancelled, True)

        # verify runlon
        self.assertEqual(item.cancellable, False)
        self.assertEqual(item.cancelled, True)

        # assert we only have one item
        self.assertEqual(1, len([i for i in runlog.items if i.name == "Reset"]))

    def test_runlog_force_interpretercommand_Wait(self):
        e = self.engine
        program = """\
Mark: A
Wait: 5s
Mark: B
"""
        item_name = "Wait: 5s"
        run_engine(e, program, 5)
        self.assert_Runlog_HasItem(item_name)
        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify that its runlog item is cancellable
        self.assertEqual(item.cancellable, False)
        self.assertEqual(item.cancelled, False)
        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)

        # print_runlog(e, "pre-force")
        # print_runtime_records(e, "pre-force")

        e.force_instruction(item.id)
        continue_engine(e, 3)

        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # print_runlog(e, "post-force")
        # print_runtime_records(e, "post-force")

        self.assertEqual(item.forcible, False)
        self.assertEqual(item.forced, True)

    def test_runlog_force_alarm(self):
        e = self.engine
        program = """
Alarm: Block Time > 3s
    Mark: Foo
"""
        run_engine(e, program, 3)
        item_name = "Alarm: Block Time > 3s"
        self.assert_Runlog_HasItem(item_name)

        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify that its runlog item is forcible
        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)
        print_runtime_records(e)
        print_runlog(e, "pre-force")

        # force it. interpreter needs a tick to process it
        e.force_instruction(instance_id=item.id)
        continue_engine(e, 1)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify it was forced
        print_runtime_records(e, "post-force")
        print_runlog(e, "post-force")

        self.assertEqual(item.forced, True)
        self.assertEqual(item.forcible, False)

        # continue_engine(e, 2)
        # self.assertEqual(['Foo'], e.interpreter.get_marks())

    def test_runlog_watch_in_alarm_body_runs_in_each_alarm_instance(self):
        e = self.engine
        program = """
Alarm: Block Time > 0s
    Watch: Block Time > 0.5s
        Mark: A
    Wait: 0.5s
"""
        run_engine(e, program, 5)
        alarm_item_name = "Alarm: Block Time > 0s"
        watch_item_name = "Watch: Block Time > 0.5s"

        #print_runtime_records(e, "start")

        self.assert_Runlog_HasItem(alarm_item_name)
        self.assert_Runlog_HasItem(watch_item_name)

        continue_engine(e, 5)
        self.assertEqual(['A'], e.interpreter.get_marks())

        continue_engine(e, 8)  # not sure how long to wait - but surely this is enough

        # print_runtime_records(e, "end")
        # print_runlog(e)
        self.assert_Runlog_HasItem_Completed(alarm_item_name, 2)  # verify we waited long enough
        self.assertEqual(['A', 'A'], e.interpreter.get_marks())

    def test_runlog_item_awaiting_threshold_is_not_rendered(self):
        e = self.engine
        program = """
2 Mark: A
"""
        run_engine(e, program, 4)

        mark_name = "Mark: A"
        self.assert_Runlog_HasNoItem(mark_name)

    def test_runlog_force_Mark_without_threshold_is_not_forcible(self):
        e = self.engine
        program = """
Mark: A
"""
        run_engine(e, program, 4)

        mark_name = "Mark: A"
        self.assert_Runlog_HasItem(mark_name)
        runlog = e.tracking.get_runlog()
        item = next(item for item in runlog.items if item.name == mark_name)
        assert item is not None

        self.assertEqual(item.forcible, False)
        self.assertEqual(item.forced, False)

    def test_wait_progress_InterpreterCommand(self):
        e = self.engine

        cmd = "Wait: 0.5s"
        item_name = cmd

        run_engine(e, cmd, start_ticks)
        print_runtime_records(e)
        print_runlog(e)

        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runlog_HasItem(item_name)

        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert item is not None and item.progress is not None
        self.assertAlmostEqual(item.progress, 0.2, delta=0.1)
        self.assertEqual(item.forcible, True)
        self.assertEqual(item.cancellable, False)

        continue_engine(e, 1)
        runlog = e.tracking.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert item is not None and item.progress is not None
        self.assertAlmostEqual(item.progress, 0.5, delta=0.1)

        continue_engine(e, 2)
        self.assert_Runlog_HasItem_Completed(cmd)

    def test_runlog_Wait_is_forcible(self):
        e = self.engine
        program = """
Wait: 0.5s
"""
        run_engine(e, program, 4)

        cmd_name = "Wait: 0.5s"
        self.assert_Runlog_HasItem(cmd_name)
        runlog = e.tracking.get_runlog()
        item = next(item for item in runlog.items if item.name == cmd_name)
        assert item is not None

        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)

        e.force_instruction(instance_id=item.id)
        continue_engine(e, 1)

        # get updated runlog
        runlog = e.tracking.get_runlog()
        item = next(item for item in runlog.items if item.name == cmd_name)
        assert item is not None

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


class TestRunlog2(unittest.TestCase):

    def test_Watch(self):
        cmd = """
Mark: a
Watch: Run Counter > -1
    Mark: b
Mark: c"""

        runner = EngineTestRunner(create_test_uod, method=cmd)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", "completed", arguments="b")

            cmd = "Mark: b"
            assert_Runtime_HasRecord_Started(instance.runtimeinfo, cmd)
            assert_Runtime_HasRecord_Completed(instance.runtimeinfo, cmd)
            assert_Runlog_HasItem_Completed(instance.runtimeinfo, cmd)

    def test_Hold_w_argument_is_cancellable_and_not_forcible(self):
        method = """
Hold: 5s
Mark: A
"""
        cmd = "Hold: 5s"
        runner = EngineTestRunner(create_test_uod, method=method)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Hold", "started")

            assert_Runtime_HasRecord_Started(instance.runtimeinfo, cmd)
            assert_Runlog_HasItem_Started(instance.runtimeinfo, cmd)
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
            self.assertLess(ticks, 3)

    def test_Hold_wo_argument_is_not_cancellable_and_not_forcible(self):
        cmd = "Hold"
        runner = EngineTestRunner(create_test_uod, method=cmd)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Hold")

            assert_Runtime_HasRecord_Started(instance.runtimeinfo, cmd)
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
        runner = EngineTestRunner(create_test_uod, method=method)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Pause", "started")

            assert_Runtime_HasRecord_Started(instance.runtimeinfo, cmd)
            assert_Runlog_HasItem_Started(instance.runtimeinfo, cmd)
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
            self.assertLess(ticks, 3)

    def test_Pause_wo_argument_is_not_cancellable_and_not_forcible(self):
        cmd = "Pause"
        runner = EngineTestRunner(create_test_uod, method=cmd)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Pause")

            assert_Runtime_HasRecord_Started(instance.runtimeinfo, cmd)
            item = instance.runtimeinfo.get_runlog().get_item_by_name(cmd)
            assert item is not None
            self.assertEqual(item.cancellable, False)
            self.assertEqual(item.forcible, False)

    def test_priority_command_Stop_interrupts_pause(self):
        cmd = "Pause: 2s"
        runner = EngineTestRunner(create_test_uod, method=cmd)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Pause", "started")

            assert_Runtime_HasRecord_Started(instance.runtimeinfo, cmd)
            assert_Runlog_HasItem_Started(instance.runtimeinfo, cmd)
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
        #record._add_state("inst1", RuntimeRecordStateEnum.Cancelled, 3, 3, None, None)
        record._add_state("inst2", RuntimeRecordStateEnum.Started, 4, 4, None, watch)
        record._add_state("inst2", RuntimeRecordStateEnum.Completed, 5, 5, None, watch)
        states_list = rti._split_states_by_instance_id(record)
        self.assertEqual(2, len(states_list))
        self.assertEqual(2, len(states_list[0]))
        #self.assertEqual(3, len(states_list[0]))
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
