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
from openpectus.protocol.models import Method
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)


configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()
logging.getLogger("openpectus.lang.exec.runlog").setLevel(logging.DEBUG)
logging.getLogger("openpectus.engine.method_manager").setLevel(logging.DEBUG)

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
            instance.engine.set_method(method2)
            with self.assertRaises(EngineError) as ctx:
                instance.run_ticks(1)
            self.assertIsInstance(ctx.exception.exception, MethodEditError)

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
            instance.engine.set_method(method2)
            with self.assertRaises(EngineError) as ctx:
                instance.run_ticks(1)
            self.assertIsInstance(ctx.exception.exception, MethodEditError)


    def test_may_edit_line_awaiting_threshold(self):

        method1 = Method.from_numbered_pcode("""\
00 Base: s
01 Mark: A
02 0.8 Mark: B
""")
        method2 = Method.from_numbered_pcode("""\
00 Base: s
01 Mark: A
02 0.8 Mark: C
""")
        method3 = Method.from_numbered_pcode("""\
00 Base: s
01 Mark: A
02 0.8 Mark: D
""")
        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="completed", arguments="A")
            instance.run_ticks(4)

            # verify no edit error
            instance.engine.set_method(method2)
            instance.run_ticks(1)

            # note that editing the node resets its threshold progress - which may be ok?
            instance.run_ticks(15)

            # verify edit error
            instance.engine.set_method(method3)
            with self.assertRaises(EngineError) as ctx:
                instance.run_ticks(1)
            self.assertIsInstance(ctx.exception.exception, MethodEditError)


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
            # instance.run_until_instruction("Mark", state="completed", arguments="A")
            instance.run_until_instruction("Mark", state="started", arguments="B")

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_event("method_end")

            # verify run behavior
            self.assertEqual(["A", "B", "C"], instance.marks)


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
04     0.2 Mark: C
""")
        method2 = Method.from_numbered_pcode("""\
01 Base: s
02 Watch: Run Time > 0s
03     Mark: B
04     0.2 Mark: C
05     Mark: D
""")

        runner = EngineTestRunner(create_test_uod, method1)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="awaiting_threshold", arguments="C")

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Mark", state="completed", arguments="D")

            # verify run behavior
            self.assertEqual(["B", "C", "D"], instance.marks)

    @unittest.skip("Looks like a straightforward fix - skip for now")
    def test_may_extend_macro_if_not_executed(self):

        # change is not included when macro is called??
        # clearly because interpreter holds macro nodes references to unmodified nodes
        # To fix:
        #   - move macro definition logic to analyzer
        #   - on method edit, rerun analyzers. this may fix other issues as well

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
            instance.run_until_instruction("Mark", state="completed", arguments="A")

            # verify no edit error
            instance.engine.set_method(method2)

            instance.run_until_instruction("Call macro", state="completed")

            # verify run behavior
            self.assertEqual(["A", "B", "C"], instance.marks)



# Case: injected code
# must also run in ffw (?)
