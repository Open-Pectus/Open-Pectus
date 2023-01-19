# Generated from c:\Projects\Novo\Open-Pectus\src\lang\grammar\pcode.g4 by ANTLR 4.9.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\f")
        buf.write("|\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\3\2\7\2\26\n\2\f\2\16\2\31\13\2\3")
        buf.write("\2\3\2\3\2\7\2\36\n\2\f\2\16\2!\13\2\3\2\7\2$\n\2\f\2")
        buf.write("\16\2\'\13\2\3\2\3\2\3\3\3\3\5\3-\n\3\3\4\7\4\60\n\4\f")
        buf.write("\4\16\4\63\13\4\3\4\7\4\66\n\4\f\4\16\49\13\4\3\4\3\4")
        buf.write("\3\4\5\4>\n\4\3\4\3\4\3\4\7\4C\n\4\f\4\16\4F\13\4\3\4")
        buf.write("\3\4\3\5\3\5\3\6\7\6M\n\6\f\6\16\6P\13\6\3\6\7\6S\n\6")
        buf.write("\f\6\16\6V\13\6\3\6\3\6\3\6\5\6[\n\6\3\6\3\6\3\6\7\6`")
        buf.write("\n\6\f\6\16\6c\13\6\3\6\5\6f\n\6\3\7\3\7\3\b\7\bk\n\b")
        buf.write("\f\b\16\bn\13\b\3\b\3\b\3\t\3\t\3\n\7\nu\n\n\f\n\16\n")
        buf.write("x\13\n\3\n\3\n\3\n\4lv\2\13\2\4\6\b\n\f\16\20\22\2\4\4")
        buf.write("\2\3\3\n\n\3\2\n\n\2\u0081\2\27\3\2\2\2\4,\3\2\2\2\6\61")
        buf.write("\3\2\2\2\bI\3\2\2\2\nN\3\2\2\2\fg\3\2\2\2\16l\3\2\2\2")
        buf.write("\20q\3\2\2\2\22v\3\2\2\2\24\26\7\13\2\2\25\24\3\2\2\2")
        buf.write("\26\31\3\2\2\2\27\25\3\2\2\2\27\30\3\2\2\2\30\32\3\2\2")
        buf.write("\2\31\27\3\2\2\2\32%\5\4\3\2\33\37\7\n\2\2\34\36\7\13")
        buf.write("\2\2\35\34\3\2\2\2\36!\3\2\2\2\37\35\3\2\2\2\37 \3\2\2")
        buf.write("\2 \"\3\2\2\2!\37\3\2\2\2\"$\5\4\3\2#\33\3\2\2\2$\'\3")
        buf.write("\2\2\2%#\3\2\2\2%&\3\2\2\2&(\3\2\2\2\'%\3\2\2\2()\7\2")
        buf.write("\2\3)\3\3\2\2\2*-\5\6\4\2+-\5\n\6\2,*\3\2\2\2,+\3\2\2")
        buf.write("\2-\5\3\2\2\2.\60\7\13\2\2/.\3\2\2\2\60\63\3\2\2\2\61")
        buf.write("/\3\2\2\2\61\62\3\2\2\2\62\67\3\2\2\2\63\61\3\2\2\2\64")
        buf.write("\66\7\b\2\2\65\64\3\2\2\2\669\3\2\2\2\67\65\3\2\2\2\67")
        buf.write("8\3\2\2\28=\3\2\2\29\67\3\2\2\2:;\5\20\t\2;<\7\b\2\2<")
        buf.write(">\3\2\2\2=:\3\2\2\2=>\3\2\2\2>?\3\2\2\2?@\7\5\2\2@D\7")
        buf.write("\4\2\2AC\7\b\2\2BA\3\2\2\2CF\3\2\2\2DB\3\2\2\2DE\3\2\2")
        buf.write("\2EG\3\2\2\2FD\3\2\2\2GH\5\b\5\2H\7\3\2\2\2IJ\7\6\2\2")
        buf.write("J\t\3\2\2\2KM\7\13\2\2LK\3\2\2\2MP\3\2\2\2NL\3\2\2\2N")
        buf.write("O\3\2\2\2OT\3\2\2\2PN\3\2\2\2QS\7\b\2\2RQ\3\2\2\2SV\3")
        buf.write("\2\2\2TR\3\2\2\2TU\3\2\2\2UZ\3\2\2\2VT\3\2\2\2WX\5\20")
        buf.write("\t\2XY\7\b\2\2Y[\3\2\2\2ZW\3\2\2\2Z[\3\2\2\2[\\\3\2\2")
        buf.write("\2\\e\5\f\7\2]a\7\4\2\2^`\7\b\2\2_^\3\2\2\2`c\3\2\2\2")
        buf.write("a_\3\2\2\2ab\3\2\2\2bd\3\2\2\2ca\3\2\2\2df\5\16\b\2e]")
        buf.write("\3\2\2\2ef\3\2\2\2f\13\3\2\2\2gh\7\6\2\2h\r\3\2\2\2ik")
        buf.write("\13\2\2\2ji\3\2\2\2kn\3\2\2\2lm\3\2\2\2lj\3\2\2\2mo\3")
        buf.write("\2\2\2nl\3\2\2\2op\n\2\2\2p\17\3\2\2\2qr\7\7\2\2r\21\3")
        buf.write("\2\2\2su\13\2\2\2ts\3\2\2\2ux\3\2\2\2vw\3\2\2\2vt\3\2")
        buf.write("\2\2wy\3\2\2\2xv\3\2\2\2yz\n\3\2\2z\23\3\2\2\2\21\27\37")
        buf.write("%,\61\67=DNTZaelv")
        return buf.getvalue()


class pcodeParser ( Parser ):

    grammarFileName = "pcode.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'#'", "':'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "' '", "','", "<INVALID>", "'\t'" ]

    symbolicNames = [ "<INVALID>", "HASH", "COLON", "BLOCK", "IDENTIFIER", 
                      "FLOAT", "WHITESPACE", "COMMA", "NEWLINE", "INDENT", 
                      "ANY" ]

    RULE_program = 0
    RULE_program_line = 1
    RULE_block = 2
    RULE_block_name = 3
    RULE_command = 4
    RULE_cmd_name = 5
    RULE_cmd_args = 6
    RULE_timeexp = 7
    RULE_comment = 8

    ruleNames =  [ "program", "program_line", "block", "block_name", "command", 
                   "cmd_name", "cmd_args", "timeexp", "comment" ]

    EOF = Token.EOF
    HASH=1
    COLON=2
    BLOCK=3
    IDENTIFIER=4
    FLOAT=5
    WHITESPACE=6
    COMMA=7
    NEWLINE=8
    INDENT=9
    ANY=10

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def program_line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pcodeParser.Program_lineContext)
            else:
                return self.getTypedRuleContext(pcodeParser.Program_lineContext,i)


        def EOF(self):
            return self.getToken(pcodeParser.EOF, 0)

        def INDENT(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.INDENT)
            else:
                return self.getToken(pcodeParser.INDENT, i)

        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.NEWLINE)
            else:
                return self.getToken(pcodeParser.NEWLINE, i)

        def getRuleIndex(self):
            return pcodeParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = pcodeParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 21
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 18
                    self.match(pcodeParser.INDENT) 
                self.state = 23
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 24
            self.program_line()
            self.state = 35
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.NEWLINE:
                self.state = 25
                self.match(pcodeParser.NEWLINE)
                self.state = 29
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 26
                        self.match(pcodeParser.INDENT) 
                    self.state = 31
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

                self.state = 32
                self.program_line()
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 38
            self.match(pcodeParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Program_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def block(self):
            return self.getTypedRuleContext(pcodeParser.BlockContext,0)


        def command(self):
            return self.getTypedRuleContext(pcodeParser.CommandContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_program_line

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram_line" ):
                listener.enterProgram_line(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram_line" ):
                listener.exitProgram_line(self)




    def program_line(self):

        localctx = pcodeParser.Program_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_program_line)
        try:
            self.state = 42
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 40
                self.block()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 41
                self.command()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BLOCK(self):
            return self.getToken(pcodeParser.BLOCK, 0)

        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def block_name(self):
            return self.getTypedRuleContext(pcodeParser.Block_nameContext,0)


        def INDENT(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.INDENT)
            else:
                return self.getToken(pcodeParser.INDENT, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def timeexp(self):
            return self.getTypedRuleContext(pcodeParser.TimeexpContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlock" ):
                listener.enterBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlock" ):
                listener.exitBlock(self)




    def block(self):

        localctx = pcodeParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.INDENT:
                self.state = 44
                self.match(pcodeParser.INDENT)
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 53
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 50
                self.match(pcodeParser.WHITESPACE)
                self.state = 55
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 59
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 56
                self.timeexp()
                self.state = 57
                self.match(pcodeParser.WHITESPACE)


            self.state = 61
            self.match(pcodeParser.BLOCK)
            self.state = 62
            self.match(pcodeParser.COLON)
            self.state = 66
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 63
                self.match(pcodeParser.WHITESPACE)
                self.state = 68
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 69
            self.block_name()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Block_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(pcodeParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_block_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlock_name" ):
                listener.enterBlock_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlock_name" ):
                listener.exitBlock_name(self)




    def block_name(self):

        localctx = pcodeParser.Block_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_block_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            self.match(pcodeParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def cmd_name(self):
            return self.getTypedRuleContext(pcodeParser.Cmd_nameContext,0)


        def INDENT(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.INDENT)
            else:
                return self.getToken(pcodeParser.INDENT, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def timeexp(self):
            return self.getTypedRuleContext(pcodeParser.TimeexpContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def cmd_args(self):
            return self.getTypedRuleContext(pcodeParser.Cmd_argsContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_command

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand" ):
                listener.enterCommand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand" ):
                listener.exitCommand(self)




    def command(self):

        localctx = pcodeParser.CommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.INDENT:
                self.state = 73
                self.match(pcodeParser.INDENT)
                self.state = 78
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 82
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 79
                self.match(pcodeParser.WHITESPACE)
                self.state = 84
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 85
                self.timeexp()
                self.state = 86
                self.match(pcodeParser.WHITESPACE)


            self.state = 90
            self.cmd_name()
            self.state = 99
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.COLON:
                self.state = 91
                self.match(pcodeParser.COLON)
                self.state = 95
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,11,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 92
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 97
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,11,self._ctx)

                self.state = 98
                self.cmd_args()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cmd_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(pcodeParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_cmd_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCmd_name" ):
                listener.enterCmd_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCmd_name" ):
                listener.exitCmd_name(self)




    def cmd_name(self):

        localctx = pcodeParser.Cmd_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_cmd_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self.match(pcodeParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Cmd_argsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_cmd_args

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCmd_args" ):
                listener.enterCmd_args(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCmd_args" ):
                listener.exitCmd_args(self)




    def cmd_args(self):

        localctx = pcodeParser.Cmd_argsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_cmd_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 106
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 103
                    self.matchWildcard() 
                self.state = 108
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

            self.state = 109
            _la = self._input.LA(1)
            if _la <= 0 or _la==pcodeParser.HASH or _la==pcodeParser.NEWLINE:
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeexpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FLOAT(self):
            return self.getToken(pcodeParser.FLOAT, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_timeexp

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeexp" ):
                listener.enterTimeexp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeexp" ):
                listener.exitTimeexp(self)




    def timeexp(self):

        localctx = pcodeParser.TimeexpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_timeexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 111
            self.match(pcodeParser.FLOAT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_comment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment" ):
                listener.enterComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment" ):
                listener.exitComment(self)




    def comment(self):

        localctx = pcodeParser.CommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_comment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 116
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 113
                    self.matchWildcard() 
                self.state = 118
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

            self.state = 119
            _la = self._input.LA(1)
            if _la <= 0 or _la==pcodeParser.NEWLINE:
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





