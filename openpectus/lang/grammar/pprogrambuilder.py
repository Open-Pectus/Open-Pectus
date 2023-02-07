import math
from typing import List

from antlr4 import ParserRuleContext

from lang.grammar.codegen.pcodeParser import pcodeParser
from lang.grammar.codegen.pcodeListener import pcodeListener

from lang.model.pprogram import (
    TimeExp,
    PNode,
    PProgram,
    PInstruction,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PMark,
    PCommand,
    PError,
    PBlank
)

INDENTATION_SPACES = 4


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

        self.instructionStart: InstructionStart | None = None
        """ Start position of the current instruction. """

        self.instructionError: PError | None = None
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

    # def with_whildren(self, ctx: ParserRuleContext, f: Callable[[ParserRuleContext], None]):
    #     if ctx.children is not None:
    #         for x in ctx.children:
    #             f(x)

    def enterProgram(self, ctx: pcodeParser.ProgramContext):
        # set program as scope
        self.program.line = ctx.start.line  # type: ignore
        self.program.indent = ctx.start.column  # type: ignore
        self.stack.append(self.program)

    def exitProgram(self, ctx: pcodeParser.ProgramContext):
        pass

    def enterInstruction(self, ctx: pcodeParser.InstructionContext):
        self.prev_instruction = self.instruction
        self.instruction = None
        self.instructionError = None
        self.instructionStart = InstructionStart(ctx.start.line, ctx.start.column)  # type: ignore

        indent = int(ctx.start.column)  # type: ignore
        if math.remainder(indent, INDENTATION_SPACES) != 0:
            # validate indentation as multiple of INDENTATION_SPACES
            self.instructionError = PError(f'Bad indentation. Should be a multiple of {INDENTATION_SPACES}')
        else:
            # validate scope indentation
            assert isinstance(self.scope.indent, int), "Expect indent always set"
            prev_indent = 0 \
                if self.prev_instruction is None or self.prev_instruction.indent is None \
                else self.prev_instruction.indent
            # if outdented, just pop to relevant parent scope
            if indent < prev_indent:
                x = indent
                while (x < prev_indent):
                    self.pop_scope()
                    x += INDENTATION_SPACES
            # if additional indent, check that this matches expectation set by previous instruction
            elif indent > prev_indent:
                if not self.expect_indent:
                    self.instructionError = PError(
                        f"Bad indentation. Additional indentation unexpected. Expected {prev_indent} spaces of indentation")
                elif indent != prev_indent + INDENTATION_SPACES:
                    self.instructionError = PError(
                        f"Bad indentation. Expected {prev_indent + INDENTATION_SPACES} spaces of indentation")
                self.expect_indent = False
            # if no change in indentation but one was expected, set error
            elif self.expect_indent:
                self.instructionError = PError(
                    f"Bad indentation. Expected additional indentation to {prev_indent + INDENTATION_SPACES} spaces")

    def exitInstruction(self, ctx: pcodeParser.InstructionContext):
        # attach any error to current instruction
        if self.instructionError is not None:
            if self.instruction is None:
                raise NotImplementedError(f"TODO Instruction not implemented: {ctx.getText()}")
            elif isinstance(self.instruction, PBlank):
                # skip indentation errors in blank lines
                # TODO use error code instead
                if 'indentation' not in (self.instructionError.message or ""):
                    self.instruction.add_error(self.instructionError)
            else:
                self.instruction.add_error(self.instructionError)

        # attach start position
        assert self.instruction is not None, f"Expected an instruction from src '{ctx.getText()}'"
        assert self.instructionStart is not None
        self.instruction.line = self.instructionStart.line
        self.instruction.indent = self.instructionStart.indent

    def enterBlock(self, ctx: pcodeParser.BlockContext):
        self.instruction = PBlock(self.scope)
        self.push_scope(self.instruction, ctx)

    def exitBlock(self, ctx: pcodeParser.BlockContext):
        pass

    def enterBlock_name(self, ctx: pcodeParser.Block_nameContext):
        if isinstance(self.scope, PBlock) and isinstance(self.instruction, PBlock):
            self.scope.name = ctx.getText()

    def exitBlock_name(self, ctx: pcodeParser.Block_nameContext):
        pass

    def enterEnd_block(self, ctx: pcodeParser.End_blockContext):
        self.instruction = PEndBlock(self.scope)

    def exitEnd_block(self, ctx: pcodeParser.End_blockContext):
        pass

    def enterEnd_blocks(self, ctx: pcodeParser.End_blocksContext):
        self.instruction = PEndBlocks(self.scope)

    def exitEnd_blocks(self, ctx: pcodeParser.End_blocksContext):
        pass

    def enterCommand(self, ctx: pcodeParser.CommandContext):
        self.instruction = PCommand(self.scope)

    def exitCommand(self, ctx: pcodeParser.CommandContext):
        pass

    def enterCommand_name(self, ctx: pcodeParser.Command_nameContext):
        assert isinstance(self.instruction, PCommand)
        self.instruction.name = ctx.getText()

    def exitCommand_name(self, ctx: pcodeParser.Command_nameContext):
        pass

    def enterCommand_args(self, ctx: pcodeParser.Command_argsContext):
        assert isinstance(self.instruction, PCommand)
        self.instruction.args = ctx.getText()

    def exitCommand_args(self, ctx: pcodeParser.Command_argsContext):
        pass

    def enterWatch(self, ctx: pcodeParser.WatchContext):
        self.instruction = PWatch(self.scope)
        self.push_scope(self.instruction, ctx)

    def exitWatch(self, ctx: pcodeParser.WatchContext):
        pass

    def enterCondition(self, ctx: pcodeParser.ConditionContext):
        assert isinstance(self.scope, PWatch | PAlarm)
        self.scope.condition = ctx.getText()

    def enterAlarm(self, ctx: pcodeParser.AlarmContext):
        self.instruction = PAlarm(self.scope)
        self.push_scope(self.instruction, ctx)

    def exitAlarm(self, ctx: pcodeParser.AlarmContext):
        pass

    def enterMark(self, ctx: pcodeParser.MarkContext):
        self.instruction = PMark(self.scope)

    def exitMark(self, ctx: pcodeParser.MarkContext):
        pass

    def enterMark_name(self, ctx: pcodeParser.Mark_nameContext):
        assert isinstance(self.instruction, PMark)
        self.instruction.name = ctx.getText()

    def exitMark_name(self, ctx: pcodeParser.Mark_nameContext):
        pass

    def enterTimeexp(self, ctx: pcodeParser.TimeexpContext):
        # NOTE: there is currently a mismatch between PInstruction which have 'time' and the grammar
        # where not all instructions have 'time'.
        assert isinstance(self.instruction, PInstruction)
        self.instruction.time = TimeExp(ctx.getText())

    def exitTimeexp(self, ctx: pcodeParser.TimeexpContext):
        pass

    def enterComment(self, ctx: pcodeParser.CommentContext):
        pass

    def exitComment(self, ctx: pcodeParser.CommentContext):
        pass

    def enterBlank(self, ctx: pcodeParser.BlankContext):
        self.instruction = PBlank(self.scope)

    def exitBlank(self, ctx: pcodeParser.BlankContext):
        pass

    def enterError(self, ctx: pcodeParser.ErrorContext):
        pass

    def exitError(self, ctx: pcodeParser.ErrorContext):
        pass


class InstructionStart():
    def __init__(self, line: int, indent: int) -> None:
        self.line = line
        self.indent = indent
