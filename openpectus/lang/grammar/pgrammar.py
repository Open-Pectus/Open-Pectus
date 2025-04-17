from typing import List

from antlr4 import InputStream, CommonTokenStream, Token, ParserRuleContext
from antlr4.tree.Tree import ParseTree, ParseTreeWalker

# from openpectus.lang.exec.analyzer import EnrichAnalyzer
from openpectus.lang.grammar.codegen.pcodeLexer import pcodeLexer
from openpectus.lang.grammar.codegen.pcodeParser import pcodeParser
from openpectus.lang.model.pprogram import PProgram
from openpectus.lang.grammar.pprogrambuilder import PProgramBuilder


class PGrammar:
    def __init__(self) -> None:
        self.lexer = pcodeLexer
        self.parser = pcodeParser

    def parse(self, code: str):  # code: TextIOWrapper):
        input = InputStream(code)
        self.lexer = pcodeLexer(input)
        stream = CommonTokenStream(self.lexer)
        self.parser = pcodeParser(stream)

    def build_model(self, skip_enrich_analyzers=False) -> PProgram:
        self.tree: pcodeParser.ProgramContext = self.parser.program()  # type: ignore
        listener = PProgramBuilder()
        walker = ParseTreeWalker()
        walker.walk(listener, self.tree)
        program = listener.get_program()
        # if not skip_enrich_analyzers:
        #     EnrichAnalyzer().analyze(program)
        program.collect_errors()
        return program

    @property
    def tokens(self) -> List[Token]:
        return list(self.lexer.getAllTokens())  # type: ignore

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
        buf: List[str] = []
        self._recursive(root, buf, 0, list(self.parser.ruleNames))
        if initial_newline:
            print()
        print("".join(buf))
