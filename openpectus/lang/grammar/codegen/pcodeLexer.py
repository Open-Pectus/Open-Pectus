# Generated from c:/Projects/Novo/Open-Pectus/openpectus/lang/grammar/pcode.g4 by ANTLR 4.13.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,29,272,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,
        2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,
        13,7,13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,
        19,2,20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,
        26,7,26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,1,0,1,0,1,1,1,1,
        1,2,1,2,1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,4,1,4,1,4,1,4,
        1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,7,1,7,1,7,
        1,7,1,7,1,8,1,8,1,8,1,8,1,8,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,10,
        1,10,1,10,1,10,1,10,1,11,1,11,1,11,1,11,1,11,1,11,1,12,1,12,1,12,
        1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,13,1,13,1,13,1,13,1,13,
        1,13,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,14,1,15,1,15,
        1,15,1,15,1,15,1,15,1,15,1,15,1,15,1,15,1,15,1,16,1,16,1,16,1,16,
        1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,
        1,16,1,16,1,16,1,16,1,16,1,17,1,17,1,17,1,17,1,17,5,17,191,8,17,
        10,17,12,17,194,9,17,1,17,1,17,1,17,4,17,199,8,17,11,17,12,17,200,
        3,17,203,8,17,1,18,4,18,206,8,18,11,18,12,18,207,1,18,1,18,4,18,
        212,8,18,11,18,12,18,213,3,18,216,8,18,1,18,4,18,219,8,18,11,18,
        12,18,220,1,18,1,18,4,18,225,8,18,11,18,12,18,226,3,18,229,8,18,
        3,18,231,8,18,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,1,19,
        1,19,3,19,244,8,19,1,20,1,20,3,20,248,8,20,1,21,1,21,1,22,1,22,1,
        23,1,23,1,24,1,24,1,25,1,25,1,26,1,26,1,27,1,27,1,28,1,28,1,29,1,
        29,1,29,3,29,269,8,29,1,30,1,30,0,0,31,1,0,3,0,5,1,7,2,9,3,11,4,
        13,5,15,6,17,7,19,8,21,9,23,10,25,11,27,12,29,13,31,14,33,15,35,
        16,37,17,39,18,41,19,43,20,45,21,47,22,49,23,51,24,53,25,55,26,57,
        27,59,28,61,29,1,0,3,2,0,65,90,97,122,1,0,48,57,2,0,10,10,13,13,
        292,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,0,13,1,0,0,
        0,0,15,1,0,0,0,0,17,1,0,0,0,0,19,1,0,0,0,0,21,1,0,0,0,0,23,1,0,0,
        0,0,25,1,0,0,0,0,27,1,0,0,0,0,29,1,0,0,0,0,31,1,0,0,0,0,33,1,0,0,
        0,0,35,1,0,0,0,0,37,1,0,0,0,0,39,1,0,0,0,0,41,1,0,0,0,0,43,1,0,0,
        0,0,45,1,0,0,0,0,47,1,0,0,0,0,49,1,0,0,0,0,51,1,0,0,0,0,53,1,0,0,
        0,0,55,1,0,0,0,0,57,1,0,0,0,0,59,1,0,0,0,0,61,1,0,0,0,1,63,1,0,0,
        0,3,65,1,0,0,0,5,67,1,0,0,0,7,73,1,0,0,0,9,79,1,0,0,0,11,85,1,0,
        0,0,13,90,1,0,0,0,15,96,1,0,0,0,17,101,1,0,0,0,19,106,1,0,0,0,21,
        114,1,0,0,0,23,119,1,0,0,0,25,125,1,0,0,0,27,136,1,0,0,0,29,142,
        1,0,0,0,31,152,1,0,0,0,33,163,1,0,0,0,35,185,1,0,0,0,37,230,1,0,
        0,0,39,243,1,0,0,0,41,247,1,0,0,0,43,249,1,0,0,0,45,251,1,0,0,0,
        47,253,1,0,0,0,49,255,1,0,0,0,51,257,1,0,0,0,53,259,1,0,0,0,55,261,
        1,0,0,0,57,263,1,0,0,0,59,268,1,0,0,0,61,270,1,0,0,0,63,64,7,0,0,
        0,64,2,1,0,0,0,65,66,7,1,0,0,66,4,1,0,0,0,67,68,5,87,0,0,68,69,5,
        97,0,0,69,70,5,116,0,0,70,71,5,99,0,0,71,72,5,104,0,0,72,6,1,0,0,
        0,73,74,5,65,0,0,74,75,5,108,0,0,75,76,5,97,0,0,76,77,5,114,0,0,
        77,78,5,109,0,0,78,8,1,0,0,0,79,80,5,77,0,0,80,81,5,97,0,0,81,82,
        5,99,0,0,82,83,5,114,0,0,83,84,5,111,0,0,84,10,1,0,0,0,85,86,5,83,
        0,0,86,87,5,116,0,0,87,88,5,111,0,0,88,89,5,112,0,0,89,12,1,0,0,
        0,90,91,5,80,0,0,91,92,5,97,0,0,92,93,5,117,0,0,93,94,5,115,0,0,
        94,95,5,101,0,0,95,14,1,0,0,0,96,97,5,72,0,0,97,98,5,111,0,0,98,
        99,5,108,0,0,99,100,5,100,0,0,100,16,1,0,0,0,101,102,5,87,0,0,102,
        103,5,97,0,0,103,104,5,105,0,0,104,105,5,116,0,0,105,18,1,0,0,0,
        106,107,5,82,0,0,107,108,5,101,0,0,108,109,5,115,0,0,109,110,5,116,
        0,0,110,111,5,97,0,0,111,112,5,114,0,0,112,113,5,116,0,0,113,20,
        1,0,0,0,114,115,5,77,0,0,115,116,5,97,0,0,116,117,5,114,0,0,117,
        118,5,107,0,0,118,22,1,0,0,0,119,120,5,66,0,0,120,121,5,97,0,0,121,
        122,5,116,0,0,122,123,5,99,0,0,123,124,5,104,0,0,124,24,1,0,0,0,
        125,126,5,67,0,0,126,127,5,97,0,0,127,128,5,108,0,0,128,129,5,108,
        0,0,129,130,5,32,0,0,130,131,5,109,0,0,131,132,5,97,0,0,132,133,
        5,99,0,0,133,134,5,114,0,0,134,135,5,111,0,0,135,26,1,0,0,0,136,
        137,5,66,0,0,137,138,5,108,0,0,138,139,5,111,0,0,139,140,5,99,0,
        0,140,141,5,107,0,0,141,28,1,0,0,0,142,143,5,69,0,0,143,144,5,110,
        0,0,144,145,5,100,0,0,145,146,5,32,0,0,146,147,5,98,0,0,147,148,
        5,108,0,0,148,149,5,111,0,0,149,150,5,99,0,0,150,151,5,107,0,0,151,
        30,1,0,0,0,152,153,5,69,0,0,153,154,5,110,0,0,154,155,5,100,0,0,
        155,156,5,32,0,0,156,157,5,98,0,0,157,158,5,108,0,0,158,159,5,111,
        0,0,159,160,5,99,0,0,160,161,5,107,0,0,161,162,5,115,0,0,162,32,
        1,0,0,0,163,164,5,73,0,0,164,165,5,110,0,0,165,166,5,99,0,0,166,
        167,5,114,0,0,167,168,5,101,0,0,168,169,5,109,0,0,169,170,5,101,
        0,0,170,171,5,110,0,0,171,172,5,116,0,0,172,173,5,32,0,0,173,174,
        5,114,0,0,174,175,5,117,0,0,175,176,5,110,0,0,176,177,5,32,0,0,177,
        178,5,99,0,0,178,179,5,111,0,0,179,180,5,117,0,0,180,181,5,110,0,
        0,181,182,5,116,0,0,182,183,5,101,0,0,183,184,5,114,0,0,184,34,1,
        0,0,0,185,202,3,1,0,0,186,191,3,1,0,0,187,191,3,3,1,0,188,191,3,
        41,20,0,189,191,3,43,21,0,190,186,1,0,0,0,190,187,1,0,0,0,190,188,
        1,0,0,0,190,189,1,0,0,0,191,194,1,0,0,0,192,190,1,0,0,0,192,193,
        1,0,0,0,193,198,1,0,0,0,194,192,1,0,0,0,195,199,3,1,0,0,196,199,
        3,3,1,0,197,199,3,43,21,0,198,195,1,0,0,0,198,196,1,0,0,0,198,197,
        1,0,0,0,199,200,1,0,0,0,200,198,1,0,0,0,200,201,1,0,0,0,201,203,
        1,0,0,0,202,192,1,0,0,0,202,203,1,0,0,0,203,36,1,0,0,0,204,206,3,
        3,1,0,205,204,1,0,0,0,206,207,1,0,0,0,207,205,1,0,0,0,207,208,1,
        0,0,0,208,215,1,0,0,0,209,211,3,45,22,0,210,212,3,3,1,0,211,210,
        1,0,0,0,212,213,1,0,0,0,213,211,1,0,0,0,213,214,1,0,0,0,214,216,
        1,0,0,0,215,209,1,0,0,0,215,216,1,0,0,0,216,231,1,0,0,0,217,219,
        3,3,1,0,218,217,1,0,0,0,219,220,1,0,0,0,220,218,1,0,0,0,220,221,
        1,0,0,0,221,228,1,0,0,0,222,224,3,47,23,0,223,225,3,3,1,0,224,223,
        1,0,0,0,225,226,1,0,0,0,226,224,1,0,0,0,226,227,1,0,0,0,227,229,
        1,0,0,0,228,222,1,0,0,0,228,229,1,0,0,0,229,231,1,0,0,0,230,205,
        1,0,0,0,230,218,1,0,0,0,231,38,1,0,0,0,232,244,5,61,0,0,233,234,
        5,61,0,0,234,244,5,61,0,0,235,236,5,60,0,0,236,244,5,61,0,0,237,
        244,5,60,0,0,238,239,5,62,0,0,239,244,5,61,0,0,240,244,5,62,0,0,
        241,242,5,33,0,0,242,244,5,61,0,0,243,232,1,0,0,0,243,233,1,0,0,
        0,243,235,1,0,0,0,243,237,1,0,0,0,243,238,1,0,0,0,243,240,1,0,0,
        0,243,241,1,0,0,0,244,40,1,0,0,0,245,248,3,49,24,0,246,248,3,51,
        25,0,247,245,1,0,0,0,247,246,1,0,0,0,248,42,1,0,0,0,249,250,5,95,
        0,0,250,44,1,0,0,0,251,252,5,46,0,0,252,46,1,0,0,0,253,254,5,44,
        0,0,254,48,1,0,0,0,255,256,5,32,0,0,256,50,1,0,0,0,257,258,5,9,0,
        0,258,52,1,0,0,0,259,260,5,35,0,0,260,54,1,0,0,0,261,262,5,58,0,
        0,262,56,1,0,0,0,263,264,5,45,0,0,264,58,1,0,0,0,265,269,7,2,0,0,
        266,267,5,13,0,0,267,269,5,10,0,0,268,265,1,0,0,0,268,266,1,0,0,
        0,269,60,1,0,0,0,270,271,9,0,0,0,271,62,1,0,0,0,16,0,190,192,198,
        200,202,207,213,215,220,226,228,230,243,247,268,0
    ]

class pcodeLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    WATCH = 1
    ALARM = 2
    MACRO = 3
    STOP = 4
    PAUSE = 5
    HOLD = 6
    WAIT = 7
    RESTART = 8
    MARK = 9
    BATCH = 10
    CALL_MACRO = 11
    BLOCK = 12
    END_BLOCK = 13
    END_BLOCKS = 14
    INCREMENT_RC = 15
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
            "'Watch'", "'Alarm'", "'Macro'", "'Stop'", "'Pause'", "'Hold'", 
            "'Wait'", "'Restart'", "'Mark'", "'Batch'", "'Call macro'", 
            "'Block'", "'End block'", "'End blocks'", "'Increment run counter'", 
            "'_'", "'.'", "','", "' '", "'\\t'", "'#'", "':'", "'-'" ]

    symbolicNames = [ "<INVALID>",
            "WATCH", "ALARM", "MACRO", "STOP", "PAUSE", "HOLD", "WAIT", 
            "RESTART", "MARK", "BATCH", "CALL_MACRO", "BLOCK", "END_BLOCK", 
            "END_BLOCKS", "INCREMENT_RC", "IDENTIFIER", "POSITIVE_FLOAT", 
            "COMPARE_OP", "WHITESPACE", "UNDERSCORE", "PERIOD", "COMMA", 
            "SPACE", "TAB", "HASH", "COLON", "MINUS", "NEWLINE", "ANY" ]

    ruleNames = [ "LETTER", "DIGIT", "WATCH", "ALARM", "MACRO", "STOP", 
                  "PAUSE", "HOLD", "WAIT", "RESTART", "MARK", "BATCH", "CALL_MACRO", 
                  "BLOCK", "END_BLOCK", "END_BLOCKS", "INCREMENT_RC", "IDENTIFIER", 
                  "POSITIVE_FLOAT", "COMPARE_OP", "WHITESPACE", "UNDERSCORE", 
                  "PERIOD", "COMMA", "SPACE", "TAB", "HASH", "COLON", "MINUS", 
                  "NEWLINE", "ANY" ]

    grammarFileName = "pcode.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


