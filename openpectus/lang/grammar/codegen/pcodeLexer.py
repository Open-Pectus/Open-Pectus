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
        4,0,30,402,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,
        2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,
        13,7,13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,
        19,2,20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,
        26,7,26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,
        32,2,33,7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,
        39,7,39,2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,
        45,2,46,7,46,2,47,7,47,2,48,7,48,2,49,7,49,2,50,7,50,2,51,7,51,2,
        52,7,52,2,53,7,53,2,54,7,54,2,55,7,55,2,56,7,56,2,57,7,57,1,0,1,
        0,1,1,1,1,1,2,1,2,1,3,1,3,1,4,1,4,1,5,1,5,1,6,1,6,1,7,1,7,1,8,1,
        8,1,9,1,9,1,10,1,10,1,11,1,11,1,12,1,12,1,13,1,13,1,14,1,14,1,15,
        1,15,1,16,1,16,1,17,1,17,1,18,1,18,1,19,1,19,1,20,1,20,1,21,1,21,
        1,22,1,22,1,23,1,23,1,24,1,24,1,25,1,25,1,26,1,26,1,27,1,27,1,28,
        1,28,1,28,1,28,1,28,1,28,1,29,1,29,1,29,1,29,1,29,1,29,1,30,1,30,
        1,30,1,30,1,30,1,31,1,31,1,31,1,31,1,31,1,31,1,32,1,32,1,32,1,32,
        1,32,1,32,1,32,1,32,1,33,1,33,1,33,1,33,1,33,1,34,1,34,1,34,1,34,
        1,34,1,34,1,35,1,35,1,35,1,35,1,35,1,35,1,36,1,36,1,36,1,36,1,36,
        1,36,1,36,1,36,1,36,1,36,1,36,1,37,1,37,1,37,1,37,1,37,1,37,1,37,
        1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,1,37,
        1,37,1,37,1,38,1,38,1,38,1,38,1,38,3,38,260,8,38,1,39,1,39,1,39,
        1,39,3,39,266,8,39,1,40,1,40,1,40,1,40,3,40,272,8,40,1,41,1,41,1,
        41,1,41,3,41,278,8,41,1,42,1,42,1,42,1,42,1,42,1,42,1,42,1,42,1,
        42,1,42,3,42,290,8,42,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,
        43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,43,1,
        43,3,43,314,8,43,1,44,1,44,1,44,1,44,1,44,5,44,321,8,44,10,44,12,
        44,324,9,44,1,44,1,44,1,44,4,44,329,8,44,11,44,12,44,330,3,44,333,
        8,44,1,45,4,45,336,8,45,11,45,12,45,337,1,45,1,45,4,45,342,8,45,
        11,45,12,45,343,3,45,346,8,45,1,45,4,45,349,8,45,11,45,12,45,350,
        1,45,1,45,4,45,355,8,45,11,45,12,45,356,3,45,359,8,45,3,45,361,8,
        45,1,46,1,46,1,46,1,46,1,46,1,46,1,46,1,46,1,46,1,46,1,46,3,46,374,
        8,46,1,47,1,47,3,47,378,8,47,1,48,1,48,1,49,1,49,1,50,1,50,1,51,
        1,51,1,52,1,52,1,53,1,53,1,54,1,54,1,55,1,55,1,56,1,56,1,56,3,56,
        399,8,56,1,57,1,57,0,0,58,1,0,3,0,5,0,7,0,9,0,11,0,13,0,15,0,17,
        0,19,0,21,0,23,0,25,0,27,0,29,0,31,0,33,0,35,0,37,0,39,0,41,0,43,
        0,45,0,47,0,49,0,51,0,53,0,55,0,57,1,59,2,61,3,63,4,65,5,67,6,69,
        7,71,8,73,9,75,10,77,11,79,12,81,13,83,14,85,15,87,16,89,17,91,18,
        93,19,95,20,97,21,99,22,101,23,103,24,105,25,107,26,109,27,111,28,
        113,29,115,30,1,0,29,2,0,65,90,97,122,1,0,48,57,2,0,65,65,97,97,
        2,0,66,66,98,98,2,0,67,67,99,99,2,0,68,68,100,100,2,0,69,69,101,
        101,2,0,70,70,102,102,2,0,71,71,103,103,2,0,72,72,104,104,2,0,73,
        73,105,105,2,0,74,74,106,106,2,0,75,75,107,107,2,0,76,76,108,108,
        2,0,77,77,109,109,2,0,78,78,110,110,2,0,79,79,111,111,2,0,80,80,
        112,112,2,0,81,81,113,113,2,0,82,82,114,114,2,0,83,83,115,115,2,
        0,84,84,116,116,2,0,85,85,117,117,2,0,86,86,118,118,2,0,87,87,119,
        119,2,0,88,88,120,120,2,0,89,89,121,121,2,0,90,90,122,122,2,0,10,
        10,13,13,411,0,57,1,0,0,0,0,59,1,0,0,0,0,61,1,0,0,0,0,63,1,0,0,0,
        0,65,1,0,0,0,0,67,1,0,0,0,0,69,1,0,0,0,0,71,1,0,0,0,0,73,1,0,0,0,
        0,75,1,0,0,0,0,77,1,0,0,0,0,79,1,0,0,0,0,81,1,0,0,0,0,83,1,0,0,0,
        0,85,1,0,0,0,0,87,1,0,0,0,0,89,1,0,0,0,0,91,1,0,0,0,0,93,1,0,0,0,
        0,95,1,0,0,0,0,97,1,0,0,0,0,99,1,0,0,0,0,101,1,0,0,0,0,103,1,0,0,
        0,0,105,1,0,0,0,0,107,1,0,0,0,0,109,1,0,0,0,0,111,1,0,0,0,0,113,
        1,0,0,0,0,115,1,0,0,0,1,117,1,0,0,0,3,119,1,0,0,0,5,121,1,0,0,0,
        7,123,1,0,0,0,9,125,1,0,0,0,11,127,1,0,0,0,13,129,1,0,0,0,15,131,
        1,0,0,0,17,133,1,0,0,0,19,135,1,0,0,0,21,137,1,0,0,0,23,139,1,0,
        0,0,25,141,1,0,0,0,27,143,1,0,0,0,29,145,1,0,0,0,31,147,1,0,0,0,
        33,149,1,0,0,0,35,151,1,0,0,0,37,153,1,0,0,0,39,155,1,0,0,0,41,157,
        1,0,0,0,43,159,1,0,0,0,45,161,1,0,0,0,47,163,1,0,0,0,49,165,1,0,
        0,0,51,167,1,0,0,0,53,169,1,0,0,0,55,171,1,0,0,0,57,173,1,0,0,0,
        59,179,1,0,0,0,61,185,1,0,0,0,63,190,1,0,0,0,65,196,1,0,0,0,67,204,
        1,0,0,0,69,209,1,0,0,0,71,215,1,0,0,0,73,221,1,0,0,0,75,232,1,0,
        0,0,77,259,1,0,0,0,79,265,1,0,0,0,81,271,1,0,0,0,83,277,1,0,0,0,
        85,289,1,0,0,0,87,313,1,0,0,0,89,315,1,0,0,0,91,360,1,0,0,0,93,373,
        1,0,0,0,95,377,1,0,0,0,97,379,1,0,0,0,99,381,1,0,0,0,101,383,1,0,
        0,0,103,385,1,0,0,0,105,387,1,0,0,0,107,389,1,0,0,0,109,391,1,0,
        0,0,111,393,1,0,0,0,113,398,1,0,0,0,115,400,1,0,0,0,117,118,7,0,
        0,0,118,2,1,0,0,0,119,120,7,1,0,0,120,4,1,0,0,0,121,122,7,2,0,0,
        122,6,1,0,0,0,123,124,7,3,0,0,124,8,1,0,0,0,125,126,7,4,0,0,126,
        10,1,0,0,0,127,128,7,5,0,0,128,12,1,0,0,0,129,130,7,6,0,0,130,14,
        1,0,0,0,131,132,7,7,0,0,132,16,1,0,0,0,133,134,7,8,0,0,134,18,1,
        0,0,0,135,136,7,9,0,0,136,20,1,0,0,0,137,138,7,10,0,0,138,22,1,0,
        0,0,139,140,7,11,0,0,140,24,1,0,0,0,141,142,7,12,0,0,142,26,1,0,
        0,0,143,144,7,13,0,0,144,28,1,0,0,0,145,146,7,14,0,0,146,30,1,0,
        0,0,147,148,7,15,0,0,148,32,1,0,0,0,149,150,7,16,0,0,150,34,1,0,
        0,0,151,152,7,17,0,0,152,36,1,0,0,0,153,154,7,18,0,0,154,38,1,0,
        0,0,155,156,7,19,0,0,156,40,1,0,0,0,157,158,7,20,0,0,158,42,1,0,
        0,0,159,160,7,21,0,0,160,44,1,0,0,0,161,162,7,22,0,0,162,46,1,0,
        0,0,163,164,7,23,0,0,164,48,1,0,0,0,165,166,7,24,0,0,166,50,1,0,
        0,0,167,168,7,25,0,0,168,52,1,0,0,0,169,170,7,26,0,0,170,54,1,0,
        0,0,171,172,7,27,0,0,172,56,1,0,0,0,173,174,3,49,24,0,174,175,3,
        5,2,0,175,176,3,43,21,0,176,177,3,9,4,0,177,178,3,19,9,0,178,58,
        1,0,0,0,179,180,3,5,2,0,180,181,3,27,13,0,181,182,3,5,2,0,182,183,
        3,39,19,0,183,184,3,29,14,0,184,60,1,0,0,0,185,186,3,41,20,0,186,
        187,3,43,21,0,187,188,3,33,16,0,188,189,3,35,17,0,189,62,1,0,0,0,
        190,191,3,35,17,0,191,192,3,5,2,0,192,193,3,45,22,0,193,194,3,41,
        20,0,194,195,3,13,6,0,195,64,1,0,0,0,196,197,3,39,19,0,197,198,3,
        13,6,0,198,199,3,41,20,0,199,200,3,43,21,0,200,201,3,5,2,0,201,202,
        3,39,19,0,202,203,3,43,21,0,203,66,1,0,0,0,204,205,3,29,14,0,205,
        206,3,5,2,0,206,207,3,39,19,0,207,208,3,25,12,0,208,68,1,0,0,0,209,
        210,3,7,3,0,210,211,3,27,13,0,211,212,3,33,16,0,212,213,3,9,4,0,
        213,214,3,25,12,0,214,70,1,0,0,0,215,216,3,13,6,0,216,217,3,31,15,
        0,217,218,3,11,5,0,218,219,3,103,51,0,219,220,3,69,34,0,220,72,1,
        0,0,0,221,222,3,13,6,0,222,223,3,31,15,0,223,224,3,11,5,0,224,225,
        3,103,51,0,225,226,3,7,3,0,226,227,3,27,13,0,227,228,3,33,16,0,228,
        229,3,9,4,0,229,230,3,25,12,0,230,231,3,41,20,0,231,74,1,0,0,0,232,
        233,3,21,10,0,233,234,3,31,15,0,234,235,3,9,4,0,235,236,3,39,19,
        0,236,237,3,13,6,0,237,238,3,29,14,0,238,239,3,13,6,0,239,240,3,
        31,15,0,240,241,3,43,21,0,241,242,3,103,51,0,242,243,3,39,19,0,243,
        244,3,45,22,0,244,245,3,31,15,0,245,246,3,103,51,0,246,247,3,9,4,
        0,247,248,3,33,16,0,248,249,3,45,22,0,249,250,3,31,15,0,250,251,
        3,43,21,0,251,252,3,13,6,0,252,253,3,39,19,0,253,76,1,0,0,0,254,
        260,3,79,39,0,255,260,3,81,40,0,256,260,3,83,41,0,257,260,3,85,42,
        0,258,260,3,87,43,0,259,254,1,0,0,0,259,255,1,0,0,0,259,256,1,0,
        0,0,259,257,1,0,0,0,259,258,1,0,0,0,260,78,1,0,0,0,261,266,3,27,
        13,0,262,263,3,29,14,0,263,264,3,27,13,0,264,266,1,0,0,0,265,261,
        1,0,0,0,265,262,1,0,0,0,266,80,1,0,0,0,267,268,3,25,12,0,268,269,
        3,17,8,0,269,272,1,0,0,0,270,272,3,17,8,0,271,267,1,0,0,0,271,270,
        1,0,0,0,272,82,1,0,0,0,273,278,3,29,14,0,274,275,3,9,4,0,275,276,
        3,29,14,0,276,278,1,0,0,0,277,273,1,0,0,0,277,274,1,0,0,0,278,84,
        1,0,0,0,279,290,3,19,9,0,280,281,3,29,14,0,281,282,3,21,10,0,282,
        283,3,31,15,0,283,290,1,0,0,0,284,290,3,41,20,0,285,286,3,41,20,
        0,286,287,3,13,6,0,287,288,3,9,4,0,288,290,1,0,0,0,289,279,1,0,0,
        0,289,280,1,0,0,0,289,284,1,0,0,0,289,285,1,0,0,0,290,86,1,0,0,0,
        291,314,5,37,0,0,292,293,3,9,4,0,293,294,3,47,23,0,294,314,1,0,0,
        0,295,296,3,5,2,0,296,297,3,45,22,0,297,314,1,0,0,0,298,299,3,27,
        13,0,299,300,5,47,0,0,300,301,3,19,9,0,301,314,1,0,0,0,302,303,3,
        25,12,0,303,304,3,17,8,0,304,305,5,47,0,0,305,306,3,19,9,0,306,314,
        1,0,0,0,307,308,3,29,14,0,308,309,3,41,20,0,309,310,5,47,0,0,310,
        311,3,9,4,0,311,312,3,29,14,0,312,314,1,0,0,0,313,291,1,0,0,0,313,
        292,1,0,0,0,313,295,1,0,0,0,313,298,1,0,0,0,313,302,1,0,0,0,313,
        307,1,0,0,0,314,88,1,0,0,0,315,332,3,1,0,0,316,321,3,1,0,0,317,321,
        3,3,1,0,318,321,3,95,47,0,319,321,3,97,48,0,320,316,1,0,0,0,320,
        317,1,0,0,0,320,318,1,0,0,0,320,319,1,0,0,0,321,324,1,0,0,0,322,
        320,1,0,0,0,322,323,1,0,0,0,323,328,1,0,0,0,324,322,1,0,0,0,325,
        329,3,1,0,0,326,329,3,3,1,0,327,329,3,97,48,0,328,325,1,0,0,0,328,
        326,1,0,0,0,328,327,1,0,0,0,329,330,1,0,0,0,330,328,1,0,0,0,330,
        331,1,0,0,0,331,333,1,0,0,0,332,322,1,0,0,0,332,333,1,0,0,0,333,
        90,1,0,0,0,334,336,3,3,1,0,335,334,1,0,0,0,336,337,1,0,0,0,337,335,
        1,0,0,0,337,338,1,0,0,0,338,345,1,0,0,0,339,341,3,99,49,0,340,342,
        3,3,1,0,341,340,1,0,0,0,342,343,1,0,0,0,343,341,1,0,0,0,343,344,
        1,0,0,0,344,346,1,0,0,0,345,339,1,0,0,0,345,346,1,0,0,0,346,361,
        1,0,0,0,347,349,3,3,1,0,348,347,1,0,0,0,349,350,1,0,0,0,350,348,
        1,0,0,0,350,351,1,0,0,0,351,358,1,0,0,0,352,354,3,101,50,0,353,355,
        3,3,1,0,354,353,1,0,0,0,355,356,1,0,0,0,356,354,1,0,0,0,356,357,
        1,0,0,0,357,359,1,0,0,0,358,352,1,0,0,0,358,359,1,0,0,0,359,361,
        1,0,0,0,360,335,1,0,0,0,360,348,1,0,0,0,361,92,1,0,0,0,362,374,5,
        61,0,0,363,364,5,61,0,0,364,374,5,61,0,0,365,366,5,60,0,0,366,374,
        5,61,0,0,367,374,5,60,0,0,368,369,5,62,0,0,369,374,5,61,0,0,370,
        374,5,62,0,0,371,372,5,33,0,0,372,374,5,61,0,0,373,362,1,0,0,0,373,
        363,1,0,0,0,373,365,1,0,0,0,373,367,1,0,0,0,373,368,1,0,0,0,373,
        370,1,0,0,0,373,371,1,0,0,0,374,94,1,0,0,0,375,378,3,103,51,0,376,
        378,3,105,52,0,377,375,1,0,0,0,377,376,1,0,0,0,378,96,1,0,0,0,379,
        380,5,95,0,0,380,98,1,0,0,0,381,382,5,46,0,0,382,100,1,0,0,0,383,
        384,5,44,0,0,384,102,1,0,0,0,385,386,5,32,0,0,386,104,1,0,0,0,387,
        388,5,9,0,0,388,106,1,0,0,0,389,390,5,35,0,0,390,108,1,0,0,0,391,
        392,5,58,0,0,392,110,1,0,0,0,393,394,5,45,0,0,394,112,1,0,0,0,395,
        399,7,28,0,0,396,397,5,13,0,0,397,399,5,10,0,0,398,395,1,0,0,0,398,
        396,1,0,0,0,399,114,1,0,0,0,400,401,9,0,0,0,401,116,1,0,0,0,22,0,
        259,265,271,277,289,313,320,322,328,330,332,337,343,345,350,356,
        358,360,373,377,398,0
    ]

class pcodeLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    WATCH = 1
    ALARM = 2
    STOP = 3
    PAUSE = 4
    RESTART = 5
    MARK = 6
    BLOCK = 7
    END_BLOCK = 8
    END_BLOCKS = 9
    INCREMENT_RC = 10
    CONDITION_UNIT = 11
    VOLUME_UNIT = 12
    MASS_UNIT = 13
    DISTANCE_UNIT = 14
    DURATION_UNIT = 15
    OTHER_UNIT = 16
    IDENTIFIER = 17
    POSITIVE_FLOAT = 18
    COMPARE_OP = 19
    WHITESPACE = 20
    UNDERSCORE = 21
    PERIOD = 22
    COMMA = 23
    SPACE = 24
    TAB = 25
    HASH = 26
    COLON = 27
    MINUS = 28
    NEWLINE = 29
    ANY = 30

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'_'", "'.'", "','", "' '", "'\\t'", "'#'", "':'", "'-'" ]

    symbolicNames = [ "<INVALID>",
            "WATCH", "ALARM", "STOP", "PAUSE", "RESTART", "MARK", "BLOCK", 
            "END_BLOCK", "END_BLOCKS", "INCREMENT_RC", "CONDITION_UNIT", 
            "VOLUME_UNIT", "MASS_UNIT", "DISTANCE_UNIT", "DURATION_UNIT", 
            "OTHER_UNIT", "IDENTIFIER", "POSITIVE_FLOAT", "COMPARE_OP", 
            "WHITESPACE", "UNDERSCORE", "PERIOD", "COMMA", "SPACE", "TAB", 
            "HASH", "COLON", "MINUS", "NEWLINE", "ANY" ]

    ruleNames = [ "LETTER", "DIGIT", "A", "B", "C", "D", "E", "F", "G", 
                  "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", 
                  "S", "T", "U", "V", "W", "X", "Y", "Z", "WATCH", "ALARM", 
                  "STOP", "PAUSE", "RESTART", "MARK", "BLOCK", "END_BLOCK", 
                  "END_BLOCKS", "INCREMENT_RC", "CONDITION_UNIT", "VOLUME_UNIT", 
                  "MASS_UNIT", "DISTANCE_UNIT", "DURATION_UNIT", "OTHER_UNIT", 
                  "IDENTIFIER", "POSITIVE_FLOAT", "COMPARE_OP", "WHITESPACE", 
                  "UNDERSCORE", "PERIOD", "COMMA", "SPACE", "TAB", "HASH", 
                  "COLON", "MINUS", "NEWLINE", "ANY" ]

    grammarFileName = "pcode.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


