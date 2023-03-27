# Generated from c:\Projects\Novo\Open-Pectus\openpectus\lang\grammar\pcode.g4 by ANTLR 4.9.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\31")
        buf.write("\u0142\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23")
        buf.write("\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30")
        buf.write("\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36")
        buf.write("\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%")
        buf.write("\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.")
        buf.write("\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63\4\64")
        buf.write("\t\64\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7")
        buf.write("\3\b\3\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16")
        buf.write("\3\16\3\17\3\17\3\20\3\20\3\21\3\21\3\22\3\22\3\23\3\23")
        buf.write("\3\24\3\24\3\25\3\25\3\26\3\26\3\27\3\27\3\30\3\30\3\31")
        buf.write("\3\31\3\32\3\32\3\33\3\33\3\34\3\34\3\35\3\35\3\36\3\36")
        buf.write("\3\36\3\36\3\36\3\36\3\37\3\37\3\37\3\37\3\37\3\37\3 ")
        buf.write("\3 \3 \3 \3 \3!\3!\3!\3!\3!\3!\3\"\3\"\3\"\3\"\3\"\3#")
        buf.write("\3#\3#\3#\3#\3#\3$\3$\3$\3$\3$\3$\3%\3%\3%\3%\3%\3%\3")
        buf.write("%\3%\3%\3%\3%\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3")
        buf.write("&\3&\3&\3&\3&\3&\3&\3&\3&\3\'\3\'\3\'\3(\3(\3(\3(\3(\7")
        buf.write("(\u00f3\n(\f(\16(\u00f6\13(\3(\3(\3(\6(\u00fb\n(\r(\16")
        buf.write("(\u00fc\5(\u00ff\n(\3)\6)\u0102\n)\r)\16)\u0103\3)\3)")
        buf.write("\6)\u0108\n)\r)\16)\u0109\5)\u010c\n)\3)\6)\u010f\n)\r")
        buf.write(")\16)\u0110\3)\3)\6)\u0115\n)\r)\16)\u0116\5)\u0119\n")
        buf.write(")\5)\u011b\n)\3*\3*\3*\3*\3*\3*\3*\3*\3*\3*\3*\5*\u0128")
        buf.write("\n*\3+\3+\5+\u012c\n+\3,\3,\3-\3-\3.\3.\3/\3/\3\60\3\60")
        buf.write("\3\61\3\61\3\62\3\62\3\63\3\63\3\63\5\63\u013f\n\63\3")
        buf.write("\64\3\64\2\2\65\3\2\5\2\7\2\t\2\13\2\r\2\17\2\21\2\23")
        buf.write("\2\25\2\27\2\31\2\33\2\35\2\37\2!\2#\2%\2\'\2)\2+\2-\2")
        buf.write("/\2\61\2\63\2\65\2\67\29\2;\3=\4?\5A\6C\7E\bG\tI\nK\13")
        buf.write("M\fO\rQ\16S\17U\20W\21Y\22[\23]\24_\25a\26c\27e\30g\31")
        buf.write("\3\2\37\4\2C\\c|\3\2\62;\4\2CCcc\4\2DDdd\4\2EEee\4\2F")
        buf.write("Fff\4\2GGgg\4\2HHhh\4\2IIii\4\2JJjj\4\2KKkk\4\2LLll\4")
        buf.write("\2MMmm\4\2NNnn\4\2OOoo\4\2PPpp\4\2QQqq\4\2RRrr\4\2SSs")
        buf.write("s\4\2TTtt\4\2UUuu\4\2VVvv\4\2WWww\4\2XXxx\4\2YYyy\4\2")
        buf.write("ZZzz\4\2[[{{\4\2\\\\||\4\2\f\f\17\17\2\u013c\2;\3\2\2")
        buf.write("\2\2=\3\2\2\2\2?\3\2\2\2\2A\3\2\2\2\2C\3\2\2\2\2E\3\2")
        buf.write("\2\2\2G\3\2\2\2\2I\3\2\2\2\2K\3\2\2\2\2M\3\2\2\2\2O\3")
        buf.write("\2\2\2\2Q\3\2\2\2\2S\3\2\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y")
        buf.write("\3\2\2\2\2[\3\2\2\2\2]\3\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2")
        buf.write("c\3\2\2\2\2e\3\2\2\2\2g\3\2\2\2\3i\3\2\2\2\5k\3\2\2\2")
        buf.write("\7m\3\2\2\2\to\3\2\2\2\13q\3\2\2\2\rs\3\2\2\2\17u\3\2")
        buf.write("\2\2\21w\3\2\2\2\23y\3\2\2\2\25{\3\2\2\2\27}\3\2\2\2\31")
        buf.write("\177\3\2\2\2\33\u0081\3\2\2\2\35\u0083\3\2\2\2\37\u0085")
        buf.write("\3\2\2\2!\u0087\3\2\2\2#\u0089\3\2\2\2%\u008b\3\2\2\2")
        buf.write("\'\u008d\3\2\2\2)\u008f\3\2\2\2+\u0091\3\2\2\2-\u0093")
        buf.write("\3\2\2\2/\u0095\3\2\2\2\61\u0097\3\2\2\2\63\u0099\3\2")
        buf.write("\2\2\65\u009b\3\2\2\2\67\u009d\3\2\2\29\u009f\3\2\2\2")
        buf.write(";\u00a1\3\2\2\2=\u00a7\3\2\2\2?\u00ad\3\2\2\2A\u00b2\3")
        buf.write("\2\2\2C\u00b8\3\2\2\2E\u00bd\3\2\2\2G\u00c3\3\2\2\2I\u00c9")
        buf.write("\3\2\2\2K\u00d4\3\2\2\2M\u00ea\3\2\2\2O\u00ed\3\2\2\2")
        buf.write("Q\u011a\3\2\2\2S\u0127\3\2\2\2U\u012b\3\2\2\2W\u012d\3")
        buf.write("\2\2\2Y\u012f\3\2\2\2[\u0131\3\2\2\2]\u0133\3\2\2\2_\u0135")
        buf.write("\3\2\2\2a\u0137\3\2\2\2c\u0139\3\2\2\2e\u013e\3\2\2\2")
        buf.write("g\u0140\3\2\2\2ij\t\2\2\2j\4\3\2\2\2kl\t\3\2\2l\6\3\2")
        buf.write("\2\2mn\t\4\2\2n\b\3\2\2\2op\t\5\2\2p\n\3\2\2\2qr\t\6\2")
        buf.write("\2r\f\3\2\2\2st\t\7\2\2t\16\3\2\2\2uv\t\b\2\2v\20\3\2")
        buf.write("\2\2wx\t\t\2\2x\22\3\2\2\2yz\t\n\2\2z\24\3\2\2\2{|\t\13")
        buf.write("\2\2|\26\3\2\2\2}~\t\f\2\2~\30\3\2\2\2\177\u0080\t\r\2")
        buf.write("\2\u0080\32\3\2\2\2\u0081\u0082\t\16\2\2\u0082\34\3\2")
        buf.write("\2\2\u0083\u0084\t\17\2\2\u0084\36\3\2\2\2\u0085\u0086")
        buf.write("\t\20\2\2\u0086 \3\2\2\2\u0087\u0088\t\21\2\2\u0088\"")
        buf.write("\3\2\2\2\u0089\u008a\t\22\2\2\u008a$\3\2\2\2\u008b\u008c")
        buf.write("\t\23\2\2\u008c&\3\2\2\2\u008d\u008e\t\24\2\2\u008e(\3")
        buf.write("\2\2\2\u008f\u0090\t\25\2\2\u0090*\3\2\2\2\u0091\u0092")
        buf.write("\t\26\2\2\u0092,\3\2\2\2\u0093\u0094\t\27\2\2\u0094.\3")
        buf.write("\2\2\2\u0095\u0096\t\30\2\2\u0096\60\3\2\2\2\u0097\u0098")
        buf.write("\t\31\2\2\u0098\62\3\2\2\2\u0099\u009a\t\32\2\2\u009a")
        buf.write("\64\3\2\2\2\u009b\u009c\t\33\2\2\u009c\66\3\2\2\2\u009d")
        buf.write("\u009e\t\34\2\2\u009e8\3\2\2\2\u009f\u00a0\t\35\2\2\u00a0")
        buf.write(":\3\2\2\2\u00a1\u00a2\5\63\32\2\u00a2\u00a3\5\7\4\2\u00a3")
        buf.write("\u00a4\5-\27\2\u00a4\u00a5\5\13\6\2\u00a5\u00a6\5\25\13")
        buf.write("\2\u00a6<\3\2\2\2\u00a7\u00a8\5\7\4\2\u00a8\u00a9\5\35")
        buf.write("\17\2\u00a9\u00aa\5\7\4\2\u00aa\u00ab\5)\25\2\u00ab\u00ac")
        buf.write("\5\37\20\2\u00ac>\3\2\2\2\u00ad\u00ae\5+\26\2\u00ae\u00af")
        buf.write("\5-\27\2\u00af\u00b0\5#\22\2\u00b0\u00b1\5%\23\2\u00b1")
        buf.write("@\3\2\2\2\u00b2\u00b3\5%\23\2\u00b3\u00b4\5\7\4\2\u00b4")
        buf.write("\u00b5\5/\30\2\u00b5\u00b6\5+\26\2\u00b6\u00b7\5\17\b")
        buf.write("\2\u00b7B\3\2\2\2\u00b8\u00b9\5\37\20\2\u00b9\u00ba\5")
        buf.write("\7\4\2\u00ba\u00bb\5)\25\2\u00bb\u00bc\5\33\16\2\u00bc")
        buf.write("D\3\2\2\2\u00bd\u00be\5\t\5\2\u00be\u00bf\5\35\17\2\u00bf")
        buf.write("\u00c0\5#\22\2\u00c0\u00c1\5\13\6\2\u00c1\u00c2\5\33\16")
        buf.write("\2\u00c2F\3\2\2\2\u00c3\u00c4\5\17\b\2\u00c4\u00c5\5!")
        buf.write("\21\2\u00c5\u00c6\5\r\7\2\u00c6\u00c7\5]/\2\u00c7\u00c8")
        buf.write("\5E#\2\u00c8H\3\2\2\2\u00c9\u00ca\5\17\b\2\u00ca\u00cb")
        buf.write("\5!\21\2\u00cb\u00cc\5\r\7\2\u00cc\u00cd\5]/\2\u00cd\u00ce")
        buf.write("\5\t\5\2\u00ce\u00cf\5\35\17\2\u00cf\u00d0\5#\22\2\u00d0")
        buf.write("\u00d1\5\13\6\2\u00d1\u00d2\5\33\16\2\u00d2\u00d3\5+\26")
        buf.write("\2\u00d3J\3\2\2\2\u00d4\u00d5\5\27\f\2\u00d5\u00d6\5!")
        buf.write("\21\2\u00d6\u00d7\5\13\6\2\u00d7\u00d8\5)\25\2\u00d8\u00d9")
        buf.write("\5\17\b\2\u00d9\u00da\5\37\20\2\u00da\u00db\5\17\b\2\u00db")
        buf.write("\u00dc\5!\21\2\u00dc\u00dd\5-\27\2\u00dd\u00de\5]/\2\u00de")
        buf.write("\u00df\5)\25\2\u00df\u00e0\5/\30\2\u00e0\u00e1\5!\21\2")
        buf.write("\u00e1\u00e2\5]/\2\u00e2\u00e3\5\13\6\2\u00e3\u00e4\5")
        buf.write("#\22\2\u00e4\u00e5\5/\30\2\u00e5\u00e6\5!\21\2\u00e6\u00e7")
        buf.write("\5-\27\2\u00e7\u00e8\5\17\b\2\u00e8\u00e9\5)\25\2\u00e9")
        buf.write("L\3\2\2\2\u00ea\u00eb\5\37\20\2\u00eb\u00ec\5\35\17\2")
        buf.write("\u00ecN\3\2\2\2\u00ed\u00fe\5\3\2\2\u00ee\u00f3\5\3\2")
        buf.write("\2\u00ef\u00f3\5\5\3\2\u00f0\u00f3\5U+\2\u00f1\u00f3\5")
        buf.write("W,\2\u00f2\u00ee\3\2\2\2\u00f2\u00ef\3\2\2\2\u00f2\u00f0")
        buf.write("\3\2\2\2\u00f2\u00f1\3\2\2\2\u00f3\u00f6\3\2\2\2\u00f4")
        buf.write("\u00f2\3\2\2\2\u00f4\u00f5\3\2\2\2\u00f5\u00fa\3\2\2\2")
        buf.write("\u00f6\u00f4\3\2\2\2\u00f7\u00fb\5\3\2\2\u00f8\u00fb\5")
        buf.write("\5\3\2\u00f9\u00fb\5W,\2\u00fa\u00f7\3\2\2\2\u00fa\u00f8")
        buf.write("\3\2\2\2\u00fa\u00f9\3\2\2\2\u00fb\u00fc\3\2\2\2\u00fc")
        buf.write("\u00fa\3\2\2\2\u00fc\u00fd\3\2\2\2\u00fd\u00ff\3\2\2\2")
        buf.write("\u00fe\u00f4\3\2\2\2\u00fe\u00ff\3\2\2\2\u00ffP\3\2\2")
        buf.write("\2\u0100\u0102\5\5\3\2\u0101\u0100\3\2\2\2\u0102\u0103")
        buf.write("\3\2\2\2\u0103\u0101\3\2\2\2\u0103\u0104\3\2\2\2\u0104")
        buf.write("\u010b\3\2\2\2\u0105\u0107\5Y-\2\u0106\u0108\5\5\3\2\u0107")
        buf.write("\u0106\3\2\2\2\u0108\u0109\3\2\2\2\u0109\u0107\3\2\2\2")
        buf.write("\u0109\u010a\3\2\2\2\u010a\u010c\3\2\2\2\u010b\u0105\3")
        buf.write("\2\2\2\u010b\u010c\3\2\2\2\u010c\u011b\3\2\2\2\u010d\u010f")
        buf.write("\5\5\3\2\u010e\u010d\3\2\2\2\u010f\u0110\3\2\2\2\u0110")
        buf.write("\u010e\3\2\2\2\u0110\u0111\3\2\2\2\u0111\u0118\3\2\2\2")
        buf.write("\u0112\u0114\5[.\2\u0113\u0115\5\5\3\2\u0114\u0113\3\2")
        buf.write("\2\2\u0115\u0116\3\2\2\2\u0116\u0114\3\2\2\2\u0116\u0117")
        buf.write("\3\2\2\2\u0117\u0119\3\2\2\2\u0118\u0112\3\2\2\2\u0118")
        buf.write("\u0119\3\2\2\2\u0119\u011b\3\2\2\2\u011a\u0101\3\2\2\2")
        buf.write("\u011a\u010e\3\2\2\2\u011bR\3\2\2\2\u011c\u0128\7?\2\2")
        buf.write("\u011d\u011e\7?\2\2\u011e\u0128\7?\2\2\u011f\u0120\7>")
        buf.write("\2\2\u0120\u0128\7?\2\2\u0121\u0128\7>\2\2\u0122\u0123")
        buf.write("\7@\2\2\u0123\u0128\7?\2\2\u0124\u0128\7@\2\2\u0125\u0126")
        buf.write("\7#\2\2\u0126\u0128\7?\2\2\u0127\u011c\3\2\2\2\u0127\u011d")
        buf.write("\3\2\2\2\u0127\u011f\3\2\2\2\u0127\u0121\3\2\2\2\u0127")
        buf.write("\u0122\3\2\2\2\u0127\u0124\3\2\2\2\u0127\u0125\3\2\2\2")
        buf.write("\u0128T\3\2\2\2\u0129\u012c\5]/\2\u012a\u012c\5_\60\2")
        buf.write("\u012b\u0129\3\2\2\2\u012b\u012a\3\2\2\2\u012cV\3\2\2")
        buf.write("\2\u012d\u012e\7a\2\2\u012eX\3\2\2\2\u012f\u0130\7\60")
        buf.write("\2\2\u0130Z\3\2\2\2\u0131\u0132\7.\2\2\u0132\\\3\2\2\2")
        buf.write("\u0133\u0134\7\"\2\2\u0134^\3\2\2\2\u0135\u0136\7\13\2")
        buf.write("\2\u0136`\3\2\2\2\u0137\u0138\7%\2\2\u0138b\3\2\2\2\u0139")
        buf.write("\u013a\7<\2\2\u013ad\3\2\2\2\u013b\u013f\t\36\2\2\u013c")
        buf.write("\u013d\7\17\2\2\u013d\u013f\7\f\2\2\u013e\u013b\3\2\2")
        buf.write("\2\u013e\u013c\3\2\2\2\u013ff\3\2\2\2\u0140\u0141\13\2")
        buf.write("\2\2\u0141h\3\2\2\2\22\2\u00f2\u00f4\u00fa\u00fc\u00fe")
        buf.write("\u0103\u0109\u010b\u0110\u0116\u0118\u011a\u0127\u012b")
        buf.write("\u013e\2")
        return buf.getvalue()


class pcodeLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    WATCH = 1
    ALARM = 2
    STOP = 3
    PAUSE = 4
    MARK = 5
    BLOCK = 6
    END_BLOCK = 7
    END_BLOCKS = 8
    INCREMENT_RC = 9
    CONDITION_UNIT = 10
    IDENTIFIER = 11
    FLOAT = 12
    COMPARE_OP = 13
    WHITESPACE = 14
    UNDERSCORE = 15
    PERIOD = 16
    COMMA = 17
    SPACE = 18
    TAB = 19
    HASH = 20
    COLON = 21
    NEWLINE = 22
    ANY = 23

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'_'", "'.'", "','", "' '", "'\t'", "'#'", "':'" ]

    symbolicNames = [ "<INVALID>",
            "WATCH", "ALARM", "STOP", "PAUSE", "MARK", "BLOCK", "END_BLOCK", 
            "END_BLOCKS", "INCREMENT_RC", "CONDITION_UNIT", "IDENTIFIER", 
            "FLOAT", "COMPARE_OP", "WHITESPACE", "UNDERSCORE", "PERIOD", 
            "COMMA", "SPACE", "TAB", "HASH", "COLON", "NEWLINE", "ANY" ]

    ruleNames = [ "LETTER", "DIGIT", "A", "B", "C", "D", "E", "F", "G", 
                  "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", 
                  "S", "T", "U", "V", "W", "X", "Y", "Z", "WATCH", "ALARM", 
                  "STOP", "PAUSE", "MARK", "BLOCK", "END_BLOCK", "END_BLOCKS", 
                  "INCREMENT_RC", "CONDITION_UNIT", "IDENTIFIER", "FLOAT", 
                  "COMPARE_OP", "WHITESPACE", "UNDERSCORE", "PERIOD", "COMMA", 
                  "SPACE", "TAB", "HASH", "COLON", "NEWLINE", "ANY" ]

    grammarFileName = "pcode.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


