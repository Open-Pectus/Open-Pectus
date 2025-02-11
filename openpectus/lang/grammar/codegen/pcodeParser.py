# Generated from openpectus/lang/grammar/pcode.g4 by ANTLR 4.13.2
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
        4,1,28,422,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,1,0,1,0,1,0,5,0,80,
        8,0,10,0,12,0,83,9,0,1,0,1,0,1,1,5,1,88,8,1,10,1,12,1,91,9,1,1,1,
        1,1,5,1,95,8,1,10,1,12,1,98,9,1,1,1,3,1,101,8,1,1,2,1,2,1,2,1,2,
        1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,3,2,121,
        8,2,1,3,3,3,124,8,3,1,3,1,3,1,3,5,3,129,8,3,10,3,12,3,132,9,3,1,
        3,3,3,135,8,3,1,3,3,3,138,8,3,1,4,1,4,1,5,3,5,143,8,5,1,5,1,5,1,
        6,3,6,148,8,6,1,6,1,6,1,7,3,7,153,8,7,1,7,1,7,1,7,5,7,158,8,7,10,
        7,12,7,161,9,7,1,7,3,7,164,8,7,1,7,3,7,167,8,7,1,8,3,8,170,8,8,1,
        8,1,8,1,8,5,8,175,8,8,10,8,12,8,178,9,8,1,8,3,8,181,8,8,1,8,3,8,
        184,8,8,1,9,3,9,187,8,9,1,9,1,9,1,9,5,9,192,8,9,10,9,12,9,195,9,
        9,1,9,3,9,198,8,9,1,9,3,9,201,8,9,1,10,1,10,1,11,1,11,5,11,207,8,
        11,10,11,12,11,210,9,11,1,11,1,11,5,11,214,8,11,10,11,12,11,217,
        9,11,1,11,1,11,1,12,1,12,1,13,5,13,224,8,13,10,13,12,13,227,9,13,
        1,13,1,13,1,14,5,14,232,8,14,10,14,12,14,235,9,14,1,14,1,14,1,15,
        3,15,240,8,15,1,15,1,15,1,16,3,16,245,8,16,1,16,1,16,1,17,3,17,250,
        8,17,1,17,1,17,1,18,3,18,255,8,18,1,18,1,18,1,18,5,18,260,8,18,10,
        18,12,18,263,9,18,1,18,3,18,266,8,18,1,18,3,18,269,8,18,1,19,3,19,
        272,8,19,1,19,1,19,1,19,5,19,277,8,19,10,19,12,19,280,9,19,1,19,
        3,19,283,8,19,1,19,3,19,286,8,19,1,20,3,20,289,8,20,1,20,1,20,1,
        20,5,20,294,8,20,10,20,12,20,297,9,20,1,20,3,20,300,8,20,1,20,3,
        20,303,8,20,1,21,5,21,306,8,21,10,21,12,21,309,9,21,1,21,1,21,1,
        22,3,22,314,8,22,1,22,1,22,1,22,5,22,319,8,22,10,22,12,22,322,9,
        22,1,22,3,22,325,8,22,1,23,1,23,1,24,3,24,330,8,24,1,24,1,24,1,24,
        5,24,335,8,24,10,24,12,24,338,9,24,1,24,3,24,341,8,24,1,25,1,25,
        1,26,1,26,4,26,347,8,26,11,26,12,26,348,1,27,1,27,1,28,1,28,1,28,
        1,29,5,29,357,8,29,10,29,12,29,360,9,29,1,29,1,29,1,30,5,30,365,
        8,30,10,30,12,30,368,9,30,1,31,3,31,371,8,31,1,31,1,31,1,31,5,31,
        376,8,31,10,31,12,31,379,9,31,1,31,3,31,382,8,31,1,32,1,32,1,33,
        5,33,387,8,33,10,33,12,33,390,9,33,1,33,1,33,1,34,1,34,1,35,1,35,
        5,35,398,8,35,10,35,12,35,401,9,35,1,35,3,35,404,8,35,1,36,5,36,
        407,8,36,10,36,12,36,410,9,36,1,36,1,36,1,37,5,37,415,8,37,10,37,
        12,37,418,9,37,1,37,1,37,1,37,8,225,233,307,358,388,399,408,416,
        0,38,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,
        44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,0,4,3,0,17,17,24,
        25,27,27,2,0,24,25,27,27,1,0,27,27,2,0,24,24,27,27,459,0,76,1,0,
        0,0,2,89,1,0,0,0,4,120,1,0,0,0,6,123,1,0,0,0,8,139,1,0,0,0,10,142,
        1,0,0,0,12,147,1,0,0,0,14,152,1,0,0,0,16,169,1,0,0,0,18,186,1,0,
        0,0,20,202,1,0,0,0,22,204,1,0,0,0,24,220,1,0,0,0,26,225,1,0,0,0,
        28,233,1,0,0,0,30,239,1,0,0,0,32,244,1,0,0,0,34,249,1,0,0,0,36,254,
        1,0,0,0,38,271,1,0,0,0,40,288,1,0,0,0,42,307,1,0,0,0,44,313,1,0,
        0,0,46,326,1,0,0,0,48,329,1,0,0,0,50,342,1,0,0,0,52,344,1,0,0,0,
        54,350,1,0,0,0,56,352,1,0,0,0,58,358,1,0,0,0,60,366,1,0,0,0,62,370,
        1,0,0,0,64,383,1,0,0,0,66,388,1,0,0,0,68,393,1,0,0,0,70,403,1,0,
        0,0,72,408,1,0,0,0,74,416,1,0,0,0,76,81,3,2,1,0,77,78,5,27,0,0,78,
        80,3,2,1,0,79,77,1,0,0,0,80,83,1,0,0,0,81,79,1,0,0,0,81,82,1,0,0,
        0,82,84,1,0,0,0,83,81,1,0,0,0,84,85,5,0,0,1,85,1,1,0,0,0,86,88,5,
        18,0,0,87,86,1,0,0,0,88,91,1,0,0,0,89,87,1,0,0,0,89,90,1,0,0,0,90,
        92,1,0,0,0,91,89,1,0,0,0,92,96,3,4,2,0,93,95,5,18,0,0,94,93,1,0,
        0,0,95,98,1,0,0,0,96,94,1,0,0,0,96,97,1,0,0,0,97,100,1,0,0,0,98,
        96,1,0,0,0,99,101,3,56,28,0,100,99,1,0,0,0,100,101,1,0,0,0,101,3,
        1,0,0,0,102,121,3,6,3,0,103,121,3,10,5,0,104,121,3,12,6,0,105,121,
        3,14,7,0,106,121,3,16,8,0,107,121,3,18,9,0,108,121,3,48,24,0,109,
        121,3,30,15,0,110,121,3,32,16,0,111,121,3,34,17,0,112,121,3,36,18,
        0,113,121,3,38,19,0,114,121,3,40,20,0,115,121,3,44,22,0,116,121,
        3,62,31,0,117,121,3,56,28,0,118,121,3,60,30,0,119,121,3,74,37,0,
        120,102,1,0,0,0,120,103,1,0,0,0,120,104,1,0,0,0,120,105,1,0,0,0,
        120,106,1,0,0,0,120,107,1,0,0,0,120,108,1,0,0,0,120,109,1,0,0,0,
        120,110,1,0,0,0,120,111,1,0,0,0,120,112,1,0,0,0,120,113,1,0,0,0,
        120,114,1,0,0,0,120,115,1,0,0,0,120,116,1,0,0,0,120,117,1,0,0,0,
        120,118,1,0,0,0,120,119,1,0,0,0,121,5,1,0,0,0,122,124,3,52,26,0,
        123,122,1,0,0,0,123,124,1,0,0,0,124,125,1,0,0,0,125,137,5,11,0,0,
        126,130,5,25,0,0,127,129,5,18,0,0,128,127,1,0,0,0,129,132,1,0,0,
        0,130,128,1,0,0,0,130,131,1,0,0,0,131,133,1,0,0,0,132,130,1,0,0,
        0,133,135,3,8,4,0,134,126,1,0,0,0,134,135,1,0,0,0,135,138,1,0,0,
        0,136,138,3,72,36,0,137,134,1,0,0,0,137,136,1,0,0,0,138,7,1,0,0,
        0,139,140,3,70,35,0,140,9,1,0,0,0,141,143,3,52,26,0,142,141,1,0,
        0,0,142,143,1,0,0,0,143,144,1,0,0,0,144,145,5,12,0,0,145,11,1,0,
        0,0,146,148,3,52,26,0,147,146,1,0,0,0,147,148,1,0,0,0,148,149,1,
        0,0,0,149,150,5,13,0,0,150,13,1,0,0,0,151,153,3,52,26,0,152,151,
        1,0,0,0,152,153,1,0,0,0,153,154,1,0,0,0,154,166,5,1,0,0,155,159,
        5,25,0,0,156,158,5,18,0,0,157,156,1,0,0,0,158,161,1,0,0,0,159,157,
        1,0,0,0,159,160,1,0,0,0,160,162,1,0,0,0,161,159,1,0,0,0,162,164,
        3,22,11,0,163,155,1,0,0,0,163,164,1,0,0,0,164,167,1,0,0,0,165,167,
        3,72,36,0,166,163,1,0,0,0,166,165,1,0,0,0,167,15,1,0,0,0,168,170,
        3,52,26,0,169,168,1,0,0,0,169,170,1,0,0,0,170,171,1,0,0,0,171,183,
        5,2,0,0,172,176,5,25,0,0,173,175,5,18,0,0,174,173,1,0,0,0,175,178,
        1,0,0,0,176,174,1,0,0,0,176,177,1,0,0,0,177,179,1,0,0,0,178,176,
        1,0,0,0,179,181,3,22,11,0,180,172,1,0,0,0,180,181,1,0,0,0,181,184,
        1,0,0,0,182,184,3,72,36,0,183,180,1,0,0,0,183,182,1,0,0,0,184,17,
        1,0,0,0,185,187,3,52,26,0,186,185,1,0,0,0,186,187,1,0,0,0,187,188,
        1,0,0,0,188,200,5,3,0,0,189,193,5,25,0,0,190,192,5,18,0,0,191,190,
        1,0,0,0,192,195,1,0,0,0,193,191,1,0,0,0,193,194,1,0,0,0,194,196,
        1,0,0,0,195,193,1,0,0,0,196,198,3,20,10,0,197,189,1,0,0,0,197,198,
        1,0,0,0,198,201,1,0,0,0,199,201,3,72,36,0,200,197,1,0,0,0,200,199,
        1,0,0,0,201,19,1,0,0,0,202,203,3,70,35,0,203,21,1,0,0,0,204,208,
        3,26,13,0,205,207,5,18,0,0,206,205,1,0,0,0,207,210,1,0,0,0,208,206,
        1,0,0,0,208,209,1,0,0,0,209,211,1,0,0,0,210,208,1,0,0,0,211,215,
        3,24,12,0,212,214,5,18,0,0,213,212,1,0,0,0,214,217,1,0,0,0,215,213,
        1,0,0,0,215,216,1,0,0,0,216,218,1,0,0,0,217,215,1,0,0,0,218,219,
        3,28,14,0,219,23,1,0,0,0,220,221,5,17,0,0,221,25,1,0,0,0,222,224,
        9,0,0,0,223,222,1,0,0,0,224,227,1,0,0,0,225,226,1,0,0,0,225,223,
        1,0,0,0,226,228,1,0,0,0,227,225,1,0,0,0,228,229,8,0,0,0,229,27,1,
        0,0,0,230,232,9,0,0,0,231,230,1,0,0,0,232,235,1,0,0,0,233,234,1,
        0,0,0,233,231,1,0,0,0,234,236,1,0,0,0,235,233,1,0,0,0,236,237,8,
        0,0,0,237,29,1,0,0,0,238,240,3,52,26,0,239,238,1,0,0,0,239,240,1,
        0,0,0,240,241,1,0,0,0,241,242,5,14,0,0,242,31,1,0,0,0,243,245,3,
        52,26,0,244,243,1,0,0,0,244,245,1,0,0,0,245,246,1,0,0,0,246,247,
        5,8,0,0,247,33,1,0,0,0,248,250,3,52,26,0,249,248,1,0,0,0,249,250,
        1,0,0,0,250,251,1,0,0,0,251,252,5,4,0,0,252,35,1,0,0,0,253,255,3,
        52,26,0,254,253,1,0,0,0,254,255,1,0,0,0,255,256,1,0,0,0,256,268,
        5,5,0,0,257,261,5,25,0,0,258,260,5,18,0,0,259,258,1,0,0,0,260,263,
        1,0,0,0,261,259,1,0,0,0,261,262,1,0,0,0,262,264,1,0,0,0,263,261,
        1,0,0,0,264,266,3,42,21,0,265,257,1,0,0,0,265,266,1,0,0,0,266,269,
        1,0,0,0,267,269,3,72,36,0,268,265,1,0,0,0,268,267,1,0,0,0,269,37,
        1,0,0,0,270,272,3,52,26,0,271,270,1,0,0,0,271,272,1,0,0,0,272,273,
        1,0,0,0,273,285,5,6,0,0,274,278,5,25,0,0,275,277,5,18,0,0,276,275,
        1,0,0,0,277,280,1,0,0,0,278,276,1,0,0,0,278,279,1,0,0,0,279,281,
        1,0,0,0,280,278,1,0,0,0,281,283,3,42,21,0,282,274,1,0,0,0,282,283,
        1,0,0,0,283,286,1,0,0,0,284,286,3,72,36,0,285,282,1,0,0,0,285,284,
        1,0,0,0,286,39,1,0,0,0,287,289,3,52,26,0,288,287,1,0,0,0,288,289,
        1,0,0,0,289,290,1,0,0,0,290,302,5,7,0,0,291,295,5,25,0,0,292,294,
        5,18,0,0,293,292,1,0,0,0,294,297,1,0,0,0,295,293,1,0,0,0,295,296,
        1,0,0,0,296,298,1,0,0,0,297,295,1,0,0,0,298,300,3,42,21,0,299,291,
        1,0,0,0,299,300,1,0,0,0,300,303,1,0,0,0,301,303,3,72,36,0,302,299,
        1,0,0,0,302,301,1,0,0,0,303,41,1,0,0,0,304,306,9,0,0,0,305,304,1,
        0,0,0,306,309,1,0,0,0,307,308,1,0,0,0,307,305,1,0,0,0,308,310,1,
        0,0,0,309,307,1,0,0,0,310,311,8,1,0,0,311,43,1,0,0,0,312,314,3,52,
        26,0,313,312,1,0,0,0,313,314,1,0,0,0,314,315,1,0,0,0,315,316,5,9,
        0,0,316,320,5,25,0,0,317,319,5,18,0,0,318,317,1,0,0,0,319,322,1,
        0,0,0,320,318,1,0,0,0,320,321,1,0,0,0,321,324,1,0,0,0,322,320,1,
        0,0,0,323,325,3,46,23,0,324,323,1,0,0,0,324,325,1,0,0,0,325,45,1,
        0,0,0,326,327,3,70,35,0,327,47,1,0,0,0,328,330,3,52,26,0,329,328,
        1,0,0,0,329,330,1,0,0,0,330,331,1,0,0,0,331,332,5,10,0,0,332,336,
        5,25,0,0,333,335,5,18,0,0,334,333,1,0,0,0,335,338,1,0,0,0,336,334,
        1,0,0,0,336,337,1,0,0,0,337,340,1,0,0,0,338,336,1,0,0,0,339,341,
        3,50,25,0,340,339,1,0,0,0,340,341,1,0,0,0,341,49,1,0,0,0,342,343,
        3,70,35,0,343,51,1,0,0,0,344,346,3,54,27,0,345,347,5,18,0,0,346,
        345,1,0,0,0,347,348,1,0,0,0,348,346,1,0,0,0,348,349,1,0,0,0,349,
        53,1,0,0,0,350,351,5,16,0,0,351,55,1,0,0,0,352,353,5,24,0,0,353,
        354,3,58,29,0,354,57,1,0,0,0,355,357,9,0,0,0,356,355,1,0,0,0,357,
        360,1,0,0,0,358,359,1,0,0,0,358,356,1,0,0,0,359,361,1,0,0,0,360,
        358,1,0,0,0,361,362,8,2,0,0,362,59,1,0,0,0,363,365,5,18,0,0,364,
        363,1,0,0,0,365,368,1,0,0,0,366,364,1,0,0,0,366,367,1,0,0,0,367,
        61,1,0,0,0,368,366,1,0,0,0,369,371,3,52,26,0,370,369,1,0,0,0,370,
        371,1,0,0,0,371,372,1,0,0,0,372,381,3,64,32,0,373,377,5,25,0,0,374,
        376,5,18,0,0,375,374,1,0,0,0,376,379,1,0,0,0,377,375,1,0,0,0,377,
        378,1,0,0,0,378,380,1,0,0,0,379,377,1,0,0,0,380,382,3,66,33,0,381,
        373,1,0,0,0,381,382,1,0,0,0,382,63,1,0,0,0,383,384,3,68,34,0,384,
        65,1,0,0,0,385,387,9,0,0,0,386,385,1,0,0,0,387,390,1,0,0,0,388,389,
        1,0,0,0,388,386,1,0,0,0,389,391,1,0,0,0,390,388,1,0,0,0,391,392,
        8,3,0,0,392,67,1,0,0,0,393,394,5,15,0,0,394,69,1,0,0,0,395,404,5,
        15,0,0,396,398,9,0,0,0,397,396,1,0,0,0,398,401,1,0,0,0,399,400,1,
        0,0,0,399,397,1,0,0,0,400,402,1,0,0,0,401,399,1,0,0,0,402,404,8,
        3,0,0,403,395,1,0,0,0,403,399,1,0,0,0,404,71,1,0,0,0,405,407,9,0,
        0,0,406,405,1,0,0,0,407,410,1,0,0,0,408,409,1,0,0,0,408,406,1,0,
        0,0,409,411,1,0,0,0,410,408,1,0,0,0,411,412,8,3,0,0,412,73,1,0,0,
        0,413,415,9,0,0,0,414,413,1,0,0,0,415,418,1,0,0,0,416,417,1,0,0,
        0,416,414,1,0,0,0,417,419,1,0,0,0,418,416,1,0,0,0,419,420,8,3,0,
        0,420,75,1,0,0,0,60,81,89,96,100,120,123,130,134,137,142,147,152,
        159,163,166,169,176,180,183,186,193,197,200,208,215,225,233,239,
        244,249,254,261,265,268,271,278,282,285,288,295,299,302,307,313,
        320,324,329,336,340,348,358,366,370,377,381,388,399,403,408,416
    ]

class pcodeParser ( Parser ):

    grammarFileName = "pcode.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'Watch'", "'Alarm'", "'Macro'", "'Stop'", 
                     "'Pause'", "'Hold'", "'Wait'", "'Restart'", "'Mark'", 
                     "'Call macro'", "'Block'", "'End block'", "'End blocks'", 
                     "'Increment run counter'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "'_'", "'.'", "','", "' '", 
                     "'\\t'", "'#'", "':'", "'-'" ]

    symbolicNames = [ "<INVALID>", "WATCH", "ALARM", "MACRO", "STOP", "PAUSE", 
                      "HOLD", "WAIT", "RESTART", "MARK", "CALL_MACRO", "BLOCK", 
                      "END_BLOCK", "END_BLOCKS", "INCREMENT_RC", "IDENTIFIER", 
                      "POSITIVE_FLOAT", "COMPARE_OP", "WHITESPACE", "UNDERSCORE", 
                      "PERIOD", "COMMA", "SPACE", "TAB", "HASH", "COLON", 
                      "MINUS", "NEWLINE", "ANY" ]

    RULE_program = 0
    RULE_instruction_line = 1
    RULE_instruction = 2
    RULE_block = 3
    RULE_block_name = 4
    RULE_end_block = 5
    RULE_end_blocks = 6
    RULE_watch = 7
    RULE_alarm = 8
    RULE_macro = 9
    RULE_macro_name = 10
    RULE_condition = 11
    RULE_compare_op = 12
    RULE_condition_lhs = 13
    RULE_condition_rhs = 14
    RULE_increment_rc = 15
    RULE_restart = 16
    RULE_stop = 17
    RULE_pause = 18
    RULE_hold = 19
    RULE_wait = 20
    RULE_duration = 21
    RULE_mark = 22
    RULE_mark_name = 23
    RULE_call_macro = 24
    RULE_call_macro_name = 25
    RULE_time = 26
    RULE_timeexp = 27
    RULE_comment = 28
    RULE_comment_text = 29
    RULE_blank = 30
    RULE_command = 31
    RULE_command_name = 32
    RULE_command_args = 33
    RULE_identifier = 34
    RULE_identifier_ext = 35
    RULE_inst_error = 36
    RULE_error = 37

    ruleNames =  [ "program", "instruction_line", "instruction", "block", 
                   "block_name", "end_block", "end_blocks", "watch", "alarm", 
                   "macro", "macro_name", "condition", "compare_op", "condition_lhs", 
                   "condition_rhs", "increment_rc", "restart", "stop", "pause", 
                   "hold", "wait", "duration", "mark", "mark_name", "call_macro", 
                   "call_macro_name", "time", "timeexp", "comment", "comment_text", 
                   "blank", "command", "command_name", "command_args", "identifier", 
                   "identifier_ext", "inst_error", "error" ]

    EOF = Token.EOF
    WATCH=1
    ALARM=2
    MACRO=3
    STOP=4
    PAUSE=5
    HOLD=6
    WAIT=7
    RESTART=8
    MARK=9
    CALL_MACRO=10
    BLOCK=11
    END_BLOCK=12
    END_BLOCKS=13
    INCREMENT_RC=14
    IDENTIFIER=15
    POSITIVE_FLOAT=16
    COMPARE_OP=17
    WHITESPACE=18
    UNDERSCORE=19
    PERIOD=20
    COMMA=21
    SPACE=22
    TAB=23
    HASH=24
    COLON=25
    MINUS=26
    NEWLINE=27
    ANY=28

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
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
            self.state = 76
            self.instruction_line()
            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==27:
                self.state = 77
                self.match(pcodeParser.NEWLINE)
                self.state = 78
                self.instruction_line()
                self.state = 83
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 84
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
            self.state = 89
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 86
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 91
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

            self.state = 92
            self.instruction()
            self.state = 96
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==18:
                self.state = 93
                self.match(pcodeParser.WHITESPACE)
                self.state = 98
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 100
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==24:
                self.state = 99
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


        def macro(self):
            return self.getTypedRuleContext(pcodeParser.MacroContext,0)


        def call_macro(self):
            return self.getTypedRuleContext(pcodeParser.Call_macroContext,0)


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
            self.state = 120
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 102
                self.block()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 103
                self.end_block()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 104
                self.end_blocks()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 105
                self.watch()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 106
                self.alarm()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 107
                self.macro()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 108
                self.call_macro()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 109
                self.increment_rc()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 110
                self.restart()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 111
                self.stop()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 112
                self.pause()
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 113
                self.hold()
                pass

            elif la_ == 13:
                self.enterOuterAlt(localctx, 13)
                self.state = 114
                self.wait()
                pass

            elif la_ == 14:
                self.enterOuterAlt(localctx, 14)
                self.state = 115
                self.mark()
                pass

            elif la_ == 15:
                self.enterOuterAlt(localctx, 15)
                self.state = 116
                self.command()
                pass

            elif la_ == 16:
                self.enterOuterAlt(localctx, 16)
                self.state = 117
                self.comment()
                pass

            elif la_ == 17:
                self.enterOuterAlt(localctx, 17)
                self.state = 118
                self.blank()
                pass

            elif la_ == 18:
                self.enterOuterAlt(localctx, 18)
                self.state = 119
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
            self.state = 123
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 122
                self.time()


            self.state = 125
            self.match(pcodeParser.BLOCK)
            self.state = 137
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 134
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 126
                    self.match(pcodeParser.COLON)
                    self.state = 130
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 127
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 132
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                    self.state = 133
                    self.block_name()


                pass

            elif la_ == 2:
                self.state = 136
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
            self.state = 139
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
            self.state = 142
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 141
                self.time()


            self.state = 144
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
            self.state = 147
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 146
                self.time()


            self.state = 149
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
            self.state = 152
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 151
                self.time()


            self.state = 154
            self.match(pcodeParser.WATCH)
            self.state = 166
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                self.state = 163
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 155
                    self.match(pcodeParser.COLON)
                    self.state = 159
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 156
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 161
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

                    self.state = 162
                    self.condition()


                pass

            elif la_ == 2:
                self.state = 165
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
            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 168
                self.time()


            self.state = 171
            self.match(pcodeParser.ALARM)
            self.state = 183
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
            if la_ == 1:
                self.state = 180
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 172
                    self.match(pcodeParser.COLON)
                    self.state = 176
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 173
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 178
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

                    self.state = 179
                    self.condition()


                pass

            elif la_ == 2:
                self.state = 182
                self.inst_error()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MacroContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MACRO(self):
            return self.getToken(pcodeParser.MACRO, 0)

        def inst_error(self):
            return self.getTypedRuleContext(pcodeParser.Inst_errorContext,0)


        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def macro_name(self):
            return self.getTypedRuleContext(pcodeParser.Macro_nameContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def getRuleIndex(self):
            return pcodeParser.RULE_macro

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMacro" ):
                listener.enterMacro(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMacro" ):
                listener.exitMacro(self)




    def macro(self):

        localctx = pcodeParser.MacroContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_macro)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 186
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 185
                self.time()


            self.state = 188
            self.match(pcodeParser.MACRO)
            self.state = 200
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,22,self._ctx)
            if la_ == 1:
                self.state = 197
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 189
                    self.match(pcodeParser.COLON)
                    self.state = 193
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,20,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 190
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 195
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

                    self.state = 196
                    self.macro_name()


                pass

            elif la_ == 2:
                self.state = 199
                self.inst_error()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Macro_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_ext(self):
            return self.getTypedRuleContext(pcodeParser.Identifier_extContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_macro_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMacro_name" ):
                listener.enterMacro_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMacro_name" ):
                listener.exitMacro_name(self)




    def macro_name(self):

        localctx = pcodeParser.Macro_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_macro_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 202
            self.identifier_ext()
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
        self.enterRule(localctx, 22, self.RULE_condition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 204
            self.condition_lhs()
            self.state = 208
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==18:
                self.state = 205
                self.match(pcodeParser.WHITESPACE)
                self.state = 210
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 211
            self.compare_op()
            self.state = 215
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,24,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 212
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 217
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,24,self._ctx)

            self.state = 218
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
        self.enterRule(localctx, 24, self.RULE_compare_op)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
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
        self.enterRule(localctx, 26, self.RULE_condition_lhs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,25,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 222
                    self.matchWildcard() 
                self.state = 227
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,25,self._ctx)

            self.state = 228
            _la = self._input.LA(1)
            if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 184680448) != 0):
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
        self.enterRule(localctx, 28, self.RULE_condition_rhs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 233
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,26,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 230
                    self.matchWildcard() 
                self.state = 235
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,26,self._ctx)

            self.state = 236
            _la = self._input.LA(1)
            if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 184680448) != 0):
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
            self.state = 239
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 238
                self.time()


            self.state = 241
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
            self.state = 244
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 243
                self.time()


            self.state = 246
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
            self.state = 249
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 248
                self.time()


            self.state = 251
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
        self.enterRule(localctx, 36, self.RULE_pause)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 254
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 253
                self.time()


            self.state = 256
            self.match(pcodeParser.PAUSE)
            self.state = 268
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                self.state = 265
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 257
                    self.match(pcodeParser.COLON)
                    self.state = 261
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,31,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 258
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 263
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,31,self._ctx)

                    self.state = 264
                    self.duration()


                pass

            elif la_ == 2:
                self.state = 267
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
        self.enterRule(localctx, 38, self.RULE_hold)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 271
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 270
                self.time()


            self.state = 273
            self.match(pcodeParser.HOLD)
            self.state = 285
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,37,self._ctx)
            if la_ == 1:
                self.state = 282
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 274
                    self.match(pcodeParser.COLON)
                    self.state = 278
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,35,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 275
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 280
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,35,self._ctx)

                    self.state = 281
                    self.duration()


                pass

            elif la_ == 2:
                self.state = 284
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
        self.enterRule(localctx, 40, self.RULE_wait)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 288
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 287
                self.time()


            self.state = 290
            self.match(pcodeParser.WAIT)
            self.state = 302
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,41,self._ctx)
            if la_ == 1:
                self.state = 299
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==25:
                    self.state = 291
                    self.match(pcodeParser.COLON)
                    self.state = 295
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,39,self._ctx)
                    while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                        if _alt==1:
                            self.state = 292
                            self.match(pcodeParser.WHITESPACE) 
                        self.state = 297
                        self._errHandler.sync(self)
                        _alt = self._interp.adaptivePredict(self._input,39,self._ctx)

                    self.state = 298
                    self.duration()


                pass

            elif la_ == 2:
                self.state = 301
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
        self.enterRule(localctx, 42, self.RULE_duration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 307
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,42,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 304
                    self.matchWildcard() 
                self.state = 309
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,42,self._ctx)

            self.state = 310
            _la = self._input.LA(1)
            if _la <= 0 or (((_la) & ~0x3f) == 0 and ((1 << _la) & 184549376) != 0):
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
        self.enterRule(localctx, 44, self.RULE_mark)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 313
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 312
                self.time()


            self.state = 315
            self.match(pcodeParser.MARK)
            self.state = 316
            self.match(pcodeParser.COLON)
            self.state = 320
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,44,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 317
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 322
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,44,self._ctx)

            self.state = 324
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,45,self._ctx)
            if la_ == 1:
                self.state = 323
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
        self.enterRule(localctx, 46, self.RULE_mark_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 326
            self.identifier_ext()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Call_macroContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CALL_MACRO(self):
            return self.getToken(pcodeParser.CALL_MACRO, 0)

        def COLON(self):
            return self.getToken(pcodeParser.COLON, 0)

        def time(self):
            return self.getTypedRuleContext(pcodeParser.TimeContext,0)


        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(pcodeParser.WHITESPACE)
            else:
                return self.getToken(pcodeParser.WHITESPACE, i)

        def call_macro_name(self):
            return self.getTypedRuleContext(pcodeParser.Call_macro_nameContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_call_macro

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCall_macro" ):
                listener.enterCall_macro(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCall_macro" ):
                listener.exitCall_macro(self)




    def call_macro(self):

        localctx = pcodeParser.Call_macroContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_call_macro)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 329
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 328
                self.time()


            self.state = 331
            self.match(pcodeParser.CALL_MACRO)
            self.state = 332
            self.match(pcodeParser.COLON)
            self.state = 336
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,47,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 333
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 338
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,47,self._ctx)

            self.state = 340
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,48,self._ctx)
            if la_ == 1:
                self.state = 339
                self.call_macro_name()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Call_macro_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_ext(self):
            return self.getTypedRuleContext(pcodeParser.Identifier_extContext,0)


        def getRuleIndex(self):
            return pcodeParser.RULE_call_macro_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCall_macro_name" ):
                listener.enterCall_macro_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCall_macro_name" ):
                listener.exitCall_macro_name(self)




    def call_macro_name(self):

        localctx = pcodeParser.Call_macro_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_call_macro_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 342
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
        self.enterRule(localctx, 52, self.RULE_time)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 344
            self.timeexp()
            self.state = 346 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 345
                self.match(pcodeParser.WHITESPACE)
                self.state = 348 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==18):
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
        self.enterRule(localctx, 54, self.RULE_timeexp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 350
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
        self.enterRule(localctx, 56, self.RULE_comment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 352
            self.match(pcodeParser.HASH)
            self.state = 353
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
        self.enterRule(localctx, 58, self.RULE_comment_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 358
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,50,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 355
                    self.matchWildcard() 
                self.state = 360
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,50,self._ctx)

            self.state = 361
            _la = self._input.LA(1)
            if _la <= 0 or _la==27:
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
        self.enterRule(localctx, 60, self.RULE_blank)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 366
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,51,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 363
                    self.match(pcodeParser.WHITESPACE) 
                self.state = 368
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,51,self._ctx)

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
        self.enterRule(localctx, 62, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 370
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 369
                self.time()


            self.state = 372
            self.command_name()
            self.state = 381
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==25:
                self.state = 373
                self.match(pcodeParser.COLON)
                self.state = 377
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,53,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 374
                        self.match(pcodeParser.WHITESPACE) 
                    self.state = 379
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,53,self._ctx)

                self.state = 380
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
        self.enterRule(localctx, 64, self.RULE_command_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 383
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
        self.enterRule(localctx, 66, self.RULE_command_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 388
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,55,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 385
                    self.matchWildcard() 
                self.state = 390
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,55,self._ctx)

            self.state = 391
            _la = self._input.LA(1)
            if _la <= 0 or _la==24 or _la==27:
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
        self.enterRule(localctx, 68, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 393
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
        self.enterRule(localctx, 70, self.RULE_identifier_ext)
        self._la = 0 # Token type
        try:
            self.state = 403
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,57,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 395
                self.match(pcodeParser.IDENTIFIER)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 399
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,56,self._ctx)
                while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1+1:
                        self.state = 396
                        self.matchWildcard() 
                    self.state = 401
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,56,self._ctx)

                self.state = 402
                _la = self._input.LA(1)
                if _la <= 0 or _la==24 or _la==27:
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
        self.enterRule(localctx, 72, self.RULE_inst_error)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 408
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,58,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 405
                    self.matchWildcard() 
                self.state = 410
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,58,self._ctx)

            self.state = 411
            _la = self._input.LA(1)
            if _la <= 0 or _la==24 or _la==27:
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
        self.enterRule(localctx, 74, self.RULE_error)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 416
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,59,self._ctx)
            while _alt!=1 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1+1:
                    self.state = 413
                    self.matchWildcard() 
                self.state = 418
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,59,self._ctx)

            self.state = 419
            _la = self._input.LA(1)
            if _la <= 0 or _la==24 or _la==27:
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





