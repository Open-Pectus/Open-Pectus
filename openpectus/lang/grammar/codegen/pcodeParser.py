# Generated from c:\Projects\Novo\Open-Pectus\openpectus\lang\grammar\pcode.g4 by ANTLR 4.9.2
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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\20")
        buf.write("\u008c\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\3\2")
        buf.write("\7\2\34\n\2\f\2\16\2\37\13\2\3\2\3\2\3\2\7\2$\n\2\f\2")
        buf.write("\16\2\'\13\2\3\2\7\2*\n\2\f\2\16\2-\13\2\3\2\3\2\3\3\3")
        buf.write("\3\5\3\63\n\3\3\3\3\3\5\3\67\n\3\3\3\3\3\5\3;\n\3\3\3")
        buf.write("\3\3\5\3?\n\3\3\3\5\3B\n\3\3\4\7\4E\n\4\f\4\16\4H\13\4")
        buf.write("\3\4\3\4\3\4\5\4M\n\4\3\4\3\4\3\4\7\4R\n\4\f\4\16\4U\13")
        buf.write("\4\3\4\3\4\3\5\3\5\3\6\7\6\\\n\6\f\6\16\6_\13\6\3\6\3")
        buf.write("\6\3\6\5\6d\n\6\3\6\3\6\3\6\7\6i\n\6\f\6\16\6l\13\6\3")
        buf.write("\6\5\6o\n\6\3\7\3\7\3\b\7\bt\n\b\f\b\16\bw\13\b\3\b\3")
        buf.write("\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\f\3\r\7\r\u0085")
        buf.write("\n\r\f\r\16\r\u0088\13\r\3\r\3\r\3\r\4u\u0086\2\16\2\4")
        buf.write("\6\b\n\f\16\20\22\24\26\30\2\4\4\2\r\r\17\17\3\2\17\17")
        buf.write("\2\u0093\2\35\3\2\2\2\4A\3\2\2\2\6F\3\2\2\2\bX\3\2\2\2")
        buf.write("\n]\3\2\2\2\fp\3\2\2\2\16u\3\2\2\2\20z\3\2\2\2\22|\3\2")
        buf.write("\2\2\24~\3\2\2\2\26\u0080\3\2\2\2\30\u0086\3\2\2\2\32")
        buf.write("\34\7\b\2\2\33\32\3\2\2\2\34\37\3\2\2\2\35\33\3\2\2\2")
        buf.write("\35\36\3\2\2\2\36 \3\2\2\2\37\35\3\2\2\2 +\5\4\3\2!%\7")
        buf.write("\17\2\2\"$\7\b\2\2#\"\3\2\2\2$\'\3\2\2\2%#\3\2\2\2%&\3")
        buf.write("\2\2\2&(\3\2\2\2\'%\3\2\2\2(*\5\4\3\2)!\3\2\2\2*-\3\2")
        buf.write("\2\2+)\3\2\2\2+,\3\2\2\2,.\3\2\2\2-+\3\2\2\2./\7\2\2\3")
        buf.write("/\3\3\2\2\2\60\62\5\6\4\2\61\63\5\26\f\2\62\61\3\2\2\2")
        buf.write("\62\63\3\2\2\2\63B\3\2\2\2\64\66\5\n\6\2\65\67\5\26\f")
        buf.write("\2\66\65\3\2\2\2\66\67\3\2\2\2\67B\3\2\2\28:\5\20\t\2")
        buf.write("9;\5\26\f\2:9\3\2\2\2:;\3\2\2\2;B\3\2\2\2<>\5\22\n\2=")
        buf.write("?\5\26\f\2>=\3\2\2\2>?\3\2\2\2?B\3\2\2\2@B\5\26\f\2A\60")
        buf.write("\3\2\2\2A\64\3\2\2\2A8\3\2\2\2A<\3\2\2\2A@\3\2\2\2B\5")
        buf.write("\3\2\2\2CE\7\b\2\2DC\3\2\2\2EH\3\2\2\2FD\3\2\2\2FG\3\2")
        buf.write("\2\2GL\3\2\2\2HF\3\2\2\2IJ\5\24\13\2JK\7\b\2\2KM\3\2\2")
        buf.write("\2LI\3\2\2\2LM\3\2\2\2MN\3\2\2\2NO\7\3\2\2OS\7\16\2\2")
        buf.write("PR\7\b\2\2QP\3\2\2\2RU\3\2\2\2SQ\3\2\2\2ST\3\2\2\2TV\3")
        buf.write("\2\2\2US\3\2\2\2VW\5\b\5\2W\7\3\2\2\2XY\7\6\2\2Y\t\3\2")
        buf.write("\2\2Z\\\7\b\2\2[Z\3\2\2\2\\_\3\2\2\2][\3\2\2\2]^\3\2\2")
        buf.write("\2^c\3\2\2\2_]\3\2\2\2`a\5\24\13\2ab\7\b\2\2bd\3\2\2\2")
        buf.write("c`\3\2\2\2cd\3\2\2\2de\3\2\2\2en\5\f\7\2fj\7\16\2\2gi")
        buf.write("\7\b\2\2hg\3\2\2\2il\3\2\2\2jh\3\2\2\2jk\3\2\2\2km\3\2")
        buf.write("\2\2lj\3\2\2\2mo\5\16\b\2nf\3\2\2\2no\3\2\2\2o\13\3\2")
        buf.write("\2\2pq\7\6\2\2q\r\3\2\2\2rt\13\2\2\2sr\3\2\2\2tw\3\2\2")
        buf.write("\2uv\3\2\2\2us\3\2\2\2vx\3\2\2\2wu\3\2\2\2xy\n\2\2\2y")
        buf.write("\17\3\2\2\2z{\7\4\2\2{\21\3\2\2\2|}\7\5\2\2}\23\3\2\2")
        buf.write("\2~\177\7\7\2\2\177\25\3\2\2\2\u0080\u0081\7\r\2\2\u0081")
        buf.write("\u0082\5\30\r\2\u0082\27\3\2\2\2\u0083\u0085\13\2\2\2")
        buf.write("\u0084\u0083\3\2\2\2\u0085\u0088\3\2\2\2\u0086\u0087\3")
        buf.write("\2\2\2\u0086\u0084\3\2\2\2\u0087\u0089\3\2\2\2\u0088\u0086")
        buf.write("\3\2\2\2\u0089\u008a\n\3\2\2\u008a\31\3\2\2\2\23\35%+")
        buf.write("\62\66:>AFLS]cjnu\u0086")
        return buf.getvalue()


class pcodeParser ( Parser ):

    grammarFileName = "pcode.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'.'", "','", 
                     "' '", "'\t'", "'#'", "':'" ]

    symbolicNames = [ "<INVALID>", "BLOCK", "WATCH", "ALARM", "IDENTIFIER", 
                      "FLOAT", "WHITESPACE", "PERIOD", "COMMA", "SPACE", 
                      "TAB", "HASH", "COLON", "NEWLINE", "ANY" ]

    RULE_program = 0
    RULE_instruction = 1
    RULE_block = 2
    RULE_block_name = 3
    RULE_command = 4
    RULE_command_name = 5
    RULE_command_args = 6
    RULE_watch = 7
    RULE_alarm = 8
    RULE_timeexp = 9
    RULE_comment = 10
    RULE_comment_text = 11

    ruleNames =  [ "program", "instruction", "block", "block_name", "command", 
                   "command_name", "command_args", "watch", "alarm", "timeexp", 
                   "comment", "comment_text" ]

    EOF = Token.EOF
    BLOCK=1
    WATCH=2
    ALARM=3
    IDENTIFIER=4
    FLOAT=5
    WHITESPACE=6
    PERIOD=7
    COMMA=8
    SPACE=9
    TAB=10
    HASH=11
    COLON=12
    NEWLINE=13
    ANY=14

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

        def instruction(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pcodeParser.InstructionContext)
            else:
                return self.getTypedRuleContext(pcodeParser.InstructionContext,i)


        def EOF(self):
            return self.getToken(pcodeParser.EOF, 0)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
            self.state = 27
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 24
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 29
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 30
            self.instruction()
            self.state = 41
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.NEWLINE:
                self.state = 31
                self.match(pcodeParser.NEWLINE)
                self.state = 35
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 32
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 37
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

                self.state = 38
                self.instruction()
                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 44
            self.match(pcodeParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class InstructionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def block(self):
            return self.getTypedRuleContext(pcodeParser.BlockContext,0)


        def comment(self):
            return self.getTypedRuleContext(pcodeParser.CommentContext,0)


        def command(self):
            return self.getTypedRuleContext(pcodeParser.CommandContext,0)


        def watch(self):
            return self.getTypedRuleContext(pcodeParser.WatchContext,0)


        def alarm(self):
            return self.getTypedRuleContext(pcodeParser.AlarmContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_instruction

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInstruction" ):
                listener.enterInstruction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInstruction" ):
                listener.exitInstruction(self)




    def instruction(self):

        localctx = pcodeParser.InstructionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_instruction)
        self._la = 0 # Token type
        try:
            self.state = 63
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 46
                self.block()
                self.state = 48
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 47
                    self.comment()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 50
                self.command()
                self.state = 52
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 51
                    self.comment()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 54
                self.watch()
                self.state = 56
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 55
                    self.comment()


                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 58
                self.alarm()
                self.state = 60
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 59
                    self.comment()


                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 62
                self.comment()
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
            self.state = 68
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 65
                self.match(pcodeParser.WHITESPACE)
                self.state = 70
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 71
                self.timeexp()
                self.state = 72
                self.match(pcodeParser.WHITESPACE)


            self.state = 76
            self.match(pcodeParser.BLOCK)
            self.state = 77
            self.match(pcodeParser.COLON)
            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 78
                self.match(pcodeParser.WHITESPACE)
                self.state = 83
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 84
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
            self.state = 86
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

        def command_name(self):
            return self.getTypedRuleContext(pcodeParser.Command_nameContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def timeexp(self):
            return self.getTypedRuleContext(pcodeParser.TimeexpContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def command_args(self):
            return self.getTypedRuleContext(pcodeParser.Command_argsContext,0)


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
            self.state = 91
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 88
                self.match(pcodeParser.WHITESPACE)
                self.state = 93
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 97
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 94
                self.timeexp()
                self.state = 95
                self.match(pcodeParser.WHITESPACE)


            self.state = 99
            self.command_name()
            self.state = 108
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.COLON:
                self.state = 100
                self.match(pcodeParser.COLON)
                self.state = 104
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 101
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 106
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                self.state = 107
                self.command_args()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Command_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(pcodeParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_command_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand_name" ):
                listener.enterCommand_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand_name" ):
                listener.exitCommand_name(self)




    def command_name(self):

        localctx = pcodeParser.Command_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_command_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 110
            self.match(pcodeParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Command_argsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_command_args

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand_args" ):
                listener.enterCommand_args(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand_args" ):
                listener.exitCommand_args(self)




    def command_args(self):

        localctx = pcodeParser.Command_argsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_command_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 115
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 112
                    self.matchWildcard() 
                self.state = 117
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

            self.state = 118
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


    class WatchContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WATCH(self):
            return self.getToken(pcodeParser.WATCH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_watch

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWatch" ):
                listener.enterWatch(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWatch" ):
                listener.exitWatch(self)




    def watch(self):

        localctx = pcodeParser.WatchContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_watch)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 120
            self.match(pcodeParser.WATCH)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlarmContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ALARM(self):
            return self.getToken(pcodeParser.ALARM, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_alarm

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAlarm" ):
                listener.enterAlarm(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAlarm" ):
                listener.exitAlarm(self)




    def alarm(self):

        localctx = pcodeParser.AlarmContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_alarm)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 122
            self.match(pcodeParser.ALARM)
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
        self.enterRule(localctx, 18, self.RULE_timeexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 124
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

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def comment_text(self):
            return self.getTypedRuleContext(pcodeParser.Comment_textContext,0)


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
        self.enterRule(localctx, 20, self.RULE_comment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 126
            self.match(pcodeParser.HASH)
            self.state = 127
            self.comment_text()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Comment_textContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_comment_text

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment_text" ):
                listener.enterComment_text(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment_text" ):
                listener.exitComment_text(self)




    def comment_text(self):

        localctx = pcodeParser.Comment_textContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_comment_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 132
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 129
                    self.matchWildcard() 
                self.state = 134
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

            self.state = 135
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





