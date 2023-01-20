from typing import List

from .codegen.pcodeLexer import pcodeLexer
from .codegen.pcodeParser import pcodeParser
from .codegen.pcodeListener import pcodeListener

from antlr4 import InputStream, CommonTokenStream, Token, ParserRuleContext
from antlr4.tree.Tree import ParseTree, ParseTreeWalker

from lang.model.pprogram import TimeExp, PNode, PProgram, PInstruction, PCommand, PBlock


class PGrammar:
    def __init__(self) -> None:
        self.lexer = pcodeLexer
        self.parser = pcodeParser

    def parse(self, code: str):  # code: TextIOWrapper):
        input = InputStream(code)  # type: ignore , TODO clean this up
        self.lexer = pcodeLexer(input)
        stream = CommonTokenStream(self.lexer)
        self.parser = pcodeParser(stream)

    def build_model(self) -> PProgram:
        self.tree = self.parser.program()  # type: ignore
        listener = PListener()
        walker = ParseTreeWalker()
        walker.walk(listener, self.tree)
        return listener.get_program()

    @property
    def tokens(self) -> List[Token]:
        return list(self.lexer.getAllTokens())  # type: ignore ,this must be a Pylance bug?

    @staticmethod
    def _recursive(aRoot: ParseTree, buf: List[str], offset: int, ruleNames: List[str]):
        for _ in range(offset):
            buf.append("  ")

        buf.append(aRoot.getText() + " | " + type(aRoot).__name__ + "\n")  # type: ignore

        if isinstance(aRoot, ParserRuleContext):
            if aRoot.children is not None:
                for child in aRoot.children:
                    PGrammar._recursive(child, buf, offset + 1, ruleNames)

    def printSyntaxTree(self, root: ParseTree):
        buf = []
        self._recursive(root, buf, 0, list(self.parser.ruleNames))
        print("".join(buf))


class PListener(pcodeListener):
    def __init__(self) -> None:
        super().__init__()

        self.program: PProgram = PProgram()
        self.stack: List[PNode] = []

    @property
    def parent(self) -> PNode | None:
        return self.stack[-1]

    def push_parent(self, new_parent: PNode):
        self.stack.append(new_parent)

    def pop_parent(self) -> PNode:
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
        self.set_start(self.program, ctx)
        self.push_parent(self.program)

    def exitProgram(self, ctx: pcodeParser.ProgramContext):
        self.pop_parent()

    def enterInstruction(self, ctx: pcodeParser.InstructionContext):
        pass

    def exitInstruction(self, ctx: pcodeParser.InstructionContext):
        pass

    def enterBlock(self, ctx: pcodeParser.BlockContext):
        if self.parent is None:
            raise NotImplementedError("No parent for block")

        block = PBlock(self.parent)
        self.set_start(block, ctx)
        self.push_parent(block)

    def exitBlock(self, ctx: pcodeParser.BlockContext):
        self.pop_parent()

    def enterBlock_name(self, ctx: pcodeParser.Block_nameContext):
        assert isinstance(self.parent, PBlock)
        self.parent.name = ctx.getText()

    def exitBlock_name(self, ctx: pcodeParser.Block_nameContext):
        pass

    def enterCommand(self, ctx: pcodeParser.CommandContext):
        assert self.parent is not None

        command = PCommand(self.parent)
        self.set_start(command, ctx)
        self.push_parent(command)

    def exitCommand(self, ctx: pcodeParser.CommandContext):
        self.pop_parent()

    def enterCommand_name(self, ctx: pcodeParser.Command_nameContext):
        assert isinstance(self.parent, PCommand)
        self.parent.name = ctx.getText()

    def exitCommand_name(self, ctx: pcodeParser.Command_nameContext):
        pass

    def enterCommand_args(self, ctx: pcodeParser.Command_argsContext):
        assert isinstance(self.parent, PCommand)
        self.parent.args = ctx.getText()

    def exitCommand_args(self, ctx: pcodeParser.Command_argsContext):
        pass

    def enterTimeexp(self, ctx: pcodeParser.TimeexpContext):
        assert self.parent is not None
        assert hasattr(self.parent, "time")
        self.parent.time = TimeExp(ctx.getText())  # type: ignore

    def exitTimeexp(self, ctx: pcodeParser.TimeexpContext):
        pass

    def enterComment(self, ctx: pcodeParser.CommentContext):
        pass

    def exitComment(self, ctx: pcodeParser.CommentContext):
        pass
