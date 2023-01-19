from io import TextIOWrapper
from typing import List

from .codegen.pcodeLexer import pcodeLexer
from .codegen.pcodeParser import pcodeParser

# from .codegen.pcodeListener import pcodeListener

from antlr4 import InputStream, CommonTokenStream, Token, ParserRuleContext
from antlr4.tree.Tree import ParseTree


class PGrammar:
    def __init__(self) -> None:
        self.lexer = pcodeLexer
        self.parser = pcodeParser

    def parse(self, code: TextIOWrapper):
        input = InputStream(code)
        self.lexer = pcodeLexer(input)
        stream = CommonTokenStream(self.lexer)
        self.parser = pcodeParser(stream)
        # self.tree = self.parser.program()

    @property
    def tokens(self) -> List[Token]:
        return list(self.lexer.getAllTokens())

    @staticmethod
    def _recursive(aRoot: ParseTree, buf: List[str], offset: int, ruleNames: List[str]):
        for _ in range(offset):
            buf.append("  ")

        buf.append(aRoot.getText() + " | " + type(aRoot).__name__ + "\n")

        if isinstance(aRoot, ParserRuleContext):
            if not aRoot.children is None:
                for child in aRoot.children:
                    PGrammar._recursive(child, buf, offset + 1, ruleNames)

    def printSyntaxTree(self, root: ParseTree):
        buf = []
        self._recursive(root, buf, 0, list(self.parser.ruleNames))
        print("".join(buf))
