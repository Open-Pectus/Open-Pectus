import unittest

from openpectus.engine.engine import Engine
from openpectus.lang.exec.runlog import RunLogItemState, RuntimeRecordStateEnum
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
        self.fail(f"Runlog has no item named '{name}'")

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

        print_runtime_records(e)
        print_runlog(e)

        cmd = "Mark: b"

        self.assert_Runtime_HasRecord_Started(cmd)
        self.assert_Runtime_HasRecord_Completed(cmd)
        self.assert_Runlog_HasItem_Completed(cmd, 3)


if __name__ == "__main__":
    unittest.main()
