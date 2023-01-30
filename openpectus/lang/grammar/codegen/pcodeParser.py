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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\25")
        buf.write("\u00e4\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23\t\23")
        buf.write("\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\3\2\7\2\60\n")
        buf.write("\2\f\2\16\2\63\13\2\3\2\3\2\3\2\7\28\n\2\f\2\16\2;\13")
        buf.write("\2\3\2\7\2>\n\2\f\2\16\2A\13\2\3\2\3\2\3\3\3\3\5\3G\n")
        buf.write("\3\3\3\3\3\5\3K\n\3\3\3\3\3\3\3\3\3\5\3Q\n\3\5\3S\n\3")
        buf.write("\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4]\n\4\3\5\5\5`\n\5")
        buf.write("\3\5\3\5\3\5\7\5e\n\5\f\5\16\5h\13\5\3\5\3\5\3\6\3\6\3")
        buf.write("\7\5\7o\n\7\3\7\3\7\3\b\5\bt\n\b\3\b\3\b\3\t\5\ty\n\t")
        buf.write("\3\t\3\t\3\t\7\t~\n\t\f\t\16\t\u0081\13\t\3\t\5\t\u0084")
        buf.write("\n\t\3\n\3\n\3\13\7\13\u0089\n\13\f\13\16\13\u008c\13")
        buf.write("\13\3\13\3\13\3\f\5\f\u0091\n\f\3\f\3\f\3\f\7\f\u0096")
        buf.write("\n\f\f\f\16\f\u0099\13\f\3\f\5\f\u009c\n\f\3\r\5\r\u009f")
        buf.write("\n\r\3\r\3\r\3\r\7\r\u00a4\n\r\f\r\16\r\u00a7\13\r\3\r")
        buf.write("\5\r\u00aa\n\r\3\16\7\16\u00ad\n\16\f\16\16\16\u00b0\13")
        buf.write("\16\3\16\3\16\3\17\5\17\u00b5\n\17\3\17\3\17\3\20\5\20")
        buf.write("\u00ba\n\20\3\20\3\20\3\21\5\21\u00bf\n\21\3\21\3\21\3")
        buf.write("\22\3\22\6\22\u00c5\n\22\r\22\16\22\u00c6\3\23\3\23\3")
        buf.write("\24\3\24\3\24\3\25\7\25\u00cf\n\25\f\25\16\25\u00d2\13")
        buf.write("\25\3\25\3\25\3\26\7\26\u00d7\n\26\f\26\16\26\u00da\13")
        buf.write("\26\3\27\7\27\u00dd\n\27\f\27\16\27\u00e0\13\27\3\27\3")
        buf.write("\27\3\27\6\u008a\u00ae\u00d0\u00de\2\30\2\4\6\b\n\f\16")
        buf.write("\20\22\24\26\30\32\34\36 \"$&(*,\2\4\4\2\22\22\24\24\3")
        buf.write("\2\24\24\2\u00f4\2\61\3\2\2\2\4R\3\2\2\2\6\\\3\2\2\2\b")
        buf.write("_\3\2\2\2\nk\3\2\2\2\fn\3\2\2\2\16s\3\2\2\2\20x\3\2\2")
        buf.write("\2\22\u0085\3\2\2\2\24\u008a\3\2\2\2\26\u0090\3\2\2\2")
        buf.write("\30\u009e\3\2\2\2\32\u00ae\3\2\2\2\34\u00b4\3\2\2\2\36")
        buf.write("\u00b9\3\2\2\2 \u00be\3\2\2\2\"\u00c2\3\2\2\2$\u00c8\3")
        buf.write("\2\2\2&\u00ca\3\2\2\2(\u00d0\3\2\2\2*\u00d8\3\2\2\2,\u00de")
        buf.write("\3\2\2\2.\60\7\r\2\2/.\3\2\2\2\60\63\3\2\2\2\61/\3\2\2")
        buf.write("\2\61\62\3\2\2\2\62\64\3\2\2\2\63\61\3\2\2\2\64?\5\4\3")
        buf.write("\2\659\7\24\2\2\668\7\r\2\2\67\66\3\2\2\28;\3\2\2\29\67")
        buf.write("\3\2\2\29:\3\2\2\2:<\3\2\2\2;9\3\2\2\2<>\5\4\3\2=\65\3")
        buf.write("\2\2\2>A\3\2\2\2?=\3\2\2\2?@\3\2\2\2@B\3\2\2\2A?\3\2\2")
        buf.write("\2BC\7\2\2\3C\3\3\2\2\2DF\5\6\4\2EG\5&\24\2FE\3\2\2\2")
        buf.write("FG\3\2\2\2GS\3\2\2\2HJ\5\20\t\2IK\5&\24\2JI\3\2\2\2JK")
        buf.write("\3\2\2\2KS\3\2\2\2LS\5&\24\2MS\5*\26\2NP\5,\27\2OQ\5&")
        buf.write("\24\2PO\3\2\2\2PQ\3\2\2\2QS\3\2\2\2RD\3\2\2\2RH\3\2\2")
        buf.write("\2RL\3\2\2\2RM\3\2\2\2RN\3\2\2\2S\5\3\2\2\2T]\5\b\5\2")
        buf.write("U]\5\f\7\2V]\5\16\b\2W]\5\26\f\2X]\5\30\r\2Y]\5\34\17")
        buf.write("\2Z]\5\36\20\2[]\5 \21\2\\T\3\2\2\2\\U\3\2\2\2\\V\3\2")
        buf.write("\2\2\\W\3\2\2\2\\X\3\2\2\2\\Y\3\2\2\2\\Z\3\2\2\2\\[\3")
        buf.write("\2\2\2]\7\3\2\2\2^`\5\"\22\2_^\3\2\2\2_`\3\2\2\2`a\3\2")
        buf.write("\2\2ab\7\7\2\2bf\7\23\2\2ce\7\r\2\2dc\3\2\2\2eh\3\2\2")
        buf.write("\2fd\3\2\2\2fg\3\2\2\2gi\3\2\2\2hf\3\2\2\2ij\5\n\6\2j")
        buf.write("\t\3\2\2\2kl\7\13\2\2l\13\3\2\2\2mo\5\"\22\2nm\3\2\2\2")
        buf.write("no\3\2\2\2op\3\2\2\2pq\7\b\2\2q\r\3\2\2\2rt\5\"\22\2s")
        buf.write("r\3\2\2\2st\3\2\2\2tu\3\2\2\2uv\7\t\2\2v\17\3\2\2\2wy")
        buf.write("\5\"\22\2xw\3\2\2\2xy\3\2\2\2yz\3\2\2\2z\u0083\5\22\n")
        buf.write("\2{\177\7\23\2\2|~\7\r\2\2}|\3\2\2\2~\u0081\3\2\2\2\177")
        buf.write("}\3\2\2\2\177\u0080\3\2\2\2\u0080\u0082\3\2\2\2\u0081")
        buf.write("\177\3\2\2\2\u0082\u0084\5\24\13\2\u0083{\3\2\2\2\u0083")
        buf.write("\u0084\3\2\2\2\u0084\21\3\2\2\2\u0085\u0086\7\13\2\2\u0086")
        buf.write("\23\3\2\2\2\u0087\u0089\13\2\2\2\u0088\u0087\3\2\2\2\u0089")
        buf.write("\u008c\3\2\2\2\u008a\u008b\3\2\2\2\u008a\u0088\3\2\2\2")
        buf.write("\u008b\u008d\3\2\2\2\u008c\u008a\3\2\2\2\u008d\u008e\n")
        buf.write("\2\2\2\u008e\25\3\2\2\2\u008f\u0091\5\"\22\2\u0090\u008f")
        buf.write("\3\2\2\2\u0090\u0091\3\2\2\2\u0091\u0092\3\2\2\2\u0092")
        buf.write("\u009b\7\3\2\2\u0093\u0097\7\23\2\2\u0094\u0096\7\r\2")
        buf.write("\2\u0095\u0094\3\2\2\2\u0096\u0099\3\2\2\2\u0097\u0095")
        buf.write("\3\2\2\2\u0097\u0098\3\2\2\2\u0098\u009a\3\2\2\2\u0099")
        buf.write("\u0097\3\2\2\2\u009a\u009c\5\32\16\2\u009b\u0093\3\2\2")
        buf.write("\2\u009b\u009c\3\2\2\2\u009c\27\3\2\2\2\u009d\u009f\5")
        buf.write("\"\22\2\u009e\u009d\3\2\2\2\u009e\u009f\3\2\2\2\u009f")
        buf.write("\u00a0\3\2\2\2\u00a0\u00a9\7\4\2\2\u00a1\u00a5\7\23\2")
        buf.write("\2\u00a2\u00a4\7\r\2\2\u00a3\u00a2\3\2\2\2\u00a4\u00a7")
        buf.write("\3\2\2\2\u00a5\u00a3\3\2\2\2\u00a5\u00a6\3\2\2\2\u00a6")
        buf.write("\u00a8\3\2\2\2\u00a7\u00a5\3\2\2\2\u00a8\u00aa\5\32\16")
        buf.write("\2\u00a9\u00a1\3\2\2\2\u00a9\u00aa\3\2\2\2\u00aa\31\3")
        buf.write("\2\2\2\u00ab\u00ad\13\2\2\2\u00ac\u00ab\3\2\2\2\u00ad")
        buf.write("\u00b0\3\2\2\2\u00ae\u00af\3\2\2\2\u00ae\u00ac\3\2\2\2")
        buf.write("\u00af\u00b1\3\2\2\2\u00b0\u00ae\3\2\2\2\u00b1\u00b2\n")
        buf.write("\2\2\2\u00b2\33\3\2\2\2\u00b3\u00b5\5\"\22\2\u00b4\u00b3")
        buf.write("\3\2\2\2\u00b4\u00b5\3\2\2\2\u00b5\u00b6\3\2\2\2\u00b6")
        buf.write("\u00b7\7\n\2\2\u00b7\35\3\2\2\2\u00b8\u00ba\5\"\22\2\u00b9")
        buf.write("\u00b8\3\2\2\2\u00b9\u00ba\3\2\2\2\u00ba\u00bb\3\2\2\2")
        buf.write("\u00bb\u00bc\7\5\2\2\u00bc\37\3\2\2\2\u00bd\u00bf\5\"")
        buf.write("\22\2\u00be\u00bd\3\2\2\2\u00be\u00bf\3\2\2\2\u00bf\u00c0")
        buf.write("\3\2\2\2\u00c0\u00c1\7\6\2\2\u00c1!\3\2\2\2\u00c2\u00c4")
        buf.write("\5$\23\2\u00c3\u00c5\7\r\2\2\u00c4\u00c3\3\2\2\2\u00c5")
        buf.write("\u00c6\3\2\2\2\u00c6\u00c4\3\2\2\2\u00c6\u00c7\3\2\2\2")
        buf.write("\u00c7#\3\2\2\2\u00c8\u00c9\7\f\2\2\u00c9%\3\2\2\2\u00ca")
        buf.write("\u00cb\7\22\2\2\u00cb\u00cc\5(\25\2\u00cc\'\3\2\2\2\u00cd")
        buf.write("\u00cf\13\2\2\2\u00ce\u00cd\3\2\2\2\u00cf\u00d2\3\2\2")
        buf.write("\2\u00d0\u00d1\3\2\2\2\u00d0\u00ce\3\2\2\2\u00d1\u00d3")
        buf.write("\3\2\2\2\u00d2\u00d0\3\2\2\2\u00d3\u00d4\n\3\2\2\u00d4")
        buf.write(")\3\2\2\2\u00d5\u00d7\7\r\2\2\u00d6\u00d5\3\2\2\2\u00d7")
        buf.write("\u00da\3\2\2\2\u00d8\u00d6\3\2\2\2\u00d8\u00d9\3\2\2\2")
        buf.write("\u00d9+\3\2\2\2\u00da\u00d8\3\2\2\2\u00db\u00dd\13\2\2")
        buf.write("\2\u00dc\u00db\3\2\2\2\u00dd\u00e0\3\2\2\2\u00de\u00df")
        buf.write("\3\2\2\2\u00de\u00dc\3\2\2\2\u00df\u00e1\3\2\2\2\u00e0")
        buf.write("\u00de\3\2\2\2\u00e1\u00e2\n\2\2\2\u00e2-\3\2\2\2 \61")
        buf.write("9?FJPR\\_fnsx\177\u0083\u008a\u0090\u0097\u009b\u009e")
        buf.write("\u00a5\u00a9\u00ae\u00b4\u00b9\u00be\u00c6\u00d0\u00d8")
        buf.write("\u00de")
        return buf.getvalue()


class pcodeParser ( Parser ):

    grammarFileName = "pcode.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'.'", "','", "' '", "'\t'", "'#'", "':'" ]

    symbolicNames = [ "<INVALID>", "WATCH", "ALARM", "STOP", "PAUSE", "BLOCK", 
                      "END_BLOCK", "END_BLOCKS", "INCREMENT_RC", "IDENTIFIER", 
                      "FLOAT", "WHITESPACE", "PERIOD", "COMMA", "SPACE", 
                      "TAB", "HASH", "COLON", "NEWLINE", "ANY" ]

    RULE_program = 0
    RULE_instruction = 1
    RULE_builtin_command = 2
    RULE_block = 3
    RULE_block_name = 4
    RULE_end_block = 5
    RULE_end_blocks = 6
    RULE_command = 7
    RULE_command_name = 8
    RULE_command_args = 9
    RULE_watch = 10
    RULE_alarm = 11
    RULE_condition = 12
    RULE_increment_rc = 13
    RULE_stop = 14
    RULE_pause = 15
    RULE_time = 16
    RULE_timeexp = 17
    RULE_comment = 18
    RULE_comment_text = 19
    RULE_blank = 20
    RULE_error = 21

    ruleNames =  [ "program", "instruction", "builtin_command", "block", 
                   "block_name", "end_block", "end_blocks", "command", "command_name", 
                   "command_args", "watch", "alarm", "condition", "increment_rc", 
                   "stop", "pause", "time", "timeexp", "comment", "comment_text", 
                   "blank", "error" ]

    EOF = Token.EOF
    WATCH=1
    ALARM=2
    STOP=3
    PAUSE=4
    BLOCK=5
    END_BLOCK=6
    END_BLOCKS=7
    INCREMENT_RC=8
    IDENTIFIER=9
    FLOAT=10
    WHITESPACE=11
    PERIOD=12
    COMMA=13
    SPACE=14
    TAB=15
    HASH=16
    COLON=17
    NEWLINE=18
    ANY=19

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
            self.state = 47
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,0,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 44
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 49
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,0,self._ctx)

            self.state = 50
            self.instruction()
            self.state = 61
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.NEWLINE:
                self.state = 51
                self.match(pcodeParser.NEWLINE)
                self.state = 55
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 52
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 57
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

                self.state = 58
                self.instruction()
                self.state = 63
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 64
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

        def builtin_command(self):
            return self.getTypedRuleContext(pcodeParser.Builtin_commandContext,0)


        def comment(self):
            return self.getTypedRuleContext(pcodeParser.CommentContext,0)


        def command(self):
            return self.getTypedRuleContext(pcodeParser.CommandContext,0)


        def blank(self):
            return self.getTypedRuleContext(pcodeParser.BlankContext,0)


        def error(self):
            return self.getTypedRuleContext(pcodeParser.ErrorContext,0)


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
            self.state = 80
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 66
                self.builtin_command()
                self.state = 68
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 67
                    self.comment()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 70
                self.command()
                self.state = 72
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 71
                    self.comment()


                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 74
                self.comment()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 75
                self.blank()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 76
                self.error()
                self.state = 78
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==pcodeParser.HASH:
                    self.state = 77
                    self.comment()


                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Builtin_commandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def block(self):
            return self.getTypedRuleContext(pcodeParser.BlockContext,0)


        def end_block(self):
            return self.getTypedRuleContext(pcodeParser.End_blockContext,0)


        def end_blocks(self):
            return self.getTypedRuleContext(pcodeParser.End_blocksContext,0)


        def watch(self):
            return self.getTypedRuleContext(pcodeParser.WatchContext,0)


        def alarm(self):
            return self.getTypedRuleContext(pcodeParser.AlarmContext,0)


        def increment_rc(self):
            return self.getTypedRuleContext(pcodeParser.Increment_rcContext,0)


        def stop(self):
            return self.getTypedRuleContext(pcodeParser.StopContext,0)


        def pause(self):
            return self.getTypedRuleContext(pcodeParser.PauseContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_builtin_command

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBuiltin_command" ):
                listener.enterBuiltin_command(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBuiltin_command" ):
                listener.exitBuiltin_command(self)




    def builtin_command(self):

        localctx = pcodeParser.Builtin_commandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_builtin_command)
        try:
            self.state = 90
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 82
                self.block()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 83
                self.end_block()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 84
                self.end_blocks()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 85
                self.watch()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 86
                self.alarm()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 87
                self.increment_rc()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 88
                self.stop()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 89
                self.pause()
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


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
        self.enterRule(localctx, 6, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 92
                self.time()


            self.state = 95
            self.match(pcodeParser.BLOCK)
            self.state = 96
            self.match(pcodeParser.COLON)
            self.state = 100
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 97
                self.match(pcodeParser.WHITESPACE)
                self.state = 102
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 103
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
        self.enterRule(localctx, 8, self.RULE_block_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.match(pcodeParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class End_blockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def END_BLOCK(self):
            return self.getToken(pcodeParser.END_BLOCK, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_end_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEnd_block" ):
                listener.enterEnd_block(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEnd_block" ):
                listener.exitEnd_block(self)




    def end_block(self):

        localctx = pcodeParser.End_blockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_end_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 108
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 107
                self.time()


            self.state = 110
            self.match(pcodeParser.END_BLOCK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class End_blocksContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def END_BLOCKS(self):
            return self.getToken(pcodeParser.END_BLOCKS, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_end_blocks

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEnd_blocks" ):
                listener.enterEnd_blocks(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEnd_blocks" ):
                listener.exitEnd_blocks(self)




    def end_blocks(self):

        localctx = pcodeParser.End_blocksContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_end_blocks)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 112
                self.time()


            self.state = 115
            self.match(pcodeParser.END_BLOCKS)
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


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def command_args(self):
            return self.getTypedRuleContext(pcodeParser.Command_argsContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
        self.enterRule(localctx, 14, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 118
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 117
                self.time()


            self.state = 120
            self.command_name()
            self.state = 129
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.COLON:
                self.state = 121
                self.match(pcodeParser.COLON)
                self.state = 125
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 122
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 127
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                self.state = 128
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
        self.enterRule(localctx, 16, self.RULE_command_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 131
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
        self.enterRule(localctx, 18, self.RULE_command_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 136
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 133
                    self.matchWildcard() 
                self.state = 138
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

            self.state = 139
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

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def condition(self):
            return self.getTypedRuleContext(pcodeParser.ConditionContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
        self.enterRule(localctx, 20, self.RULE_watch)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 142
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 141
                self.time()


            self.state = 144
            self.match(pcodeParser.WATCH)
            self.state = 153
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.COLON:
                self.state = 145
                self.match(pcodeParser.COLON)
                self.state = 149
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,17,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 146
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 151
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,17,self._ctx)

                self.state = 152
                self.condition()


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

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def condition(self):
            return self.getTypedRuleContext(pcodeParser.ConditionContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
        self.enterRule(localctx, 22, self.RULE_alarm)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 156
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 155
                self.time()


            self.state = 158
            self.match(pcodeParser.ALARM)
            self.state = 167
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.COLON:
                self.state = 159
                self.match(pcodeParser.COLON)
                self.state = 163
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,20,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 160
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 165
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

                self.state = 166
                self.condition()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_condition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition" ):
                listener.enterCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition" ):
                listener.exitCondition(self)




    def condition(self):

        localctx = pcodeParser.ConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_condition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 172
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 169
                    self.matchWildcard() 
                self.state = 174
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

            self.state = 175
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


    class Increment_rcContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INCREMENT_RC(self):
            return self.getToken(pcodeParser.INCREMENT_RC, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_increment_rc

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIncrement_rc" ):
                listener.enterIncrement_rc(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIncrement_rc" ):
                listener.exitIncrement_rc(self)




    def increment_rc(self):

        localctx = pcodeParser.Increment_rcContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_increment_rc)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 178
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 177
                self.time()


            self.state = 180
            self.match(pcodeParser.INCREMENT_RC)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StopContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STOP(self):
            return self.getToken(pcodeParser.STOP, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_stop

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStop" ):
                listener.enterStop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStop" ):
                listener.exitStop(self)




    def stop(self):

        localctx = pcodeParser.StopContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_stop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 183
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 182
                self.time()


            self.state = 185
            self.match(pcodeParser.STOP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PauseContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PAUSE(self):
            return self.getToken(pcodeParser.PAUSE, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_pause

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPause" ):
                listener.enterPause(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPause" ):
                listener.exitPause(self)




    def pause(self):

        localctx = pcodeParser.PauseContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_pause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 188
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==pcodeParser.FLOAT:
                self.state = 187
                self.time()


            self.state = 190
            self.match(pcodeParser.PAUSE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timeexp(self):
            return self.getTypedRuleContext(pcodeParser.TimeexpContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def getRuleIndex(self):
            return pcodeParser.RULE_time

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTime" ):
                listener.enterTime(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTime" ):
                listener.exitTime(self)




    def time(self):

        localctx = pcodeParser.TimeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_time)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 192
            self.timeexp()
            self.state = 194 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 193
                self.match(pcodeParser.WHITESPACE)
                self.state = 196 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==pcodeParser.WHITESPACE):
                    break

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
        self.enterRule(localctx, 34, self.RULE_timeexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 198
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
        self.enterRule(localctx, 36, self.RULE_comment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 200
            self.match(pcodeParser.HASH)
            self.state = 201
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
        self.enterRule(localctx, 38, self.RULE_comment_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 206
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,27,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 203
                    self.matchWildcard() 
                self.state = 208
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,27,self._ctx)

            self.state = 209
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


    class BlankContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def getRuleIndex(self):
            return pcodeParser.RULE_blank

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlank" ):
                listener.enterBlank(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlank" ):
                listener.exitBlank(self)




    def blank(self):

        localctx = pcodeParser.BlankContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_blank)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 214
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pcodeParser.WHITESPACE:
                self.state = 211
                self.match(pcodeParser.WHITESPACE)
                self.state = 216
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ErrorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_error

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterError" ):
                listener.enterError(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitError" ):
                listener.exitError(self)




    def error(self):

        localctx = pcodeParser.ErrorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_error)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,29,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 217
                    self.matchWildcard() 
                self.state = 222
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,29,self._ctx)

            self.state = 223
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





