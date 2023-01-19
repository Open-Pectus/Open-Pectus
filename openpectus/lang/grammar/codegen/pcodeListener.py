# Generated from c:\Projects\Novo\Open-Pectus\src\lang\grammar\pcode.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .pcodeParser import pcodeParser
else:
    from pcodeParser import pcodeParser

# This class defines a complete listener for a parse tree produced by pcodeParser.
class pcodeListener(ParseTreeListener):

    # Enter a parse tree produced by pcodeParser#program.
    def enterProgram(self, ctx:pcodeParser.ProgramContext):
        pass

    # Exit a parse tree produced by pcodeParser#program.
    def exitProgram(self, ctx:pcodeParser.ProgramContext):
        pass


    # Enter a parse tree produced by pcodeParser#program_line.
    def enterProgram_line(self, ctx:pcodeParser.Program_lineContext):
        pass

    # Exit a parse tree produced by pcodeParser#program_line.
    def exitProgram_line(self, ctx:pcodeParser.Program_lineContext):
        pass


    # Enter a parse tree produced by pcodeParser#block.
    def enterBlock(self, ctx:pcodeParser.BlockContext):
        pass

    # Exit a parse tree produced by pcodeParser#block.
    def exitBlock(self, ctx:pcodeParser.BlockContext):
        pass


    # Enter a parse tree produced by pcodeParser#block_name.
    def enterBlock_name(self, ctx:pcodeParser.Block_nameContext):
        pass

    # Exit a parse tree produced by pcodeParser#block_name.
    def exitBlock_name(self, ctx:pcodeParser.Block_nameContext):
        pass


    # Enter a parse tree produced by pcodeParser#command.
    def enterCommand(self, ctx:pcodeParser.CommandContext):
        pass

    # Exit a parse tree produced by pcodeParser#command.
    def exitCommand(self, ctx:pcodeParser.CommandContext):
        pass


    # Enter a parse tree produced by pcodeParser#cmd_name.
    def enterCmd_name(self, ctx:pcodeParser.Cmd_nameContext):
        pass

    # Exit a parse tree produced by pcodeParser#cmd_name.
    def exitCmd_name(self, ctx:pcodeParser.Cmd_nameContext):
        pass


    # Enter a parse tree produced by pcodeParser#cmd_args.
    def enterCmd_args(self, ctx:pcodeParser.Cmd_argsContext):
        pass

    # Exit a parse tree produced by pcodeParser#cmd_args.
    def exitCmd_args(self, ctx:pcodeParser.Cmd_argsContext):
        pass


    # Enter a parse tree produced by pcodeParser#timeexp.
    def enterTimeexp(self, ctx:pcodeParser.TimeexpContext):
        pass

    # Exit a parse tree produced by pcodeParser#timeexp.
    def exitTimeexp(self, ctx:pcodeParser.TimeexpContext):
        pass


    # Enter a parse tree produced by pcodeParser#comment.
    def enterComment(self, ctx:pcodeParser.CommentContext):
        pass

    # Exit a parse tree produced by pcodeParser#comment.
    def exitComment(self, ctx:pcodeParser.CommentContext):
        pass



del pcodeParser