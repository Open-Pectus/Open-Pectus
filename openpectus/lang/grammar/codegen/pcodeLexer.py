# Generated from c:\Projects\Novo\Open-Pectus\src\lang\grammar\pcode.g4 by ANTLR 4.9.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\f")
        buf.write("_\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\3\2\3\2")
        buf.write("\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3\b\3\t\3")
        buf.write("\t\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\f\3\f\3\f\7")
        buf.write("\fA\n\f\f\f\16\fD\13\f\3\r\6\rG\n\r\r\r\16\rH\3\r\3\r")
        buf.write("\6\rM\n\r\r\r\16\rN\5\rQ\n\r\3\16\3\16\3\17\3\17\3\20")
        buf.write("\3\20\3\20\5\20Z\n\20\3\21\3\21\3\22\3\22\2\2\23\3\2\5")
        buf.write("\2\7\2\t\2\13\2\r\2\17\2\21\3\23\4\25\5\27\6\31\7\33\b")
        buf.write("\35\t\37\n!\13#\f\3\2\n\4\2C\\c|\3\2\62;\4\2DDdd\4\2N")
        buf.write("Nnn\4\2QQqq\4\2EEee\4\2MMmm\4\2\f\f\17\17\2]\2\21\3\2")
        buf.write("\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2")
        buf.write("\2\2\33\3\2\2\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2")
        buf.write("#\3\2\2\2\3%\3\2\2\2\5\'\3\2\2\2\7)\3\2\2\2\t+\3\2\2\2")
        buf.write("\13-\3\2\2\2\r/\3\2\2\2\17\61\3\2\2\2\21\63\3\2\2\2\23")
        buf.write("\65\3\2\2\2\25\67\3\2\2\2\27=\3\2\2\2\31F\3\2\2\2\33R")
        buf.write("\3\2\2\2\35T\3\2\2\2\37Y\3\2\2\2![\3\2\2\2#]\3\2\2\2%")
        buf.write("&\t\2\2\2&\4\3\2\2\2\'(\t\3\2\2(\6\3\2\2\2)*\t\4\2\2*")
        buf.write("\b\3\2\2\2+,\t\5\2\2,\n\3\2\2\2-.\t\6\2\2.\f\3\2\2\2/")
        buf.write("\60\t\7\2\2\60\16\3\2\2\2\61\62\t\b\2\2\62\20\3\2\2\2")
        buf.write("\63\64\7%\2\2\64\22\3\2\2\2\65\66\7<\2\2\66\24\3\2\2\2")
        buf.write("\678\5\7\4\289\5\t\5\29:\5\13\6\2:;\5\r\7\2;<\5\17\b\2")
        buf.write("<\26\3\2\2\2=B\5\3\2\2>A\5\3\2\2?A\5\5\3\2@>\3\2\2\2@")
        buf.write("?\3\2\2\2AD\3\2\2\2B@\3\2\2\2BC\3\2\2\2C\30\3\2\2\2DB")
        buf.write("\3\2\2\2EG\5\5\3\2FE\3\2\2\2GH\3\2\2\2HF\3\2\2\2HI\3\2")
        buf.write("\2\2IP\3\2\2\2JL\7\60\2\2KM\5\5\3\2LK\3\2\2\2MN\3\2\2")
        buf.write("\2NL\3\2\2\2NO\3\2\2\2OQ\3\2\2\2PJ\3\2\2\2PQ\3\2\2\2Q")
        buf.write("\32\3\2\2\2RS\7\"\2\2S\34\3\2\2\2TU\7.\2\2U\36\3\2\2\2")
        buf.write("VZ\t\t\2\2WX\7\17\2\2XZ\7\f\2\2YV\3\2\2\2YW\3\2\2\2Z ")
        buf.write("\3\2\2\2[\\\7\13\2\2\\\"\3\2\2\2]^\13\2\2\2^$\3\2\2\2")
        buf.write("\t\2@BHNPY\2")
        return buf.getvalue()


class pcodeLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    HASH = 1
    COLON = 2
    BLOCK = 3
    IDENTIFIER = 4
    FLOAT = 5
    WHITESPACE = 6
    COMMA = 7
    NEWLINE = 8
    INDENT = 9
    ANY = 10

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'#'", "':'", "' '", "','", "'\t'" ]

    symbolicNames = [ "<INVALID>",
            "HASH", "COLON", "BLOCK", "IDENTIFIER", "FLOAT", "WHITESPACE", 
            "COMMA", "NEWLINE", "INDENT", "ANY" ]

    ruleNames = [ "LETTER", "DIGIT", "B", "L", "O", "C", "K", "HASH", "COLON", 
                  "BLOCK", "IDENTIFIER", "FLOAT", "WHITESPACE", "COMMA", 
                  "NEWLINE", "INDENT", "ANY" ]

    grammarFileName = "pcode.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


