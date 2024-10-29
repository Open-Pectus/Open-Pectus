import unittest
from uuid import UUID

from openpectus.aggregator.models import RunLog, RunLogLine
from openpectus.engine.engine import Engine
from openpectus.lang.exec.runlog import RunLogItem, RunLogItemState, RuntimeRecordStateEnum
from openpectus.test.engine.test_engine import create_engine
from openpectus.test.engine.utility_methods import (
    continue_engine, run_engine, print_runlog, print_runtime_records,
    configure_test_logger, set_engine_debug_logging
)

configure_test_logger()
set_engine_debug_logging()

class TestRunlog(unittest.TestCase):
    def setUp(self):
        self.engine: Engine = create_engine()

    def tearDown(self):
        self.engine.cleanup()

    def assert_Runlog_HasItem(self, name: str):
        runlog = self.engine.runtimeinfo.get_runlog()
        for item in runlog.items:
            if item.name == name:
                return
        item_names = [item.name for item in runlog.items]
        self.fail(f"Runlog has no item named '{name}'. It has these names:  {','.join(item_names)}")

    def assert_Runlog_HasItem_Started(self, name: str):
        runlog = self.engine.runtimeinfo.get_runlog()
        for item in runlog.items:
            if item.name == name and item.state == RunLogItemState.Started:
                return
        self.fail(f"Runlog has no item named '{name}' in Started state")

    def assert_Runlog_HasItem_Completed(self, name: str, min_times=1):
        occurrences = 0
        runlog = self.engine.runtimeinfo.get_runlog()
        for item in runlog.items:
            if item.name == name and item.state == RunLogItemState.Completed:
                occurrences += 1

        if occurrences < min_times:
            self.fail(f"Runlog item named '{name}' did not occur in Completed state at least " +
                      f"{min_times} time(s). It did occur {occurrences} time(s)")

    def assert_Runtime_HasRecord(self, name: str):
        for r in self.engine.runtimeinfo.records:
            if r.name == name:
                return
        self.fail(f"Runtime has no record named '{name}'")

    def assert_Runtime_HasRecord_Started(self, name: str):
        for r in self.engine.runtimeinfo.records:
            if r.name == name and r.has_state(RuntimeRecordStateEnum.Started):
                return
        self.fail(f"Runtime has no record named '{name}' in state Started")

    def assert_Runtime_HasRecord_Completed(self, name: str):
        for r in self.engine.runtimeinfo.records:
            if r.name == name and r.has_state(RuntimeRecordStateEnum.Started):
                return
        self.fail(f"Runtime has no record named '{name}' in state Completed")

    def test_start_complete_UodCommand(self):
        e = self.engine

        run_engine(e, "Reset", 3)
        self.assert_Runlog_HasItem_Started("Reset")

        continue_engine(e, 5)

        print_runtime_records(e)
        print_runlog(e)

        self.assert_Runlog_HasItem_Completed("Reset")

        self.assert_Runtime_HasRecord_Started("Reset")
        self.assert_Runtime_HasRecord_Completed("Reset")

    def test_start_complete_InstructionUodCommand(self):
        e = self.engine

        run_engine(e, "Mark: A", 3)

        self.assert_Runtime_HasRecord_Started("Mark: A")
        self.assert_Runtime_HasRecord_Completed("Mark: A")

        self.assert_Runlog_HasItem_Completed("Mark: A")

    def test_start_complete_EngineInternalCommand(self):
        e = self.engine

        cmd = "Increment run counter"
        run_engine(e, cmd, 5)

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
        run_engine(e, cmd, 5)

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
        run_engine(e, cmd, 5)

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
        run_engine(e, cmd, 10)

        # print_runtime_records(e)
        # print_runlog(e)

        cmd = "Mark: b"

        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)
        self.assert_Runlog_HasItem_Completed(cmd, 3)

        # print_runtime_records(e)

    def test_runlog_cancel_watch(self):
        e = self.engine
        program = """
Watch: Block Time > .3s
    Mark: Foo
"""
        run_engine(e, program, 3)
        item_name = "Watch: Block Time > .3s"
        self.assert_Runlog_HasItem(item_name)

        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)
        exec_id = item.id

        # verify that its runlog item is cancelable
        self.assertEqual(item.cancellable, True)
        self.assertEqual(item.cancelled, False)
        print_runtime_records(e)
        print_runlog(e, "pre-cancel")

        # cancel it. interpreter needs a tick to process it
        e.cancel_instruction(UUID(exec_id))
        continue_engine(e, 5)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify it was cancelled
        print_runtime_records(e, "post-cancel")
        print_runlog(e, "post-cancel")

        self.assertEqual(item.cancelled, True)
        self.assertEqual(item.cancellable, False)
        self.assertEqual([], e.interpreter.get_marks())

        # needs end to be set or the frontend won't know the state is and end state
        self.assertIsNotNone(item.end)

    def test_runlog_force_watch(self):
        e = self.engine
        program = """
Watch: Block Time > .3s
    Mark: Foo
"""
        run_engine(e, program, 3)
        item_name = "Watch: Block Time > .3s"
        self.assert_Runlog_HasItem(item_name)

        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)
        exec_id = item.id

        # verify that its runlog item is forcible
        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)
        print_runtime_records(e)
        print_runlog(e, "pre-force")

        # force it. interpreter needs a tick to process it
        e.force_instruction(UUID(exec_id))
        continue_engine(e, 1)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify it was forced
        print_runtime_records(e, "post-force")
        print_runlog(e, "post-force")

        self.assertEqual(item.forced, True)
        self.assertEqual(item.forcible, False)
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

    def test_runlog_cancel_uod_command(self):
        e = self.engine
        # start uod command
        run_engine(e, "Reset", 3)
        self.assert_Runlog_HasItem_Started("Reset")

        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == "Reset"), None)
        assert isinstance(item, RunLogItem)
        exec_id = item.id

        # verify that its runlog item is cancelable
        print_runlog(e)
        self.assertEqual(item.cancellable, True)
        self.assertEqual(item.cancelled, False)

        print_runtime_records(e)
        assert item.progress is not None
        self.assertEqual(item.progress > 0.0, True)

        # cancel it. engine needs a tick to process it
        e.cancel_instruction(UUID(exec_id))
        continue_engine(e, 1)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == "Reset"), None)
        assert isinstance(item, RunLogItem)

        # verify it was cancelled
        print_runlog(e)
        print_runtime_records(e, "post-cancel")
        self.assertEqual(item.cancelled, True)
        self.assertEqual(item.cancellable, False)

    def test_runlog_force_alarm(self):
        e = self.engine
        program = """
Alarm: Block Time > .3s
    Mark: Foo
"""
        run_engine(e, program, 3)
        item_name = "Alarm: Block Time > .3s"
        self.assert_Runlog_HasItem(item_name)

        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)
        exec_id = item.id

        # verify that its runlog item is forcible
        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)
        print_runtime_records(e)
        print_runlog(e, "pre-force")

        # force it. interpreter needs a tick to process it
        e.force_instruction(UUID(exec_id))
        continue_engine(e, 1)

        # fetch the updated (rebuilt from runtime records) runlog
        runlog = e.runtimeinfo.get_runlog()
        item = next((i for i in runlog.items if i.name == item_name), None)
        assert isinstance(item, RunLogItem)

        # verify it was forced
        print_runtime_records(e, "post-force")
        print_runlog(e, "post-force")

        self.assertEqual(item.forced, True)
        self.assertEqual(item.forcible, False)
        self.assertEqual(['Foo'], e.interpreter.get_marks())

    def test_runlog_watch_in_alarm_body_runs_in_each_alarm_instance(self):
        e = self.engine
        program = """
Alarm: Block Time > 0s
    Watch: Block Time > 0.5s
        Mark: A
    Wait: 0.5s
"""
        run_engine(e, program, 4)
        alarm_item_name = "Alarm: Block Time > 0s"
        watch_item_name = "Watch: Block Time > 0.5s"

        print_runtime_records(e, "start")

        self.assert_Runlog_HasItem(alarm_item_name)
        self.assert_Runlog_HasItem(watch_item_name)

        continue_engine(e, 6)
        self.assertEqual(['A'], e.interpreter.get_marks())

        continue_engine(e, 10)  # not sure how long to wait - but surely this is enough
        self.assert_Runlog_HasItem_Completed(alarm_item_name, 2)  # verify we waited long enough
        self.assertEqual(['A', 'A'], e.interpreter.get_marks())

    def test_runlog_force_Mark_w_threshold_is_forcible(self):
        e = self.engine
        program = """
2 Mark: A
"""
        run_engine(e, program, 4)

        mark_name = "Mark: A"
        self.assert_Runlog_HasItem(mark_name)
        runlog = e.runtimeinfo.get_runlog()
        item = next(item for item in runlog.items if item.name == mark_name)
        assert item is not None
        exec_id = UUID(item.id)

        self.assertEqual(item.forcible, True)
        self.assertEqual(item.forced, False)

        e.force_instruction(exec_id)
        continue_engine(e, 1)

        # get updated runlog
        runlog = e.runtimeinfo.get_runlog()
        item = next(item for item in runlog.items if item.name == mark_name)
        assert item is not None

        self.assertEqual(item.forcible, False)
        self.assertEqual(item.forced, True)

    def test_runlog_force_Mark_without_threshold_is_not_forcible(self):
        e = self.engine
        program = """
Mark: A
"""
        run_engine(e, program, 4)

        mark_name = "Mark: A"
        self.assert_Runlog_HasItem(mark_name)
        runlog = e.runtimeinfo.get_runlog()
        item = next(item for item in runlog.items if item.name == mark_name)
        assert item is not None

        self.assertEqual(item.forcible, False)
        self.assertEqual(item.forced, False)


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


if __name__ == "__main__":
    unittest.main()
