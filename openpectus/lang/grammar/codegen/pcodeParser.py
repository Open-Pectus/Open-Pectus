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
        4,1,30,305,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,1,0,1,0,1,0,5,0,66,8,0,10,
        0,12,0,69,9,0,1,0,1,0,1,1,5,1,74,8,1,10,1,12,1,77,9,1,1,1,1,1,5,
        1,81,8,1,10,1,12,1,84,9,1,1,1,3,1,87,8,1,1,2,1,2,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,103,8,2,1,3,3,3,106,8,3,1,3,
        1,3,1,3,5,3,111,8,3,10,3,12,3,114,9,3,1,3,1,3,1,4,1,4,1,5,3,5,121,
        8,5,1,5,1,5,1,6,3,6,126,8,6,1,6,1,6,1,7,3,7,131,8,7,1,7,1,7,1,7,
        5,7,136,8,7,10,7,12,7,139,9,7,1,7,3,7,142,8,7,1,8,3,8,145,8,8,1,
        8,1,8,1,8,5,8,150,8,8,10,8,12,8,153,9,8,1,8,3,8,156,8,8,1,9,1,9,
        5,9,160,8,9,10,9,12,9,163,9,9,1,9,1,9,5,9,167,8,9,10,9,12,9,170,
        9,9,1,9,1,9,5,9,174,8,9,10,9,12,9,177,9,9,1,9,3,9,180,8,9,1,9,5,
        9,183,8,9,10,9,12,9,186,9,9,1,9,3,9,189,8,9,1,10,1,10,1,11,1,11,
        1,12,1,12,1,12,3,12,198,8,12,1,13,1,13,1,14,5,14,203,8,14,10,14,
        12,14,206,9,14,1,14,1,14,1,15,3,15,211,8,15,1,15,1,15,1,16,3,16,
        216,8,16,1,16,1,16,1,17,3,17,221,8,17,1,17,1,17,1,18,3,18,226,8,
        18,1,18,1,18,1,19,3,19,231,8,19,1,19,1,19,1,19,5,19,236,8,19,10,
        19,12,19,239,9,19,1,19,3,19,242,8,19,1,20,1,20,1,21,1,21,4,21,248,
        8,21,11,21,12,21,249,1,22,1,22,1,23,1,23,1,23,1,24,5,24,258,8,24,
        10,24,12,24,261,9,24,1,24,1,24,1,25,5,25,266,8,25,10,25,12,25,269,
        9,25,1,26,3,26,272,8,26,1,26,1,26,1,26,5,26,277,8,26,10,26,12,26,
        280,9,26,1,26,3,26,283,8,26,1,27,1,27,1,28,5,28,288,8,28,10,28,12,
        28,291,9,28,1,28,1,28,1,29,1,29,1,30,5,30,298,8,30,10,30,12,30,301,
        9,30,1,30,1,30,1,30,4,204,259,289,299,0,31,0,2,4,6,8,10,12,14,16,
        18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,
        0,2,2,0,26,26,29,29,1,0,29,29,323,0,62,1,0,0,0,2,75,1,0,0,0,4,102,
        1,0,0,0,6,105,1,0,0,0,8,117,1,0,0,0,10,120,1,0,0,0,12,125,1,0,0,
        0,14,130,1,0,0,0,16,144,1,0,0,0,18,188,1,0,0,0,20,190,1,0,0,0,22,
        192,1,0,0,0,24,197,1,0,0,0,26,199,1,0,0,0,28,204,1,0,0,0,30,210,
        1,0,0,0,32,215,1,0,0,0,34,220,1,0,0,0,36,225,1,0,0,0,38,230,1,0,
        0,0,40,243,1,0,0,0,42,245,1,0,0,0,44,251,1,0,0,0,46,253,1,0,0,0,
        48,259,1,0,0,0,50,267,1,0,0,0,52,271,1,0,0,0,54,284,1,0,0,0,56,289,
        1,0,0,0,58,294,1,0,0,0,60,299,1,0,0,0,62,67,3,2,1,0,63,64,5,29,0,
        0,64,66,3,2,1,0,65,63,1,0,0,0,66,69,1,0,0,0,67,65,1,0,0,0,67,68,
        1,0,0,0,68,70,1,0,0,0,69,67,1,0,0,0,70,71,5,0,0,1,71,1,1,0,0,0,72,
        74,5,20,0,0,73,72,1,0,0,0,74,77,1,0,0,0,75,73,1,0,0,0,75,76,1,0,
        0,0,76,78,1,0,0,0,77,75,1,0,0,0,78,82,3,4,2,0,79,81,5,20,0,0,80,
        79,1,0,0,0,81,84,1,0,0,0,82,80,1,0,0,0,82,83,1,0,0,0,83,86,1,0,0,
        0,84,82,1,0,0,0,85,87,3,46,23,0,86,85,1,0,0,0,86,87,1,0,0,0,87,3,
        1,0,0,0,88,103,3,6,3,0,89,103,3,10,5,0,90,103,3,12,6,0,91,103,3,
        14,7,0,92,103,3,16,8,0,93,103,3,30,15,0,94,103,3,32,16,0,95,103,
        3,34,17,0,96,103,3,36,18,0,97,103,3,38,19,0,98,103,3,52,26,0,99,
        103,3,46,23,0,100,103,3,50,25,0,101,103,3,60,30,0,102,88,1,0,0,0,
        102,89,1,0,0,0,102,90,1,0,0,0,102,91,1,0,0,0,102,92,1,0,0,0,102,
        93,1,0,0,0,102,94,1,0,0,0,102,95,1,0,0,0,102,96,1,0,0,0,102,97,1,
        0,0,0,102,98,1,0,0,0,102,99,1,0,0,0,102,100,1,0,0,0,102,101,1,0,
        0,0,103,5,1,0,0,0,104,106,3,42,21,0,105,104,1,0,0,0,105,106,1,0,
        0,0,106,107,1,0,0,0,107,108,5,7,0,0,108,112,5,27,0,0,109,111,5,20,
        0,0,110,109,1,0,0,0,111,114,1,0,0,0,112,110,1,0,0,0,112,113,1,0,
        0,0,113,115,1,0,0,0,114,112,1,0,0,0,115,116,3,8,4,0,116,7,1,0,0,
        0,117,118,3,58,29,0,118,9,1,0,0,0,119,121,3,42,21,0,120,119,1,0,
        0,0,120,121,1,0,0,0,121,122,1,0,0,0,122,123,5,8,0,0,123,11,1,0,0,
        0,124,126,3,42,21,0,125,124,1,0,0,0,125,126,1,0,0,0,126,127,1,0,
        0,0,127,128,5,9,0,0,128,13,1,0,0,0,129,131,3,42,21,0,130,129,1,0,
        0,0,130,131,1,0,0,0,131,132,1,0,0,0,132,141,5,1,0,0,133,137,5,27,
        0,0,134,136,5,20,0,0,135,134,1,0,0,0,136,139,1,0,0,0,137,135,1,0,
        0,0,137,138,1,0,0,0,138,140,1,0,0,0,139,137,1,0,0,0,140,142,3,18,
        9,0,141,133,1,0,0,0,141,142,1,0,0,0,142,15,1,0,0,0,143,145,3,42,
        21,0,144,143,1,0,0,0,144,145,1,0,0,0,145,146,1,0,0,0,146,155,5,2,
        0,0,147,151,5,27,0,0,148,150,5,20,0,0,149,148,1,0,0,0,150,153,1,
        0,0,0,151,149,1,0,0,0,151,152,1,0,0,0,152,154,1,0,0,0,153,151,1,
        0,0,0,154,156,3,18,9,0,155,147,1,0,0,0,155,156,1,0,0,0,156,17,1,
        0,0,0,157,161,3,20,10,0,158,160,5,20,0,0,159,158,1,0,0,0,160,163,
        1,0,0,0,161,159,1,0,0,0,161,162,1,0,0,0,162,164,1,0,0,0,163,161,
        1,0,0,0,164,168,3,22,11,0,165,167,5,20,0,0,166,165,1,0,0,0,167,170,
        1,0,0,0,168,166,1,0,0,0,168,169,1,0,0,0,169,171,1,0,0,0,170,168,
        1,0,0,0,171,179,3,24,12,0,172,174,5,20,0,0,173,172,1,0,0,0,174,177,
        1,0,0,0,175,173,1,0,0,0,175,176,1,0,0,0,176,178,1,0,0,0,177,175,
        1,0,0,0,178,180,3,26,13,0,179,175,1,0,0,0,179,180,1,0,0,0,180,184,
        1,0,0,0,181,183,5,20,0,0,182,181,1,0,0,0,183,186,1,0,0,0,184,182,
        1,0,0,0,184,185,1,0,0,0,185,189,1,0,0,0,186,184,1,0,0,0,187,189,
        3,28,14,0,188,157,1,0,0,0,188,187,1,0,0,0,189,19,1,0,0,0,190,191,
        3,58,29,0,191,21,1,0,0,0,192,193,5,19,0,0,193,23,1,0,0,0,194,198,
        5,18,0,0,195,196,5,28,0,0,196,198,5,18,0,0,197,194,1,0,0,0,197,195,
        1,0,0,0,198,25,1,0,0,0,199,200,5,11,0,0,200,27,1,0,0,0,201,203,9,
        0,0,0,202,201,1,0,0,0,203,206,1,0,0,0,204,205,1,0,0,0,204,202,1,
        0,0,0,205,207,1,0,0,0,206,204,1,0,0,0,207,208,8,0,0,0,208,29,1,0,
        0,0,209,211,3,42,21,0,210,209,1,0,0,0,210,211,1,0,0,0,211,212,1,
        0,0,0,212,213,5,10,0,0,213,31,1,0,0,0,214,216,3,42,21,0,215,214,
        1,0,0,0,215,216,1,0,0,0,216,217,1,0,0,0,217,218,5,5,0,0,218,33,1,
        0,0,0,219,221,3,42,21,0,220,219,1,0,0,0,220,221,1,0,0,0,221,222,
        1,0,0,0,222,223,5,3,0,0,223,35,1,0,0,0,224,226,3,42,21,0,225,224,
        1,0,0,0,225,226,1,0,0,0,226,227,1,0,0,0,227,228,5,4,0,0,228,37,1,
        0,0,0,229,231,3,42,21,0,230,229,1,0,0,0,230,231,1,0,0,0,231,232,
        1,0,0,0,232,233,5,6,0,0,233,237,5,27,0,0,234,236,5,20,0,0,235,234,
        1,0,0,0,236,239,1,0,0,0,237,235,1,0,0,0,237,238,1,0,0,0,238,241,
        1,0,0,0,239,237,1,0,0,0,240,242,3,40,20,0,241,240,1,0,0,0,241,242,
        1,0,0,0,242,39,1,0,0,0,243,244,3,58,29,0,244,41,1,0,0,0,245,247,
        3,44,22,0,246,248,5,20,0,0,247,246,1,0,0,0,248,249,1,0,0,0,249,247,
        1,0,0,0,249,250,1,0,0,0,250,43,1,0,0,0,251,252,5,18,0,0,252,45,1,
        0,0,0,253,254,5,26,0,0,254,255,3,48,24,0,255,47,1,0,0,0,256,258,
        9,0,0,0,257,256,1,0,0,0,258,261,1,0,0,0,259,260,1,0,0,0,259,257,
        1,0,0,0,260,262,1,0,0,0,261,259,1,0,0,0,262,263,8,1,0,0,263,49,1,
        0,0,0,264,266,5,20,0,0,265,264,1,0,0,0,266,269,1,0,0,0,267,265,1,
        0,0,0,267,268,1,0,0,0,268,51,1,0,0,0,269,267,1,0,0,0,270,272,3,42,
        21,0,271,270,1,0,0,0,271,272,1,0,0,0,272,273,1,0,0,0,273,282,3,54,
        27,0,274,278,5,27,0,0,275,277,5,20,0,0,276,275,1,0,0,0,277,280,1,
        0,0,0,278,276,1,0,0,0,278,279,1,0,0,0,279,281,1,0,0,0,280,278,1,
        0,0,0,281,283,3,56,28,0,282,274,1,0,0,0,282,283,1,0,0,0,283,53,1,
        0,0,0,284,285,3,58,29,0,285,55,1,0,0,0,286,288,9,0,0,0,287,286,1,
        0,0,0,288,291,1,0,0,0,289,290,1,0,0,0,289,287,1,0,0,0,290,292,1,
        0,0,0,291,289,1,0,0,0,292,293,8,0,0,0,293,57,1,0,0,0,294,295,5,17,
        0,0,295,59,1,0,0,0,296,298,9,0,0,0,297,296,1,0,0,0,298,301,1,0,0,
        0,299,300,1,0,0,0,299,297,1,0,0,0,300,302,1,0,0,0,301,299,1,0,0,
        0,302,303,8,0,0,0,303,61,1,0,0,0,38,67,75,82,86,102,105,112,120,
        125,130,137,141,144,151,155,161,168,175,179,184,188,197,204,210,
        215,220,225,230,237,241,249,259,267,271,278,282,289,299
    ]

class pcodeParser ( Parser ):

    grammarFileName = "pcode.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'Watch'", "'Alarm'", "'Stop'", "'Pause'", 
                     "'Restart'", "'Mark'", "'Block'", "'End block'", "'End blocks'", 
                     "'Increment run counter'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'_'", "'.'", "','", "' '", "'\\t'", "'#'", "':'", 
                     "'-'" ]

    symbolicNames = [ "<INVALID>", "WATCH", "ALARM", "STOP", "PAUSE", "RESTART", 
                      "MARK", "BLOCK", "END_BLOCK", "END_BLOCKS", "INCREMENT_RC", 
                      "CONDITION_UNIT", "VOLUME_UNIT", "MASS_UNIT", "DISTANCE_UNIT", 
                      "DURATION_UNIT", "OTHER_UNIT", "IDENTIFIER", "POSITIVE_FLOAT", 
                      "COMPARE_OP", "WHITESPACE", "UNDERSCORE", "PERIOD", 
                      "COMMA", "SPACE", "TAB", "HASH", "COLON", "MINUS", 
                      "NEWLINE", "ANY" ]

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
    RULE_condition_tag = 10
    RULE_compare_op = 11
    RULE_condition_value = 12
    RULE_condition_unit = 13
    RULE_condition_error = 14
    RULE_increment_rc = 15
    RULE_restart = 16
    RULE_stop = 17
    RULE_pause = 18
    RULE_mark = 19
    RULE_mark_name = 20
    RULE_time = 21
    RULE_timeexp = 22
    RULE_comment = 23
    RULE_comment_text = 24
    RULE_blank = 25
    RULE_command = 26
    RULE_command_name = 27
    RULE_command_args = 28
    RULE_identifier = 29
    RULE_error = 30

    ruleNames =  [ "program", "instruction_line", "instruction", "block", 
                   "block_name", "end_block", "end_blocks", "watch", "alarm", 
                   "condition", "condition_tag", "compare_op", "condition_value", 
                   "condition_unit", "condition_error", "increment_rc", 
                   "restart", "stop", "pause", "mark", "mark_name", "time", 
                   "timeexp", "comment", "comment_text", "blank", "command", 
                   "command_name", "command_args", "identifier", "error" ]

    EOF = Token.EOF
    WATCH=1
    ALARM=2
    STOP=3
    PAUSE=4
    RESTART=5
    MARK=6
    BLOCK=7
    END_BLOCK=8
    END_BLOCKS=9
    INCREMENT_RC=10
    CONDITION_UNIT=11
    VOLUME_UNIT=12
    MASS_UNIT=13
    DISTANCE_UNIT=14
    DURATION_UNIT=15
    OTHER_UNIT=16
    IDENTIFIER=17
    POSITIVE_FLOAT=18
    COMPARE_OP=19
    WHITESPACE=20
    UNDERSCORE=21
    PERIOD=22
    COMMA=23
    SPACE=24
    TAB=25
    HASH=26
    COLON=27
    MINUS=28
    NEWLINE=29
    ANY=30

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
            self.state = 62
            self.instruction_line()
            self.state = 67
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==29:
                self.state = 63
                self.match(pcodeParser.NEWLINE)
                self.state = 64
                self.instruction_line()
                self.state = 69
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 70
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
            self.state = 75
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 72
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 77
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 78
            self.instruction()
            self.state = 82
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==20:
                self.state = 79
                self.match(pcodeParser.WHITESPACE)
                self.state = 84
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 86
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==26:
                self.state = 85
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
            self.state = 102
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 88
                self.block()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 89
                self.end_block()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 90
                self.end_blocks()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 91
                self.watch()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 92
                self.alarm()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 93
                self.increment_rc()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 94
                self.restart()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 95
                self.stop()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 96
                self.pause()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 97
                self.mark()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 98
                self.command()
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 99
                self.comment()
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 100
                self.blank()
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 101
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
            self.state = 105
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 104
                self.time()


            self.state = 107
            self.match(pcodeParser.BLOCK)
            self.state = 108
            self.match(pcodeParser.COLON)
            self.state = 112
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==20:
                self.state = 109
                self.match(pcodeParser.WHITESPACE)
                self.state = 114
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 115
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

        def identifier(self):
            return self.getTypedRuleContext(pcodeParser.IdentifierContext,0)


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
            self.state = 117
            self.identifier()
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
            self.state = 120
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 119
                self.time()


            self.state = 122
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
            self.state = 125
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 124
                self.time()


            self.state = 127
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
            self.state = 130
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 129
                self.time()


            self.state = 132
            self.match(pcodeParser.WATCH)
            self.state = 141
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 133
                self.match(pcodeParser.COLON)
                self.state = 137
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,10,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 134
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 139
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                self.state = 140
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
        self.enterRule(localctx, 16, self.RULE_alarm)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 144
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 143
                self.time()


            self.state = 146
            self.match(pcodeParser.ALARM)
            self.state = 155
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 147
                self.match(pcodeParser.COLON)
                self.state = 151
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,13,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 148
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 153
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,13,self._ctx)

                self.state = 154
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

        def condition_tag(self):
            return self.getTypedRuleContext(pcodeParser.Condition_tagContext,0)


        def compare_op(self):
            return self.getTypedRuleContext(pcodeParser.Compare_opContext,0)


        def condition_value(self):
            return self.getTypedRuleContext(pcodeParser.Condition_valueContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def condition_unit(self):
            return self.getTypedRuleContext(pcodeParser.Condition_unitContext,0)


        def condition_error(self):
            return self.getTypedRuleContext(pcodeParser.Condition_errorContext,0)


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
            self.state = 188
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,20,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 157
                self.condition_tag()
                self.state = 161
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==20:
                    self.state = 158
                    self.match(pcodeParser.WHITESPACE)
                    self.state = 163
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 164
                self.compare_op()
                self.state = 168
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==20:
                    self.state = 165
                    self.match(pcodeParser.WHITESPACE)
                    self.state = 170
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 171
                self.condition_value()
                self.state = 179
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
                if la_ == 1:
                    self.state = 175
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==20:
                        self.state = 172
                        self.match(pcodeParser.WHITESPACE)
                        self.state = 177
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)

                    self.state = 178
                    self.condition_unit()


                self.state = 184
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,19,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 181
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 186
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,19,self._ctx)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 187
                self.condition_error()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Condition_tagContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(pcodeParser.IdentifierContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_condition_tag

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition_tag" ):
                listener.enterCondition_tag(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition_tag" ):
                listener.exitCondition_tag(self)




    def condition_tag(self):

        localctx = pcodeParser.Condition_tagContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_condition_tag)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.identifier()
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
        self.enterRule(localctx, 22, self.RULE_compare_op)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 192
            self.match(pcodeParser.COMPARE_OP)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Condition_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def POSITIVE_FLOAT(self):
            return self.getToken(pcodeParser.POSITIVE_FLOAT, 0)

        def MINUS(self):
            return self.getToken(pcodeParser.MINUS, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_condition_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition_value" ):
                listener.enterCondition_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition_value" ):
                listener.exitCondition_value(self)




    def condition_value(self):

        localctx = pcodeParser.Condition_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_condition_value)
        try:
            self.state = 197
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [18]:
                self.enterOuterAlt(localctx, 1)
                self.state = 194
                self.match(pcodeParser.POSITIVE_FLOAT)
                pass
            elif token in [28]:
                self.enterOuterAlt(localctx, 2)
                self.state = 195
                self.match(pcodeParser.MINUS)
                self.state = 196
                self.match(pcodeParser.POSITIVE_FLOAT)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Condition_unitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CONDITION_UNIT(self):
            return self.getToken(pcodeParser.CONDITION_UNIT, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_condition_unit

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition_unit" ):
                listener.enterCondition_unit(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition_unit" ):
                listener.exitCondition_unit(self)




    def condition_unit(self):

        localctx = pcodeParser.Condition_unitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_condition_unit)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 199
            self.match(pcodeParser.CONDITION_UNIT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Condition_errorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(pcodeParser.NEWLINE, 0)

        def HASH(self):
            return self.getToken(pcodeParser.HASH, 0)

        def getRuleIndex(self):
            return pcodeParser.RULE_condition_error

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition_error" ):
                listener.enterCondition_error(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition_error" ):
                listener.exitCondition_error(self)




    def condition_error(self):

        localctx = pcodeParser.Condition_errorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_condition_error)
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
            if _la <= 0 or _la==26 or _la==29:
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
        self.enterRule(localctx, 30, self.RULE_increment_rc)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 210
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
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
        self.enterRule(localctx, 32, self.RULE_restart)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 215
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
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
        self.enterRule(localctx, 34, self.RULE_stop)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
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
        self.enterRule(localctx, 36, self.RULE_pause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 224
                self.time()


            self.state = 227
            self.match(pcodeParser.PAUSE)
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
        self.enterRule(localctx, 38, self.RULE_mark)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 230
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 229
                self.time()


            self.state = 232
            self.match(pcodeParser.MARK)
            self.state = 233
            self.match(pcodeParser.COLON)
            self.state = 237
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,28,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 234
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 239
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,28,self._ctx)

            self.state = 241
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 240
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

        def identifier(self):
            return self.getTypedRuleContext(pcodeParser.IdentifierContext,0)


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
        self.enterRule(localctx, 40, self.RULE_mark_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 243
            self.identifier()
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
        self.enterRule(localctx, 42, self.RULE_time)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 245
            self.timeexp()
            self.state = 247 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 246
                self.match(pcodeParser.WHITESPACE)
                self.state = 249 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==20):
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
        self.enterRule(localctx, 44, self.RULE_timeexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 251
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
        self.enterRule(localctx, 46, self.RULE_comment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 253
            self.match(pcodeParser.HASH)
            self.state = 254
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
        self.enterRule(localctx, 48, self.RULE_comment_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 259
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,31,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 256
                    self.matchWildcard() 
                self.state = 261
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,31,self._ctx)

            self.state = 262
            _la = self._input.LA(1)
            if _la <= 0 or _la==29:
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
        self.enterRule(localctx, 50, self.RULE_blank)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 267
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,32,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 264
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 269
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,32,self._ctx)

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
        self.enterRule(localctx, 52, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 271
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==18:
                self.state = 270
                self.time()


            self.state = 273
            self.command_name()
            self.state = 282
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 274
                self.match(pcodeParser.COLON)
                self.state = 278
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,34,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 275
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 280
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,34,self._ctx)

                self.state = 281
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
        self.enterRule(localctx, 54, self.RULE_command_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 284
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
        self.enterRule(localctx, 56, self.RULE_command_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 289
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,36,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 286
                    self.matchWildcard() 
                self.state = 291
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,36,self._ctx)

            self.state = 292
            _la = self._input.LA(1)
            if _la <= 0 or _la==26 or _la==29:
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
        self.enterRule(localctx, 58, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 294
            self.match(pcodeParser.IDENTIFIER)
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
        self.enterRule(localctx, 60, self.RULE_error)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 299
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,37,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 296
                    self.matchWildcard() 
                self.state = 301
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,37,self._ctx)

            self.state = 302
            _la = self._input.LA(1)
            if _la <= 0 or _la==26 or _la==29:
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





