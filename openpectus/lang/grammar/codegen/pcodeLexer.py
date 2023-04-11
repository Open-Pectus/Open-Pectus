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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\37")
        buf.write("\u018a\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23")
        buf.write("\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30")
        buf.write("\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36")
        buf.write("\t\36\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%")
        buf.write("\4&\t&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.")
        buf.write("\t.\4/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63\4\64")
        buf.write("\t\64\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\49\t9\4:\t:")
        buf.write("\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\7\3\7\3\b\3")
        buf.write("\b\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\16\3\16")
        buf.write("\3\17\3\17\3\20\3\20\3\21\3\21\3\22\3\22\3\23\3\23\3\24")
        buf.write("\3\24\3\25\3\25\3\26\3\26\3\27\3\27\3\30\3\30\3\31\3\31")
        buf.write("\3\32\3\32\3\33\3\33\3\34\3\34\3\35\3\35\3\36\3\36\3\36")
        buf.write("\3\36\3\36\3\36\3\37\3\37\3\37\3\37\3\37\3\37\3 \3 \3")
        buf.write(" \3 \3 \3!\3!\3!\3!\3!\3!\3\"\3\"\3\"\3\"\3\"\3#\3#\3")
        buf.write("#\3#\3#\3#\3$\3$\3$\3$\3$\3$\3%\3%\3%\3%\3%\3%\3%\3%\3")
        buf.write("%\3%\3%\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3&\3")
        buf.write("&\3&\3&\3&\3&\3&\3&\3\'\3\'\3\'\3\'\3\'\5\'\u00fc\n\'")
        buf.write("\3(\3(\3(\3(\5(\u0102\n(\3)\3)\3)\3)\5)\u0108\n)\3*\3")
        buf.write("*\3*\3*\5*\u010e\n*\3+\3+\3+\3+\3+\3+\3+\3+\3+\3+\5+\u011a")
        buf.write("\n+\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3")
        buf.write(",\3,\3,\3,\3,\3,\5,\u0132\n,\3-\3-\3-\3-\3-\7-\u0139\n")
        buf.write("-\f-\16-\u013c\13-\3-\3-\3-\6-\u0141\n-\r-\16-\u0142\5")
        buf.write("-\u0145\n-\3.\6.\u0148\n.\r.\16.\u0149\3.\3.\6.\u014e")
        buf.write("\n.\r.\16.\u014f\5.\u0152\n.\3.\6.\u0155\n.\r.\16.\u0156")
        buf.write("\3.\3.\6.\u015b\n.\r.\16.\u015c\5.\u015f\n.\5.\u0161\n")
        buf.write(".\3/\3/\3/\3/\3/\3/\3/\3/\3/\3/\3/\5/\u016e\n/\3\60\3")
        buf.write("\60\5\60\u0172\n\60\3\61\3\61\3\62\3\62\3\63\3\63\3\64")
        buf.write("\3\64\3\65\3\65\3\66\3\66\3\67\3\67\38\38\39\39\39\59")
        buf.write("\u0187\n9\3:\3:\2\2;\3\2\5\2\7\2\t\2\13\2\r\2\17\2\21")
        buf.write("\2\23\2\25\2\27\2\31\2\33\2\35\2\37\2!\2#\2%\2\'\2)\2")
        buf.write("+\2-\2/\2\61\2\63\2\65\2\67\29\2;\3=\4?\5A\6C\7E\bG\t")
        buf.write("I\nK\13M\fO\rQ\16S\17U\20W\21Y\22[\23]\24_\25a\26c\27")
        buf.write("e\30g\31i\32k\33m\34o\35q\36s\37\3\2\37\4\2C\\c|\3\2\62")
        buf.write(";\4\2CCcc\4\2DDdd\4\2EEee\4\2FFff\4\2GGgg\4\2HHhh\4\2")
        buf.write("IIii\4\2JJjj\4\2KKkk\4\2LLll\4\2MMmm\4\2NNnn\4\2OOoo\4")
        buf.write("\2PPpp\4\2QQqq\4\2RRrr\4\2SSss\4\2TTtt\4\2UUuu\4\2VVv")
        buf.write("v\4\2WWww\4\2XXxx\4\2YYyy\4\2ZZzz\4\2[[{{\4\2\\\\||\4")
        buf.write("\2\f\f\17\17\2\u0193\2;\3\2\2\2\2=\3\2\2\2\2?\3\2\2\2")
        buf.write("\2A\3\2\2\2\2C\3\2\2\2\2E\3\2\2\2\2G\3\2\2\2\2I\3\2\2")
        buf.write("\2\2K\3\2\2\2\2M\3\2\2\2\2O\3\2\2\2\2Q\3\2\2\2\2S\3\2")
        buf.write("\2\2\2U\3\2\2\2\2W\3\2\2\2\2Y\3\2\2\2\2[\3\2\2\2\2]\3")
        buf.write("\2\2\2\2_\3\2\2\2\2a\3\2\2\2\2c\3\2\2\2\2e\3\2\2\2\2g")
        buf.write("\3\2\2\2\2i\3\2\2\2\2k\3\2\2\2\2m\3\2\2\2\2o\3\2\2\2\2")
        buf.write("q\3\2\2\2\2s\3\2\2\2\3u\3\2\2\2\5w\3\2\2\2\7y\3\2\2\2")
        buf.write("\t{\3\2\2\2\13}\3\2\2\2\r\177\3\2\2\2\17\u0081\3\2\2\2")
        buf.write("\21\u0083\3\2\2\2\23\u0085\3\2\2\2\25\u0087\3\2\2\2\27")
        buf.write("\u0089\3\2\2\2\31\u008b\3\2\2\2\33\u008d\3\2\2\2\35\u008f")
        buf.write("\3\2\2\2\37\u0091\3\2\2\2!\u0093\3\2\2\2#\u0095\3\2\2")
        buf.write("\2%\u0097\3\2\2\2\'\u0099\3\2\2\2)\u009b\3\2\2\2+\u009d")
        buf.write("\3\2\2\2-\u009f\3\2\2\2/\u00a1\3\2\2\2\61\u00a3\3\2\2")
        buf.write("\2\63\u00a5\3\2\2\2\65\u00a7\3\2\2\2\67\u00a9\3\2\2\2")
        buf.write("9\u00ab\3\2\2\2;\u00ad\3\2\2\2=\u00b3\3\2\2\2?\u00b9\3")
        buf.write("\2\2\2A\u00be\3\2\2\2C\u00c4\3\2\2\2E\u00c9\3\2\2\2G\u00cf")
        buf.write("\3\2\2\2I\u00d5\3\2\2\2K\u00e0\3\2\2\2M\u00fb\3\2\2\2")
        buf.write("O\u0101\3\2\2\2Q\u0107\3\2\2\2S\u010d\3\2\2\2U\u0119\3")
        buf.write("\2\2\2W\u0131\3\2\2\2Y\u0133\3\2\2\2[\u0160\3\2\2\2]\u016d")
        buf.write("\3\2\2\2_\u0171\3\2\2\2a\u0173\3\2\2\2c\u0175\3\2\2\2")
        buf.write("e\u0177\3\2\2\2g\u0179\3\2\2\2i\u017b\3\2\2\2k\u017d\3")
        buf.write("\2\2\2m\u017f\3\2\2\2o\u0181\3\2\2\2q\u0186\3\2\2\2s\u0188")
        buf.write("\3\2\2\2uv\t\2\2\2v\4\3\2\2\2wx\t\3\2\2x\6\3\2\2\2yz\t")
        buf.write("\4\2\2z\b\3\2\2\2{|\t\5\2\2|\n\3\2\2\2}~\t\6\2\2~\f\3")
        buf.write("\2\2\2\177\u0080\t\7\2\2\u0080\16\3\2\2\2\u0081\u0082")
        buf.write("\t\b\2\2\u0082\20\3\2\2\2\u0083\u0084\t\t\2\2\u0084\22")
        buf.write("\3\2\2\2\u0085\u0086\t\n\2\2\u0086\24\3\2\2\2\u0087\u0088")
        buf.write("\t\13\2\2\u0088\26\3\2\2\2\u0089\u008a\t\f\2\2\u008a\30")
        buf.write("\3\2\2\2\u008b\u008c\t\r\2\2\u008c\32\3\2\2\2\u008d\u008e")
        buf.write("\t\16\2\2\u008e\34\3\2\2\2\u008f\u0090\t\17\2\2\u0090")
        buf.write("\36\3\2\2\2\u0091\u0092\t\20\2\2\u0092 \3\2\2\2\u0093")
        buf.write("\u0094\t\21\2\2\u0094\"\3\2\2\2\u0095\u0096\t\22\2\2\u0096")
        buf.write("$\3\2\2\2\u0097\u0098\t\23\2\2\u0098&\3\2\2\2\u0099\u009a")
        buf.write("\t\24\2\2\u009a(\3\2\2\2\u009b\u009c\t\25\2\2\u009c*\3")
        buf.write("\2\2\2\u009d\u009e\t\26\2\2\u009e,\3\2\2\2\u009f\u00a0")
        buf.write("\t\27\2\2\u00a0.\3\2\2\2\u00a1\u00a2\t\30\2\2\u00a2\60")
        buf.write("\3\2\2\2\u00a3\u00a4\t\31\2\2\u00a4\62\3\2\2\2\u00a5\u00a6")
        buf.write("\t\32\2\2\u00a6\64\3\2\2\2\u00a7\u00a8\t\33\2\2\u00a8")
        buf.write("\66\3\2\2\2\u00a9\u00aa\t\34\2\2\u00aa8\3\2\2\2\u00ab")
        buf.write("\u00ac\t\35\2\2\u00ac:\3\2\2\2\u00ad\u00ae\5\63\32\2\u00ae")
        buf.write("\u00af\5\7\4\2\u00af\u00b0\5-\27\2\u00b0\u00b1\5\13\6")
        buf.write("\2\u00b1\u00b2\5\25\13\2\u00b2<\3\2\2\2\u00b3\u00b4\5")
        buf.write("\7\4\2\u00b4\u00b5\5\35\17\2\u00b5\u00b6\5\7\4\2\u00b6")
        buf.write("\u00b7\5)\25\2\u00b7\u00b8\5\37\20\2\u00b8>\3\2\2\2\u00b9")
        buf.write("\u00ba\5+\26\2\u00ba\u00bb\5-\27\2\u00bb\u00bc\5#\22\2")
        buf.write("\u00bc\u00bd\5%\23\2\u00bd@\3\2\2\2\u00be\u00bf\5%\23")
        buf.write("\2\u00bf\u00c0\5\7\4\2\u00c0\u00c1\5/\30\2\u00c1\u00c2")
        buf.write("\5+\26\2\u00c2\u00c3\5\17\b\2\u00c3B\3\2\2\2\u00c4\u00c5")
        buf.write("\5\37\20\2\u00c5\u00c6\5\7\4\2\u00c6\u00c7\5)\25\2\u00c7")
        buf.write("\u00c8\5\33\16\2\u00c8D\3\2\2\2\u00c9\u00ca\5\t\5\2\u00ca")
        buf.write("\u00cb\5\35\17\2\u00cb\u00cc\5#\22\2\u00cc\u00cd\5\13")
        buf.write("\6\2\u00cd\u00ce\5\33\16\2\u00ceF\3\2\2\2\u00cf\u00d0")
        buf.write("\5\17\b\2\u00d0\u00d1\5!\21\2\u00d1\u00d2\5\r\7\2\u00d2")
        buf.write("\u00d3\5g\64\2\u00d3\u00d4\5E#\2\u00d4H\3\2\2\2\u00d5")
        buf.write("\u00d6\5\17\b\2\u00d6\u00d7\5!\21\2\u00d7\u00d8\5\r\7")
        buf.write("\2\u00d8\u00d9\5g\64\2\u00d9\u00da\5\t\5\2\u00da\u00db")
        buf.write("\5\35\17\2\u00db\u00dc\5#\22\2\u00dc\u00dd\5\13\6\2\u00dd")
        buf.write("\u00de\5\33\16\2\u00de\u00df\5+\26\2\u00dfJ\3\2\2\2\u00e0")
        buf.write("\u00e1\5\27\f\2\u00e1\u00e2\5!\21\2\u00e2\u00e3\5\13\6")
        buf.write("\2\u00e3\u00e4\5)\25\2\u00e4\u00e5\5\17\b\2\u00e5\u00e6")
        buf.write("\5\37\20\2\u00e6\u00e7\5\17\b\2\u00e7\u00e8\5!\21\2\u00e8")
        buf.write("\u00e9\5-\27\2\u00e9\u00ea\5g\64\2\u00ea\u00eb\5)\25\2")
        buf.write("\u00eb\u00ec\5/\30\2\u00ec\u00ed\5!\21\2\u00ed\u00ee\5")
        buf.write("g\64\2\u00ee\u00ef\5\13\6\2\u00ef\u00f0\5#\22\2\u00f0")
        buf.write("\u00f1\5/\30\2\u00f1\u00f2\5!\21\2\u00f2\u00f3\5-\27\2")
        buf.write("\u00f3\u00f4\5\17\b\2\u00f4\u00f5\5)\25\2\u00f5L\3\2\2")
        buf.write("\2\u00f6\u00fc\5O(\2\u00f7\u00fc\5Q)\2\u00f8\u00fc\5S")
        buf.write("*\2\u00f9\u00fc\5U+\2\u00fa\u00fc\5W,\2\u00fb\u00f6\3")
        buf.write("\2\2\2\u00fb\u00f7\3\2\2\2\u00fb\u00f8\3\2\2\2\u00fb\u00f9")
        buf.write("\3\2\2\2\u00fb\u00fa\3\2\2\2\u00fcN\3\2\2\2\u00fd\u0102")
        buf.write("\5\35\17\2\u00fe\u00ff\5\37\20\2\u00ff\u0100\5\35\17\2")
        buf.write("\u0100\u0102\3\2\2\2\u0101\u00fd\3\2\2\2\u0101\u00fe\3")
        buf.write("\2\2\2\u0102P\3\2\2\2\u0103\u0104\5\33\16\2\u0104\u0105")
        buf.write("\5\23\n\2\u0105\u0108\3\2\2\2\u0106\u0108\5\23\n\2\u0107")
        buf.write("\u0103\3\2\2\2\u0107\u0106\3\2\2\2\u0108R\3\2\2\2\u0109")
        buf.write("\u010e\5\37\20\2\u010a\u010b\5\13\6\2\u010b\u010c\5\37")
        buf.write("\20\2\u010c\u010e\3\2\2\2\u010d\u0109\3\2\2\2\u010d\u010a")
        buf.write("\3\2\2\2\u010eT\3\2\2\2\u010f\u011a\5\25\13\2\u0110\u0111")
        buf.write("\5\37\20\2\u0111\u0112\5\27\f\2\u0112\u0113\5!\21\2\u0113")
        buf.write("\u011a\3\2\2\2\u0114\u011a\5+\26\2\u0115\u0116\5+\26\2")
        buf.write("\u0116\u0117\5\17\b\2\u0117\u0118\5\13\6\2\u0118\u011a")
        buf.write("\3\2\2\2\u0119\u010f\3\2\2\2\u0119\u0110\3\2\2\2\u0119")
        buf.write("\u0114\3\2\2\2\u0119\u0115\3\2\2\2\u011aV\3\2\2\2\u011b")
        buf.write("\u0132\7\'\2\2\u011c\u011d\5\13\6\2\u011d\u011e\5\61\31")
        buf.write("\2\u011e\u0132\3\2\2\2\u011f\u0120\5\7\4\2\u0120\u0121")
        buf.write("\5/\30\2\u0121\u0132\3\2\2\2\u0122\u0123\5\35\17\2\u0123")
        buf.write("\u0124\7\61\2\2\u0124\u0125\5\25\13\2\u0125\u0132\3\2")
        buf.write("\2\2\u0126\u0127\5\33\16\2\u0127\u0128\5\23\n\2\u0128")
        buf.write("\u0129\7\61\2\2\u0129\u012a\5\25\13\2\u012a\u0132\3\2")
        buf.write("\2\2\u012b\u012c\5\37\20\2\u012c\u012d\5+\26\2\u012d\u012e")
        buf.write("\7\61\2\2\u012e\u012f\5\13\6\2\u012f\u0130\5\37\20\2\u0130")
        buf.write("\u0132\3\2\2\2\u0131\u011b\3\2\2\2\u0131\u011c\3\2\2\2")
        buf.write("\u0131\u011f\3\2\2\2\u0131\u0122\3\2\2\2\u0131\u0126\3")
        buf.write("\2\2\2\u0131\u012b\3\2\2\2\u0132X\3\2\2\2\u0133\u0144")
        buf.write("\5\3\2\2\u0134\u0139\5\3\2\2\u0135\u0139\5\5\3\2\u0136")
        buf.write("\u0139\5_\60\2\u0137\u0139\5a\61\2\u0138\u0134\3\2\2\2")
        buf.write("\u0138\u0135\3\2\2\2\u0138\u0136\3\2\2\2\u0138\u0137\3")
        buf.write("\2\2\2\u0139\u013c\3\2\2\2\u013a\u0138\3\2\2\2\u013a\u013b")
        buf.write("\3\2\2\2\u013b\u0140\3\2\2\2\u013c\u013a\3\2\2\2\u013d")
        buf.write("\u0141\5\3\2\2\u013e\u0141\5\5\3\2\u013f\u0141\5a\61\2")
        buf.write("\u0140\u013d\3\2\2\2\u0140\u013e\3\2\2\2\u0140\u013f\3")
        buf.write("\2\2\2\u0141\u0142\3\2\2\2\u0142\u0140\3\2\2\2\u0142\u0143")
        buf.write("\3\2\2\2\u0143\u0145\3\2\2\2\u0144\u013a\3\2\2\2\u0144")
        buf.write("\u0145\3\2\2\2\u0145Z\3\2\2\2\u0146\u0148\5\5\3\2\u0147")
        buf.write("\u0146\3\2\2\2\u0148\u0149\3\2\2\2\u0149\u0147\3\2\2\2")
        buf.write("\u0149\u014a\3\2\2\2\u014a\u0151\3\2\2\2\u014b\u014d\5")
        buf.write("c\62\2\u014c\u014e\5\5\3\2\u014d\u014c\3\2\2\2\u014e\u014f")
        buf.write("\3\2\2\2\u014f\u014d\3\2\2\2\u014f\u0150\3\2\2\2\u0150")
        buf.write("\u0152\3\2\2\2\u0151\u014b\3\2\2\2\u0151\u0152\3\2\2\2")
        buf.write("\u0152\u0161\3\2\2\2\u0153\u0155\5\5\3\2\u0154\u0153\3")
        buf.write("\2\2\2\u0155\u0156\3\2\2\2\u0156\u0154\3\2\2\2\u0156\u0157")
        buf.write("\3\2\2\2\u0157\u015e\3\2\2\2\u0158\u015a\5e\63\2\u0159")
        buf.write("\u015b\5\5\3\2\u015a\u0159\3\2\2\2\u015b\u015c\3\2\2\2")
        buf.write("\u015c\u015a\3\2\2\2\u015c\u015d\3\2\2\2\u015d\u015f\3")
        buf.write("\2\2\2\u015e\u0158\3\2\2\2\u015e\u015f\3\2\2\2\u015f\u0161")
        buf.write("\3\2\2\2\u0160\u0147\3\2\2\2\u0160\u0154\3\2\2\2\u0161")
        buf.write("\\\3\2\2\2\u0162\u016e\7?\2\2\u0163\u0164\7?\2\2\u0164")
        buf.write("\u016e\7?\2\2\u0165\u0166\7>\2\2\u0166\u016e\7?\2\2\u0167")
        buf.write("\u016e\7>\2\2\u0168\u0169\7@\2\2\u0169\u016e\7?\2\2\u016a")
        buf.write("\u016e\7@\2\2\u016b\u016c\7#\2\2\u016c\u016e\7?\2\2\u016d")
        buf.write("\u0162\3\2\2\2\u016d\u0163\3\2\2\2\u016d\u0165\3\2\2\2")
        buf.write("\u016d\u0167\3\2\2\2\u016d\u0168\3\2\2\2\u016d\u016a\3")
        buf.write("\2\2\2\u016d\u016b\3\2\2\2\u016e^\3\2\2\2\u016f\u0172")
        buf.write("\5g\64\2\u0170\u0172\5i\65\2\u0171\u016f\3\2\2\2\u0171")
        buf.write("\u0170\3\2\2\2\u0172`\3\2\2\2\u0173\u0174\7a\2\2\u0174")
        buf.write("b\3\2\2\2\u0175\u0176\7\60\2\2\u0176d\3\2\2\2\u0177\u0178")
        buf.write("\7.\2\2\u0178f\3\2\2\2\u0179\u017a\7\"\2\2\u017ah\3\2")
        buf.write("\2\2\u017b\u017c\7\13\2\2\u017cj\3\2\2\2\u017d\u017e\7")
        buf.write("%\2\2\u017el\3\2\2\2\u017f\u0180\7<\2\2\u0180n\3\2\2\2")
        buf.write("\u0181\u0182\7/\2\2\u0182p\3\2\2\2\u0183\u0187\t\36\2")
        buf.write("\2\u0184\u0185\7\17\2\2\u0185\u0187\7\f\2\2\u0186\u0183")
        buf.write("\3\2\2\2\u0186\u0184\3\2\2\2\u0187r\3\2\2\2\u0188\u0189")
        buf.write("\13\2\2\2\u0189t\3\2\2\2\30\2\u00fb\u0101\u0107\u010d")
        buf.write("\u0119\u0131\u0138\u013a\u0140\u0142\u0144\u0149\u014f")
        buf.write("\u0151\u0156\u015c\u015e\u0160\u016d\u0171\u0186\2")
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
    VOLUME_UNIT = 11
    MASS_UNIT = 12
    DISTANCE_UNIT = 13
    DURATION_UNIT = 14
    OTHER_UNIT = 15
    IDENTIFIER = 16
    POSITIVE_FLOAT = 17
    COMPARE_OP = 18
    WHITESPACE = 19
    UNDERSCORE = 20
    PERIOD = 21
    COMMA = 22
    SPACE = 23
    TAB = 24
    HASH = 25
    COLON = 26
    MINUS = 27
    NEWLINE = 28
    ANY = 29

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'_'", "'.'", "','", "' '", "'\t'", "'#'", "':'", "'-'" ]

    symbolicNames = [ "<INVALID>",
            "WATCH", "ALARM", "STOP", "PAUSE", "MARK", "BLOCK", "END_BLOCK", 
            "END_BLOCKS", "INCREMENT_RC", "CONDITION_UNIT", "VOLUME_UNIT", 
            "MASS_UNIT", "DISTANCE_UNIT", "DURATION_UNIT", "OTHER_UNIT", 
            "IDENTIFIER", "POSITIVE_FLOAT", "COMPARE_OP", "WHITESPACE", 
            "UNDERSCORE", "PERIOD", "COMMA", "SPACE", "TAB", "HASH", "COLON", 
            "MINUS", "NEWLINE", "ANY" ]

    ruleNames = [ "LETTER", "DIGIT", "A", "B", "C", "D", "E", "F", "G", 
                  "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", 
                  "S", "T", "U", "V", "W", "X", "Y", "Z", "WATCH", "ALARM", 
                  "STOP", "PAUSE", "MARK", "BLOCK", "END_BLOCK", "END_BLOCKS", 
                  "INCREMENT_RC", "CONDITION_UNIT", "VOLUME_UNIT", "MASS_UNIT", 
                  "DISTANCE_UNIT", "DURATION_UNIT", "OTHER_UNIT", "IDENTIFIER", 
                  "POSITIVE_FLOAT", "COMPARE_OP", "WHITESPACE", "UNDERSCORE", 
                  "PERIOD", "COMMA", "SPACE", "TAB", "HASH", "COLON", "MINUS", 
                  "NEWLINE", "ANY" ]

    grammarFileName = "pcode.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


