import logging
import math
from typing import List

from antlr4 import ParserRuleContext
from antlr4.Token import CommonToken

from openpectus.lang.grammar.codegen.pcodeParser import pcodeParser
from openpectus.lang.grammar.codegen.pcodeListener import pcodeListener

from openpectus.lang.model.pprogram import (
    PCommandWithDuration,
    PDuration,
    PInstError,
    PNode,
    PProgram,
    PInstruction,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PMacro,
    PCallMacro,
    PMark,
    PBatch,
    PCommand,
    PError,
    PBlank,
    PCondition,
    PComment,
    PErrorInstruction
)

INDENTATION_SPACES = 4

logger = logging.getLogger(__name__)


class PProgramBuilder(pcodeListener):
    def __init__(self) -> None:
        super().__init__()

        self.program: PProgram = PProgram()
        self.stack: List[PNode] = []
        """ Stack of scopes. """

        self.instruction: PInstruction | None = None
        """ The current instruction being built. """

        self.prev_instruction: PInstruction | None = None
        """ The previous instruction. """

        self.instruction_start: InstructionStart | None = None
        """ Start position of the current instruction. """

        self.instruction_error: PError | None = None
        """ Error to be attached to the current instruction. """

        self.expect_indent: bool = False
        """ Flag raised by instructions that expect the next instruction to be additionally indented """

    @property
    def scope(self) -> PNode:
        """ Returns the current program or instruction scope. """
        if not self.has_scope():
            raise LookupError("No scope has been set")
        return self.stack[-1]

    def has_scope(self) -> bool:
        return len(self.stack) > 0

    def push_scope(self, new_scope: PInstruction, ctx: ParserRuleContext) -> PInstruction:
        """ Add instruction as the new inner scope.
        """
        self.stack.append(new_scope)
        self.expect_indent = True

        return new_scope

    def pop_scope(self) -> PNode:
        """ Leave the current scope and return to outer scope.
        """
        if len(self.stack) < 1:
            raise ValueError("Stack underflow")
        parent_scope = self.stack.pop()
        return parent_scope

    def get_program(self) -> PProgram:
        return self.program


    def enterProgram(self, ctx: pcodeParser.ProgramContext):
        # set program as scope
        self.program.line = ctx.start.line
        self.program.indent = ctx.start.column
        self.stack.append(self.program)

    def enterInstruction(self, ctx: pcodeParser.InstructionContext):
        instruction_text = ctx.getText()
        instruction_text = "" if instruction_text is None else instruction_text.strip()

        def is_blank_or_comment():
            if instruction_text == "":
                return True
            elif instruction_text.startswith("#"):
                return True
            return False

        if not isinstance(self.instruction, (PBlank, PComment)):
            self.prev_instruction = self.instruction
        self.instruction = None
        self.instruction_error = None
        self.instruction_start = InstructionStart(ctx.start.line, ctx.start.column)

        indent = int(ctx.start.column)
        if math.remainder(indent, INDENTATION_SPACES) != 0:
            # validate indentation as multiple of INDENTATION_SPACES
            self.instruction_error = PError(f'Bad indentation. Should be a multiple of {INDENTATION_SPACES}')
        else:
            # validate scope indentation
            assert isinstance(self.scope.indent, int), "Expect indent always set"
            prev_indent = 0 \
                if self.prev_instruction is None or self.prev_instruction.indent is None \
                else self.prev_instruction.indent
            # if outdented, just pop to relevant parent scope
            # unless it's a blank or comment
            if not is_blank_or_comment():
                if indent < prev_indent:
                    x = indent
                    while (x < prev_indent):
                        self.pop_scope()
                        x += INDENTATION_SPACES
                # if additional indent, check that this matches expectation set by previous instruction
                elif indent > prev_indent:
                    if not self.expect_indent:
                        self.instruction_error = PError(
                            f"Bad indentation. Additional indentation unexpected. Expected {prev_indent} " +
                            " spaces of indentation")
                        # clear the invalid extra indentation to avoid errors in following instructions
                        self.instruction_start.indent = prev_indent
                    elif indent != prev_indent + INDENTATION_SPACES:
                        self.instruction_error = PError(
                            f"Bad indentation. Expected {prev_indent + INDENTATION_SPACES} spaces of indentation")
                    self.expect_indent = False
                # if no change in indentation but one was expected, set error
                elif self.expect_indent:
                    self.instruction_error = PError(
                        f"Bad indentation. Expected additional indentation to {prev_indent + INDENTATION_SPACES} spaces")

    def exitInstruction(self, ctx: pcodeParser.InstructionContext):
        # attach any error to current instruction
        if self.instruction_error is not None:
            if self.instruction is None:
                self.instruction = PErrorInstruction(self.scope, ctx.getText())
            elif isinstance(self.instruction, PBlank):
                # skip indentation errors in blank lines
                # TODO use error code instead
                if 'indentation' not in (self.instruction_error.message or ""):
                    self.instruction.add_error(self.instruction_error)
            else:
                self.instruction.add_error(self.instruction_error)

        # attach start position
        assert self.instruction_start is not None
        if self.instruction is None:
            self.instruction = PErrorInstruction(self.scope, ctx.getText())

        self.instruction.line = self.instruction_start.line
        self.instruction.indent = self.instruction_start.indent

    def enterBlock(self, ctx: pcodeParser.BlockContext):
        self.instruction = PBlock(self.scope)
        self.push_scope(self.instruction, ctx)

    def enterBlock_name(self, ctx: pcodeParser.Block_nameContext):
        if isinstance(self.scope, PBlock) and isinstance(self.instruction, PBlock):
            self.scope.name = ctx.getText()

    def enterEnd_block(self, ctx: pcodeParser.End_blockContext):
        self.instruction = PEndBlock(self.scope)

    def enterEnd_blocks(self, ctx: pcodeParser.End_blocksContext):
        self.instruction = PEndBlocks(self.scope)

    def enterCommand(self, ctx: pcodeParser.CommandContext):
        self.instruction = PCommand(self.scope)

    def enterCommand_name(self, ctx: pcodeParser.Command_nameContext):
        assert isinstance(self.instruction, PCommand)
        self.instruction.name = ctx.getText()

    def enterCommand_args(self, ctx: pcodeParser.Command_argsContext):
        assert isinstance(self.instruction, PCommand)
        self.instruction.args = ctx.getText()

    def enterWatch(self, ctx: pcodeParser.WatchContext):
        self.instruction = PWatch(self.scope)
        self.push_scope(self.instruction, ctx)

    def enterCondition(self, ctx: pcodeParser.ConditionContext):
        assert isinstance(self.scope, PWatch | PAlarm)
        assert isinstance(ctx.start, CommonToken)
        assert isinstance(ctx.stop, CommonToken)
        self.scope.condition = PCondition(ctx.getText(), ctx.start.column, ctx.stop.column)

    def enterCompare_op(self, ctx: pcodeParser.Compare_opContext):
        if isinstance(self.scope, (PAlarm, PWatch)) and self.scope.condition:
            self.scope.condition.op = ctx.getText()
            assert isinstance(ctx.start, CommonToken)
            assert isinstance(ctx.stop, CommonToken)
            self.scope.condition.op_start = ctx.start.column
            self.scope.condition.op_end = ctx.stop.column

    def enterCondition_lhs(self, ctx: pcodeParser.Condition_lhsContext):
        if isinstance(self.scope, (PAlarm, PWatch)) and self.scope.condition:
            self.scope.condition.lhs = ctx.getText()
            assert isinstance(ctx.start, CommonToken)
            assert isinstance(ctx.stop, CommonToken)
            self.scope.condition.lhs_start = ctx.start.column
            self.scope.condition.lhs_end = ctx.stop.column

    def enterCondition_rhs(self, ctx: pcodeParser.Condition_rhsContext):
        if isinstance(self.scope, (PAlarm, PWatch)) and self.scope.condition:
            self.scope.condition.rhs = ctx.getText()
            assert isinstance(ctx.start, CommonToken)
            assert isinstance(ctx.stop, CommonToken)
            self.scope.condition.rhs_start = ctx.start.column
            self.scope.condition.rhs_end = ctx.stop.column

    def enterAlarm(self, ctx: pcodeParser.AlarmContext):
        self.instruction = PAlarm(self.scope)
        self.push_scope(self.instruction, ctx)

    def enterMacro(self, ctx: pcodeParser.MacroContext):
        self.instruction = PMacro(self.scope)
        self.push_scope(self.instruction, ctx)

    def enterMacro_name(self, ctx: pcodeParser.Macro_nameContext):
        if isinstance(self.scope, PMacro) and isinstance(self.instruction, PMacro):
            self.scope.name = ctx.getText()

    def enterIncrement_rc(self, ctx: pcodeParser.Increment_rcContext):
        if self.instruction is None:
            self.instruction = PCommand(self.scope)
            self.instruction.name = ctx.getText()

    def enterRestart(self, ctx: pcodeParser.RestartContext):
        if self.instruction is None:
            self.instruction = PCommand(self.scope)
            self.instruction.name = ctx.getText()

    def enterStop(self, ctx: pcodeParser.StopContext):
        if self.instruction is None:
            self.instruction = PCommand(self.scope)
            self.instruction.name = ctx.getText()

    def enterPause(self, ctx: pcodeParser.PauseContext):
        assert self.instruction is None
        self.instruction = PCommandWithDuration(self.scope)
        self.instruction.name = ctx.PAUSE().getText()

    def enterHold(self, ctx: pcodeParser.HoldContext):
        assert self.instruction is None
        self.instruction = PCommandWithDuration(self.scope)
        self.instruction.name = ctx.HOLD().getText()

    def enterWait(self, ctx: pcodeParser.WaitContext):
        assert self.instruction is None
        self.instruction = PCommandWithDuration(self.scope)
        self.instruction.name = ctx.WAIT().getText()

    def enterDuration(self, ctx: pcodeParser.DurationContext):
        assert isinstance(self.instruction, PCommandWithDuration)
        self.instruction.duration = PDuration(ctx.getText())

    def enterMark(self, ctx: pcodeParser.MarkContext):
        self.instruction = PMark(self.scope)

    def enterMark_name(self, ctx: pcodeParser.Mark_nameContext):
        assert isinstance(self.instruction, PMark)
        self.instruction.name = ctx.getText()

    def enterBatch(self, ctx: pcodeParser.BatchContext):
        self.instruction = PBatch(self.scope)

    def enterBatch_name(self, ctx: pcodeParser.Batch_nameContext):
        assert isinstance(self.instruction, PBatch)
        self.instruction.name = ctx.getText()

    def enterCall_macro(self, ctx: pcodeParser.Call_macroContext):
        self.instruction = PCallMacro(self.scope)

    def enterCall_macro_name(self, ctx: pcodeParser.Call_macro_nameContext):
        assert isinstance(self.instruction, PCallMacro)
        self.instruction.name = ctx.getText()

    def enterTimeexp(self, ctx: pcodeParser.TimeexpContext):
        # NOTE: there is currently a mismatch between PInstruction which have 'time' and the grammar
        # where not all instructions have 'time'.
        assert isinstance(self.instruction, PInstruction)
        time = ctx.getText()
        self.instruction.time = None if time is None or time.strip() == '' else float(time)

    def enterComment(self, ctx: pcodeParser.CommentContext):
        if self.instruction is None:
            self.instruction = PComment(self.scope)

        if self.instruction.comment == "":
            comment = ctx.getText()
            comment = "" if comment is None else comment[1:]
            self.instruction.comment = comment
        else:
            # account for multiple comments on same line
            self.instruction.comment += ctx.getText()

    def enterBlank(self, ctx: pcodeParser.BlankContext):
        self.instruction = PBlank(self.scope)

    def enterInst_error(self, ctx: pcodeParser.Inst_errorContext):
        if self.instruction is not None:
            self.instruction._inst_error = PInstError(ctx.getText())
        else:
            logger.warning("In enterInst_error, instruction was none. This should not happen")

    def enterError(self, ctx: pcodeParser.ErrorContext):
        pass

class InstructionStart():
    def __init__(self, line: int, indent: int) -> None:
        self.line = line
        self.indent = indent
