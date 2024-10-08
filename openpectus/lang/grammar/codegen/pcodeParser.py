# Generated from c:/Projects/Novo/Open-Pectus/openpectus/lang/grammar/pcode.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,26,377,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,1,0,1,0,1,0,5,0,72,8,0,10,0,12,0,75,9,0,1,0,1,0,1,1,5,1,80,
        8,1,10,1,12,1,83,9,1,1,1,1,1,5,1,87,8,1,10,1,12,1,90,9,1,1,1,3,1,
        93,8,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,3,2,111,8,2,1,3,3,3,114,8,3,1,3,1,3,1,3,5,3,119,8,3,10,3,12,
        3,122,9,3,1,3,3,3,125,8,3,1,3,3,3,128,8,3,1,4,1,4,1,5,3,5,133,8,
        5,1,5,1,5,1,6,3,6,138,8,6,1,6,1,6,1,7,3,7,143,8,7,1,7,1,7,1,7,5,
        7,148,8,7,10,7,12,7,151,9,7,1,7,3,7,154,8,7,1,7,3,7,157,8,7,1,8,
        3,8,160,8,8,1,8,1,8,1,8,5,8,165,8,8,10,8,12,8,168,9,8,1,8,3,8,171,
        8,8,1,8,3,8,174,8,8,1,9,1,9,5,9,178,8,9,10,9,12,9,181,9,9,1,9,1,
        9,5,9,185,8,9,10,9,12,9,188,9,9,1,9,1,9,1,10,1,10,1,11,5,11,195,
        8,11,10,11,12,11,198,9,11,1,11,1,11,1,12,5,12,203,8,12,10,12,12,
        12,206,9,12,1,12,1,12,1,13,3,13,211,8,13,1,13,1,13,1,14,3,14,216,
        8,14,1,14,1,14,1,15,3,15,221,8,15,1,15,1,15,1,16,3,16,226,8,16,1,
        16,1,16,1,16,5,16,231,8,16,10,16,12,16,234,9,16,1,16,3,16,237,8,
        16,1,16,3,16,240,8,16,1,17,3,17,243,8,17,1,17,1,17,1,17,5,17,248,
        8,17,10,17,12,17,251,9,17,1,17,3,17,254,8,17,1,17,3,17,257,8,17,
        1,18,3,18,260,8,18,1,18,1,18,1,18,5,18,265,8,18,10,18,12,18,268,
        9,18,1,18,3,18,271,8,18,1,18,3,18,274,8,18,1,19,5,19,277,8,19,10,
        19,12,19,280,9,19,1,19,1,19,1,20,3,20,285,8,20,1,20,1,20,1,20,5,
        20,290,8,20,10,20,12,20,293,9,20,1,20,3,20,296,8,20,1,21,1,21,1,
        22,1,22,4,22,302,8,22,11,22,12,22,303,1,23,1,23,1,24,1,24,1,24,1,
        25,5,25,312,8,25,10,25,12,25,315,9,25,1,25,1,25,1,26,5,26,320,8,
        26,10,26,12,26,323,9,26,1,27,3,27,326,8,27,1,27,1,27,1,27,5,27,331,
        8,27,10,27,12,27,334,9,27,1,27,3,27,337,8,27,1,28,1,28,1,29,5,29,
        342,8,29,10,29,12,29,345,9,29,1,29,1,29,1,30,1,30,1,31,1,31,5,31,
        353,8,31,10,31,12,31,356,9,31,1,31,3,31,359,8,31,1,32,5,32,362,8,
        32,10,32,12,32,365,9,32,1,32,1,32,1,33,5,33,370,8,33,10,33,12,33,
        373,9,33,1,33,1,33,1,33,8,196,204,278,313,343,354,363,371,0,34,0,
        2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,
        48,50,52,54,56,58,60,62,64,66,0,4,3,0,15,15,22,23,25,25,2,0,22,23,
        25,25,1,0,25,25,2,0,22,22,25,25,409,0,68,1,0,0,0,2,81,1,0,0,0,4,
        110,1,0,0,0,6,113,1,0,0,0,8,129,1,0,0,0,10,132,1,0,0,0,12,137,1,
        0,0,0,14,142,1,0,0,0,16,159,1,0,0,0,18,175,1,0,0,0,20,191,1,0,0,
        0,22,196,1,0,0,0,24,204,1,0,0,0,26,210,1,0,0,0,28,215,1,0,0,0,30,
        220,1,0,0,0,32,225,1,0,0,0,34,242,1,0,0,0,36,259,1,0,0,0,38,278,
        1,0,0,0,40,284,1,0,0,0,42,297,1,0,0,0,44,299,1,0,0,0,46,305,1,0,
        0,0,48,307,1,0,0,0,50,313,1,0,0,0,52,321,1,0,0,0,54,325,1,0,0,0,
        56,338,1,0,0,0,58,343,1,0,0,0,60,348,1,0,0,0,62,358,1,0,0,0,64,363,
        1,0,0,0,66,371,1,0,0,0,68,73,3,2,1,0,69,70,5,25,0,0,70,72,3,2,1,
        0,71,69,1,0,0,0,72,75,1,0,0,0,73,71,1,0,0,0,73,74,1,0,0,0,74,76,
        1,0,0,0,75,73,1,0,0,0,76,77,5,0,0,1,77,1,1,0,0,0,78,80,5,16,0,0,
        79,78,1,0,0,0,80,83,1,0,0,0,81,79,1,0,0,0,81,82,1,0,0,0,82,84,1,
        0,0,0,83,81,1,0,0,0,84,88,3,4,2,0,85,87,5,16,0,0,86,85,1,0,0,0,87,
        90,1,0,0,0,88,86,1,0,0,0,88,89,1,0,0,0,89,92,1,0,0,0,90,88,1,0,0,
        0,91,93,3,48,24,0,92,91,1,0,0,0,92,93,1,0,0,0,93,3,1,0,0,0,94,111,
        3,6,3,0,95,111,3,10,5,0,96,111,3,12,6,0,97,111,3,14,7,0,98,111,3,
        16,8,0,99,111,3,26,13,0,100,111,3,28,14,0,101,111,3,30,15,0,102,
        111,3,32,16,0,103,111,3,34,17,0,104,111,3,36,18,0,105,111,3,40,20,
        0,106,111,3,54,27,0,107,111,3,48,24,0,108,111,3,52,26,0,109,111,
        3,66,33,0,110,94,1,0,0,0,110,95,1,0,0,0,110,96,1,0,0,0,110,97,1,
        0,0,0,110,98,1,0,0,0,110,99,1,0,0,0,110,100,1,0,0,0,110,101,1,0,
        0,0,110,102,1,0,0,0,110,103,1,0,0,0,110,104,1,0,0,0,110,105,1,0,
        0,0,110,106,1,0,0,0,110,107,1,0,0,0,110,108,1,0,0,0,110,109,1,0,
        0,0,111,5,1,0,0,0,112,114,3,44,22,0,113,112,1,0,0,0,113,114,1,0,
        0,0,114,115,1,0,0,0,115,127,5,9,0,0,116,120,5,23,0,0,117,119,5,16,
        0,0,118,117,1,0,0,0,119,122,1,0,0,0,120,118,1,0,0,0,120,121,1,0,
        0,0,121,123,1,0,0,0,122,120,1,0,0,0,123,125,3,8,4,0,124,116,1,0,
        0,0,124,125,1,0,0,0,125,128,1,0,0,0,126,128,3,64,32,0,127,124,1,
        0,0,0,127,126,1,0,0,0,128,7,1,0,0,0,129,130,3,62,31,0,130,9,1,0,
        0,0,131,133,3,44,22,0,132,131,1,0,0,0,132,133,1,0,0,0,133,134,1,
        0,0,0,134,135,5,10,0,0,135,11,1,0,0,0,136,138,3,44,22,0,137,136,
        1,0,0,0,137,138,1,0,0,0,138,139,1,0,0,0,139,140,5,11,0,0,140,13,
        1,0,0,0,141,143,3,44,22,0,142,141,1,0,0,0,142,143,1,0,0,0,143,144,
        1,0,0,0,144,156,5,1,0,0,145,149,5,23,0,0,146,148,5,16,0,0,147,146,
        1,0,0,0,148,151,1,0,0,0,149,147,1,0,0,0,149,150,1,0,0,0,150,152,
        1,0,0,0,151,149,1,0,0,0,152,154,3,18,9,0,153,145,1,0,0,0,153,154,
        1,0,0,0,154,157,1,0,0,0,155,157,3,64,32,0,156,153,1,0,0,0,156,155,
        1,0,0,0,157,15,1,0,0,0,158,160,3,44,22,0,159,158,1,0,0,0,159,160,
        1,0,0,0,160,161,1,0,0,0,161,173,5,2,0,0,162,166,5,23,0,0,163,165,
        5,16,0,0,164,163,1,0,0,0,165,168,1,0,0,0,166,164,1,0,0,0,166,167,
        1,0,0,0,167,169,1,0,0,0,168,166,1,0,0,0,169,171,3,18,9,0,170,162,
        1,0,0,0,170,171,1,0,0,0,171,174,1,0,0,0,172,174,3,64,32,0,173,170,
        1,0,0,0,173,172,1,0,0,0,174,17,1,0,0,0,175,179,3,22,11,0,176,178,
        5,16,0,0,177,176,1,0,0,0,178,181,1,0,0,0,179,177,1,0,0,0,179,180,
        1,0,0,0,180,182,1,0,0,0,181,179,1,0,0,0,182,186,3,20,10,0,183,185,
        5,16,0,0,184,183,1,0,0,0,185,188,1,0,0,0,186,184,1,0,0,0,186,187,
        1,0,0,0,187,189,1,0,0,0,188,186,1,0,0,0,189,190,3,24,12,0,190,19,
        1,0,0,0,191,192,5,15,0,0,192,21,1,0,0,0,193,195,9,0,0,0,194,193,
        1,0,0,0,195,198,1,0,0,0,196,197,1,0,0,0,196,194,1,0,0,0,197,199,
        1,0,0,0,198,196,1,0,0,0,199,200,8,0,0,0,200,23,1,0,0,0,201,203,9,
        0,0,0,202,201,1,0,0,0,203,206,1,0,0,0,204,205,1,0,0,0,204,202,1,
        0,0,0,205,207,1,0,0,0,206,204,1,0,0,0,207,208,8,0,0,0,208,25,1,0,
        0,0,209,211,3,44,22,0,210,209,1,0,0,0,210,211,1,0,0,0,211,212,1,
        0,0,0,212,213,5,12,0,0,213,27,1,0,0,0,214,216,3,44,22,0,215,214,
        1,0,0,0,215,216,1,0,0,0,216,217,1,0,0,0,217,218,5,7,0,0,218,29,1,
        0,0,0,219,221,3,44,22,0,220,219,1,0,0,0,220,221,1,0,0,0,221,222,
        1,0,0,0,222,223,5,3,0,0,223,31,1,0,0,0,224,226,3,44,22,0,225,224,
        1,0,0,0,225,226,1,0,0,0,226,227,1,0,0,0,227,239,5,4,0,0,228,232,
        5,23,0,0,229,231,5,16,0,0,230,229,1,0,0,0,231,234,1,0,0,0,232,230,
        1,0,0,0,232,233,1,0,0,0,233,235,1,0,0,0,234,232,1,0,0,0,235,237,
        3,38,19,0,236,228,1,0,0,0,236,237,1,0,0,0,237,240,1,0,0,0,238,240,
        3,64,32,0,239,236,1,0,0,0,239,238,1,0,0,0,240,33,1,0,0,0,241,243,
        3,44,22,0,242,241,1,0,0,0,242,243,1,0,0,0,243,244,1,0,0,0,244,256,
        5,5,0,0,245,249,5,23,0,0,246,248,5,16,0,0,247,246,1,0,0,0,248,251,
        1,0,0,0,249,247,1,0,0,0,249,250,1,0,0,0,250,252,1,0,0,0,251,249,
        1,0,0,0,252,254,3,38,19,0,253,245,1,0,0,0,253,254,1,0,0,0,254,257,
        1,0,0,0,255,257,3,64,32,0,256,253,1,0,0,0,256,255,1,0,0,0,257,35,
        1,0,0,0,258,260,3,44,22,0,259,258,1,0,0,0,259,260,1,0,0,0,260,261,
        1,0,0,0,261,273,5,6,0,0,262,266,5,23,0,0,263,265,5,16,0,0,264,263,
        1,0,0,0,265,268,1,0,0,0,266,264,1,0,0,0,266,267,1,0,0,0,267,269,
        1,0,0,0,268,266,1,0,0,0,269,271,3,38,19,0,270,262,1,0,0,0,270,271,
        1,0,0,0,271,274,1,0,0,0,272,274,3,64,32,0,273,270,1,0,0,0,273,272,
        1,0,0,0,274,37,1,0,0,0,275,277,9,0,0,0,276,275,1,0,0,0,277,280,1,
        0,0,0,278,279,1,0,0,0,278,276,1,0,0,0,279,281,1,0,0,0,280,278,1,
        0,0,0,281,282,8,1,0,0,282,39,1,0,0,0,283,285,3,44,22,0,284,283,1,
        0,0,0,284,285,1,0,0,0,285,286,1,0,0,0,286,287,5,8,0,0,287,291,5,
        23,0,0,288,290,5,16,0,0,289,288,1,0,0,0,290,293,1,0,0,0,291,289,
        1,0,0,0,291,292,1,0,0,0,292,295,1,0,0,0,293,291,1,0,0,0,294,296,
        3,42,21,0,295,294,1,0,0,0,295,296,1,0,0,0,296,41,1,0,0,0,297,298,
        3,62,31,0,298,43,1,0,0,0,299,301,3,46,23,0,300,302,5,16,0,0,301,
        300,1,0,0,0,302,303,1,0,0,0,303,301,1,0,0,0,303,304,1,0,0,0,304,
        45,1,0,0,0,305,306,5,14,0,0,306,47,1,0,0,0,307,308,5,22,0,0,308,
        309,3,50,25,0,309,49,1,0,0,0,310,312,9,0,0,0,311,310,1,0,0,0,312,
        315,1,0,0,0,313,314,1,0,0,0,313,311,1,0,0,0,314,316,1,0,0,0,315,
        313,1,0,0,0,316,317,8,2,0,0,317,51,1,0,0,0,318,320,5,16,0,0,319,
        318,1,0,0,0,320,323,1,0,0,0,321,319,1,0,0,0,321,322,1,0,0,0,322,
        53,1,0,0,0,323,321,1,0,0,0,324,326,3,44,22,0,325,324,1,0,0,0,325,
        326,1,0,0,0,326,327,1,0,0,0,327,336,3,56,28,0,328,332,5,23,0,0,329,
        331,5,16,0,0,330,329,1,0,0,0,331,334,1,0,0,0,332,330,1,0,0,0,332,
        333,1,0,0,0,333,335,1,0,0,0,334,332,1,0,0,0,335,337,3,58,29,0,336,
        328,1,0,0,0,336,337,1,0,0,0,337,55,1,0,0,0,338,339,3,60,30,0,339,
        57,1,0,0,0,340,342,9,0,0,0,341,340,1,0,0,0,342,345,1,0,0,0,343,344,
        1,0,0,0,343,341,1,0,0,0,344,346,1,0,0,0,345,343,1,0,0,0,346,347,
        8,3,0,0,347,59,1,0,0,0,348,349,5,13,0,0,349,61,1,0,0,0,350,359,5,
        13,0,0,351,353,9,0,0,0,352,351,1,0,0,0,353,356,1,0,0,0,354,355,1,
        0,0,0,354,352,1,0,0,0,355,357,1,0,0,0,356,354,1,0,0,0,357,359,8,
        3,0,0,358,350,1,0,0,0,358,354,1,0,0,0,359,63,1,0,0,0,360,362,9,0,
        0,0,361,360,1,0,0,0,362,365,1,0,0,0,363,364,1,0,0,0,363,361,1,0,
        0,0,364,366,1,0,0,0,365,363,1,0,0,0,366,367,8,3,0,0,367,65,1,0,0,
        0,368,370,9,0,0,0,369,368,1,0,0,0,370,373,1,0,0,0,371,372,1,0,0,
        0,371,369,1,0,0,0,372,374,1,0,0,0,373,371,1,0,0,0,374,375,8,3,0,
        0,375,67,1,0,0,0,53,73,81,88,92,110,113,120,124,127,132,137,142,
        149,153,156,159,166,170,173,179,186,196,204,210,215,220,225,232,
        236,239,242,249,253,256,259,266,270,273,278,284,291,295,303,313,
        321,325,332,336,343,354,358,363,371
    ]

class pcodeParser ( Parser ):

    grammarFileName = "pcode.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'Watch'", "'Alarm'", "'Stop'", "'Pause'", 
                     "'Hold'", "'Wait'", "'Restart'", "'Mark'", "'Block'", 
                     "'End block'", "'End blocks'", "'Increment run counter'", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'_'", "'.'", "','", "' '", "'\\t'", "'#'", "':'", 
                     "'-'" ]

    symbolicNames = [ "<INVALID>", "WATCH", "ALARM", "STOP", "PAUSE", "HOLD", 
                      "WAIT", "RESTART", "MARK", "BLOCK", "END_BLOCK", "END_BLOCKS", 
                      "INCREMENT_RC", "IDENTIFIER", "POSITIVE_FLOAT", "COMPARE_OP", 
                      "WHITESPACE", "UNDERSCORE", "PERIOD", "COMMA", "SPACE", 
                      "TAB", "HASH", "COLON", "MINUS", "NEWLINE", "ANY" ]

    RULE_program = 0
    RULE_instruction_line = 1
    RULE_instruction = 2
    RULE_block = 3
    RULE_block_name = 4
    RULE_end_block = 5
    RULE_end_blocks = 6
    RULE_watch = 7
    RULE_alarm = 8
    RULE_condition = 9
    RULE_compare_op = 10
    RULE_condition_lhs = 11
    RULE_condition_rhs = 12
    RULE_increment_rc = 13
    RULE_restart = 14
    RULE_stop = 15
    RULE_pause = 16
    RULE_hold = 17
    RULE_wait = 18
    RULE_duration = 19
    RULE_mark = 20
    RULE_mark_name = 21
    RULE_time = 22
    RULE_timeexp = 23
    RULE_comment = 24
    RULE_comment_text = 25
    RULE_blank = 26
    RULE_command = 27
    RULE_command_name = 28
    RULE_command_args = 29
    RULE_identifier = 30
    RULE_identifier_ext = 31
    RULE_inst_error = 32
    RULE_error = 33

    ruleNames =  [ "program", "instruction_line", "instruction", "block", 
                   "block_name", "end_block", "end_blocks", "watch", "alarm", 
                   "condition", "compare_op", "condition_lhs", "condition_rhs", 
                   "increment_rc", "restart", "stop", "pause", "hold", "wait", 
                   "duration", "mark", "mark_name", "time", "timeexp", "comment", 
                   "comment_text", "blank", "command", "command_name", "command_args", 
                   "identifier", "identifier_ext", "inst_error", "error" ]

    EOF = Token.EOF
    WATCH=1
    ALARM=2
    STOP=3
    PAUSE=4
    HOLD=5
    WAIT=6
    RESTART=7
    MARK=8
    BLOCK=9
    END_BLOCK=10
    END_BLOCKS=11
    INCREMENT_RC=12
    IDENTIFIER=13
    POSITIVE_FLOAT=14
    COMPARE_OP=15
    WHITESPACE=16
    UNDERSCORE=17
    PERIOD=18
    COMMA=19
    SPACE=20
    TAB=21
    HASH=22
    COLON=23
    MINUS=24
    NEWLINE=25
    ANY=26

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def instruction_line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pcodeParser.Instruction_lineContext)
            else:
                return self.getTypedRuleContext(pcodeParser.Instruction_lineContext,i)


        def EOF(self):
            return self.getToken(pcodeParser.EOF, 0)

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
            self.state = 68
            self.instruction_line()
            self.state = 73
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==25:
                self.state = 69
                self.match(pcodeParser.NEWLINE)
                self.state = 70
                self.instruction_line()
                self.state = 75
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 76
            self.match(pcodeParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Instruction_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def instruction(self):
            return self.getTypedRuleContext(pcodeParser.InstructionContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def comment(self):
            return self.getTypedRuleContext(pcodeParser.CommentContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_instruction_line

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInstruction_line" ):
                listener.enterInstruction_line(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInstruction_line" ):
                listener.exitInstruction_line(self)




    def instruction_line(self):

        localctx = pcodeParser.Instruction_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_instruction_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 78
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 83
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 84
            self.instruction()
            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==16:
                self.state = 85
                self.match(pcodeParser.WHITESPACE)
                self.state = 90
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 92
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==22:
                self.state = 91
                self.comment()


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


        def restart(self):
            return self.getTypedRuleContext(pcodeParser.RestartContext,0)


        def stop(self):
            return self.getTypedRuleContext(pcodeParser.StopContext,0)


        def pause(self):
            return self.getTypedRuleContext(pcodeParser.PauseContext,0)


        def hold(self):
            return self.getTypedRuleContext(pcodeParser.HoldContext,0)


        def wait(self):
            return self.getTypedRuleContext(pcodeParser.WaitContext,0)


        def mark(self):
            return self.getTypedRuleContext(pcodeParser.MarkContext,0)


        def command(self):
            return self.getTypedRuleContext(pcodeParser.CommandContext,0)


        def comment(self):
            return self.getTypedRuleContext(pcodeParser.CommentContext,0)


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
        self.enterRule(localctx, 4, self.RULE_instruction)
        try:
            self.state = 110
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 94
                self.block()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 95
                self.end_block()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 96
                self.end_blocks()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 97
                self.watch()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 98
                self.alarm()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 99
                self.increment_rc()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 100
                self.restart()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 101
                self.stop()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 102
                self.pause()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 103
                self.hold()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 104
                self.wait()
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 105
                self.mark()
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 106
                self.command()
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 107
                self.comment()
                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 108
                self.blank()
                pass

            elif la_ == 16:
                self.enterOuterAlt(localctx, 16)
                self.state = 109
                self.error()
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

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def block_name(self):
            return self.getTypedRuleContext(pcodeParser.Block_nameContext,0)


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
            self.state = 113
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 112
                self.time()


            self.state = 115
            self.match(pcodeParser.BLOCK)
            self.state = 127
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 124
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 116
                    self.match(pcodeParser.COLON)
                    self.state = 120
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 117
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 122
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                    self.state = 123
                    self.block_name()


                pass

            elif la_ == 2:
                self.state = 126
                self.inst_error()
                pass


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

        def identifier_ext(self):
            return self.getTypedRuleContext(pcodeParser.Identifier_extContext,0)


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
            self.state = 129
            self.identifier_ext()
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
            self.state = 132
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 131
                self.time()


            self.state = 134
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
            self.state = 137
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 136
                self.time()


            self.state = 139
            self.match(pcodeParser.END_BLOCKS)
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

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


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
        self.enterRule(localctx, 14, self.RULE_watch)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 142
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 141
                self.time()


            self.state = 144
            self.match(pcodeParser.WATCH)
            self.state = 156
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                self.state = 153
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 145
                    self.match(pcodeParser.COLON)
                    self.state = 149
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 146
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 151
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

                    self.state = 152
                    self.condition()


                pass

            elif la_ == 2:
                self.state = 155
                self.inst_error()
                pass


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

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


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
        self.enterRule(localctx, 16, self.RULE_alarm)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 159
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 158
                self.time()


            self.state = 161
            self.match(pcodeParser.ALARM)
            self.state = 173
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
            if la_ == 1:
                self.state = 170
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 162
                    self.match(pcodeParser.COLON)
                    self.state = 166
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 163
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 168
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

                    self.state = 169
                    self.condition()


                pass

            elif la_ == 2:
                self.state = 172
                self.inst_error()
                pass


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

        def condition_lhs(self):
            return self.getTypedRuleContext(pcodeParser.Condition_lhsContext,0)


        def compare_op(self):
            return self.getTypedRuleContext(pcodeParser.Compare_opContext,0)


        def condition_rhs(self):
            return self.getTypedRuleContext(pcodeParser.Condition_rhsContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
        self.enterRule(localctx, 18, self.RULE_condition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.condition_lhs()
            self.state = 179
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==16:
                self.state = 176
                self.match(pcodeParser.WHITESPACE)
                self.state = 181
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 182
            self.compare_op()
            self.state = 186
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,20,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 183
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 188
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

            self.state = 189
            self.condition_rhs()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compare_opContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COMPARE_OP(self):
            return self.getToken(pcodeParser.COMPARE_OP, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_compare_op

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompare_op" ):
                listener.enterCompare_op(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompare_op" ):
                listener.exitCompare_op(self)




    def compare_op(self):

        localctx = pcodeParser.Compare_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_compare_op)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 191
            self.match(pcodeParser.COMPARE_OP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Condition_lhsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def COMPARE_OP(self):
            return self.getToken(pcodeParser.COMPARE_OP, 0)

        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_condition_lhs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition_lhs" ):
                listener.enterCondition_lhs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition_lhs" ):
                listener.exitCondition_lhs(self)




    def condition_lhs(self):

        localctx = pcodeParser.Condition_lhsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_condition_lhs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 196
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,21,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 193
                    self.matchWildcard() 
                self.state = 198
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

            self.state = 199
            _la = self._input.LA(1)
            if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 46170112) != 0):
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


    class Condition_rhsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def COMPARE_OP(self):
            return self.getToken(pcodeParser.COMPARE_OP, 0)

        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_condition_rhs

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition_rhs" ):
                listener.enterCondition_rhs(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition_rhs" ):
                listener.exitCondition_rhs(self)




    def condition_rhs(self):

        localctx = pcodeParser.Condition_rhsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_condition_rhs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 204
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 201
                    self.matchWildcard() 
                self.state = 206
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

            self.state = 207
            _la = self._input.LA(1)
            if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 46170112) != 0):
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
            self.state = 210
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 209
                self.time()


            self.state = 212
            self.match(pcodeParser.INCREMENT_RC)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RestartContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RESTART(self):
            return self.getToken(pcodeParser.RESTART, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_restart

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRestart" ):
                listener.enterRestart(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRestart" ):
                listener.exitRestart(self)




    def restart(self):

        localctx = pcodeParser.RestartContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_restart)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 215
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 214
                self.time()


            self.state = 217
            self.match(pcodeParser.RESTART)
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
        self.enterRule(localctx, 30, self.RULE_stop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 219
                self.time()


            self.state = 222
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

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def duration(self):
            return self.getTypedRuleContext(pcodeParser.DurationContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

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
        self.enterRule(localctx, 32, self.RULE_pause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 224
                self.time()


            self.state = 227
            self.match(pcodeParser.PAUSE)
            self.state = 239
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.state = 236
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 228
                    self.match(pcodeParser.COLON)
                    self.state = 232
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,27,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 229
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 234
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,27,self._ctx)

                    self.state = 235
                    self.duration()


                pass

            elif la_ == 2:
                self.state = 238
                self.inst_error()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HoldContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def HOLD(self):
            return self.getToken(pcodeParser.HOLD, 0)

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def duration(self):
            return self.getTypedRuleContext(pcodeParser.DurationContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def getRuleIndex(self):
            return pcodeParser.RULE_hold

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterHold" ):
                listener.enterHold(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitHold" ):
                listener.exitHold(self)




    def hold(self):

        localctx = pcodeParser.HoldContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_hold)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 242
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 241
                self.time()


            self.state = 244
            self.match(pcodeParser.HOLD)
            self.state = 256
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                self.state = 253
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 245
                    self.match(pcodeParser.COLON)
                    self.state = 249
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,31,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 246
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 251
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,31,self._ctx)

                    self.state = 252
                    self.duration()


                pass

            elif la_ == 2:
                self.state = 255
                self.inst_error()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WaitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WAIT(self):
            return self.getToken(pcodeParser.WAIT, 0)

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def duration(self):
            return self.getTypedRuleContext(pcodeParser.DurationContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def getRuleIndex(self):
            return pcodeParser.RULE_wait

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWait" ):
                listener.enterWait(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWait" ):
                listener.exitWait(self)




    def wait(self):

        localctx = pcodeParser.WaitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_wait)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 259
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 258
                self.time()


            self.state = 261
            self.match(pcodeParser.WAIT)
            self.state = 273
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,37,self._ctx)
            if la_ == 1:
                self.state = 270
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==23:
                    self.state = 262
                    self.match(pcodeParser.COLON)
                    self.state = 266
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,35,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 263
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 268
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,35,self._ctx)

                    self.state = 269
                    self.duration()


                pass

            elif la_ == 2:
                self.state = 272
                self.inst_error()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DurationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_duration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDuration" ):
                listener.enterDuration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDuration" ):
                listener.exitDuration(self)




    def duration(self):

        localctx = pcodeParser.DurationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_duration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 278
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,38,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 275
                    self.matchWildcard() 
                self.state = 280
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,38,self._ctx)

            self.state = 281
            _la = self._input.LA(1)
            if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 46137344) != 0):
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


    class MarkContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MARK(self):
            return self.getToken(pcodeParser.MARK, 0)

        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def mark_name(self):
            return self.getTypedRuleContext(pcodeParser.Mark_nameContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_mark

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMark" ):
                listener.enterMark(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMark" ):
                listener.exitMark(self)




    def mark(self):

        localctx = pcodeParser.MarkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_mark)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 284
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 283
                self.time()


            self.state = 286
            self.match(pcodeParser.MARK)
            self.state = 287
            self.match(pcodeParser.COLON)
            self.state = 291
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,40,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 288
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 293
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,40,self._ctx)

            self.state = 295
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,41,self._ctx)
            if la_ == 1:
                self.state = 294
                self.mark_name()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Mark_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_ext(self):
            return self.getTypedRuleContext(pcodeParser.Identifier_extContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_mark_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMark_name" ):
                listener.enterMark_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMark_name" ):
                listener.exitMark_name(self)




    def mark_name(self):

        localctx = pcodeParser.Mark_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_mark_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 297
            self.identifier_ext()
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
        self.enterRule(localctx, 44, self.RULE_time)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 299
            self.timeexp()
            self.state = 301 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 300
                self.match(pcodeParser.WHITESPACE)
                self.state = 303 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==16):
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

        def POSITIVE_FLOAT(self):
            return self.getToken(pcodeParser.POSITIVE_FLOAT, 0)

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
        self.enterRule(localctx, 46, self.RULE_timeexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 305
            self.match(pcodeParser.POSITIVE_FLOAT)
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
        self.enterRule(localctx, 48, self.RULE_comment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 307
            self.match(pcodeParser.HASH)
            self.state = 308
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
        self.enterRule(localctx, 50, self.RULE_comment_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 313
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,43,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 310
                    self.matchWildcard() 
                self.state = 315
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,43,self._ctx)

            self.state = 316
            _la = self._input.LA(1)
            if _la <= 0 or _la==25:
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
        self.enterRule(localctx, 52, self.RULE_blank)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 321
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,44,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 318
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 323
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,44,self._ctx)

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
        self.enterRule(localctx, 54, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 325
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 324
                self.time()


            self.state = 327
            self.command_name()
            self.state = 336
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==23:
                self.state = 328
                self.match(pcodeParser.COLON)
                self.state = 332
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,46,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 329
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 334
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,46,self._ctx)

                self.state = 335
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

        def identifier(self):
            return self.getTypedRuleContext(pcodeParser.IdentifierContext,0)


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
        self.enterRule(localctx, 56, self.RULE_command_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 338
            self.identifier()
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
        self.enterRule(localctx, 58, self.RULE_command_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 343
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,48,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 340
                    self.matchWildcard() 
                self.state = 345
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,48,self._ctx)

            self.state = 346
            _la = self._input.LA(1)
            if _la <= 0 or _la==22 or _la==25:
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


    class IdentifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(pcodeParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)




    def identifier(self):

        localctx = pcodeParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 348
            self.match(pcodeParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Identifier_extContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(pcodeParser.IDENTIFIER, 0)

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_identifier_ext

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier_ext" ):
                listener.enterIdentifier_ext(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier_ext" ):
                listener.exitIdentifier_ext(self)




    def identifier_ext(self):

        localctx = pcodeParser.Identifier_extContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_identifier_ext)
        self._la = 0 # Token type
        try:
            self.state = 358
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,50,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 350
                self.match(pcodeParser.IDENTIFIER)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 354
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,49,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 351
                        self.matchWildcard() 
                    self.state = 356
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,49,self._ctx)

                self.state = 357
                _la = self._input.LA(1)
                if _la <= 0 or _la==22 or _la==25:
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Inst_errorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_inst_error

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInst_error" ):
                listener.enterInst_error(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInst_error" ):
                listener.exitInst_error(self)




    def inst_error(self):

        localctx = pcodeParser.Inst_errorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_inst_error)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 363
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,51,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 360
                    self.matchWildcard() 
                self.state = 365
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,51,self._ctx)

            self.state = 366
            _la = self._input.LA(1)
            if _la <= 0 or _la==22 or _la==25:
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
        self.enterRule(localctx, 66, self.RULE_error)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 371
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,52,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 368
                    self.matchWildcard() 
                self.state = 373
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,52,self._ctx)

            self.state = 374
            _la = self._input.LA(1)
            if _la <= 0 or _la==22 or _la==25:
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





