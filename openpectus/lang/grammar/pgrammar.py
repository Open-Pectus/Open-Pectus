from typing import List

from antlr4 import InputStream, CommonTokenStream, Token, ParserRuleContext
from antlr4.tree.Tree import ParseTree, ParseTreeWalker

from lang.grammar.codegen.pcodeLexer import pcodeLexer
from lang.grammar.codegen.pcodeParser import pcodeParser
from lang.model.pprogram import PProgram
from lang.grammar.pprogrambuilder import PProgramBuilder


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
        listener = PProgramBuilder()
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

    def printSyntaxTree(self, root: ParseTree, initial_newline: bool = True):
        buf = []
        self._recursive(root, buf, 0, list(self.parser.ruleNames))
        if initial_newline:
            print()
        print("".join(buf))
