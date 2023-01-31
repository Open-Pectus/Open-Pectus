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
    PCommand,
    PError
)

INDENTATION_SPACES = 4


class PProgramBuilder(pcodeListener):
    def __init__(self) -> None:
        super().__init__()

        self.program: PProgram = PProgram()
        self.stack: List[PNode] = []
        """ Stack of scopes. """
        self.instruction: PInstruction | None = None
        self.last_instruction: PInstruction | None = None
        self.instructionError: PError | None = None
        """ The current instruction being built. """

    @property
    def scope(self) -> PNode:
        """ Returns the current program or instruction scope. """
        if not self.has_scope():
            raise LookupError("No scope has been set")
        return self.stack[-1]

    def has_scope(self) -> bool:
        return len(self.stack) > 0

    def scope_requires_indent(self, node: PNode):
        if isinstance(node, PBlock):
            return True
        return False

    def scope_requires_outdent(self, node: PNode):
        # TODO in end block(s) possibly reference outer scope. this allows static knowledge of outdent level
        # TODO multiple outdent not yet supported
        if isinstance(node, PEndBlock) or isinstance(node, PEndBlocks):
            return True
        return False

    def push_scope(self, new_scope: PInstruction, ctx: ParserRuleContext) -> PInstruction:
        """ Add instruction as the new inner scope.
        """
        self.set_start(new_scope, ctx)
        self.stack.append(new_scope)

        return new_scope

    def pop_scope(self) -> PNode:
        """ Leave the current scope and return to outer scope.
        """
        if len(self.stack) < 1:
            raise ValueError("Stack underflow")
        parent = self.stack.pop()
        return parent

    def get_program(self) -> PProgram:
        return self.program

    # def with_whildren(self, ctx: ParserRuleContext, f: Callable[[ParserRuleContext], None]):
    #     if ctx.children is not None:
    #         for x in ctx.children:
    #             f(x)

    def set_start(self, node: PNode, ctx: ParserRuleContext):
        node.line = ctx.start.line  # type: ignore
        node.indent = ctx.start.column  # type: ignore

    def enterProgram(self, ctx: pcodeParser.ProgramContext):
        # set program as scope
        self.program.line = ctx.start.line  # type: ignore
        self.program.indent = ctx.start.column  # type: ignore
        self.stack.append(self.program)

    def exitProgram(self, ctx: pcodeParser.ProgramContext):
        pass

    def enterInstruction(self, ctx: pcodeParser.InstructionContext):
        if self.instruction is not None:
            self.last_instruction = self.instruction
        self.instruction = None
        self.instructionError = None

        # validate indentation
        indent = int(ctx.start.column)  # type: ignore
        if math.remainder(indent, INDENTATION_SPACES) != 0:
            self.instructionError = PError(f'Bad indentation. Should be a multiple of {INDENTATION_SPACES}')

        # validate scope indentation
        scope = self.scope if self.has_scope() else self.program

        expected_indent = scope.indent
        if self.last_instruction is not None:
            if self.scope_requires_indent(scope):
                expected_indent += INDENTATION_SPACES
            elif self.scope_requires_outdent(scope):
                expected_indent = max(scope.indent - INDENTATION_SPACES, 0)

        if not indent == expected_indent:
            self.instructionError = PError(
                f'Bad indentation for new scope. Expected {expected_indent} spaces of indentation')

    def exitInstruction(self, ctx: pcodeParser.InstructionContext):
        # attach any error to current instruction
        if self.instructionError is not None:
            if self.instruction is not None:
                self.instruction.add_error(self.instructionError)
            else:
                raise ValueError(f"instructionError '{self.instructionError.message}' without instruction")

    def enterBlock(self, ctx: pcodeParser.BlockContext):
        if self.scope is None:
            raise NotImplementedError("No parent for block")

        block = PBlock(self.scope)
        self.set_start(block, ctx)
        self.instruction = block
        self.push_scope(block, ctx)

    def exitBlock(self, ctx: pcodeParser.BlockContext):
        pass

    def enterBlock_name(self, ctx: pcodeParser.Block_nameContext):
        if isinstance(self.scope, PBlock) and isinstance(self.instruction, PBlock):
            self.scope.name = ctx.getText()

    def exitBlock_name(self, ctx: pcodeParser.Block_nameContext):
        pass

    def enterEnd_block(self, ctx: pcodeParser.End_blockContext):
        if self.scope is None:
            raise NotImplementedError("No parent for end_block")
        self.instruction = PEndBlock(self.scope)

    def exitEnd_block(self, ctx: pcodeParser.End_blockContext):
        pass

    def enterEnd_blocks(self, ctx: pcodeParser.End_blocksContext):
        if self.scope is None:
            raise NotImplementedError("No parent for end_blocks")
        self.instruction = PEndBlocks(self.scope)

    def exitEnd_blocks(self, ctx: pcodeParser.End_blocksContext):
        pass

    def enterCommand(self, ctx: pcodeParser.CommandContext):
        assert self.scope is not None
        command = PCommand(self.scope)
        self.set_start(command, ctx)
        self.instruction = command

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
        assert self.scope is not None
        node = PWatch(self.scope)
        self.push_scope(node, ctx)

    def exitWatch(self, ctx: pcodeParser.WatchContext):
        pass

    def enterCondition(self, ctx: pcodeParser.ConditionContext):
        assert isinstance(self.scope, PWatch | PAlarm)
        self.scope.condition = ctx.getText()

    def enterAlarm(self, ctx: pcodeParser.AlarmContext):
        assert self.scope is not None
        node = PAlarm(self.scope)
        self.instruction = node
        self.push_scope(node, ctx)

    def exitAlarm(self, ctx: pcodeParser.AlarmContext):
        pass

    def enterTimeexp(self, ctx: pcodeParser.TimeexpContext):
        assert self.scope is not None
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
