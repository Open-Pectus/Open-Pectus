import unittest

from antlr4.tree.Tree import ErrorNode as antlrErrorNode

from openpectus.lang.grammar.codegen.pcodeParser import ParserRuleContext, pcodeParser
from openpectus.lang.grammar.pgrammar import PGrammar


def parse(s):
    p = PGrammar()
    p.parse(s)
    return p


def get_first_child(ctx: ParserRuleContext, type) -> ParserRuleContext | None:
    """ Return the first child of the specified type (recursively) if one exists. Else return None"""
    if isinstance(ctx, type):
        return ctx
    if hasattr(ctx, "getChildren"):
        for child in ctx.getChildren():
            if isinstance(child, type):
                return child
            val = get_first_child(child, type)
            if val:
                return val


class ParserTest(unittest.TestCase):

    def assertContextHasNoChildError(self, ctx: ParserRuleContext):
        # if hasattr(ctx, 'exception'):
        #     self.assertIsNone(ctx.exception)
        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                self.assertNotIsInstance(
                    child,
                    antlrErrorNode,
                    f"Child of context '{ctx.getText()}' with type '{type(ctx).__name__}' was unexpectedly an ErrorNode")
                self.assertContextHasNoChildError(child)

    def test_mark(self):
        p = parse("Mark:   a  ")
        c = p.parser.mark()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.MarkContext)
        self.assertContextHasNoChildError(c)

    def test_block(self):
        p = parse("Block: foo")
        c = p.parser.block()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.BlockContext)
        self.assertContextHasNoChildError(c)

        p = parse("Block: foo")
        c = p.parser.program()  # type: ignore
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.ProgramContext)
        self.assertContextHasNoChildError(c)

    def test_macro(self):
        p = parse("Macro: foo")
        c = p.parser.macro()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.MacroContext)
        self.assertContextHasNoChildError(c)

    def test_end_block(self):
        p = parse("End block")
        c = p.parser.end_block()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.End_blockContext)
        self.assertContextHasNoChildError(c)

    def test_end_blocks(self):
        p = parse("End blocks")
        c = p.parser.end_blocks()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.End_blocksContext)
        self.assertContextHasNoChildError(c)

    def test_watch(self):
        p = parse("Watch")
        c = p.parser.watch()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.WatchContext)
        self.assertContextHasNoChildError(c)

    def test_watch_unit(self):
        p = parse("Watch: A > 2 mL")
        c = p.parser.watch()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.WatchContext)
        self.assertConditionValue(c.condition(), "A", ">", "2 mL")
        self.assertContextHasNoChildError(c)

    def test_watch_unitless(self):
        p = parse("Watch: A > 2")
        c = p.parser.watch()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.WatchContext)
        self.assertConditionValue(c.condition(), "A", ">", "2")
        self.assertContextHasNoChildError(c)

    def test_watch_with_mark(self):
        p = parse("""
Watch: A > 2 mL
    Mark: a
""")
        program = p.parser.program()  # type: ignore
        watch = get_first_child(program, pcodeParser.WatchContext)
        self.assertIsInstance(watch, pcodeParser.WatchContext)
        self.assertIsWatchWithCondition(watch, "A > 2 mL")  # type: ignore
        self.assertConditionValue(watch.condition(), "A", ">", "2 mL")  # type: ignore

        mark = get_first_child(program, pcodeParser.MarkContext)
        self.assertIsInstance(mark, pcodeParser.MarkContext)

    def test_watch_w_inst_error_colon(self):
        p = parse("""
Watch:
    Mark: A""")
        program = p.parser.program()  # type: ignore
        # p.printSyntaxTree(program)
        watch = get_first_child(program, pcodeParser.WatchContext)
        assert isinstance(watch, pcodeParser.WatchContext)
        mark = get_first_child(program, pcodeParser.MarkContext)
        self.assertIsInstance(mark, pcodeParser.MarkContext)

    def test_watch_w_inst_error_colon_comment(self):
        p = parse("""
Watch: # foo
    Mark: A""")
        program = p.parser.program()  # type: ignore
        # p.printSyntaxTree(program)
        watch = get_first_child(program, pcodeParser.WatchContext)
        assert isinstance(watch, pcodeParser.WatchContext)
        mark = get_first_child(program, pcodeParser.MarkContext)
        self.assertIsInstance(mark, pcodeParser.MarkContext)

    def test_watch_w_inst_error_minimal(self):
        p = parse("""
Watch
    Mark: A""")
        program = p.parser.program()  # type: ignore
        # p.printSyntaxTree(program)
        watch = get_first_child(program, pcodeParser.WatchContext)
        assert isinstance(watch, pcodeParser.WatchContext)
        mark = get_first_child(program, pcodeParser.MarkContext)
        self.assertIsInstance(mark, pcodeParser.MarkContext)

    def test_condition_unit(self):
        p = parse("X > 10 mL")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "X", ">", "10 mL")
        self.assertContextHasNoChildError(c)

    def test_condition_unit_no_ws(self):
        p = parse("X > 10mL")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "X", ">", "10mL")
        self.assertContextHasNoChildError(c)

    def test_condition_unit_percentage(self):
        p = parse("X > 10 %")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "X", ">", "10 %")
        self.assertContextHasNoChildError(c)

    def test_condition_ws(self):
        p = parse("X> 10mL")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "X", ">", "10mL")
        self.assertContextHasNoChildError(c)

    def test_identifier(self):
        def test(tag: str):
            with self.subTest(tag):
                p = parse(tag)
                c = p.parser.identifier()  # type: ignore
                self.assertIsNotNone(c)
                # p.printSyntaxTree(c)
                self.assertIsInstance(c, pcodeParser.IdentifierContext)
                self.assertContextHasNoChildError(c)
        test("X2")
        test("XY2")
        test("x2")
        test("foo")
        test("foo bar")

        test("KaZ")
        test("e 2")
        test("e")
        test("X")
        test("xY")
        test("Xy")

        # these are also valid identifiers even though they are also units
        test("s")
        test("L")
        test("min")
        test("mL")

    def test_identifier_ext(self):
        def test(tag: str):
            with self.subTest(tag):
                p = parse(tag)
                c = p.parser.identifier_ext()  # type: ignore
                self.assertIsNotNone(c)
                # p.printSyntaxTree(c)
                self.assertIsInstance(c, pcodeParser.Identifier_extContext)
                self.assertContextHasNoChildError(c)
                self.assertEqual(tag, c.getText())
        test("X2")
        test("XY2")
        test("x2")
        test("foo")
        test("foo bar")

        test("KaZ")
        test("e 2")
        test("e")
        test("X")
        test("xY")
        test("Xy")

        # these are also valid identifiers even though they are also units
        test("s")
        test("L")
        test("min")
        test("mL")

        # stuff that is not an identifier
        test("87")
        test("_")
        test(" 87: _")
        test("s+")
        test("B %")
        test("5%: test")

    def test_condition_tag_ws(self):
        p = parse("Block Time > 0.2 min")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "Block Time", ">", "0.2 min")
        self.assertContextHasNoChildError(c)

    def test_condition_unitless(self):
        p = parse("X > 10")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "X", ">", "10")
        self.assertContextHasNoChildError(c)

    def test_condition_negative_value(self):
        p = parse("X > -10")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        self.assertConditionValue(c, "X", ">", "-10")
        self.assertContextHasNoChildError(c)

    def test_condition_error(self):
        p = parse("X > ab mL")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        # this is not a parse error - will fail during build
        self.assertConditionValue(c, "X", ">", "ab mL")

    def test_condition_error_2(self):
        p = parse("X>-ab mL")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)
        # this is not a parse error - will fail during build
        self.assertConditionValue(c, "X", ">", "-ab mL")

    def assertIsWatchWithCondition(self, c: ParserRuleContext, condition: str):
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.WatchContext)
        _args = None
        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.ConditionContext):
                    _args = x.getText()
        self.assertEqual(_args, condition)

    def assertConditionValue(self, c: pcodeParser.ConditionContext,
                             expected_lhs, expected_op, expected_rhs):
        lhs, op, rhs = None, None, None
        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.Condition_lhsContext):
                    lhs = x.getText()
                elif isinstance(x, pcodeParser.Compare_opContext):
                    op = x.getText()
                elif isinstance(x, pcodeParser.Condition_rhsContext):
                    rhs = x.getText()
        self.assertEqual(lhs, expected_lhs)
        self.assertEqual(op, expected_op)
        self.assertEqual(rhs, expected_rhs)

    def test_watch_with_condition(self):
        p = parse("Watch: X > 10 mL")
        c = p.parser.watch()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsWatchWithCondition(c, "X > 10 mL")
        self.assertConditionValue(c.condition(), "X", ">", "10 mL")
        self.assertContextHasNoChildError(c)

    def assertIsAlarmWithCondition(self, c: ParserRuleContext, condition: str):
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.AlarmContext)
        _args = None
        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.ConditionContext):
                    _args = x.getText()
        self.assertEqual(_args, condition)

    def test_alarm(self):
        p = parse("Alarm")
        c = p.parser.alarm()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.AlarmContext)
        self.assertContextHasNoChildError(c)

    def test_alarm_with_condition(self):
        p = parse("Alarm: X > 10 mL")
        c = p.parser.alarm()  # type: ignore
        condition = c.condition()
        assert isinstance(condition, pcodeParser.ConditionContext)
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsAlarmWithCondition(c, "X > 10 mL")
        self.assertConditionValue(condition, "X", ">", "10 mL")
        self.assertContextHasNoChildError(c)

    def test_macro_with_mark(self):
        p = parse("""
Macro: A
    Mark: a
""")
        program = p.parser.program()  # type: ignore
        macro = get_first_child(program, pcodeParser.MacroContext)
        self.assertIsInstance(macro, pcodeParser.MacroContext)

        mark = get_first_child(program, pcodeParser.MarkContext)
        self.assertIsInstance(mark, pcodeParser.MarkContext)

    @unittest.skip("Fix in #662")
    def test_macro_invalid_with_mark(self):
        p = parse("""
Macro:
    Mark: a
""")
        program = p.parser.program()  # type: ignore
        macro = get_first_child(program, pcodeParser.MacroContext)
        self.assertIsInstance(macro, pcodeParser.MacroContext)

        mark = get_first_child(program, pcodeParser.MarkContext)
        self.assertIsInstance(mark, pcodeParser.MarkContext)

    def test_increment_rc(self):
        p = parse("Increment run counter")
        c = p.parser.increment_rc()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.Increment_rcContext)
        self.assertContextHasNoChildError(c)

    def test_stop(self):
        p = parse("Stop")
        c = p.parser.stop()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.StopContext)
        self.assertContextHasNoChildError(c)

    def test_pause(self):
        p = parse("Pause")
        c = p.parser.pause()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.PauseContext)
        self.assertContextHasNoChildError(c)

    def test_pause_w_arg(self):
        p = parse("Pause: 1 min")
        c = p.parser.pause()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.PauseContext)
        self.assertContextHasNoChildError(c)

    def test_hold(self):
        p = parse("Hold")
        c = p.parser.hold()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.HoldContext)
        self.assertContextHasNoChildError(c)

    def test_hold_w_arg(self):
        p = parse("Hold: 1 min")
        c = p.parser.hold()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.HoldContext)
        self.assertContextHasNoChildError(c)

    def test_wait_w_arg(self):
        p = parse("Wait:1s")
        c = p.parser.wait()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.WaitContext)
        self.assertContextHasNoChildError(c)

    def test_wait(self):
        # Note: Wait without duration is not a valid command, but its validity
        # is checked post-parsing so parsing itself must succeed
        p = parse("Wait")
        c = p.parser.wait()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.WaitContext)
        self.assertContextHasNoChildError(c)

    def test_duration(self):
        def test(code):
            with self.subTest(code):
                p = parse(code)
                c = p.parser.duration()  # type: ignore
                self.assertIsNotNone(c)
                # p.printSyntaxTree(c)
                self.assertIsInstance(c, pcodeParser.DurationContext)
                self.assertContextHasNoChildError(c)

        test("1 min")
        test("1.0 min")
        test("131,654 min")
        test("1.0 s")
        test("1s")
        test("87 h")
        test("87 foo")


    def test_restart(self):
        p = parse("Restart")
        c = p.parser.restart()  # type: ignore
        self.assertIsNotNone(c)
        # p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.RestartContext)
        self.assertContextHasNoChildError(c)

    def assertIsPCommandWithNameArgs(self, c: ParserRuleContext, name: str, args: str):
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.CommandContext)

        _name = None
        _args = None

        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.Command_nameContext):
                    _name = x.getText()
                elif isinstance(x, pcodeParser.Command_argsContext):
                    _args = x.getText()

        self.assertEqual(_name, name)
        self.assertEqual(_args, args)

    def test_command_name(self):
        self.assertEqual(parse("foo").parser.command_name().getText(), "foo")  # type: ignore

    def test_command_args(self):
        def test(code, expected_args):
            with self.subTest(code):
                # print(f"\nCode: '{code}'")
                p = parse(code)
                c = p.parser.command_args()  # type: ignore
                # print("Tree:")
                # p.printSyntaxTree(c)
                self.assertEqual(c.getText(), expected_args)

        test("bar", "bar")
        test("bar baz", "bar baz")
        test("bar=baz", "bar=baz")
        test("bar,baz", "bar,baz")
        # TODO test("bar,baz #comment", "bar,baz")

    def test_command(self):
        def test(code):
            with self.subTest(code):
                c = parse(code).parser.command()  # type: ignore
                self.assertIsNotNone(c)
                self.assertIsInstance(c, pcodeParser.CommandContext)
                # self.assertContextHasNoChildError(c)

        test("foo")
        test(" foo")
        test("   foo")
        test("1 foo")
        test("1.1 foo")
        test("1.02 foo")
        test("  1.3 foo")
        test("   1.02 foo")

        test("foo:")
        test(" foo:a:3")
        test(" foo: a:3")
        test("   foo:a=3")
        test("1 foo:3,4 ")
        test("1.1 foo: 3=4,5:6")
        test("2.95 Zero UV")

    def test_command_name_args_simple(self):
        def test(code, expected_name, expected_args):
            with self.subTest(code):
                # print(f"\nCode: '{code}'")
                p = parse(code)
                c = p.parser.command()  # type: ignore
                # print("Tree:")
                # p.printSyntaxTree(c)
                self.assertIsPCommandWithNameArgs(c, expected_name, expected_args)
                self.assertContextHasNoChildError(c)

        test("foo", "foo", None)
        test("foo: bar", "foo", "bar")
        test("1 foo: bar", "foo", "bar")
        test("7.89 foo: bar", "foo", "bar")
        test("7,89 foo: bar", "foo", "bar")
        test("2.95 Zero UV", "Zero UV", None)

    def test_command_name_args(self):
        def test(code, expected_name, expected_args):
            with self.subTest(code):
                # print(f"\nCode: '{code}'")
                p = parse(code)
                c = p.parser.command()  # type: ignore
                # print("Tree:")
                # p.printSyntaxTree(c)
                self.assertIsPCommandWithNameArgs(c, expected_name, expected_args)
                self.assertContextHasNoChildError(c)

        test("1.23 foo bar", "foo bar", None)
        test("foo: bar,baz", "foo", "bar,baz")
        test("1.23 foo: bar baz", "foo", "bar baz")
        test("foo: 3,5", "foo", "3,5")
        test("foo: 3=5", "foo", "3=5")

        test("Inlet PU01: VA01", "Inlet PU01", "VA01")
        test("PU01: 77.64 %", "PU01", "77.64 %")

    def test_program_ws(self):
        code = """
Block
    Mark : 1
        """
        p = parse(code)
        ctx = p.parser.program()  # type: ignore

        # p.printSyntaxTree(ctx)
        self.assertContextHasNoChildError(ctx)


if __name__ == "__main__":
    unittest.main()
