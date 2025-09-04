import logging
import time
import unittest
from typing import Any

from openpectus.lang.exec.errors import EngineError, MethodEditError
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.engine.hardware import RegisterDirection

import pint
from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection
from openpectus.lang.exec.uod import (
    UnitOperationDefinitionBase,
    UodCommand,
    UodBuilder,
)
from openpectus.lang.model.parser import ParserMethod, create_method_parser
from openpectus.protocol.models import Method
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)
import openpectus.lang.model.ast as p


configure_test_logger()
#set_engine_debug_logging()
set_interpreter_debug_logging()
logging.getLogger("openpectus.lang.exec.runlog").setLevel(logging.DEBUG)
logging.getLogger("openpectus.engine.method_manager").setLevel(logging.DEBUG)
#logging.getLogger("openpectus.lang.exec.visitor").setLevel(logging.DEBUG)


# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 s")


def create_test_uod() -> UnitOperationDefinitionBase:  # noqa
    def reset(cmd: UodCommand, **kvargs) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time.time())
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A", time.time())
            cmd.set_complete()

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
        cmd.context.tags["CmdWithRegex_Area"].set_value(number + number_unit, time.time())
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
        .with_hardware_none()
        .with_location("Test location")
        .with_hardware_register("FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
        .with_hardware_register(
            "Reset",
            RegisterDirection.Both,
            path="Objects;2:System;2:RESET",
            from_tag=lambda x: 1 if x == "Reset" else 0,
            to_tag=lambda x: "Reset" if x == 1 else "N/A",
        )
        .with_hardware_register(
            "Danger",
            RegisterDirection.Write,
            path="Objects;2:System;2:Danger",
            safe_value=False,
        )
        # Readings
        .with_tag(ReadingTag("FT01", "L/h"))
        .with_tag(SelectTag("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.Output))
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
    return uod


class TestMethodManager(unittest.TestCase):

    def test_may_not_edit_an_executed_line(self):
        method1 = Method.from_numbered_pcode("01 Mark: A")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="completed")

            method2 = Method.from_numbered_pcode("01 Mark: B")

            # verify edit error
            with self.assertRaises(MethodEditError):
                instance.engine.set_method(method2)

    def test_may_not_edit_a_started_line(self):
        # consider what changes we want to accept:
        # SPEC: can edit until threshold is completed - which is the same as node.started being set
        #   in get_method_state - return line as not started until threshold has passed
        #   change this test - may not edit started line
        # add line break to last line and then adding new lines (cannot currently express this in MethodState)
        #

        method1 = Method.from_numbered_pcode("01 Mark: A")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="started")

            method2 = Method.from_numbered_pcode("01 Mark: B")

            # verify edit error
            with self.assertRaises(MethodEditError):
                instance.engine.set_method(method2)


    def test_may_edit_line_awaiting_threshold(self):

        method1 = Method.from_numbered_pcode("""\
00 Base: s
01 Mark: A
02 0.8 Mark: B
03 
""")
        method2 = Method.from_numbered_pcode("""\
00 Base: s
01 Mark: A
02 0.8 Mark: C
03 
""")
        method3 = Method.from_numbered_pcode("""\
00 Base: s
01 Mark: A
02 0.8 Mark: D
03 
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.engine.interpreter.ffw_tick_limit = 50
            instance.start()
            instance.run_until_instruction("Mark", state="completed", arguments="A")
            instance.run_ticks(4)
            self.assertEqual(0, instance.method_manager.program.revision)
            self.assertEqual(True, instance.method_manager.program_is_started)

            # verify no edit error
            instance.engine.set_method(method2)

            self.assertEqual(1, instance.method_manager.program.revision)
            self.assertEqual(True, instance.method_manager.program_is_started)

            instance.run_until_instruction("Mark", state="completed", arguments="C")

            # verify edit error
            with self.assertRaises(MethodEditError):
                instance.engine.set_method(method3)

    def test_may_add_line_after_started_line(self):

        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Mark: B
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Mark: B
03 Mark: C
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="completed", arguments="A")

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_event("method_end")

            # verify run behavior
            self.assertEqual(["A", "B", "C"], instance.marks)

    def test_may_edit_line_after_started_line(self):
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Wait: 0.1s
03 Mark: B
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Wait: 0.1s
03 Info: C
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="completed", arguments="A")
            self.assertEqual(["A"], instance.marks)

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Info", state="completed", arguments="C")
            self.assertEqual(["A"], instance.marks)

    def test_may_extend_block_after_block_started(self):

        method1 = Method.from_numbered_pcode("""\
01 Block: A
02     Mark: B
""")
        method2 = Method.from_numbered_pcode("""\
01 Block: A
02     Mark: B
03     Mark: C
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="started", arguments="B")

            # verify no edit error
            instance.engine.set_method(method2)
            instance.run_ticks(1)

            instance.run_until_instruction("Mark", state="completed", arguments="C")

            # verify run behavior
            self.assertEqual(["B", "C"], instance.marks)


    def test_extended_block_does_end(self):
        method1 = Method.from_numbered_pcode("""\
01 Base: s
02 Block: B1
03     0.5 Mark: A
05     End block
""")

        method2 = Method.from_numbered_pcode("""\
01 Base: s
02 Block: B1
03     0.5 Mark: A
04     1.0 Mark: B
05     End block
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            block_tag = instance.engine.tags[SystemTagName.BLOCK]
            instance.run_until_instruction("Mark", state="started", arguments="A")

            # edit method
            instance.engine.set_method(method2)
            instance.run_ticks(1)

            self.assertEqual("B1", block_tag.get_value())
            instance.run_until_instruction("End block", state="completed")
            instance.run_ticks(5)

            # verify run behavior
            self.assertEqual(["A", "B"], instance.marks)

            # verify that block execution has completed
            self.assertEqual(None, block_tag.get_value())

    def test_may_extend_watch_after_watch_activated(self):

        # Editing a Watch body requires that FFW will also run interrupt handlers to find
        # the current node. This test verifies that.

        method1 = Method.from_numbered_pcode("""\
01 Base: s
02 Watch: Run Time > 0s
03     Mark: B
04     0.5 Mark: C
""")
        method2 = Method.from_numbered_pcode("""\
01 Base: s
02 Watch: Run Time > 0s
03     Mark: B
04     0.5 Mark: C
05     Mark: D
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.engine.interpreter.ffw_tick_limit = 50

            #instance.run_until_instruction("Mark", state="awaiting_threshold", arguments="C")
            instance.run_until_instruction("Mark", state="completed", arguments="B")

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Mark", state="completed", arguments="D")

            # verify run behavior
            self.assertEqual(["B", "C", "D"], instance.marks)

    def test_may_extend_alarm_after_alarm_activated(self):

        # Editing an Alarm body requires that FFW will also run interrupt handlers to find
        # the current node. This test verifies that.

        method1 = Method.from_numbered_pcode("""\
01 Base: s
02 Alarm: Run Time > 0s
03     Mark: B
04     0.5 Mark: C
""")
        method2 = Method.from_numbered_pcode("""\
01 Base: s
02 Alarm: Run Time > 0s
03     Mark: B
04     0.5 Mark: C
05     Mark: D
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.engine.interpreter.ffw_tick_limit = 50

            #instance.run_until_instruction("Mark", state="awaiting_threshold", arguments="C")
            instance.run_until_instruction("Mark", state="completed", arguments="B")

            # insert Mark: D and verify no edit error
            instance.engine.set_method(method2)
            instance.run_ticks(1)

            instance.run_until_instruction("Mark", state="completed", arguments="D")

            # verify run behavior
            self.assertEqual(["B", "C", "D"], instance.marks)

            # verify alarm is repeated
            alarm_node = instance.method_manager.program.get_first_child(p.AlarmNode)
            assert alarm_node is not None
            instance.run_until_condition(lambda: alarm_node.run_count == 2)
            self.assertEqual(["B", "C", "D", "B", "C", "D"], instance.marks)


    def test_may_extend_nested_alarm_after_alarm_activated(self):
        method1 = Method.from_numbered_pcode("""\
01 Base: s
02 Alarm: Run Time > 0s
03     Mark: B
04     0.5 Mark: C
""")
        method2 = Method.from_numbered_pcode("""\
01 Base: s
02 Alarm: Run Time > 0s
03     Mark: B
04     0.5 Mark: C
05     Watch: Run Time > 0s
06         Mark: D
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.engine.interpreter.ffw_tick_limit = 50

            instance.run_until_instruction("Mark", state="completed", arguments="B")

            # insert Mark: D and verify no edit error
            instance.engine.set_method(method2)
            instance.run_ticks(1)

            instance.run_until_instruction("Mark", state="completed", arguments="D")

            # verify run behavior
            self.assertEqual(["B", "C", "D"], instance.marks)


    def test_may_extend_alarm(self):
        method1 = Method.from_numbered_pcode("""\
02 Alarm: Run Time > 0s
03     Mark: B
04     Mark: C
""")
        method2 = Method.from_numbered_pcode("""\
02 Alarm: Run Time > 0s
03     Mark: B
04     Mark: C
05     Mark: D
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.engine.interpreter.ffw_tick_limit = 50

            instance.run_until_instruction("Mark", state="completed", arguments="B")

            # insert Mark: D and verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Mark", state="completed", arguments="D")

            # verify run behavior
            self.assertEqual(["B", "C", "D"], instance.marks)

            # verify alarm is repeated
            alarm_node = instance.method_manager.program.get_first_child(p.AlarmNode)
            assert alarm_node is not None
            instance.run_until_condition(lambda: alarm_node.run_count == 2)
            self.assertEqual(["B", "C", "D", "B", "C", "D"], instance.marks)

    def test_may_edit_blank_to_other_instruction(self):
        # When editing the last line, it is interpreted as an edited node type. This type of edit
        # is generally not supported, but if the source is blank, it should obviously be allowed
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Mark: B
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # Method from frontend must always be sent with a trailing blank line.
            # This means we should only test on such data

            instance.run_until_instruction("Mark", "completed", arguments="A")
            instance.run_ticks(2)

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Mark", "completed", arguments="B")
            self.assertEqual(["A", "B"], instance.marks)


    def test_may_edit_blank_to_other_instruction_in_watch(self):
        # When editing the last line, it is interpreted as an edited node type. This type of edit
        # is generally not supported, but if the source is blank, it should obviously be allowed
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Watch: Run Counter > -1
03     Mark: B
04 
05 Mark: X
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Watch: Run Counter > -1
03     Mark: B
04     Mark: C
05 Mark: X
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # Note line 04 - it does not matter whether it is indented or not in method1. 
            # Its indentation will be set to whatever method2 specifies            

            instance.run_until_instruction("Mark", "completed", arguments="B")

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Mark", "completed", arguments="X")

            self.assertEqual(["A", "B", "C", "X"], instance.marks)

    @unittest.skip(reason="Not yet implemented")
    def test_may_not_add_instruction_text_in_empty_lines(self):
        
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 
03 Watch: Run Counter > -1
04     Mark: X
05 
06 Mark: B
""")
        # in this method line 05 is not marked as completed even when 06 is completed. Not sure why.
        # but we have to validate against this

    def test_macro_allows_editing_uncalled_macro(self):
        # Can edit macro until it has run the first time
        # consider line state
        method1 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: A
03 Mark: C
04 Call macro: M
05 Mark: D
""")
        method2 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: B
03 Mark: C
04 Call macro: M
05 Mark: D
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="completed", arguments="C")

            # verify no edit error
            instance.engine.set_method(method2)

            # verify macros are defined in new revision
            self.assertEqual(1, len(instance.method_manager.program.macros))

            # method2 runs
            instance.run_until_instruction("Mark", state="completed", arguments="D")
            self.assertEqual(["C", "B", "D"], instance.marks)

    def test_macro_disallows_editing_called_macro(self):

        method1 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: B
03 Mark: A
04 Call macro: M
""")
        method2 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: B
05     Mark: C
03 Mark: A
04 Call macro: M
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Call macro", state="completed")

            # verify edit error
            with self.assertRaises(MethodEditError):
                instance.engine.set_method(method2)

    def test_compare_macro_source(self):
        logger = logging.getLogger("null")

        def test(macro1_pcode: str, macro2_pcode: str, expected_match: bool, id: int):
            with self.subTest(f"macro source match test {id}"):
                method1 = ParserMethod.from_pcode(macro1_pcode)
                method2 = ParserMethod.from_pcode(macro2_pcode)
                program1 = create_method_parser(method1).parse_method(method1)
                program2 = create_method_parser(method2).parse_method(method2)
                result = program1.matches_source(program2, logger)
                if result != expected_match:
                    self.fail(f"Expected match result {expected_match}, but was {result}")

        test(
            "Macro: M\n    Mark: A",
            "Macro: M\n    Mark: A",
            expected_match=True, id=1)
        test(
            "Macro: M\n    Mark: A",
            "Macro: M\n    Mark: A # comment",
            expected_match=True, id=2)
        test(
            "Macro: M\n    Mark: A",
            "Macro: X\n    Mark: A",
            expected_match=False, id=3)

        test("""\
Macro: M
    Mark: A
    Watch: Run counter > 0
        Mark: B
""",
             """\
Macro: M
    Mark: A
    Watch: Run counter > 0
        Mark: B

""",
             expected_match=True, id=4)

        test("""\
Macro: M
    Mark: A
    Watch: Run counter > 0
        Mark: B
        Mark: C
""",
             """\
Macro: M
    Mark: A
    Watch: Run counter > 0
        Mark: B

""",
             expected_match=False, id=5)

        test("""\
# foo

Macro: M
    Mark: A

    Watch: Run counter > 0
        Mark: B
        # baz
        Mark: C

    # bar

""",
             """\
Macro: M
    Mark: A
    Watch: Run counter > 0
        Mark: B
        Mark:     C
""",
             expected_match=True, id=6)
        
        

        # it works for all nodes even though we have only needed it for macros
        test("""\
# foo
Watch: Run counter > 0 # bar
    Mark: B
    # baz
""",
             """\
Watch: Run counter > 0
    Mark: B
""",
             expected_match=True, id=6)


# Generational Edits - multiple edits of running method revisions

    def test_edit_2_revisions(self):
        # test re-edits of method with interrupts and macros
        method1 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: A
03 Watch: Run Time > 1s
04     Mark: B
05 Wait: 0.2s
06 Mark: E
07  
""")
        method2 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: A
03 Watch: Run Time > 1s
04     Mark: B
05 Wait: 0.2s
06 Mark: E
07 Mark: F
""")
        method3 = Method.from_numbered_pcode("""\
01 Macro: M
02     Mark: A
03 Watch: Run Time > 1s
04     Mark: B
05 Wait: 0.2s
06 Mark: E
07 Mark: G
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Wait", state="completed")
            self.assertEqual([], instance.marks)

            # method2 runs
            instance.engine.set_method(method2)
            instance.run_until_instruction("Mark", state="completed", arguments="E")
            self.assertEqual(["E"], instance.marks)

            # method3 runs
            instance.engine.set_method(method3)
            instance.run_until_instruction("Mark", state="completed", arguments="G")
            self.assertEqual(["E", "G"], instance.marks)

    def test_watch_edit_2_revisions_1(self):
        # test re-edits of method with interrupt
        method1 = Method.from_numbered_pcode("""\
01 Watch: Run Time > 0.5s
02     Mark: A
03 Mark: B
04 Wait: 0.5s
05 Mark: C
06 
""")
        method2 = Method.from_numbered_pcode("""\
01 Watch: Run Time > 0.5s
02     Mark: A
03 Mark: B
04 Wait: 0.5s
05 Mark: D
06 
""")
        method3 = Method.from_numbered_pcode("""\
01 Watch: Run Time > 0.5s
02     Mark: A
03 Mark: B
04 Wait: 0.5s
05 Mark: D
06 Mark: E
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # method1 runs - watch interrupt registeret
            instance.run_until_instruction("Mark", state="completed", arguments="B")
            self.assertEqual(["B"], instance.marks)

            # method2 runs - watch interrupt executed
            instance.engine.set_method(method2)
            instance.run_until_instruction("Mark", state="completed", arguments="D")
            self.assertEqual(["B", "A", "D"], instance.marks)

            # method3 runs - does nothing
            instance.engine.set_method(method3)
            instance.run_until_instruction("Mark", state="completed", arguments="E")
            self.assertEqual(["B", "A", "D", "E"], instance.marks)

    def test_watch_edit_2_revisions_2(self):
        # test re-edits of method with interrupt
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Watch: Run Time > 0.5s
03     Mark: B
04 Mark: C
05 Wait: 0.5s
06 Mark: D
06 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Watch: Run Time > 0.5s
03     Mark: B
04 Mark: C
05 Wait: 0.5s
06 Mark: D
06 
""")
        method3 = Method.from_numbered_pcode("""\
01 Mark: A
02 Watch: Run Time > 0.5s
03     Mark: B
04 Mark: C
05 Wait: 0.5s
06 Mark: E
06 
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # method1 runs - watch interrupt not registeret
            instance.run_until_instruction("Mark", state="completed", arguments="A")
            self.assertEqual(["A"], instance.marks)

            # method2 runs - watch interrupt registered during ffw
            instance.engine.set_method(method2)
            instance.run_until_instruction("Mark", state="completed", arguments="C")
            self.assertEqual(["A", "C"], instance.marks)

            # method3 runs - watch interrupt executed
            instance.engine.set_method(method3)
            instance.run_until_instruction("Mark", state="completed", arguments="E")
            self.assertEqual(["A", "C", "B", "E"], instance.marks)


    def test_macro_edit_2_revisions_1(self):
        # test re-edits of method with macro
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Macro: M
03     Mark: B
04 Mark: C
05 Call macro: M
06 Mark: D
07 # 1
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Macro: M
03     Mark: B
04 Mark: C
05 Call macro: M
06 Mark: D
07 # 2
""")
        method3 = Method.from_numbered_pcode("""\
01 Mark: A
02 Macro: M
03     Mark: B
04 Mark: C
05 Call macro: M
06 Mark: D
07 # 3
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # method1 runs - nothing
            instance.run_until_instruction("Mark", state="completed", arguments="A")
            self.assertEqual(["A"], instance.marks)

            # method2 runs - macro registered
            instance.engine.set_method(method2)
            instance.run_until_instruction("Mark", state="completed", arguments="C")
            self.assertEqual(["A", "C"], instance.marks)

            # method3 runs - macro runs
            instance.engine.set_method(method3)
            instance.run_until_instruction("Mark", state="completed", arguments="D")
            self.assertEqual(["A", "C", "B", "D"], instance.marks)

    def test_macro_edit_2_revisions_2(self):
        # test re-edits of method with macro
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Macro: M
03     Mark: B
04 Mark: C
05 Call macro: M
06 Mark: D
07 # 1
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Macro: M
03     Mark: B
04 Mark: C
05 Call macro: M
06 Mark: D
07 # 2
""")
        method3 = Method.from_numbered_pcode("""\
01 Mark: A
02 Macro: M
03     Mark: B
04 Mark: C
05 Call macro: M
06 Mark: D
07 Call macro: M
08 Mark: E
09 
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # method1 runs - macro registered
            instance.run_until_instruction("Mark", state="completed", arguments="C")
            self.assertEqual(["A", "C"], instance.marks)

            # method2 runs - macro re-registers and runs
            instance.engine.set_method(method2)
            instance.run_until_instruction("Mark", state="completed", arguments="D")
            self.assertEqual(["A", "C", "B", "D"], instance.marks)

            # method3 runs - macro re-re-registers re-runs
            instance.engine.set_method(method3)
            instance.run_until_instruction("Mark", state="completed", arguments="E")
            self.assertEqual(["A", "C", "B", "D", "B", "E"], instance.marks)

# End Generational Edits

    @unittest.skip("TODO")
    def test_edit_injected(self):
        # hmm this is weird. a method is running and user injects code - that's not a method edit, just an injection
        # discussion in issue #829
        raise NotImplementedError()

    def test_active_node(self):
        # program.active_node is never ProgramNode and is only None right at the beginning until the first program child
        # node is visited. In this case, a method merge is not necessary, and a simple set will do. Automatic fallback is
        # implemented for this because it simplifiex merge to always have a valid target_node_id
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Mark: B
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_ticks(1)  # break fast (before first instruction is set as active_node)
            self.assertIsNone(instance.method_manager.program.active_node)

            rev_0 = instance.engine.method_manager.program.revision

            # verify no edit error
            status = instance.engine.set_method(method2)

            # verify fall back to set_method
            self.assertTrue(status == "set_method")

            rev_1 = instance.engine.method_manager.program.revision

            # not entirely sure how revisions (should) work, who increments and such
            # and its probably different when setting than merging
            self.assertEqual(rev_0, rev_1,
                             "Expected same method revision meaning that set_method happened instead of merge_method ")

            instance.run_until_instruction("Mark", state="completed", arguments="B")

            # verify run behavior
            self.assertEqual(["A", "B"], instance.marks)

    def test_wait(self):
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Wait: 0.3s
03 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Wait: 0.3s
03 Wait: 0.6s
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Wait", state="completed", arguments="0.3s")
            instance.engine.set_method(method2)

            instance.run_until_instruction("Wait", state="completed", arguments="0.6s")

    def test_wait_2(self):
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Wait: 0.3s
03 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Wait: 0.3s
03 Mark: B
04 
""")

        def edit_at(ticks: int):
            with self.subTest(ticks):
                runner = EngineTestRunner(create_test_uod, method1)
                with runner.run() as instance:
                    instance.start()
                    instance.run_ticks(ticks)
                    action = instance.engine.set_method(method2)
                    self.assertTrue(action == "merge_method")
                    instance.run_until_instruction("Mark", state="completed", arguments="B")

        edit_at(2)
        edit_at(3)
        edit_at(4)
        edit_at(5)
        edit_at(6)
        edit_at(7)


    def test_command_exec_id(self):
        # Check how it works if a program containing commands is edited.
        # Specifically, RuntimeInfo.with_edited_program() use RuntimeRecordState.clone() which reuses the
        # command instance and command_exec_id which may be a problem.
        # command is set by RuntimeRecord.add_state_internal_engine_command_set() and add_state_uod_command_set()
        # command_exec_id is set RuntimeRecord.add_command_state_started() and friends
        # so how to test this?

        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Reset
03 Wait: 0.2s
04 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Reset
03 Wait: 0.2s
04 Wait: 0.6s
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # Wait until mid-execution of Reset's 5 ticks, note that this is right at the end of the v0 method
            instance.run_until_instruction("Wait", state="completed", arguments="0.2s")

            instance.engine.set_method(method2)

            # note how Reset still gets ticked by engine, even though it's water under the bridge for interpreter
            instance.run_until_instruction("Wait", state="completed", arguments="0.6s")

    def test_command_exec_id_2(self):
        # Variation of the above that performs the edit earlier than end-of-method

        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Reset
03 Wait: 0.2s
04 
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Reset
03 Wait: 0.2s
04 Wait: 0.6s
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            # Wait until mid-execution of Reset's 5 ticks but also not at the end of the v0 method
            instance.run_until_instruction("Wait", state="started", arguments="0.2s")

            instance.engine.set_method(method2)

            # note how Reset still gets ticked by engine, even though interpreter
            instance.run_until_instruction("Wait", state="completed", arguments="0.6s")


    def test_continue_after_failed_edit(self):
        # if an edit fails, we should be able to continue running the old method, as if
        # no edit has happened, i.e. the old interpreter instance still works
        method1 = Method.from_numbered_pcode("""\
01 Mark: A
02 Mark: B
03 Mark: C
""")
        method2 = Method.from_numbered_pcode("""\
01 Mark: A
02 Mark: D
03 Mark: C
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()

            self.assertEqual(0, instance.method_manager.program.revision)
            instance.run_until_instruction("Mark", arguments="B")

            # can't edit running/completed line
            with self.assertRaises(MethodEditError):
                instance.engine.set_method(method2)

            # but the previous interpreter can still continue
            self.assertEqual(0, instance.method_manager.program.revision)
            instance.run_until_instruction("Mark", arguments="C")
            self.assertEqual(['A', 'B', 'C'], instance.marks)
