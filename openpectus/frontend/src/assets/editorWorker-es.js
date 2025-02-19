var L;
(function(e) {
  e[e.Null = 0] = "Null", e[e.Backspace = 8] = "Backspace", e[e.Tab = 9] = "Tab", e[e.LineFeed = 10] = "LineFeed", e[e.CarriageReturn = 13] = "CarriageReturn", e[e.Space = 32] = "Space", e[e.ExclamationMark = 33] = "ExclamationMark", e[e.DoubleQuote = 34] = "DoubleQuote", e[e.Hash = 35] = "Hash", e[e.DollarSign = 36] = "DollarSign", e[e.PercentSign = 37] = "PercentSign", e[e.Ampersand = 38] = "Ampersand", e[e.SingleQuote = 39] = "SingleQuote", e[e.OpenParen = 40] = "OpenParen", e[e.CloseParen = 41] = "CloseParen", e[e.Asterisk = 42] = "Asterisk", e[e.Plus = 43] = "Plus", e[e.Comma = 44] = "Comma", e[e.Dash = 45] = "Dash", e[e.Period = 46] = "Period", e[e.Slash = 47] = "Slash", e[e.Digit0 = 48] = "Digit0", e[e.Digit1 = 49] = "Digit1", e[e.Digit2 = 50] = "Digit2", e[e.Digit3 = 51] = "Digit3", e[e.Digit4 = 52] = "Digit4", e[e.Digit5 = 53] = "Digit5", e[e.Digit6 = 54] = "Digit6", e[e.Digit7 = 55] = "Digit7", e[e.Digit8 = 56] = "Digit8", e[e.Digit9 = 57] = "Digit9", e[e.Colon = 58] = "Colon", e[e.Semicolon = 59] = "Semicolon", e[e.LessThan = 60] = "LessThan", e[e.Equals = 61] = "Equals", e[e.GreaterThan = 62] = "GreaterThan", e[e.QuestionMark = 63] = "QuestionMark", e[e.AtSign = 64] = "AtSign", e[e.A = 65] = "A", e[e.B = 66] = "B", e[e.C = 67] = "C", e[e.D = 68] = "D", e[e.E = 69] = "E", e[e.F = 70] = "F", e[e.G = 71] = "G", e[e.H = 72] = "H", e[e.I = 73] = "I", e[e.J = 74] = "J", e[e.K = 75] = "K", e[e.L = 76] = "L", e[e.M = 77] = "M", e[e.N = 78] = "N", e[e.O = 79] = "O", e[e.P = 80] = "P", e[e.Q = 81] = "Q", e[e.R = 82] = "R", e[e.S = 83] = "S", e[e.T = 84] = "T", e[e.U = 85] = "U", e[e.V = 86] = "V", e[e.W = 87] = "W", e[e.X = 88] = "X", e[e.Y = 89] = "Y", e[e.Z = 90] = "Z", e[e.OpenSquareBracket = 91] = "OpenSquareBracket", e[e.Backslash = 92] = "Backslash", e[e.CloseSquareBracket = 93] = "CloseSquareBracket", e[e.Caret = 94] = "Caret", e[e.Underline = 95] = "Underline", e[e.BackTick = 96] = "BackTick", e[e.a = 97] = "a", e[e.b = 98] = "b", e[e.c = 99] = "c", e[e.d = 100] = "d", e[e.e = 101] = "e", e[e.f = 102] = "f", e[e.g = 103] = "g", e[e.h = 104] = "h", e[e.i = 105] = "i", e[e.j = 106] = "j", e[e.k = 107] = "k", e[e.l = 108] = "l", e[e.m = 109] = "m", e[e.n = 110] = "n", e[e.o = 111] = "o", e[e.p = 112] = "p", e[e.q = 113] = "q", e[e.r = 114] = "r", e[e.s = 115] = "s", e[e.t = 116] = "t", e[e.u = 117] = "u", e[e.v = 118] = "v", e[e.w = 119] = "w", e[e.x = 120] = "x", e[e.y = 121] = "y", e[e.z = 122] = "z", e[e.OpenCurlyBrace = 123] = "OpenCurlyBrace", e[e.Pipe = 124] = "Pipe", e[e.CloseCurlyBrace = 125] = "CloseCurlyBrace", e[e.Tilde = 126] = "Tilde", e[e.NoBreakSpace = 160] = "NoBreakSpace", e[e.U_Combining_Grave_Accent = 768] = "U_Combining_Grave_Accent", e[e.U_Combining_Acute_Accent = 769] = "U_Combining_Acute_Accent", e[e.U_Combining_Circumflex_Accent = 770] = "U_Combining_Circumflex_Accent", e[e.U_Combining_Tilde = 771] = "U_Combining_Tilde", e[e.U_Combining_Macron = 772] = "U_Combining_Macron", e[e.U_Combining_Overline = 773] = "U_Combining_Overline", e[e.U_Combining_Breve = 774] = "U_Combining_Breve", e[e.U_Combining_Dot_Above = 775] = "U_Combining_Dot_Above", e[e.U_Combining_Diaeresis = 776] = "U_Combining_Diaeresis", e[e.U_Combining_Hook_Above = 777] = "U_Combining_Hook_Above", e[e.U_Combining_Ring_Above = 778] = "U_Combining_Ring_Above", e[e.U_Combining_Double_Acute_Accent = 779] = "U_Combining_Double_Acute_Accent", e[e.U_Combining_Caron = 780] = "U_Combining_Caron", e[e.U_Combining_Vertical_Line_Above = 781] = "U_Combining_Vertical_Line_Above", e[e.U_Combining_Double_Vertical_Line_Above = 782] = "U_Combining_Double_Vertical_Line_Above", e[e.U_Combining_Double_Grave_Accent = 783] = "U_Combining_Double_Grave_Accent", e[e.U_Combining_Candrabindu = 784] = "U_Combining_Candrabindu", e[e.U_Combining_Inverted_Breve = 785] = "U_Combining_Inverted_Breve", e[e.U_Combining_Turned_Comma_Above = 786] = "U_Combining_Turned_Comma_Above", e[e.U_Combining_Comma_Above = 787] = "U_Combining_Comma_Above", e[e.U_Combining_Reversed_Comma_Above = 788] = "U_Combining_Reversed_Comma_Above", e[e.U_Combining_Comma_Above_Right = 789] = "U_Combining_Comma_Above_Right", e[e.U_Combining_Grave_Accent_Below = 790] = "U_Combining_Grave_Accent_Below", e[e.U_Combining_Acute_Accent_Below = 791] = "U_Combining_Acute_Accent_Below", e[e.U_Combining_Left_Tack_Below = 792] = "U_Combining_Left_Tack_Below", e[e.U_Combining_Right_Tack_Below = 793] = "U_Combining_Right_Tack_Below", e[e.U_Combining_Left_Angle_Above = 794] = "U_Combining_Left_Angle_Above", e[e.U_Combining_Horn = 795] = "U_Combining_Horn", e[e.U_Combining_Left_Half_Ring_Below = 796] = "U_Combining_Left_Half_Ring_Below", e[e.U_Combining_Up_Tack_Below = 797] = "U_Combining_Up_Tack_Below", e[e.U_Combining_Down_Tack_Below = 798] = "U_Combining_Down_Tack_Below", e[e.U_Combining_Plus_Sign_Below = 799] = "U_Combining_Plus_Sign_Below", e[e.U_Combining_Minus_Sign_Below = 800] = "U_Combining_Minus_Sign_Below", e[e.U_Combining_Palatalized_Hook_Below = 801] = "U_Combining_Palatalized_Hook_Below", e[e.U_Combining_Retroflex_Hook_Below = 802] = "U_Combining_Retroflex_Hook_Below", e[e.U_Combining_Dot_Below = 803] = "U_Combining_Dot_Below", e[e.U_Combining_Diaeresis_Below = 804] = "U_Combining_Diaeresis_Below", e[e.U_Combining_Ring_Below = 805] = "U_Combining_Ring_Below", e[e.U_Combining_Comma_Below = 806] = "U_Combining_Comma_Below", e[e.U_Combining_Cedilla = 807] = "U_Combining_Cedilla", e[e.U_Combining_Ogonek = 808] = "U_Combining_Ogonek", e[e.U_Combining_Vertical_Line_Below = 809] = "U_Combining_Vertical_Line_Below", e[e.U_Combining_Bridge_Below = 810] = "U_Combining_Bridge_Below", e[e.U_Combining_Inverted_Double_Arch_Below = 811] = "U_Combining_Inverted_Double_Arch_Below", e[e.U_Combining_Caron_Below = 812] = "U_Combining_Caron_Below", e[e.U_Combining_Circumflex_Accent_Below = 813] = "U_Combining_Circumflex_Accent_Below", e[e.U_Combining_Breve_Below = 814] = "U_Combining_Breve_Below", e[e.U_Combining_Inverted_Breve_Below = 815] = "U_Combining_Inverted_Breve_Below", e[e.U_Combining_Tilde_Below = 816] = "U_Combining_Tilde_Below", e[e.U_Combining_Macron_Below = 817] = "U_Combining_Macron_Below", e[e.U_Combining_Low_Line = 818] = "U_Combining_Low_Line", e[e.U_Combining_Double_Low_Line = 819] = "U_Combining_Double_Low_Line", e[e.U_Combining_Tilde_Overlay = 820] = "U_Combining_Tilde_Overlay", e[e.U_Combining_Short_Stroke_Overlay = 821] = "U_Combining_Short_Stroke_Overlay", e[e.U_Combining_Long_Stroke_Overlay = 822] = "U_Combining_Long_Stroke_Overlay", e[e.U_Combining_Short_Solidus_Overlay = 823] = "U_Combining_Short_Solidus_Overlay", e[e.U_Combining_Long_Solidus_Overlay = 824] = "U_Combining_Long_Solidus_Overlay", e[e.U_Combining_Right_Half_Ring_Below = 825] = "U_Combining_Right_Half_Ring_Below", e[e.U_Combining_Inverted_Bridge_Below = 826] = "U_Combining_Inverted_Bridge_Below", e[e.U_Combining_Square_Below = 827] = "U_Combining_Square_Below", e[e.U_Combining_Seagull_Below = 828] = "U_Combining_Seagull_Below", e[e.U_Combining_X_Above = 829] = "U_Combining_X_Above", e[e.U_Combining_Vertical_Tilde = 830] = "U_Combining_Vertical_Tilde", e[e.U_Combining_Double_Overline = 831] = "U_Combining_Double_Overline", e[e.U_Combining_Grave_Tone_Mark = 832] = "U_Combining_Grave_Tone_Mark", e[e.U_Combining_Acute_Tone_Mark = 833] = "U_Combining_Acute_Tone_Mark", e[e.U_Combining_Greek_Perispomeni = 834] = "U_Combining_Greek_Perispomeni", e[e.U_Combining_Greek_Koronis = 835] = "U_Combining_Greek_Koronis", e[e.U_Combining_Greek_Dialytika_Tonos = 836] = "U_Combining_Greek_Dialytika_Tonos", e[e.U_Combining_Greek_Ypogegrammeni = 837] = "U_Combining_Greek_Ypogegrammeni", e[e.U_Combining_Bridge_Above = 838] = "U_Combining_Bridge_Above", e[e.U_Combining_Equals_Sign_Below = 839] = "U_Combining_Equals_Sign_Below", e[e.U_Combining_Double_Vertical_Line_Below = 840] = "U_Combining_Double_Vertical_Line_Below", e[e.U_Combining_Left_Angle_Below = 841] = "U_Combining_Left_Angle_Below", e[e.U_Combining_Not_Tilde_Above = 842] = "U_Combining_Not_Tilde_Above", e[e.U_Combining_Homothetic_Above = 843] = "U_Combining_Homothetic_Above", e[e.U_Combining_Almost_Equal_To_Above = 844] = "U_Combining_Almost_Equal_To_Above", e[e.U_Combining_Left_Right_Arrow_Below = 845] = "U_Combining_Left_Right_Arrow_Below", e[e.U_Combining_Upwards_Arrow_Below = 846] = "U_Combining_Upwards_Arrow_Below", e[e.U_Combining_Grapheme_Joiner = 847] = "U_Combining_Grapheme_Joiner", e[e.U_Combining_Right_Arrowhead_Above = 848] = "U_Combining_Right_Arrowhead_Above", e[e.U_Combining_Left_Half_Ring_Above = 849] = "U_Combining_Left_Half_Ring_Above", e[e.U_Combining_Fermata = 850] = "U_Combining_Fermata", e[e.U_Combining_X_Below = 851] = "U_Combining_X_Below", e[e.U_Combining_Left_Arrowhead_Below = 852] = "U_Combining_Left_Arrowhead_Below", e[e.U_Combining_Right_Arrowhead_Below = 853] = "U_Combining_Right_Arrowhead_Below", e[e.U_Combining_Right_Arrowhead_And_Up_Arrowhead_Below = 854] = "U_Combining_Right_Arrowhead_And_Up_Arrowhead_Below", e[e.U_Combining_Right_Half_Ring_Above = 855] = "U_Combining_Right_Half_Ring_Above", e[e.U_Combining_Dot_Above_Right = 856] = "U_Combining_Dot_Above_Right", e[e.U_Combining_Asterisk_Below = 857] = "U_Combining_Asterisk_Below", e[e.U_Combining_Double_Ring_Below = 858] = "U_Combining_Double_Ring_Below", e[e.U_Combining_Zigzag_Above = 859] = "U_Combining_Zigzag_Above", e[e.U_Combining_Double_Breve_Below = 860] = "U_Combining_Double_Breve_Below", e[e.U_Combining_Double_Breve = 861] = "U_Combining_Double_Breve", e[e.U_Combining_Double_Macron = 862] = "U_Combining_Double_Macron", e[e.U_Combining_Double_Macron_Below = 863] = "U_Combining_Double_Macron_Below", e[e.U_Combining_Double_Tilde = 864] = "U_Combining_Double_Tilde", e[e.U_Combining_Double_Inverted_Breve = 865] = "U_Combining_Double_Inverted_Breve", e[e.U_Combining_Double_Rightwards_Arrow_Below = 866] = "U_Combining_Double_Rightwards_Arrow_Below", e[e.U_Combining_Latin_Small_Letter_A = 867] = "U_Combining_Latin_Small_Letter_A", e[e.U_Combining_Latin_Small_Letter_E = 868] = "U_Combining_Latin_Small_Letter_E", e[e.U_Combining_Latin_Small_Letter_I = 869] = "U_Combining_Latin_Small_Letter_I", e[e.U_Combining_Latin_Small_Letter_O = 870] = "U_Combining_Latin_Small_Letter_O", e[e.U_Combining_Latin_Small_Letter_U = 871] = "U_Combining_Latin_Small_Letter_U", e[e.U_Combining_Latin_Small_Letter_C = 872] = "U_Combining_Latin_Small_Letter_C", e[e.U_Combining_Latin_Small_Letter_D = 873] = "U_Combining_Latin_Small_Letter_D", e[e.U_Combining_Latin_Small_Letter_H = 874] = "U_Combining_Latin_Small_Letter_H", e[e.U_Combining_Latin_Small_Letter_M = 875] = "U_Combining_Latin_Small_Letter_M", e[e.U_Combining_Latin_Small_Letter_R = 876] = "U_Combining_Latin_Small_Letter_R", e[e.U_Combining_Latin_Small_Letter_T = 877] = "U_Combining_Latin_Small_Letter_T", e[e.U_Combining_Latin_Small_Letter_V = 878] = "U_Combining_Latin_Small_Letter_V", e[e.U_Combining_Latin_Small_Letter_X = 879] = "U_Combining_Latin_Small_Letter_X", e[e.LINE_SEPARATOR = 8232] = "LINE_SEPARATOR", e[e.PARAGRAPH_SEPARATOR = 8233] = "PARAGRAPH_SEPARATOR", e[e.NEXT_LINE = 133] = "NEXT_LINE", e[e.U_CIRCUMFLEX = 94] = "U_CIRCUMFLEX", e[e.U_GRAVE_ACCENT = 96] = "U_GRAVE_ACCENT", e[e.U_DIAERESIS = 168] = "U_DIAERESIS", e[e.U_MACRON = 175] = "U_MACRON", e[e.U_ACUTE_ACCENT = 180] = "U_ACUTE_ACCENT", e[e.U_CEDILLA = 184] = "U_CEDILLA", e[e.U_MODIFIER_LETTER_LEFT_ARROWHEAD = 706] = "U_MODIFIER_LETTER_LEFT_ARROWHEAD", e[e.U_MODIFIER_LETTER_RIGHT_ARROWHEAD = 707] = "U_MODIFIER_LETTER_RIGHT_ARROWHEAD", e[e.U_MODIFIER_LETTER_UP_ARROWHEAD = 708] = "U_MODIFIER_LETTER_UP_ARROWHEAD", e[e.U_MODIFIER_LETTER_DOWN_ARROWHEAD = 709] = "U_MODIFIER_LETTER_DOWN_ARROWHEAD", e[e.U_MODIFIER_LETTER_CENTRED_RIGHT_HALF_RING = 722] = "U_MODIFIER_LETTER_CENTRED_RIGHT_HALF_RING", e[e.U_MODIFIER_LETTER_CENTRED_LEFT_HALF_RING = 723] = "U_MODIFIER_LETTER_CENTRED_LEFT_HALF_RING", e[e.U_MODIFIER_LETTER_UP_TACK = 724] = "U_MODIFIER_LETTER_UP_TACK", e[e.U_MODIFIER_LETTER_DOWN_TACK = 725] = "U_MODIFIER_LETTER_DOWN_TACK", e[e.U_MODIFIER_LETTER_PLUS_SIGN = 726] = "U_MODIFIER_LETTER_PLUS_SIGN", e[e.U_MODIFIER_LETTER_MINUS_SIGN = 727] = "U_MODIFIER_LETTER_MINUS_SIGN", e[e.U_BREVE = 728] = "U_BREVE", e[e.U_DOT_ABOVE = 729] = "U_DOT_ABOVE", e[e.U_RING_ABOVE = 730] = "U_RING_ABOVE", e[e.U_OGONEK = 731] = "U_OGONEK", e[e.U_SMALL_TILDE = 732] = "U_SMALL_TILDE", e[e.U_DOUBLE_ACUTE_ACCENT = 733] = "U_DOUBLE_ACUTE_ACCENT", e[e.U_MODIFIER_LETTER_RHOTIC_HOOK = 734] = "U_MODIFIER_LETTER_RHOTIC_HOOK", e[e.U_MODIFIER_LETTER_CROSS_ACCENT = 735] = "U_MODIFIER_LETTER_CROSS_ACCENT", e[e.U_MODIFIER_LETTER_EXTRA_HIGH_TONE_BAR = 741] = "U_MODIFIER_LETTER_EXTRA_HIGH_TONE_BAR", e[e.U_MODIFIER_LETTER_HIGH_TONE_BAR = 742] = "U_MODIFIER_LETTER_HIGH_TONE_BAR", e[e.U_MODIFIER_LETTER_MID_TONE_BAR = 743] = "U_MODIFIER_LETTER_MID_TONE_BAR", e[e.U_MODIFIER_LETTER_LOW_TONE_BAR = 744] = "U_MODIFIER_LETTER_LOW_TONE_BAR", e[e.U_MODIFIER_LETTER_EXTRA_LOW_TONE_BAR = 745] = "U_MODIFIER_LETTER_EXTRA_LOW_TONE_BAR", e[e.U_MODIFIER_LETTER_YIN_DEPARTING_TONE_MARK = 746] = "U_MODIFIER_LETTER_YIN_DEPARTING_TONE_MARK", e[e.U_MODIFIER_LETTER_YANG_DEPARTING_TONE_MARK = 747] = "U_MODIFIER_LETTER_YANG_DEPARTING_TONE_MARK", e[e.U_MODIFIER_LETTER_UNASPIRATED = 749] = "U_MODIFIER_LETTER_UNASPIRATED", e[e.U_MODIFIER_LETTER_LOW_DOWN_ARROWHEAD = 751] = "U_MODIFIER_LETTER_LOW_DOWN_ARROWHEAD", e[e.U_MODIFIER_LETTER_LOW_UP_ARROWHEAD = 752] = "U_MODIFIER_LETTER_LOW_UP_ARROWHEAD", e[e.U_MODIFIER_LETTER_LOW_LEFT_ARROWHEAD = 753] = "U_MODIFIER_LETTER_LOW_LEFT_ARROWHEAD", e[e.U_MODIFIER_LETTER_LOW_RIGHT_ARROWHEAD = 754] = "U_MODIFIER_LETTER_LOW_RIGHT_ARROWHEAD", e[e.U_MODIFIER_LETTER_LOW_RING = 755] = "U_MODIFIER_LETTER_LOW_RING", e[e.U_MODIFIER_LETTER_MIDDLE_GRAVE_ACCENT = 756] = "U_MODIFIER_LETTER_MIDDLE_GRAVE_ACCENT", e[e.U_MODIFIER_LETTER_MIDDLE_DOUBLE_GRAVE_ACCENT = 757] = "U_MODIFIER_LETTER_MIDDLE_DOUBLE_GRAVE_ACCENT", e[e.U_MODIFIER_LETTER_MIDDLE_DOUBLE_ACUTE_ACCENT = 758] = "U_MODIFIER_LETTER_MIDDLE_DOUBLE_ACUTE_ACCENT", e[e.U_MODIFIER_LETTER_LOW_TILDE = 759] = "U_MODIFIER_LETTER_LOW_TILDE", e[e.U_MODIFIER_LETTER_RAISED_COLON = 760] = "U_MODIFIER_LETTER_RAISED_COLON", e[e.U_MODIFIER_LETTER_BEGIN_HIGH_TONE = 761] = "U_MODIFIER_LETTER_BEGIN_HIGH_TONE", e[e.U_MODIFIER_LETTER_END_HIGH_TONE = 762] = "U_MODIFIER_LETTER_END_HIGH_TONE", e[e.U_MODIFIER_LETTER_BEGIN_LOW_TONE = 763] = "U_MODIFIER_LETTER_BEGIN_LOW_TONE", e[e.U_MODIFIER_LETTER_END_LOW_TONE = 764] = "U_MODIFIER_LETTER_END_LOW_TONE", e[e.U_MODIFIER_LETTER_SHELF = 765] = "U_MODIFIER_LETTER_SHELF", e[e.U_MODIFIER_LETTER_OPEN_SHELF = 766] = "U_MODIFIER_LETTER_OPEN_SHELF", e[e.U_MODIFIER_LETTER_LOW_LEFT_ARROW = 767] = "U_MODIFIER_LETTER_LOW_LEFT_ARROW", e[e.U_GREEK_LOWER_NUMERAL_SIGN = 885] = "U_GREEK_LOWER_NUMERAL_SIGN", e[e.U_GREEK_TONOS = 900] = "U_GREEK_TONOS", e[e.U_GREEK_DIALYTIKA_TONOS = 901] = "U_GREEK_DIALYTIKA_TONOS", e[e.U_GREEK_KORONIS = 8125] = "U_GREEK_KORONIS", e[e.U_GREEK_PSILI = 8127] = "U_GREEK_PSILI", e[e.U_GREEK_PERISPOMENI = 8128] = "U_GREEK_PERISPOMENI", e[e.U_GREEK_DIALYTIKA_AND_PERISPOMENI = 8129] = "U_GREEK_DIALYTIKA_AND_PERISPOMENI", e[e.U_GREEK_PSILI_AND_VARIA = 8141] = "U_GREEK_PSILI_AND_VARIA", e[e.U_GREEK_PSILI_AND_OXIA = 8142] = "U_GREEK_PSILI_AND_OXIA", e[e.U_GREEK_PSILI_AND_PERISPOMENI = 8143] = "U_GREEK_PSILI_AND_PERISPOMENI", e[e.U_GREEK_DASIA_AND_VARIA = 8157] = "U_GREEK_DASIA_AND_VARIA", e[e.U_GREEK_DASIA_AND_OXIA = 8158] = "U_GREEK_DASIA_AND_OXIA", e[e.U_GREEK_DASIA_AND_PERISPOMENI = 8159] = "U_GREEK_DASIA_AND_PERISPOMENI", e[e.U_GREEK_DIALYTIKA_AND_VARIA = 8173] = "U_GREEK_DIALYTIKA_AND_VARIA", e[e.U_GREEK_DIALYTIKA_AND_OXIA = 8174] = "U_GREEK_DIALYTIKA_AND_OXIA", e[e.U_GREEK_VARIA = 8175] = "U_GREEK_VARIA", e[e.U_GREEK_OXIA = 8189] = "U_GREEK_OXIA", e[e.U_GREEK_DASIA = 8190] = "U_GREEK_DASIA", e[e.U_IDEOGRAPHIC_FULL_STOP = 12290] = "U_IDEOGRAPHIC_FULL_STOP", e[e.U_LEFT_CORNER_BRACKET = 12300] = "U_LEFT_CORNER_BRACKET", e[e.U_RIGHT_CORNER_BRACKET = 12301] = "U_RIGHT_CORNER_BRACKET", e[e.U_LEFT_BLACK_LENTICULAR_BRACKET = 12304] = "U_LEFT_BLACK_LENTICULAR_BRACKET", e[e.U_RIGHT_BLACK_LENTICULAR_BRACKET = 12305] = "U_RIGHT_BLACK_LENTICULAR_BRACKET", e[e.U_OVERLINE = 8254] = "U_OVERLINE", e[e.UTF8_BOM = 65279] = "UTF8_BOM", e[e.U_FULLWIDTH_SEMICOLON = 65307] = "U_FULLWIDTH_SEMICOLON", e[e.U_FULLWIDTH_COMMA = 65292] = "U_FULLWIDTH_COMMA";
})(L || (L = {}));
class Ms {
  constructor() {
    this.listeners = [], this.unexpectedErrorHandler = function(t) {
      setTimeout(() => {
        throw t.stack ? xt.isErrorNoTelemetry(t) ? new xt(t.message + `

` + t.stack) : new Error(t.message + `

` + t.stack) : t;
      }, 0);
    };
  }
  addListener(t) {
    return this.listeners.push(t), () => {
      this._removeListener(t);
    };
  }
  emit(t) {
    this.listeners.forEach((n) => {
      n(t);
    });
  }
  _removeListener(t) {
    this.listeners.splice(this.listeners.indexOf(t), 1);
  }
  setUnexpectedErrorHandler(t) {
    this.unexpectedErrorHandler = t;
  }
  getUnexpectedErrorHandler() {
    return this.unexpectedErrorHandler;
  }
  onUnexpectedError(t) {
    this.unexpectedErrorHandler(t), this.emit(t);
  }
  onUnexpectedExternalError(t) {
    this.unexpectedErrorHandler(t);
  }
}
const Ds = new Ms();
function St(e) {
  ks(e) || Ds.onUnexpectedError(e);
}
function On(e) {
  if (e instanceof Error) {
    const { name: t, message: n, cause: i } = e, r = e.stacktrace || e.stack;
    return {
      $isError: !0,
      name: t,
      message: n,
      stack: r,
      noTelemetry: xt.isErrorNoTelemetry(e),
      cause: i ? On(i) : void 0,
      code: e.code
    };
  }
  return e;
}
const Vn = "Canceled";
function ks(e) {
  return e instanceof Fs ? !0 : e instanceof Error && e.name === Vn && e.message === Vn;
}
class Fs extends Error {
  constructor() {
    super(Vn), this.name = this.message;
  }
}
class xt extends Error {
  constructor(t) {
    super(t), this.name = "CodeExpectedError";
  }
  static fromError(t) {
    if (t instanceof xt)
      return t;
    const n = new xt();
    return n.message = t.message, n.stack = t.stack, n;
  }
  static isErrorNoTelemetry(t) {
    return t.name === "CodeExpectedError";
  }
}
class ae extends Error {
  constructor(t) {
    super(t || "An unexpected bug occurred."), Object.setPrototypeOf(this, ae.prototype);
  }
}
function Is(e, t) {
  const n = /* @__PURE__ */ Object.create(null);
  for (const i of e) {
    const r = t(i);
    let s = n[r];
    s || (s = n[r] = []), s.push(i);
  }
  return n;
}
function Ss(e, t) {
  const n = this;
  let i = !1, r;
  return function() {
    return i || (i = !0, r = e.apply(n, arguments)), r;
  };
}
function At(e, t) {
  const n = vt(e, t);
  return n === -1 ? void 0 : e[n];
}
function vt(e, t, n = 0, i = e.length) {
  let r = n, s = i;
  for (; r < s; ) {
    const a = Math.floor((r + s) / 2);
    t(e[a]) ? r = a + 1 : s = a;
  }
  return r - 1;
}
function Ps(e, t) {
  const n = qn(e, t);
  return n === e.length ? void 0 : e[n];
}
function qn(e, t, n = 0, i = e.length) {
  let r = n, s = i;
  for (; r < s; ) {
    const a = Math.floor((r + s) / 2);
    t(e[a]) ? s = a : r = a + 1;
  }
  return r;
}
const En = class En {
  constructor(t) {
    this._array = t, this._findLastMonotonousLastIdx = 0;
  }
  findLastMonotonous(t) {
    if (En.assertInvariants) {
      if (this._prevFindLastPredicate) {
        for (const i of this._array)
          if (this._prevFindLastPredicate(i) && !t(i))
            throw new Error(
              "MonotonousArray: current predicate must be weaker than (or equal to) the previous predicate."
            );
      }
      this._prevFindLastPredicate = t;
    }
    const n = vt(this._array, t, this._findLastMonotonousLastIdx);
    return this._findLastMonotonousLastIdx = n + 1, n === -1 ? void 0 : this._array[n];
  }
};
En.assertInvariants = !1;
let cn = En;
function Zr(e, t, n = (i, r) => i === r) {
  if (e === t)
    return !0;
  if (!e || !t || e.length !== t.length)
    return !1;
  for (let i = 0, r = e.length; i < r; i++)
    if (!n(e[i], t[i]))
      return !1;
  return !0;
}
function* ys(e, t) {
  let n, i;
  for (const r of e)
    i !== void 0 && t(i, r) ? n.push(r) : (n && (yield n), n = [r]), i = r;
  n && (yield n);
}
function Bs(e, t) {
  for (let n = 0; n <= e.length; n++)
    t(n === 0 ? void 0 : e[n - 1], n === e.length ? void 0 : e[n]);
}
function Os(e, t) {
  for (let n = 0; n < e.length; n++)
    t(n === 0 ? void 0 : e[n - 1], e[n], n + 1 === e.length ? void 0 : e[n + 1]);
}
function Vs(e, t) {
  for (const n of t)
    e.push(n);
}
var Hn;
(function(e) {
  function t(s) {
    return s < 0;
  }
  e.isLessThan = t;
  function n(s) {
    return s <= 0;
  }
  e.isLessThanOrEqual = n;
  function i(s) {
    return s > 0;
  }
  e.isGreaterThan = i;
  function r(s) {
    return s === 0;
  }
  e.isNeitherLessOrGreaterThan = r, e.greaterThan = 1, e.lessThan = -1, e.neitherLessOrGreaterThan = 0;
})(Hn || (Hn = {}));
function Pt(e, t) {
  return (n, i) => t(e(n), e(i));
}
const yt = (e, t) => e - t;
function qs(e) {
  return (t, n) => -e(t, n);
}
const bt = class bt {
  constructor(t) {
    this.iterate = t;
  }
  forEach(t) {
    this.iterate((n) => (t(n), !0));
  }
  toArray() {
    const t = [];
    return this.iterate((n) => (t.push(n), !0)), t;
  }
  filter(t) {
    return new bt((n) => this.iterate((i) => t(i) ? n(i) : !0));
  }
  map(t) {
    return new bt((n) => this.iterate((i) => n(t(i))));
  }
  some(t) {
    let n = !1;
    return this.iterate((i) => (n = t(i), !n)), n;
  }
  findFirst(t) {
    let n;
    return this.iterate((i) => t(i) ? (n = i, !1) : !0), n;
  }
  findLast(t) {
    let n;
    return this.iterate((i) => (t(i) && (n = i), !0)), n;
  }
  findLastMaxBy(t) {
    let n, i = !0;
    return this.iterate((r) => ((i || Hn.isGreaterThan(t(r, n))) && (i = !1, n = r), !0)), n;
  }
};
bt.empty = new bt((t) => {
});
let pi = bt;
var Ni, Ei;
class Hs {
  constructor(t, n) {
    this.uri = t, this.value = n;
  }
}
function Ws(e) {
  return Array.isArray(e);
}
const tt = class tt {
  constructor(t, n) {
    if (this[Ni] = "ResourceMap", t instanceof tt)
      this.map = new Map(t.map), this.toKey = n ?? tt.defaultToKey;
    else if (Ws(t)) {
      this.map = /* @__PURE__ */ new Map(), this.toKey = n ?? tt.defaultToKey;
      for (const [i, r] of t)
        this.set(i, r);
    } else
      this.map = /* @__PURE__ */ new Map(), this.toKey = t ?? tt.defaultToKey;
  }
  set(t, n) {
    return this.map.set(this.toKey(t), new Hs(t, n)), this;
  }
  get(t) {
    var n;
    return (n = this.map.get(this.toKey(t))) == null ? void 0 : n.value;
  }
  has(t) {
    return this.map.has(this.toKey(t));
  }
  get size() {
    return this.map.size;
  }
  clear() {
    this.map.clear();
  }
  delete(t) {
    return this.map.delete(this.toKey(t));
  }
  forEach(t, n) {
    typeof n < "u" && (t = t.bind(n));
    for (const [i, r] of this.map)
      t(r.value, r.uri, this);
  }
  *values() {
    for (const t of this.map.values())
      yield t.value;
  }
  *keys() {
    for (const t of this.map.values())
      yield t.uri;
  }
  *entries() {
    for (const t of this.map.values())
      yield [t.uri, t.value];
  }
  *[(Ni = Symbol.toStringTag, Symbol.iterator)]() {
    for (const [, t] of this.map)
      yield [t.uri, t.value];
  }
};
tt.defaultToKey = (t) => t.toString();
let Wn = tt;
var ge;
(function(e) {
  e[e.None = 0] = "None", e[e.AsOld = 1] = "AsOld", e[e.AsNew = 2] = "AsNew";
})(ge || (ge = {}));
class Gs {
  constructor() {
    this[Ei] = "LinkedMap", this._map = /* @__PURE__ */ new Map(), this._head = void 0, this._tail = void 0, this._size = 0, this._state = 0;
  }
  clear() {
    this._map.clear(), this._head = void 0, this._tail = void 0, this._size = 0, this._state++;
  }
  isEmpty() {
    return !this._head && !this._tail;
  }
  get size() {
    return this._size;
  }
  get first() {
    var t;
    return (t = this._head) == null ? void 0 : t.value;
  }
  get last() {
    var t;
    return (t = this._tail) == null ? void 0 : t.value;
  }
  has(t) {
    return this._map.has(t);
  }
  get(t, n = ge.None) {
    const i = this._map.get(t);
    if (i)
      return n !== ge.None && this.touch(i, n), i.value;
  }
  set(t, n, i = ge.None) {
    let r = this._map.get(t);
    if (r)
      r.value = n, i !== ge.None && this.touch(r, i);
    else {
      switch (r = { key: t, value: n, next: void 0, previous: void 0 }, i) {
        case ge.None:
          this.addItemLast(r);
          break;
        case ge.AsOld:
          this.addItemFirst(r);
          break;
        case ge.AsNew:
          this.addItemLast(r);
          break;
        default:
          this.addItemLast(r);
          break;
      }
      this._map.set(t, r), this._size++;
    }
    return this;
  }
  delete(t) {
    return !!this.remove(t);
  }
  remove(t) {
    const n = this._map.get(t);
    if (n)
      return this._map.delete(t), this.removeItem(n), this._size--, n.value;
  }
  shift() {
    if (!this._head && !this._tail)
      return;
    if (!this._head || !this._tail)
      throw new Error("Invalid list");
    const t = this._head;
    return this._map.delete(t.key), this.removeItem(t), this._size--, t.value;
  }
  forEach(t, n) {
    const i = this._state;
    let r = this._head;
    for (; r; ) {
      if (n ? t.bind(n)(r.value, r.key, this) : t(r.value, r.key, this), this._state !== i)
        throw new Error("LinkedMap got modified during iteration.");
      r = r.next;
    }
  }
  keys() {
    const t = this, n = this._state;
    let i = this._head;
    const r = {
      [Symbol.iterator]() {
        return r;
      },
      next() {
        if (t._state !== n)
          throw new Error("LinkedMap got modified during iteration.");
        if (i) {
          const s = { value: i.key, done: !1 };
          return i = i.next, s;
        } else
          return { value: void 0, done: !0 };
      }
    };
    return r;
  }
  values() {
    const t = this, n = this._state;
    let i = this._head;
    const r = {
      [Symbol.iterator]() {
        return r;
      },
      next() {
        if (t._state !== n)
          throw new Error("LinkedMap got modified during iteration.");
        if (i) {
          const s = { value: i.value, done: !1 };
          return i = i.next, s;
        } else
          return { value: void 0, done: !0 };
      }
    };
    return r;
  }
  entries() {
    const t = this, n = this._state;
    let i = this._head;
    const r = {
      [Symbol.iterator]() {
        return r;
      },
      next() {
        if (t._state !== n)
          throw new Error("LinkedMap got modified during iteration.");
        if (i) {
          const s = { value: [i.key, i.value], done: !1 };
          return i = i.next, s;
        } else
          return { value: void 0, done: !0 };
      }
    };
    return r;
  }
  [(Ei = Symbol.toStringTag, Symbol.iterator)]() {
    return this.entries();
  }
  trimOld(t) {
    if (t >= this.size)
      return;
    if (t === 0) {
      this.clear();
      return;
    }
    let n = this._head, i = this.size;
    for (; n && i > t; )
      this._map.delete(n.key), n = n.next, i--;
    this._head = n, this._size = i, n && (n.previous = void 0), this._state++;
  }
  trimNew(t) {
    if (t >= this.size)
      return;
    if (t === 0) {
      this.clear();
      return;
    }
    let n = this._tail, i = this.size;
    for (; n && i > t; )
      this._map.delete(n.key), n = n.previous, i--;
    this._tail = n, this._size = i, n && (n.next = void 0), this._state++;
  }
  addItemFirst(t) {
    if (!this._head && !this._tail)
      this._tail = t;
    else if (this._head)
      t.next = this._head, this._head.previous = t;
    else
      throw new Error("Invalid list");
    this._head = t, this._state++;
  }
  addItemLast(t) {
    if (!this._head && !this._tail)
      this._head = t;
    else if (this._tail)
      t.previous = this._tail, this._tail.next = t;
    else
      throw new Error("Invalid list");
    this._tail = t, this._state++;
  }
  removeItem(t) {
    if (t === this._head && t === this._tail)
      this._head = void 0, this._tail = void 0;
    else if (t === this._head) {
      if (!t.next)
        throw new Error("Invalid list");
      t.next.previous = void 0, this._head = t.next;
    } else if (t === this._tail) {
      if (!t.previous)
        throw new Error("Invalid list");
      t.previous.next = void 0, this._tail = t.previous;
    } else {
      const n = t.next, i = t.previous;
      if (!n || !i)
        throw new Error("Invalid list");
      n.previous = i, i.next = n;
    }
    t.next = void 0, t.previous = void 0, this._state++;
  }
  touch(t, n) {
    if (!this._head || !this._tail)
      throw new Error("Invalid list");
    if (!(n !== ge.AsOld && n !== ge.AsNew)) {
      if (n === ge.AsOld) {
        if (t === this._head)
          return;
        const i = t.next, r = t.previous;
        t === this._tail ? (r.next = void 0, this._tail = r) : (i.previous = r, r.next = i), t.previous = void 0, t.next = this._head, this._head.previous = t, this._head = t, this._state++;
      } else if (n === ge.AsNew) {
        if (t === this._tail)
          return;
        const i = t.next, r = t.previous;
        t === this._head ? (i.previous = void 0, this._head = i) : (i.previous = r, r.next = i), t.next = void 0, t.previous = this._tail, this._tail.next = t, this._tail = t, this._state++;
      }
    }
  }
  toJSON() {
    const t = [];
    return this.forEach((n, i) => {
      t.push([i, n]);
    }), t;
  }
  fromJSON(t) {
    this.clear();
    for (const [n, i] of t)
      this.set(n, i);
  }
}
class $s extends Gs {
  constructor(t, n = 1) {
    super(), this._limit = t, this._ratio = Math.min(Math.max(0, n), 1);
  }
  get limit() {
    return this._limit;
  }
  set limit(t) {
    this._limit = t, this.checkTrim();
  }
  get ratio() {
    return this._ratio;
  }
  set ratio(t) {
    this._ratio = Math.min(Math.max(0, t), 1), this.checkTrim();
  }
  get(t, n = ge.AsNew) {
    return super.get(t, n);
  }
  peek(t) {
    return super.get(t, ge.None);
  }
  set(t, n) {
    return super.set(t, n, ge.AsNew), this;
  }
  checkTrim() {
    this.size > this._limit && this.trim(Math.round(this._limit * this._ratio));
  }
}
class zs extends $s {
  constructor(t, n = 1) {
    super(t, n);
  }
  trim(t) {
    this.trimOld(t);
  }
  set(t, n) {
    return super.set(t, n), this.checkTrim(), this;
  }
}
class Jr {
  constructor() {
    this.map = /* @__PURE__ */ new Map();
  }
  add(t, n) {
    let i = this.map.get(t);
    i || (i = /* @__PURE__ */ new Set(), this.map.set(t, i)), i.add(n);
  }
  delete(t, n) {
    const i = this.map.get(t);
    i && (i.delete(n), i.size === 0 && this.map.delete(t));
  }
  forEach(t, n) {
    const i = this.map.get(t);
    i && i.forEach(n);
  }
  get(t) {
    const n = this.map.get(t);
    return n || /* @__PURE__ */ new Set();
  }
}
function js(e, t = "Unreachable") {
  throw new Error(t);
}
function Xs(e, t = "unexpected state") {
  if (!e)
    throw typeof t == "string" ? new ae(`Assertion Failed: ${t}`) : t;
}
function Gt(e) {
  if (!e()) {
    debugger;
    e(), St(new ae("Assertion Failed"));
  }
}
function hi(e, t) {
  let n = 0;
  for (; n < e.length - 1; ) {
    const i = e[n], r = e[n + 1];
    if (!t(i, r))
      return !1;
    n++;
  }
  return !0;
}
function Ys(e) {
  return typeof e == "string";
}
function Qs(e) {
  return !!e && typeof e[Symbol.iterator] == "function";
}
var hn;
(function(e) {
  function t(N) {
    return N && typeof N == "object" && typeof N[Symbol.iterator] == "function";
  }
  e.is = t;
  const n = Object.freeze([]);
  function i() {
    return n;
  }
  e.empty = i;
  function* r(N) {
    yield N;
  }
  e.single = r;
  function s(N) {
    return t(N) ? N : r(N);
  }
  e.wrap = s;
  function a(N) {
    return N || n;
  }
  e.from = a;
  function* u(N) {
    for (let E = N.length - 1; E >= 0; E--)
      yield N[E];
  }
  e.reverse = u;
  function o(N) {
    return !N || N[Symbol.iterator]().next().done === !0;
  }
  e.isEmpty = o;
  function c(N) {
    return N[Symbol.iterator]().next().value;
  }
  e.first = c;
  function h(N, E) {
    let U = 0;
    for (const D of N)
      if (E(D, U++))
        return !0;
    return !1;
  }
  e.some = h;
  function f(N, E) {
    for (const U of N)
      if (E(U))
        return U;
  }
  e.find = f;
  function* _(N, E) {
    for (const U of N)
      E(U) && (yield U);
  }
  e.filter = _;
  function* p(N, E) {
    let U = 0;
    for (const D of N)
      yield E(D, U++);
  }
  e.map = p;
  function* d(N, E) {
    let U = 0;
    for (const D of N)
      yield* E(D, U++);
  }
  e.flatMap = d;
  function* b(...N) {
    for (const E of N)
      Qs(E) ? yield* E : yield E;
  }
  e.concat = b;
  function A(N, E, U) {
    let D = U;
    for (const S of N)
      D = E(D, S);
    return D;
  }
  e.reduce = A;
  function* v(N, E, U = N.length) {
    for (E < -N.length && (E = 0), E < 0 && (E += N.length), U < 0 ? U += N.length : U > N.length && (U = N.length); E < U; E++)
      yield N[E];
  }
  e.slice = v;
  function x(N, E = Number.POSITIVE_INFINITY) {
    const U = [];
    if (E === 0)
      return [U, N];
    const D = N[Symbol.iterator]();
    for (let S = 0; S < E; S++) {
      const X = D.next();
      if (X.done)
        return [U, e.empty()];
      U.push(X.value);
    }
    return [U, { [Symbol.iterator]() {
      return D;
    } }];
  }
  e.consume = x;
  async function R(N) {
    const E = [];
    for await (const U of N)
      E.push(U);
    return Promise.resolve(E);
  }
  e.asyncToArray = R;
})(hn || (hn = {}));
const xn = class xn {
  constructor() {
    this.livingDisposables = /* @__PURE__ */ new Map();
  }
  getDisposableData(t) {
    let n = this.livingDisposables.get(t);
    return n || (n = { parent: null, source: null, isSingleton: !1, value: t, idx: xn.idx++ }, this.livingDisposables.set(t, n)), n;
  }
  trackDisposable(t) {
    const n = this.getDisposableData(t);
    n.source || (n.source = new Error().stack);
  }
  setParent(t, n) {
    const i = this.getDisposableData(t);
    i.parent = n;
  }
  markAsDisposed(t) {
    this.livingDisposables.delete(t);
  }
  markAsSingleton(t) {
    this.getDisposableData(t).isSingleton = !0;
  }
  getRootParent(t, n) {
    const i = n.get(t);
    if (i)
      return i;
    const r = t.parent ? this.getRootParent(this.getDisposableData(t.parent), n) : t;
    return n.set(t, r), r;
  }
  getTrackedDisposables() {
    const t = /* @__PURE__ */ new Map();
    return [...this.livingDisposables.entries()].filter(([, i]) => i.source !== null && !this.getRootParent(i, t).isSingleton).flatMap(([i]) => i);
  }
  computeLeakingDisposables(t = 10, n) {
    let i;
    if (n)
      i = n;
    else {
      const o = /* @__PURE__ */ new Map(), c = [...this.livingDisposables.values()].filter((f) => f.source !== null && !this.getRootParent(f, o).isSingleton);
      if (c.length === 0)
        return;
      const h = new Set(c.map((f) => f.value));
      if (i = c.filter((f) => !(f.parent && h.has(f.parent))), i.length === 0)
        throw new Error("There are cyclic diposable chains!");
    }
    if (!i)
      return;
    function r(o) {
      function c(f, _) {
        for (; f.length > 0 && _.some(
          (p) => typeof p == "string" ? p === f[0] : f[0].match(p)
        ); )
          f.shift();
      }
      const h = o.source.split(`
`).map((f) => f.trim().replace("at ", "")).filter((f) => f !== "");
      return c(h, ["Error", /^trackDisposable \(.*\)$/, /^DisposableTracker.trackDisposable \(.*\)$/]), h.reverse();
    }
    const s = new Jr();
    for (const o of i) {
      const c = r(o);
      for (let h = 0; h <= c.length; h++)
        s.add(c.slice(0, h).join(`
`), o);
    }
    i.sort(Pt((o) => o.idx, yt));
    let a = "", u = 0;
    for (const o of i.slice(0, t)) {
      u++;
      const c = r(o), h = [];
      for (let f = 0; f < c.length; f++) {
        let _ = c[f];
        _ = `(shared with ${s.get(c.slice(0, f + 1).join(`
`)).size}/${i.length} leaks) at ${_}`;
        const d = s.get(c.slice(0, f).join(`
`)), b = Is([...d].map((A) => r(A)[f]), (A) => A);
        delete b[c[f]];
        for (const [A, v] of Object.entries(b))
          h.unshift(`    - stacktraces of ${v.length} other leaks continue with ${A}`);
        h.unshift(_);
      }
      a += `


==================== Leaking disposable ${u}/${i.length}: ${o.value.constructor.name} ====================
${h.join(`
`)}
============================================================

`;
    }
    return i.length > t && (a += `


... and ${i.length - t} more leaking disposables

`), { leaks: i, details: a };
  }
};
xn.idx = 0;
let xi = xn;
function Kr(e) {
  if (hn.is(e)) {
    const t = [];
    for (const n of e)
      if (n)
        try {
          n.dispose();
        } catch (i) {
          t.push(i);
        }
    if (t.length === 1)
      throw t[0];
    if (t.length > 1)
      throw new AggregateError(t, "Encountered errors while disposing of store");
    return Array.isArray(e) ? [] : e;
  } else if (e)
    return e.dispose(), e;
}
function Zs(...e) {
  return $t(() => Kr(e));
}
function $t(e) {
  return {
    dispose: Ss(() => {
      e();
    })
  };
}
const An = class An {
  constructor() {
    this._toDispose = /* @__PURE__ */ new Set(), this._isDisposed = !1;
  }
  dispose() {
    this._isDisposed || (this._isDisposed = !0, this.clear());
  }
  get isDisposed() {
    return this._isDisposed;
  }
  clear() {
    if (this._toDispose.size !== 0)
      try {
        Kr(this._toDispose);
      } finally {
        this._toDispose.clear();
      }
  }
  add(t) {
    if (!t)
      return t;
    if (t === this)
      throw new Error("Cannot register a disposable on itself!");
    return this._isDisposed ? An.DISABLE_DISPOSED_WARNING || console.warn(new Error(
      "Trying to add a disposable to a DisposableStore that has already been disposed of. The added object will be leaked!"
    ).stack) : this._toDispose.add(t), t;
  }
  delete(t) {
    if (t) {
      if (t === this)
        throw new Error("Cannot dispose a disposable on itself!");
      this._toDispose.delete(t), t.dispose();
    }
  }
  deleteAndLeak(t) {
    t && this._toDispose.has(t) && this._toDispose.delete(t);
  }
};
An.DISABLE_DISPOSED_WARNING = !1;
let zt = An;
const Li = class Li {
  constructor() {
    this._store = new zt(), this._store;
  }
  dispose() {
    this._store.dispose();
  }
  _register(t) {
    if (t === this)
      throw new Error("Cannot register a disposable on itself!");
    return this._store.add(t);
  }
};
Li.None = Object.freeze({ dispose() {
} });
let Rt = Li;
const dt = class dt {
  constructor(t) {
    this.element = t, this.next = dt.Undefined, this.prev = dt.Undefined;
  }
};
dt.Undefined = new dt(void 0);
let te = dt;
class Js {
  constructor() {
    this._first = te.Undefined, this._last = te.Undefined, this._size = 0;
  }
  get size() {
    return this._size;
  }
  isEmpty() {
    return this._first === te.Undefined;
  }
  clear() {
    let t = this._first;
    for (; t !== te.Undefined; ) {
      const n = t.next;
      t.prev = te.Undefined, t.next = te.Undefined, t = n;
    }
    this._first = te.Undefined, this._last = te.Undefined, this._size = 0;
  }
  unshift(t) {
    return this._insert(t, !1);
  }
  push(t) {
    return this._insert(t, !0);
  }
  _insert(t, n) {
    const i = new te(t);
    if (this._first === te.Undefined)
      this._first = i, this._last = i;
    else if (n) {
      const s = this._last;
      this._last = i, i.prev = s, s.next = i;
    } else {
      const s = this._first;
      this._first = i, i.next = s, s.prev = i;
    }
    this._size += 1;
    let r = !1;
    return () => {
      r || (r = !0, this._remove(i));
    };
  }
  shift() {
    if (this._first !== te.Undefined) {
      const t = this._first.element;
      return this._remove(this._first), t;
    }
  }
  pop() {
    if (this._last !== te.Undefined) {
      const t = this._last.element;
      return this._remove(this._last), t;
    }
  }
  _remove(t) {
    if (t.prev !== te.Undefined && t.next !== te.Undefined) {
      const n = t.prev;
      n.next = t.next, t.next.prev = n;
    } else t.prev === te.Undefined && t.next === te.Undefined ? (this._first = te.Undefined, this._last = te.Undefined) : t.next === te.Undefined ? (this._last = this._last.prev, this._last.next = te.Undefined) : t.prev === te.Undefined && (this._first = this._first.next, this._first.prev = te.Undefined);
    this._size -= 1;
  }
  *[Symbol.iterator]() {
    let t = this._first;
    for (; t !== te.Undefined; )
      yield t.element, t = t.next;
  }
}
const Ks = globalThis.performance && typeof globalThis.performance.now == "function";
class Dn {
  static create(t) {
    return new Dn(t);
  }
  constructor(t) {
    this._now = Ks && t === !1 ? Date.now : globalThis.performance.now.bind(globalThis.performance), this._startTime = this._now(), this._stopTime = -1;
  }
  stop() {
    this._stopTime = this._now();
  }
  reset() {
    this._startTime = this._now(), this._stopTime = -1;
  }
  elapsed() {
    return this._stopTime !== -1 ? this._stopTime - this._startTime : this._now() - this._startTime;
  }
}
var fn;
(function(e) {
  e.None = () => Rt.None;
  function t(I, M) {
    return _(I, () => {
    }, 0, void 0, !0, void 0, M);
  }
  e.defer = t;
  function n(I) {
    return (M, y = null, P) => {
      let V = !1, $;
      return $ = I((Z) => {
        if (!V)
          return $ ? $.dispose() : V = !0, M.call(y, Z);
      }, null, P), V && $.dispose(), $;
    };
  }
  e.once = n;
  function i(I, M) {
    return e.once(e.filter(I, M));
  }
  e.onceIf = i;
  function r(I, M, y) {
    return h((P, V = null, $) => I((Z) => P.call(V, M(Z)), null, $), y);
  }
  e.map = r;
  function s(I, M, y) {
    return h((P, V = null, $) => I((Z) => {
      M(Z), P.call(V, Z);
    }, null, $), y);
  }
  e.forEach = s;
  function a(I, M, y) {
    return h((P, V = null, $) => I((Z) => M(Z) && P.call(V, Z), null, $), y);
  }
  e.filter = a;
  function u(I) {
    return I;
  }
  e.signal = u;
  function o(...I) {
    return (M, y = null, P) => {
      const V = Zs(...I.map(($) => $((Z) => M.call(y, Z))));
      return f(V, P);
    };
  }
  e.any = o;
  function c(I, M, y, P) {
    let V = y;
    return r(I, ($) => (V = M(V, $), V), P);
  }
  e.reduce = c;
  function h(I, M) {
    let y;
    const P = {
      onWillAddFirstListener() {
        y = I(V.fire, V);
      },
      onDidRemoveLastListener() {
        y == null || y.dispose();
      }
    }, V = new Ae(P);
    return M == null || M.add(V), V.event;
  }
  function f(I, M) {
    return M instanceof Array ? M.push(I) : M && M.add(I), I;
  }
  function _(I, M, y = 100, P = !1, V = !1, $, Z) {
    let le, me, at, Jt = 0, Ke;
    const Rs = {
      leakWarningThreshold: $,
      onWillAddFirstListener() {
        le = I((Ts) => {
          Jt++, me = M(me, Ts), P && !at && (Kt.fire(me), me = void 0), Ke = () => {
            const Us = me;
            me = void 0, at = void 0, (!P || Jt > 1) && Kt.fire(Us), Jt = 0;
          }, typeof y == "number" ? (clearTimeout(at), at = setTimeout(Ke, y)) : at === void 0 && (at = 0, queueMicrotask(Ke));
        });
      },
      onWillRemoveListener() {
        V && Jt > 0 && (Ke == null || Ke());
      },
      onDidRemoveLastListener() {
        Ke = void 0, le.dispose();
      }
    }, Kt = new Ae(Rs);
    return Z == null || Z.add(Kt), Kt.event;
  }
  e.debounce = _;
  function p(I, M = 0, y) {
    return e.debounce(I, (P, V) => P ? (P.push(V), P) : [V], M, void 0, !0, void 0, y);
  }
  e.accumulate = p;
  function d(I, M = (P, V) => P === V, y) {
    let P = !0, V;
    return a(I, ($) => {
      const Z = P || !M($, V);
      return P = !1, V = $, Z;
    }, y);
  }
  e.latch = d;
  function b(I, M, y) {
    return [
      e.filter(I, M, y),
      e.filter(I, (P) => !M(P), y)
    ];
  }
  e.split = b;
  function A(I, M = !1, y = [], P) {
    let V = y.slice(), $ = I((me) => {
      V ? V.push(me) : le.fire(me);
    });
    P && P.add($);
    const Z = () => {
      V == null || V.forEach((me) => le.fire(me)), V = null;
    }, le = new Ae({
      onWillAddFirstListener() {
        $ || ($ = I((me) => le.fire(me)), P && P.add($));
      },
      onDidAddFirstListener() {
        V && (M ? setTimeout(Z) : Z());
      },
      onDidRemoveLastListener() {
        $ && $.dispose(), $ = null;
      }
    });
    return P && P.add(le), le.event;
  }
  e.buffer = A;
  function v(I, M) {
    return (P, V, $) => {
      const Z = M(new R());
      return I(function(le) {
        const me = Z.evaluate(le);
        me !== x && P.call(V, me);
      }, void 0, $);
    };
  }
  e.chain = v;
  const x = Symbol("HaltChainable");
  class R {
    constructor() {
      this.steps = [];
    }
    map(M) {
      return this.steps.push(M), this;
    }
    forEach(M) {
      return this.steps.push((y) => (M(y), y)), this;
    }
    filter(M) {
      return this.steps.push((y) => M(y) ? y : x), this;
    }
    reduce(M, y) {
      let P = y;
      return this.steps.push((V) => (P = M(P, V), P)), this;
    }
    latch(M = (y, P) => y === P) {
      let y = !0, P;
      return this.steps.push((V) => {
        const $ = y || !M(V, P);
        return y = !1, P = V, $ ? V : x;
      }), this;
    }
    evaluate(M) {
      for (const y of this.steps)
        if (M = y(M), M === x)
          break;
      return M;
    }
  }
  function N(I, M, y = (P) => P) {
    const P = (...le) => Z.fire(y(...le)), V = () => I.on(M, P), $ = () => I.removeListener(M, P), Z = new Ae(
      { onWillAddFirstListener: V, onDidRemoveLastListener: $ }
    );
    return Z.event;
  }
  e.fromNodeEventEmitter = N;
  function E(I, M, y = (P) => P) {
    const P = (...le) => Z.fire(y(...le)), V = () => I.addEventListener(M, P), $ = () => I.removeEventListener(M, P), Z = new Ae(
      { onWillAddFirstListener: V, onDidRemoveLastListener: $ }
    );
    return Z.event;
  }
  e.fromDOMEventEmitter = E;
  function U(I, M) {
    return new Promise((y) => n(I)(y, null, M));
  }
  e.toPromise = U;
  function D(I) {
    const M = new Ae();
    return I.then((y) => {
      M.fire(y);
    }, () => {
      M.fire(void 0);
    }).finally(() => {
      M.dispose();
    }), M.event;
  }
  e.fromPromise = D;
  function S(I, M) {
    return I((y) => M.fire(y));
  }
  e.forward = S;
  function X(I, M, y) {
    return M(y), I((P) => M(P));
  }
  e.runAndSubscribe = X;
  class ie {
    constructor(M, y) {
      this._observable = M, this._counter = 0, this._hasChanged = !1;
      const P = {
        onWillAddFirstListener: () => {
          M.addObserver(this), this._observable.reportChanges();
        },
        onDidRemoveLastListener: () => {
          M.removeObserver(this);
        }
      };
      this.emitter = new Ae(P), y && y.add(this.emitter);
    }
    beginUpdate(M) {
      this._counter++;
    }
    handlePossibleChange(M) {
    }
    handleChange(M, y) {
      this._hasChanged = !0;
    }
    endUpdate(M) {
      this._counter--, this._counter === 0 && (this._observable.reportChanges(), this._hasChanged && (this._hasChanged = !1, this.emitter.fire(this._observable.get())));
    }
  }
  function Y(I, M) {
    return new ie(I, M).emitter.event;
  }
  e.fromObservable = Y;
  function H(I) {
    return (M, y, P) => {
      let V = 0, $ = !1;
      const Z = {
        beginUpdate() {
          V++;
        },
        endUpdate() {
          V--, V === 0 && (I.reportChanges(), $ && ($ = !1, M.call(y)));
        },
        handlePossibleChange() {
        },
        handleChange() {
          $ = !0;
        }
      };
      I.addObserver(Z), I.reportChanges();
      const le = {
        dispose() {
          I.removeObserver(Z);
        }
      };
      return P instanceof zt ? P.add(le) : Array.isArray(P) && P.push(le), le;
    };
  }
  e.fromObservableLight = H;
})(fn || (fn = {}));
const wt = class wt {
  constructor(t) {
    this.listenerCount = 0, this.invocationCount = 0, this.elapsedOverall = 0, this.durations = [], this.name = `${t}_${wt._idPool++}`, wt.all.add(this);
  }
  start(t) {
    this._stopWatch = new Dn(), this.listenerCount = t;
  }
  stop() {
    if (this._stopWatch) {
      const t = this._stopWatch.elapsed();
      this.durations.push(t), this.elapsedOverall += t, this.invocationCount += 1, this._stopWatch = void 0;
    }
  }
};
wt.all = /* @__PURE__ */ new Set(), wt._idPool = 0;
let Gn = wt, Cs = -1;
const vn = class vn {
  constructor(t, n, i = (vn._idPool++).toString(16).padStart(3, "0")) {
    this._errorHandler = t, this.threshold = n, this.name = i, this._warnCountdown = 0;
  }
  dispose() {
    var t;
    (t = this._stacks) == null || t.clear();
  }
  check(t, n) {
    const i = this.threshold;
    if (i <= 0 || n < i)
      return;
    this._stacks || (this._stacks = /* @__PURE__ */ new Map());
    const r = this._stacks.get(t.value) || 0;
    if (this._stacks.set(t.value, r + 1), this._warnCountdown -= 1, this._warnCountdown <= 0) {
      this._warnCountdown = i * 0.5;
      const [s, a] = this.getMostFrequentStack(), u = `[${this.name}] potential listener LEAK detected, having ${n} listeners already. MOST frequent listener (${a}):`;
      console.warn(u), console.warn(s);
      const o = new ea(u, s);
      this._errorHandler(o);
    }
    return () => {
      const s = this._stacks.get(t.value) || 0;
      this._stacks.set(t.value, s - 1);
    };
  }
  getMostFrequentStack() {
    if (!this._stacks)
      return;
    let t, n = 0;
    for (const [i, r] of this._stacks)
      (!t || n < r) && (t = [i, r], n = r);
    return t;
  }
};
vn._idPool = 1;
let $n = vn;
class fi {
  static create() {
    const t = new Error();
    return new fi(t.stack ?? "");
  }
  constructor(t) {
    this.value = t;
  }
  print() {
    console.warn(this.value.split(`
`).slice(2).join(`
`));
  }
}
class ea extends Error {
  constructor(t, n) {
    super(t), this.name = "ListenerLeakError", this.stack = n;
  }
}
class ta extends Error {
  constructor(t, n) {
    super(t), this.name = "ListenerRefusalError", this.stack = n;
  }
}
let na = 0;
class kn {
  constructor(t) {
    this.value = t, this.id = na++;
  }
}
const ia = 2;
class Ae {
  constructor(t) {
    var n, i, r, s;
    this._size = 0, this._options = t, this._leakageMon = (n = this._options) != null && n.leakWarningThreshold ? new $n(
      (t == null ? void 0 : t.onListenerError) ?? St,
      ((i = this._options) == null ? void 0 : i.leakWarningThreshold) ?? Cs
    ) : void 0, this._perfMon = (r = this._options) != null && r._profName ? new Gn(this._options._profName) : void 0, this._deliveryQueue = (s = this._options) == null ? void 0 : s.deliveryQueue;
  }
  dispose() {
    var t, n, i, r;
    this._disposed || (this._disposed = !0, ((t = this._deliveryQueue) == null ? void 0 : t.current) === this && this._deliveryQueue.reset(), this._listeners && (this._listeners = void 0, this._size = 0), (i = (n = this._options) == null ? void 0 : n.onDidRemoveLastListener) == null || i.call(n), (r = this._leakageMon) == null || r.dispose());
  }
  get event() {
    return this._event ?? (this._event = (t, n, i) => {
      var u, o, c, h, f, _, p;
      if (this._leakageMon && this._size > this._leakageMon.threshold ** 2) {
        const d = `[${this._leakageMon.name}] REFUSES to accept new listeners because it exceeded its threshold by far (${this._size} vs ${this._leakageMon.threshold})`;
        console.warn(d);
        const b = this._leakageMon.getMostFrequentStack() ?? ["UNKNOWN stack", -1], A = new ta(
          `${d}. HINT: Stack shows most frequent listener (${b[1]}-times)`,
          b[0]
        );
        return (((u = this._options) == null ? void 0 : u.onListenerError) || St)(A), Rt.None;
      }
      if (this._disposed)
        return Rt.None;
      n && (t = t.bind(n));
      const r = new kn(t);
      let s;
      this._leakageMon && this._size >= Math.ceil(this._leakageMon.threshold * 0.2) && (r.stack = fi.create(), s = this._leakageMon.check(r.stack, this._size + 1)), this._listeners ? this._listeners instanceof kn ? (this._deliveryQueue ?? (this._deliveryQueue = new ra()), this._listeners = [this._listeners, r]) : this._listeners.push(r) : ((c = (o = this._options) == null ? void 0 : o.onWillAddFirstListener) == null || c.call(o, this), this._listeners = r, (f = (h = this._options) == null ? void 0 : h.onDidAddFirstListener) == null || f.call(h, this)), (p = (_ = this._options) == null ? void 0 : _.onDidAddListener) == null || p.call(_, this), this._size++;
      const a = $t(() => {
        s == null || s(), this._removeListener(r);
      });
      return i instanceof zt ? i.add(a) : Array.isArray(i) && i.push(a), a;
    }), this._event;
  }
  _removeListener(t) {
    var s, a, u, o;
    if ((a = (s = this._options) == null ? void 0 : s.onWillRemoveListener) == null || a.call(s, this), !this._listeners)
      return;
    if (this._size === 1) {
      this._listeners = void 0, (o = (u = this._options) == null ? void 0 : u.onDidRemoveLastListener) == null || o.call(u, this), this._size = 0;
      return;
    }
    const n = this._listeners, i = n.indexOf(t);
    if (i === -1)
      throw console.log("disposed?", this._disposed), console.log("size?", this._size), console.log("arr?", JSON.stringify(this._listeners)), new Error("Attempted to dispose unknown listener");
    this._size--, n[i] = void 0;
    const r = this._deliveryQueue.current === this;
    if (this._size * ia <= n.length) {
      let c = 0;
      for (let h = 0; h < n.length; h++)
        n[h] ? n[c++] = n[h] : r && c < this._deliveryQueue.end && (this._deliveryQueue.end--, c < this._deliveryQueue.i && this._deliveryQueue.i--);
      n.length = c;
    }
  }
  _deliver(t, n) {
    var r;
    if (!t)
      return;
    const i = ((r = this._options) == null ? void 0 : r.onListenerError) || St;
    if (!i) {
      t.value(n);
      return;
    }
    try {
      t.value(n);
    } catch (s) {
      i(s);
    }
  }
  _deliverQueue(t) {
    const n = t.current._listeners;
    for (; t.i < t.end; )
      this._deliver(n[t.i++], t.value);
    t.reset();
  }
  fire(t) {
    var n, i, r, s;
    if ((n = this._deliveryQueue) != null && n.current && (this._deliverQueue(this._deliveryQueue), (i = this._perfMon) == null || i.stop()), (r = this._perfMon) == null || r.start(this._size), this._listeners) if (this._listeners instanceof kn)
      this._deliver(this._listeners, t);
    else {
      const a = this._deliveryQueue;
      a.enqueue(this, t, this._listeners.length), this._deliverQueue(a);
    }
    (s = this._perfMon) == null || s.stop();
  }
  hasListeners() {
    return this._size > 0;
  }
}
class ra {
  constructor() {
    this.i = -1, this.end = 0;
  }
  enqueue(t, n, i) {
    this.i = 0, this.end = i, this.current = t, this.value = n;
  }
  reset() {
    this.i = this.end, this.current = void 0, this.value = void 0;
  }
}
function sa() {
  return globalThis._VSCODE_NLS_MESSAGES;
}
function Cr() {
  return globalThis._VSCODE_NLS_LANGUAGE;
}
const aa = Cr() === "pseudo" || typeof document < "u" && document.location && typeof document.location.hash == "string" && document.location.hash.indexOf("pseudo=true") >= 0;
function Ai(e, t) {
  let n;
  return t.length === 0 ? n = e : n = e.replace(/\{(\d+)\}/g, (i, r) => {
    const s = r[0], a = t[s];
    let u = i;
    return typeof a == "string" ? u = a : (typeof a == "number" || typeof a == "boolean" || a === void 0 || a === null) && (u = String(a)), u;
  }), aa && (n = "［" + n.replace(/[aouei]/g, "$&$&") + "］"), n;
}
function ee(e, t, ...n) {
  return Ai(typeof e == "number" ? la(e, t) : t, n);
}
function la(e, t) {
  var i;
  const n = (i = sa()) == null ? void 0 : i[e];
  if (typeof n != "string") {
    if (typeof t == "string")
      return t;
    throw new Error(`!!! NLS MISSING: ${e} !!!`);
  }
  return n;
}
const mt = "en";
let jt = !1, Xt = !1, rn = !1, es = !1, mi = !1, ts = !1, Ct, sn = mt, vi = mt, ua, Me;
const Ve = globalThis;
let he;
var jr;
typeof Ve.vscode < "u" && typeof Ve.vscode.process < "u" ? he = Ve.vscode.process : typeof process < "u" && typeof ((jr = process == null ? void 0 : process.versions) == null ? void 0 : jr.node) == "string" && (he = process);
var Xr;
const oa = typeof ((Xr = he == null ? void 0 : he.versions) == null ? void 0 : Xr.electron) == "string", ca = oa && (he == null ? void 0 : he.type) === "renderer";
var Yr;
if (typeof he == "object") {
  jt = he.platform === "win32", Xt = he.platform === "darwin", rn = he.platform === "linux", rn && he.env.SNAP && he.env.SNAP_REVISION, he.env.CI || he.env.BUILD_ARTIFACTSTAGINGDIRECTORY, Ct = mt, sn = mt;
  const e = he.env.VSCODE_NLS_CONFIG;
  if (e)
    try {
      const t = JSON.parse(e);
      Ct = t.userLocale, vi = t.osLocale, sn = t.resolvedLanguage || mt, ua = (Yr = t.languagePack) == null ? void 0 : Yr.translationsConfigFile;
    } catch {
    }
  es = !0;
} else typeof navigator == "object" && !ca ? (Me = navigator.userAgent, jt = Me.indexOf("Windows") >= 0, Xt = Me.indexOf("Macintosh") >= 0, ts = (Me.indexOf("Macintosh") >= 0 || Me.indexOf("iPad") >= 0 || Me.indexOf("iPhone") >= 0) && !!navigator.maxTouchPoints && navigator.maxTouchPoints > 0, rn = Me.indexOf("Linux") >= 0, (Me == null ? void 0 : Me.indexOf("Mobi")) >= 0, mi = !0, sn = Cr() || mt, Ct = navigator.language.toLowerCase(), vi = Ct) : console.error("Unable to resolve platform.");
var Nt;
(function(e) {
  e[e.Web = 0] = "Web", e[e.Mac = 1] = "Mac", e[e.Linux = 2] = "Linux", e[e.Windows = 3] = "Windows";
})(Nt || (Nt = {}));
Nt.Web;
Xt ? Nt.Mac : jt ? Nt.Windows : rn && Nt.Linux;
const Tt = jt, ha = Xt, fa = es, ma = mi, ga = mi && typeof Ve.importScripts == "function", _a = ga ? Ve.origin : void 0, Pe = Me, We = sn;
var Ri;
(function(e) {
  function t() {
    return We;
  }
  e.value = t;
  function n() {
    return We.length === 2 ? We === "en" : We.length >= 3 ? We[0] === "e" && We[1] === "n" && We[2] === "-" : !1;
  }
  e.isDefaultVariant = n;
  function i() {
    return We === "en";
  }
  e.isDefault = i;
})(Ri || (Ri = {}));
const ba = typeof Ve.postMessage == "function" && !Ve.importScripts;
(() => {
  if (ba) {
    const e = [];
    Ve.addEventListener("message", (n) => {
      if (n.data && n.data.vscodeScheduleAsyncWork)
        for (let i = 0, r = e.length; i < r; i++) {
          const s = e[i];
          if (s.id === n.data.vscodeScheduleAsyncWork) {
            e.splice(i, 1), s.callback();
            return;
          }
        }
    });
    let t = 0;
    return (n) => {
      const i = ++t;
      e.push({
        id: i,
        callback: n
      }), Ve.postMessage({ vscodeScheduleAsyncWork: i }, "*");
    };
  }
  return (e) => setTimeout(e);
})();
var Bt;
(function(e) {
  e[e.Windows = 1] = "Windows", e[e.Macintosh = 2] = "Macintosh", e[e.Linux = 3] = "Linux";
})(Bt || (Bt = {}));
Xt || ts ? Bt.Macintosh : jt ? Bt.Windows : Bt.Linux;
const da = !!(Pe && Pe.indexOf("Chrome") >= 0);
Pe && Pe.indexOf("Firefox") >= 0;
!da && Pe && Pe.indexOf("Safari") >= 0;
Pe && Pe.indexOf("Edg/") >= 0;
Pe && Pe.indexOf("Android") >= 0;
const ns = Object.freeze(function(e, t) {
  const n = setTimeout(e.bind(t), 0);
  return { dispose() {
    clearTimeout(n);
  } };
});
var mn;
(function(e) {
  function t(n) {
    return n === e.None || n === e.Cancelled || n instanceof an ? !0 : !n || typeof n != "object" ? !1 : typeof n.isCancellationRequested == "boolean" && typeof n.onCancellationRequested == "function";
  }
  e.isCancellationToken = t, e.None = Object.freeze({
    isCancellationRequested: !1,
    onCancellationRequested: fn.None
  }), e.Cancelled = Object.freeze({
    isCancellationRequested: !0,
    onCancellationRequested: ns
  });
})(mn || (mn = {}));
class an {
  constructor() {
    this._isCancelled = !1, this._emitter = null;
  }
  cancel() {
    this._isCancelled || (this._isCancelled = !0, this._emitter && (this._emitter.fire(void 0), this.dispose()));
  }
  get isCancellationRequested() {
    return this._isCancelled;
  }
  get onCancellationRequested() {
    return this._isCancelled ? ns : (this._emitter || (this._emitter = new Ae()), this._emitter.event);
  }
  dispose() {
    this._emitter && (this._emitter.dispose(), this._emitter = null);
  }
}
class wa {
  constructor(t) {
    this._token = void 0, this._parentListener = void 0, this._parentListener = t && t.onCancellationRequested(this.cancel, this);
  }
  get token() {
    return this._token || (this._token = new an()), this._token;
  }
  cancel() {
    this._token ? this._token instanceof an && this._token.cancel() : this._token = mn.Cancelled;
  }
  dispose(t = !1) {
    var n;
    t && this.cancel(), (n = this._parentListener) == null || n.dispose(), this._token ? this._token instanceof an && this._token.dispose() : this._token = mn.None;
  }
}
function La(e) {
  return e;
}
class pa {
  constructor(t, n) {
    this.lastCache = void 0, this.lastArgKey = void 0, typeof t == "function" ? (this._fn = t, this._computeKey = La) : (this._fn = n, this._computeKey = t.getCacheKey);
  }
  get(t) {
    const n = this._computeKey(t);
    return this.lastArgKey !== n && (this.lastArgKey = n, this.lastCache = this._fn(t)), this.lastCache;
  }
}
class Ti {
  constructor(t) {
    this.executor = t, this._didRun = !1;
  }
  get hasValue() {
    return this._didRun;
  }
  get value() {
    if (!this._didRun)
      try {
        this._value = this.executor();
      } catch (t) {
        this._error = t;
      } finally {
        this._didRun = !0;
      }
    if (this._error)
      throw this._error;
    return this._value;
  }
  get rawValue() {
    return this._value;
  }
}
var Ue;
(function(e) {
  e[e.MAX_SAFE_SMALL_INTEGER = 1073741824] = "MAX_SAFE_SMALL_INTEGER", e[e.MIN_SAFE_SMALL_INTEGER = -1073741824] = "MIN_SAFE_SMALL_INTEGER", e[e.MAX_UINT_8 = 255] = "MAX_UINT_8", e[e.MAX_UINT_16 = 65535] = "MAX_UINT_16", e[e.MAX_UINT_32 = 4294967295] = "MAX_UINT_32", e[e.UNICODE_SUPPLEMENTARY_PLANE_BEGIN = 65536] = "UNICODE_SUPPLEMENTARY_PLANE_BEGIN";
})(Ue || (Ue = {}));
function Ui(e) {
  return e < 0 ? 0 : e > Ue.MAX_UINT_8 ? Ue.MAX_UINT_8 : e | 0;
}
function lt(e) {
  return e < 0 ? 0 : e > Ue.MAX_UINT_32 ? Ue.MAX_UINT_32 : e | 0;
}
function Na(e) {
  return e.replace(/[\\\{\}\*\+\?\|\^\$\.\[\]\(\)]/g, "\\$&");
}
function is(e) {
  return e.split(/\r\n|\r|\n/);
}
function Ea(e) {
  for (let t = 0, n = e.length; t < n; t++) {
    const i = e.charCodeAt(t);
    if (i !== L.Space && i !== L.Tab)
      return t;
  }
  return -1;
}
function xa(e, t = e.length - 1) {
  for (let n = t; n >= 0; n--) {
    const i = e.charCodeAt(n);
    if (i !== L.Space && i !== L.Tab)
      return n;
  }
  return -1;
}
function Aa(e, t) {
  return e < t ? -1 : e > t ? 1 : 0;
}
function va(e, t, n = 0, i = e.length, r = 0, s = t.length) {
  for (; n < i && r < s; n++, r++) {
    const o = e.charCodeAt(n), c = t.charCodeAt(r);
    if (o < c)
      return -1;
    if (o > c)
      return 1;
  }
  const a = i - n, u = s - r;
  return a < u ? -1 : a > u ? 1 : 0;
}
function rs(e, t, n = 0, i = e.length, r = 0, s = t.length) {
  for (; n < i && r < s; n++, r++) {
    let o = e.charCodeAt(n), c = t.charCodeAt(r);
    if (o === c)
      continue;
    if (o >= 128 || c >= 128)
      return va(e.toLowerCase(), t.toLowerCase(), n, i, r, s);
    Mi(o) && (o -= 32), Mi(c) && (c -= 32);
    const h = o - c;
    if (h !== 0)
      return h;
  }
  const a = i - n, u = s - r;
  return a < u ? -1 : a > u ? 1 : 0;
}
function Mi(e) {
  return e >= L.a && e <= L.z;
}
function ss(e) {
  return e >= L.A && e <= L.Z;
}
function Ra(e, t) {
  return e.length === t.length && rs(e, t) === 0;
}
function Ta(e, t) {
  const n = t.length;
  return t.length > e.length ? !1 : rs(e, t, 0, n) === 0;
}
function Di(e, t) {
  const n = Math.min(e.length, t.length);
  let i;
  for (i = 0; i < n; i++)
    if (e.charCodeAt(i) !== t.charCodeAt(i))
      return i;
  return n;
}
function Ua(e, t) {
  const n = Math.min(e.length, t.length);
  let i;
  const r = e.length - 1, s = t.length - 1;
  for (i = 0; i < n; i++)
    if (e.charCodeAt(r - i) !== t.charCodeAt(s - i))
      return i;
  return n;
}
function gn(e) {
  return 55296 <= e && e <= 56319;
}
function zn(e) {
  return 56320 <= e && e <= 57343;
}
function as(e, t) {
  return (e - 55296 << 10) + (t - 56320) + 65536;
}
function Ma(e, t, n) {
  const i = e.charCodeAt(n);
  if (gn(i) && n + 1 < t) {
    const r = e.charCodeAt(n + 1);
    if (zn(r))
      return as(i, r);
  }
  return i;
}
const Da = /^[\t\n\r\x20-\x7E]*$/;
function ka(e) {
  return Da.test(e);
}
String.fromCharCode(L.UTF8_BOM);
var Ce;
(function(e) {
  e[e.Other = 0] = "Other", e[e.Prepend = 1] = "Prepend", e[e.CR = 2] = "CR", e[e.LF = 3] = "LF", e[e.Control = 4] = "Control", e[e.Extend = 5] = "Extend", e[e.Regional_Indicator = 6] = "Regional_Indicator", e[e.SpacingMark = 7] = "SpacingMark", e[e.L = 8] = "L", e[e.V = 9] = "V", e[e.T = 10] = "T", e[e.LV = 11] = "LV", e[e.LVT = 12] = "LVT", e[e.ZWJ = 13] = "ZWJ", e[e.Extended_Pictographic = 14] = "Extended_Pictographic";
})(Ce || (Ce = {}));
const nt = class nt {
  static getInstance() {
    return nt._INSTANCE || (nt._INSTANCE = new nt()), nt._INSTANCE;
  }
  constructor() {
    this._data = Fa();
  }
  getGraphemeBreakType(t) {
    if (t < 32)
      return t === L.LineFeed ? Ce.LF : t === L.CarriageReturn ? Ce.CR : Ce.Control;
    if (t < 127)
      return Ce.Other;
    const n = this._data, i = n.length / 3;
    let r = 1;
    for (; r <= i; )
      if (t < n[3 * r])
        r = 2 * r;
      else if (t > n[3 * r + 1])
        r = 2 * r + 1;
      else
        return n[3 * r + 2];
    return Ce.Other;
  }
};
nt._INSTANCE = null;
let ki = nt;
function Fa() {
  return JSON.parse("[0,0,0,51229,51255,12,44061,44087,12,127462,127487,6,7083,7085,5,47645,47671,12,54813,54839,12,128678,128678,14,3270,3270,5,9919,9923,14,45853,45879,12,49437,49463,12,53021,53047,12,71216,71218,7,128398,128399,14,129360,129374,14,2519,2519,5,4448,4519,9,9742,9742,14,12336,12336,14,44957,44983,12,46749,46775,12,48541,48567,12,50333,50359,12,52125,52151,12,53917,53943,12,69888,69890,5,73018,73018,5,127990,127990,14,128558,128559,14,128759,128760,14,129653,129655,14,2027,2035,5,2891,2892,7,3761,3761,5,6683,6683,5,8293,8293,4,9825,9826,14,9999,9999,14,43452,43453,5,44509,44535,12,45405,45431,12,46301,46327,12,47197,47223,12,48093,48119,12,48989,49015,12,49885,49911,12,50781,50807,12,51677,51703,12,52573,52599,12,53469,53495,12,54365,54391,12,65279,65279,4,70471,70472,7,72145,72147,7,119173,119179,5,127799,127818,14,128240,128244,14,128512,128512,14,128652,128652,14,128721,128722,14,129292,129292,14,129445,129450,14,129734,129743,14,1476,1477,5,2366,2368,7,2750,2752,7,3076,3076,5,3415,3415,5,4141,4144,5,6109,6109,5,6964,6964,5,7394,7400,5,9197,9198,14,9770,9770,14,9877,9877,14,9968,9969,14,10084,10084,14,43052,43052,5,43713,43713,5,44285,44311,12,44733,44759,12,45181,45207,12,45629,45655,12,46077,46103,12,46525,46551,12,46973,46999,12,47421,47447,12,47869,47895,12,48317,48343,12,48765,48791,12,49213,49239,12,49661,49687,12,50109,50135,12,50557,50583,12,51005,51031,12,51453,51479,12,51901,51927,12,52349,52375,12,52797,52823,12,53245,53271,12,53693,53719,12,54141,54167,12,54589,54615,12,55037,55063,12,69506,69509,5,70191,70193,5,70841,70841,7,71463,71467,5,72330,72342,5,94031,94031,5,123628,123631,5,127763,127765,14,127941,127941,14,128043,128062,14,128302,128317,14,128465,128467,14,128539,128539,14,128640,128640,14,128662,128662,14,128703,128703,14,128745,128745,14,129004,129007,14,129329,129330,14,129402,129402,14,129483,129483,14,129686,129704,14,130048,131069,14,173,173,4,1757,1757,1,2200,2207,5,2434,2435,7,2631,2632,5,2817,2817,5,3008,3008,5,3201,3201,5,3387,3388,5,3542,3542,5,3902,3903,7,4190,4192,5,6002,6003,5,6439,6440,5,6765,6770,7,7019,7027,5,7154,7155,7,8205,8205,13,8505,8505,14,9654,9654,14,9757,9757,14,9792,9792,14,9852,9853,14,9890,9894,14,9937,9937,14,9981,9981,14,10035,10036,14,11035,11036,14,42654,42655,5,43346,43347,7,43587,43587,5,44006,44007,7,44173,44199,12,44397,44423,12,44621,44647,12,44845,44871,12,45069,45095,12,45293,45319,12,45517,45543,12,45741,45767,12,45965,45991,12,46189,46215,12,46413,46439,12,46637,46663,12,46861,46887,12,47085,47111,12,47309,47335,12,47533,47559,12,47757,47783,12,47981,48007,12,48205,48231,12,48429,48455,12,48653,48679,12,48877,48903,12,49101,49127,12,49325,49351,12,49549,49575,12,49773,49799,12,49997,50023,12,50221,50247,12,50445,50471,12,50669,50695,12,50893,50919,12,51117,51143,12,51341,51367,12,51565,51591,12,51789,51815,12,52013,52039,12,52237,52263,12,52461,52487,12,52685,52711,12,52909,52935,12,53133,53159,12,53357,53383,12,53581,53607,12,53805,53831,12,54029,54055,12,54253,54279,12,54477,54503,12,54701,54727,12,54925,54951,12,55149,55175,12,68101,68102,5,69762,69762,7,70067,70069,7,70371,70378,5,70720,70721,7,71087,71087,5,71341,71341,5,71995,71996,5,72249,72249,7,72850,72871,5,73109,73109,5,118576,118598,5,121505,121519,5,127245,127247,14,127568,127569,14,127777,127777,14,127872,127891,14,127956,127967,14,128015,128016,14,128110,128172,14,128259,128259,14,128367,128368,14,128424,128424,14,128488,128488,14,128530,128532,14,128550,128551,14,128566,128566,14,128647,128647,14,128656,128656,14,128667,128673,14,128691,128693,14,128715,128715,14,128728,128732,14,128752,128752,14,128765,128767,14,129096,129103,14,129311,129311,14,129344,129349,14,129394,129394,14,129413,129425,14,129466,129471,14,129511,129535,14,129664,129666,14,129719,129722,14,129760,129767,14,917536,917631,5,13,13,2,1160,1161,5,1564,1564,4,1807,1807,1,2085,2087,5,2307,2307,7,2382,2383,7,2497,2500,5,2563,2563,7,2677,2677,5,2763,2764,7,2879,2879,5,2914,2915,5,3021,3021,5,3142,3144,5,3263,3263,5,3285,3286,5,3398,3400,7,3530,3530,5,3633,3633,5,3864,3865,5,3974,3975,5,4155,4156,7,4229,4230,5,5909,5909,7,6078,6085,7,6277,6278,5,6451,6456,7,6744,6750,5,6846,6846,5,6972,6972,5,7074,7077,5,7146,7148,7,7222,7223,5,7416,7417,5,8234,8238,4,8417,8417,5,9000,9000,14,9203,9203,14,9730,9731,14,9748,9749,14,9762,9763,14,9776,9783,14,9800,9811,14,9831,9831,14,9872,9873,14,9882,9882,14,9900,9903,14,9929,9933,14,9941,9960,14,9974,9974,14,9989,9989,14,10006,10006,14,10062,10062,14,10160,10160,14,11647,11647,5,12953,12953,14,43019,43019,5,43232,43249,5,43443,43443,5,43567,43568,7,43696,43696,5,43765,43765,7,44013,44013,5,44117,44143,12,44229,44255,12,44341,44367,12,44453,44479,12,44565,44591,12,44677,44703,12,44789,44815,12,44901,44927,12,45013,45039,12,45125,45151,12,45237,45263,12,45349,45375,12,45461,45487,12,45573,45599,12,45685,45711,12,45797,45823,12,45909,45935,12,46021,46047,12,46133,46159,12,46245,46271,12,46357,46383,12,46469,46495,12,46581,46607,12,46693,46719,12,46805,46831,12,46917,46943,12,47029,47055,12,47141,47167,12,47253,47279,12,47365,47391,12,47477,47503,12,47589,47615,12,47701,47727,12,47813,47839,12,47925,47951,12,48037,48063,12,48149,48175,12,48261,48287,12,48373,48399,12,48485,48511,12,48597,48623,12,48709,48735,12,48821,48847,12,48933,48959,12,49045,49071,12,49157,49183,12,49269,49295,12,49381,49407,12,49493,49519,12,49605,49631,12,49717,49743,12,49829,49855,12,49941,49967,12,50053,50079,12,50165,50191,12,50277,50303,12,50389,50415,12,50501,50527,12,50613,50639,12,50725,50751,12,50837,50863,12,50949,50975,12,51061,51087,12,51173,51199,12,51285,51311,12,51397,51423,12,51509,51535,12,51621,51647,12,51733,51759,12,51845,51871,12,51957,51983,12,52069,52095,12,52181,52207,12,52293,52319,12,52405,52431,12,52517,52543,12,52629,52655,12,52741,52767,12,52853,52879,12,52965,52991,12,53077,53103,12,53189,53215,12,53301,53327,12,53413,53439,12,53525,53551,12,53637,53663,12,53749,53775,12,53861,53887,12,53973,53999,12,54085,54111,12,54197,54223,12,54309,54335,12,54421,54447,12,54533,54559,12,54645,54671,12,54757,54783,12,54869,54895,12,54981,55007,12,55093,55119,12,55243,55291,10,66045,66045,5,68325,68326,5,69688,69702,5,69817,69818,5,69957,69958,7,70089,70092,5,70198,70199,5,70462,70462,5,70502,70508,5,70750,70750,5,70846,70846,7,71100,71101,5,71230,71230,7,71351,71351,5,71737,71738,5,72000,72000,7,72160,72160,5,72273,72278,5,72752,72758,5,72882,72883,5,73031,73031,5,73461,73462,7,94192,94193,7,119149,119149,7,121403,121452,5,122915,122916,5,126980,126980,14,127358,127359,14,127535,127535,14,127759,127759,14,127771,127771,14,127792,127793,14,127825,127867,14,127897,127899,14,127945,127945,14,127985,127986,14,128000,128007,14,128021,128021,14,128066,128100,14,128184,128235,14,128249,128252,14,128266,128276,14,128335,128335,14,128379,128390,14,128407,128419,14,128444,128444,14,128481,128481,14,128499,128499,14,128526,128526,14,128536,128536,14,128543,128543,14,128556,128556,14,128564,128564,14,128577,128580,14,128643,128645,14,128649,128649,14,128654,128654,14,128660,128660,14,128664,128664,14,128675,128675,14,128686,128689,14,128695,128696,14,128705,128709,14,128717,128719,14,128725,128725,14,128736,128741,14,128747,128748,14,128755,128755,14,128762,128762,14,128981,128991,14,129009,129023,14,129160,129167,14,129296,129304,14,129320,129327,14,129340,129342,14,129356,129356,14,129388,129392,14,129399,129400,14,129404,129407,14,129432,129442,14,129454,129455,14,129473,129474,14,129485,129487,14,129648,129651,14,129659,129660,14,129671,129679,14,129709,129711,14,129728,129730,14,129751,129753,14,129776,129782,14,917505,917505,4,917760,917999,5,10,10,3,127,159,4,768,879,5,1471,1471,5,1536,1541,1,1648,1648,5,1767,1768,5,1840,1866,5,2070,2073,5,2137,2139,5,2274,2274,1,2363,2363,7,2377,2380,7,2402,2403,5,2494,2494,5,2507,2508,7,2558,2558,5,2622,2624,7,2641,2641,5,2691,2691,7,2759,2760,5,2786,2787,5,2876,2876,5,2881,2884,5,2901,2902,5,3006,3006,5,3014,3016,7,3072,3072,5,3134,3136,5,3157,3158,5,3260,3260,5,3266,3266,5,3274,3275,7,3328,3329,5,3391,3392,7,3405,3405,5,3457,3457,5,3536,3537,7,3551,3551,5,3636,3642,5,3764,3772,5,3895,3895,5,3967,3967,7,3993,4028,5,4146,4151,5,4182,4183,7,4226,4226,5,4253,4253,5,4957,4959,5,5940,5940,7,6070,6070,7,6087,6088,7,6158,6158,4,6432,6434,5,6448,6449,7,6679,6680,5,6742,6742,5,6754,6754,5,6783,6783,5,6912,6915,5,6966,6970,5,6978,6978,5,7042,7042,7,7080,7081,5,7143,7143,7,7150,7150,7,7212,7219,5,7380,7392,5,7412,7412,5,8203,8203,4,8232,8232,4,8265,8265,14,8400,8412,5,8421,8432,5,8617,8618,14,9167,9167,14,9200,9200,14,9410,9410,14,9723,9726,14,9733,9733,14,9745,9745,14,9752,9752,14,9760,9760,14,9766,9766,14,9774,9774,14,9786,9786,14,9794,9794,14,9823,9823,14,9828,9828,14,9833,9850,14,9855,9855,14,9875,9875,14,9880,9880,14,9885,9887,14,9896,9897,14,9906,9916,14,9926,9927,14,9935,9935,14,9939,9939,14,9962,9962,14,9972,9972,14,9978,9978,14,9986,9986,14,9997,9997,14,10002,10002,14,10017,10017,14,10055,10055,14,10071,10071,14,10133,10135,14,10548,10549,14,11093,11093,14,12330,12333,5,12441,12442,5,42608,42610,5,43010,43010,5,43045,43046,5,43188,43203,7,43302,43309,5,43392,43394,5,43446,43449,5,43493,43493,5,43571,43572,7,43597,43597,7,43703,43704,5,43756,43757,5,44003,44004,7,44009,44010,7,44033,44059,12,44089,44115,12,44145,44171,12,44201,44227,12,44257,44283,12,44313,44339,12,44369,44395,12,44425,44451,12,44481,44507,12,44537,44563,12,44593,44619,12,44649,44675,12,44705,44731,12,44761,44787,12,44817,44843,12,44873,44899,12,44929,44955,12,44985,45011,12,45041,45067,12,45097,45123,12,45153,45179,12,45209,45235,12,45265,45291,12,45321,45347,12,45377,45403,12,45433,45459,12,45489,45515,12,45545,45571,12,45601,45627,12,45657,45683,12,45713,45739,12,45769,45795,12,45825,45851,12,45881,45907,12,45937,45963,12,45993,46019,12,46049,46075,12,46105,46131,12,46161,46187,12,46217,46243,12,46273,46299,12,46329,46355,12,46385,46411,12,46441,46467,12,46497,46523,12,46553,46579,12,46609,46635,12,46665,46691,12,46721,46747,12,46777,46803,12,46833,46859,12,46889,46915,12,46945,46971,12,47001,47027,12,47057,47083,12,47113,47139,12,47169,47195,12,47225,47251,12,47281,47307,12,47337,47363,12,47393,47419,12,47449,47475,12,47505,47531,12,47561,47587,12,47617,47643,12,47673,47699,12,47729,47755,12,47785,47811,12,47841,47867,12,47897,47923,12,47953,47979,12,48009,48035,12,48065,48091,12,48121,48147,12,48177,48203,12,48233,48259,12,48289,48315,12,48345,48371,12,48401,48427,12,48457,48483,12,48513,48539,12,48569,48595,12,48625,48651,12,48681,48707,12,48737,48763,12,48793,48819,12,48849,48875,12,48905,48931,12,48961,48987,12,49017,49043,12,49073,49099,12,49129,49155,12,49185,49211,12,49241,49267,12,49297,49323,12,49353,49379,12,49409,49435,12,49465,49491,12,49521,49547,12,49577,49603,12,49633,49659,12,49689,49715,12,49745,49771,12,49801,49827,12,49857,49883,12,49913,49939,12,49969,49995,12,50025,50051,12,50081,50107,12,50137,50163,12,50193,50219,12,50249,50275,12,50305,50331,12,50361,50387,12,50417,50443,12,50473,50499,12,50529,50555,12,50585,50611,12,50641,50667,12,50697,50723,12,50753,50779,12,50809,50835,12,50865,50891,12,50921,50947,12,50977,51003,12,51033,51059,12,51089,51115,12,51145,51171,12,51201,51227,12,51257,51283,12,51313,51339,12,51369,51395,12,51425,51451,12,51481,51507,12,51537,51563,12,51593,51619,12,51649,51675,12,51705,51731,12,51761,51787,12,51817,51843,12,51873,51899,12,51929,51955,12,51985,52011,12,52041,52067,12,52097,52123,12,52153,52179,12,52209,52235,12,52265,52291,12,52321,52347,12,52377,52403,12,52433,52459,12,52489,52515,12,52545,52571,12,52601,52627,12,52657,52683,12,52713,52739,12,52769,52795,12,52825,52851,12,52881,52907,12,52937,52963,12,52993,53019,12,53049,53075,12,53105,53131,12,53161,53187,12,53217,53243,12,53273,53299,12,53329,53355,12,53385,53411,12,53441,53467,12,53497,53523,12,53553,53579,12,53609,53635,12,53665,53691,12,53721,53747,12,53777,53803,12,53833,53859,12,53889,53915,12,53945,53971,12,54001,54027,12,54057,54083,12,54113,54139,12,54169,54195,12,54225,54251,12,54281,54307,12,54337,54363,12,54393,54419,12,54449,54475,12,54505,54531,12,54561,54587,12,54617,54643,12,54673,54699,12,54729,54755,12,54785,54811,12,54841,54867,12,54897,54923,12,54953,54979,12,55009,55035,12,55065,55091,12,55121,55147,12,55177,55203,12,65024,65039,5,65520,65528,4,66422,66426,5,68152,68154,5,69291,69292,5,69633,69633,5,69747,69748,5,69811,69814,5,69826,69826,5,69932,69932,7,70016,70017,5,70079,70080,7,70095,70095,5,70196,70196,5,70367,70367,5,70402,70403,7,70464,70464,5,70487,70487,5,70709,70711,7,70725,70725,7,70833,70834,7,70843,70844,7,70849,70849,7,71090,71093,5,71103,71104,5,71227,71228,7,71339,71339,5,71344,71349,5,71458,71461,5,71727,71735,5,71985,71989,7,71998,71998,5,72002,72002,7,72154,72155,5,72193,72202,5,72251,72254,5,72281,72283,5,72344,72345,5,72766,72766,7,72874,72880,5,72885,72886,5,73023,73029,5,73104,73105,5,73111,73111,5,92912,92916,5,94095,94098,5,113824,113827,4,119142,119142,7,119155,119162,4,119362,119364,5,121476,121476,5,122888,122904,5,123184,123190,5,125252,125258,5,127183,127183,14,127340,127343,14,127377,127386,14,127491,127503,14,127548,127551,14,127744,127756,14,127761,127761,14,127769,127769,14,127773,127774,14,127780,127788,14,127796,127797,14,127820,127823,14,127869,127869,14,127894,127895,14,127902,127903,14,127943,127943,14,127947,127950,14,127972,127972,14,127988,127988,14,127992,127994,14,128009,128011,14,128019,128019,14,128023,128041,14,128064,128064,14,128102,128107,14,128174,128181,14,128238,128238,14,128246,128247,14,128254,128254,14,128264,128264,14,128278,128299,14,128329,128330,14,128348,128359,14,128371,128377,14,128392,128393,14,128401,128404,14,128421,128421,14,128433,128434,14,128450,128452,14,128476,128478,14,128483,128483,14,128495,128495,14,128506,128506,14,128519,128520,14,128528,128528,14,128534,128534,14,128538,128538,14,128540,128542,14,128544,128549,14,128552,128555,14,128557,128557,14,128560,128563,14,128565,128565,14,128567,128576,14,128581,128591,14,128641,128642,14,128646,128646,14,128648,128648,14,128650,128651,14,128653,128653,14,128655,128655,14,128657,128659,14,128661,128661,14,128663,128663,14,128665,128666,14,128674,128674,14,128676,128677,14,128679,128685,14,128690,128690,14,128694,128694,14,128697,128702,14,128704,128704,14,128710,128714,14,128716,128716,14,128720,128720,14,128723,128724,14,128726,128727,14,128733,128735,14,128742,128744,14,128746,128746,14,128749,128751,14,128753,128754,14,128756,128758,14,128761,128761,14,128763,128764,14,128884,128895,14,128992,129003,14,129008,129008,14,129036,129039,14,129114,129119,14,129198,129279,14,129293,129295,14,129305,129310,14,129312,129319,14,129328,129328,14,129331,129338,14,129343,129343,14,129351,129355,14,129357,129359,14,129375,129387,14,129393,129393,14,129395,129398,14,129401,129401,14,129403,129403,14,129408,129412,14,129426,129431,14,129443,129444,14,129451,129453,14,129456,129465,14,129472,129472,14,129475,129482,14,129484,129484,14,129488,129510,14,129536,129647,14,129652,129652,14,129656,129658,14,129661,129663,14,129667,129670,14,129680,129685,14,129705,129708,14,129712,129718,14,129723,129727,14,129731,129733,14,129744,129750,14,129754,129759,14,129768,129775,14,129783,129791,14,917504,917504,4,917506,917535,4,917632,917759,4,918000,921599,4,0,9,4,11,12,4,14,31,4,169,169,14,174,174,14,1155,1159,5,1425,1469,5,1473,1474,5,1479,1479,5,1552,1562,5,1611,1631,5,1750,1756,5,1759,1764,5,1770,1773,5,1809,1809,5,1958,1968,5,2045,2045,5,2075,2083,5,2089,2093,5,2192,2193,1,2250,2273,5,2275,2306,5,2362,2362,5,2364,2364,5,2369,2376,5,2381,2381,5,2385,2391,5,2433,2433,5,2492,2492,5,2495,2496,7,2503,2504,7,2509,2509,5,2530,2531,5,2561,2562,5,2620,2620,5,2625,2626,5,2635,2637,5,2672,2673,5,2689,2690,5,2748,2748,5,2753,2757,5,2761,2761,7,2765,2765,5,2810,2815,5,2818,2819,7,2878,2878,5,2880,2880,7,2887,2888,7,2893,2893,5,2903,2903,5,2946,2946,5,3007,3007,7,3009,3010,7,3018,3020,7,3031,3031,5,3073,3075,7,3132,3132,5,3137,3140,7,3146,3149,5,3170,3171,5,3202,3203,7,3262,3262,7,3264,3265,7,3267,3268,7,3271,3272,7,3276,3277,5,3298,3299,5,3330,3331,7,3390,3390,5,3393,3396,5,3402,3404,7,3406,3406,1,3426,3427,5,3458,3459,7,3535,3535,5,3538,3540,5,3544,3550,7,3570,3571,7,3635,3635,7,3655,3662,5,3763,3763,7,3784,3789,5,3893,3893,5,3897,3897,5,3953,3966,5,3968,3972,5,3981,3991,5,4038,4038,5,4145,4145,7,4153,4154,5,4157,4158,5,4184,4185,5,4209,4212,5,4228,4228,7,4237,4237,5,4352,4447,8,4520,4607,10,5906,5908,5,5938,5939,5,5970,5971,5,6068,6069,5,6071,6077,5,6086,6086,5,6089,6099,5,6155,6157,5,6159,6159,5,6313,6313,5,6435,6438,7,6441,6443,7,6450,6450,5,6457,6459,5,6681,6682,7,6741,6741,7,6743,6743,7,6752,6752,5,6757,6764,5,6771,6780,5,6832,6845,5,6847,6862,5,6916,6916,7,6965,6965,5,6971,6971,7,6973,6977,7,6979,6980,7,7040,7041,5,7073,7073,7,7078,7079,7,7082,7082,7,7142,7142,5,7144,7145,5,7149,7149,5,7151,7153,5,7204,7211,7,7220,7221,7,7376,7378,5,7393,7393,7,7405,7405,5,7415,7415,7,7616,7679,5,8204,8204,5,8206,8207,4,8233,8233,4,8252,8252,14,8288,8292,4,8294,8303,4,8413,8416,5,8418,8420,5,8482,8482,14,8596,8601,14,8986,8987,14,9096,9096,14,9193,9196,14,9199,9199,14,9201,9202,14,9208,9210,14,9642,9643,14,9664,9664,14,9728,9729,14,9732,9732,14,9735,9741,14,9743,9744,14,9746,9746,14,9750,9751,14,9753,9756,14,9758,9759,14,9761,9761,14,9764,9765,14,9767,9769,14,9771,9773,14,9775,9775,14,9784,9785,14,9787,9791,14,9793,9793,14,9795,9799,14,9812,9822,14,9824,9824,14,9827,9827,14,9829,9830,14,9832,9832,14,9851,9851,14,9854,9854,14,9856,9861,14,9874,9874,14,9876,9876,14,9878,9879,14,9881,9881,14,9883,9884,14,9888,9889,14,9895,9895,14,9898,9899,14,9904,9905,14,9917,9918,14,9924,9925,14,9928,9928,14,9934,9934,14,9936,9936,14,9938,9938,14,9940,9940,14,9961,9961,14,9963,9967,14,9970,9971,14,9973,9973,14,9975,9977,14,9979,9980,14,9982,9985,14,9987,9988,14,9992,9996,14,9998,9998,14,10000,10001,14,10004,10004,14,10013,10013,14,10024,10024,14,10052,10052,14,10060,10060,14,10067,10069,14,10083,10083,14,10085,10087,14,10145,10145,14,10175,10175,14,11013,11015,14,11088,11088,14,11503,11505,5,11744,11775,5,12334,12335,5,12349,12349,14,12951,12951,14,42607,42607,5,42612,42621,5,42736,42737,5,43014,43014,5,43043,43044,7,43047,43047,7,43136,43137,7,43204,43205,5,43263,43263,5,43335,43345,5,43360,43388,8,43395,43395,7,43444,43445,7,43450,43451,7,43454,43456,7,43561,43566,5,43569,43570,5,43573,43574,5,43596,43596,5,43644,43644,5,43698,43700,5,43710,43711,5,43755,43755,7,43758,43759,7,43766,43766,5,44005,44005,5,44008,44008,5,44012,44012,7,44032,44032,11,44060,44060,11,44088,44088,11,44116,44116,11,44144,44144,11,44172,44172,11,44200,44200,11,44228,44228,11,44256,44256,11,44284,44284,11,44312,44312,11,44340,44340,11,44368,44368,11,44396,44396,11,44424,44424,11,44452,44452,11,44480,44480,11,44508,44508,11,44536,44536,11,44564,44564,11,44592,44592,11,44620,44620,11,44648,44648,11,44676,44676,11,44704,44704,11,44732,44732,11,44760,44760,11,44788,44788,11,44816,44816,11,44844,44844,11,44872,44872,11,44900,44900,11,44928,44928,11,44956,44956,11,44984,44984,11,45012,45012,11,45040,45040,11,45068,45068,11,45096,45096,11,45124,45124,11,45152,45152,11,45180,45180,11,45208,45208,11,45236,45236,11,45264,45264,11,45292,45292,11,45320,45320,11,45348,45348,11,45376,45376,11,45404,45404,11,45432,45432,11,45460,45460,11,45488,45488,11,45516,45516,11,45544,45544,11,45572,45572,11,45600,45600,11,45628,45628,11,45656,45656,11,45684,45684,11,45712,45712,11,45740,45740,11,45768,45768,11,45796,45796,11,45824,45824,11,45852,45852,11,45880,45880,11,45908,45908,11,45936,45936,11,45964,45964,11,45992,45992,11,46020,46020,11,46048,46048,11,46076,46076,11,46104,46104,11,46132,46132,11,46160,46160,11,46188,46188,11,46216,46216,11,46244,46244,11,46272,46272,11,46300,46300,11,46328,46328,11,46356,46356,11,46384,46384,11,46412,46412,11,46440,46440,11,46468,46468,11,46496,46496,11,46524,46524,11,46552,46552,11,46580,46580,11,46608,46608,11,46636,46636,11,46664,46664,11,46692,46692,11,46720,46720,11,46748,46748,11,46776,46776,11,46804,46804,11,46832,46832,11,46860,46860,11,46888,46888,11,46916,46916,11,46944,46944,11,46972,46972,11,47000,47000,11,47028,47028,11,47056,47056,11,47084,47084,11,47112,47112,11,47140,47140,11,47168,47168,11,47196,47196,11,47224,47224,11,47252,47252,11,47280,47280,11,47308,47308,11,47336,47336,11,47364,47364,11,47392,47392,11,47420,47420,11,47448,47448,11,47476,47476,11,47504,47504,11,47532,47532,11,47560,47560,11,47588,47588,11,47616,47616,11,47644,47644,11,47672,47672,11,47700,47700,11,47728,47728,11,47756,47756,11,47784,47784,11,47812,47812,11,47840,47840,11,47868,47868,11,47896,47896,11,47924,47924,11,47952,47952,11,47980,47980,11,48008,48008,11,48036,48036,11,48064,48064,11,48092,48092,11,48120,48120,11,48148,48148,11,48176,48176,11,48204,48204,11,48232,48232,11,48260,48260,11,48288,48288,11,48316,48316,11,48344,48344,11,48372,48372,11,48400,48400,11,48428,48428,11,48456,48456,11,48484,48484,11,48512,48512,11,48540,48540,11,48568,48568,11,48596,48596,11,48624,48624,11,48652,48652,11,48680,48680,11,48708,48708,11,48736,48736,11,48764,48764,11,48792,48792,11,48820,48820,11,48848,48848,11,48876,48876,11,48904,48904,11,48932,48932,11,48960,48960,11,48988,48988,11,49016,49016,11,49044,49044,11,49072,49072,11,49100,49100,11,49128,49128,11,49156,49156,11,49184,49184,11,49212,49212,11,49240,49240,11,49268,49268,11,49296,49296,11,49324,49324,11,49352,49352,11,49380,49380,11,49408,49408,11,49436,49436,11,49464,49464,11,49492,49492,11,49520,49520,11,49548,49548,11,49576,49576,11,49604,49604,11,49632,49632,11,49660,49660,11,49688,49688,11,49716,49716,11,49744,49744,11,49772,49772,11,49800,49800,11,49828,49828,11,49856,49856,11,49884,49884,11,49912,49912,11,49940,49940,11,49968,49968,11,49996,49996,11,50024,50024,11,50052,50052,11,50080,50080,11,50108,50108,11,50136,50136,11,50164,50164,11,50192,50192,11,50220,50220,11,50248,50248,11,50276,50276,11,50304,50304,11,50332,50332,11,50360,50360,11,50388,50388,11,50416,50416,11,50444,50444,11,50472,50472,11,50500,50500,11,50528,50528,11,50556,50556,11,50584,50584,11,50612,50612,11,50640,50640,11,50668,50668,11,50696,50696,11,50724,50724,11,50752,50752,11,50780,50780,11,50808,50808,11,50836,50836,11,50864,50864,11,50892,50892,11,50920,50920,11,50948,50948,11,50976,50976,11,51004,51004,11,51032,51032,11,51060,51060,11,51088,51088,11,51116,51116,11,51144,51144,11,51172,51172,11,51200,51200,11,51228,51228,11,51256,51256,11,51284,51284,11,51312,51312,11,51340,51340,11,51368,51368,11,51396,51396,11,51424,51424,11,51452,51452,11,51480,51480,11,51508,51508,11,51536,51536,11,51564,51564,11,51592,51592,11,51620,51620,11,51648,51648,11,51676,51676,11,51704,51704,11,51732,51732,11,51760,51760,11,51788,51788,11,51816,51816,11,51844,51844,11,51872,51872,11,51900,51900,11,51928,51928,11,51956,51956,11,51984,51984,11,52012,52012,11,52040,52040,11,52068,52068,11,52096,52096,11,52124,52124,11,52152,52152,11,52180,52180,11,52208,52208,11,52236,52236,11,52264,52264,11,52292,52292,11,52320,52320,11,52348,52348,11,52376,52376,11,52404,52404,11,52432,52432,11,52460,52460,11,52488,52488,11,52516,52516,11,52544,52544,11,52572,52572,11,52600,52600,11,52628,52628,11,52656,52656,11,52684,52684,11,52712,52712,11,52740,52740,11,52768,52768,11,52796,52796,11,52824,52824,11,52852,52852,11,52880,52880,11,52908,52908,11,52936,52936,11,52964,52964,11,52992,52992,11,53020,53020,11,53048,53048,11,53076,53076,11,53104,53104,11,53132,53132,11,53160,53160,11,53188,53188,11,53216,53216,11,53244,53244,11,53272,53272,11,53300,53300,11,53328,53328,11,53356,53356,11,53384,53384,11,53412,53412,11,53440,53440,11,53468,53468,11,53496,53496,11,53524,53524,11,53552,53552,11,53580,53580,11,53608,53608,11,53636,53636,11,53664,53664,11,53692,53692,11,53720,53720,11,53748,53748,11,53776,53776,11,53804,53804,11,53832,53832,11,53860,53860,11,53888,53888,11,53916,53916,11,53944,53944,11,53972,53972,11,54000,54000,11,54028,54028,11,54056,54056,11,54084,54084,11,54112,54112,11,54140,54140,11,54168,54168,11,54196,54196,11,54224,54224,11,54252,54252,11,54280,54280,11,54308,54308,11,54336,54336,11,54364,54364,11,54392,54392,11,54420,54420,11,54448,54448,11,54476,54476,11,54504,54504,11,54532,54532,11,54560,54560,11,54588,54588,11,54616,54616,11,54644,54644,11,54672,54672,11,54700,54700,11,54728,54728,11,54756,54756,11,54784,54784,11,54812,54812,11,54840,54840,11,54868,54868,11,54896,54896,11,54924,54924,11,54952,54952,11,54980,54980,11,55008,55008,11,55036,55036,11,55064,55064,11,55092,55092,11,55120,55120,11,55148,55148,11,55176,55176,11,55216,55238,9,64286,64286,5,65056,65071,5,65438,65439,5,65529,65531,4,66272,66272,5,68097,68099,5,68108,68111,5,68159,68159,5,68900,68903,5,69446,69456,5,69632,69632,7,69634,69634,7,69744,69744,5,69759,69761,5,69808,69810,7,69815,69816,7,69821,69821,1,69837,69837,1,69927,69931,5,69933,69940,5,70003,70003,5,70018,70018,7,70070,70078,5,70082,70083,1,70094,70094,7,70188,70190,7,70194,70195,7,70197,70197,7,70206,70206,5,70368,70370,7,70400,70401,5,70459,70460,5,70463,70463,7,70465,70468,7,70475,70477,7,70498,70499,7,70512,70516,5,70712,70719,5,70722,70724,5,70726,70726,5,70832,70832,5,70835,70840,5,70842,70842,5,70845,70845,5,70847,70848,5,70850,70851,5,71088,71089,7,71096,71099,7,71102,71102,7,71132,71133,5,71219,71226,5,71229,71229,5,71231,71232,5,71340,71340,7,71342,71343,7,71350,71350,7,71453,71455,5,71462,71462,7,71724,71726,7,71736,71736,7,71984,71984,5,71991,71992,7,71997,71997,7,71999,71999,1,72001,72001,1,72003,72003,5,72148,72151,5,72156,72159,7,72164,72164,7,72243,72248,5,72250,72250,1,72263,72263,5,72279,72280,7,72324,72329,1,72343,72343,7,72751,72751,7,72760,72765,5,72767,72767,5,72873,72873,7,72881,72881,7,72884,72884,7,73009,73014,5,73020,73021,5,73030,73030,1,73098,73102,7,73107,73108,7,73110,73110,7,73459,73460,5,78896,78904,4,92976,92982,5,94033,94087,7,94180,94180,5,113821,113822,5,118528,118573,5,119141,119141,5,119143,119145,5,119150,119154,5,119163,119170,5,119210,119213,5,121344,121398,5,121461,121461,5,121499,121503,5,122880,122886,5,122907,122913,5,122918,122922,5,123566,123566,5,125136,125142,5,126976,126979,14,126981,127182,14,127184,127231,14,127279,127279,14,127344,127345,14,127374,127374,14,127405,127461,14,127489,127490,14,127514,127514,14,127538,127546,14,127561,127567,14,127570,127743,14,127757,127758,14,127760,127760,14,127762,127762,14,127766,127768,14,127770,127770,14,127772,127772,14,127775,127776,14,127778,127779,14,127789,127791,14,127794,127795,14,127798,127798,14,127819,127819,14,127824,127824,14,127868,127868,14,127870,127871,14,127892,127893,14,127896,127896,14,127900,127901,14,127904,127940,14,127942,127942,14,127944,127944,14,127946,127946,14,127951,127955,14,127968,127971,14,127973,127984,14,127987,127987,14,127989,127989,14,127991,127991,14,127995,127999,5,128008,128008,14,128012,128014,14,128017,128018,14,128020,128020,14,128022,128022,14,128042,128042,14,128063,128063,14,128065,128065,14,128101,128101,14,128108,128109,14,128173,128173,14,128182,128183,14,128236,128237,14,128239,128239,14,128245,128245,14,128248,128248,14,128253,128253,14,128255,128258,14,128260,128263,14,128265,128265,14,128277,128277,14,128300,128301,14,128326,128328,14,128331,128334,14,128336,128347,14,128360,128366,14,128369,128370,14,128378,128378,14,128391,128391,14,128394,128397,14,128400,128400,14,128405,128406,14,128420,128420,14,128422,128423,14,128425,128432,14,128435,128443,14,128445,128449,14,128453,128464,14,128468,128475,14,128479,128480,14,128482,128482,14,128484,128487,14,128489,128494,14,128496,128498,14,128500,128505,14,128507,128511,14,128513,128518,14,128521,128525,14,128527,128527,14,128529,128529,14,128533,128533,14,128535,128535,14,128537,128537,14]");
}
var Fi;
(function(e) {
  e[e.zwj = 8205] = "zwj", e[e.emojiVariantSelector = 65039] = "emojiVariantSelector", e[e.enclosingKeyCap = 8419] = "enclosingKeyCap";
})(Fi || (Fi = {}));
const Ie = class Ie {
  static getInstance(t) {
    return Ie.cache.get(Array.from(t));
  }
  static getLocales() {
    return Ie._locales.value;
  }
  constructor(t) {
    this.confusableDictionary = t;
  }
  isAmbiguous(t) {
    return this.confusableDictionary.has(t);
  }
  containsAmbiguousCharacter(t) {
    for (let n = 0; n < t.length; n++) {
      const i = t.codePointAt(n);
      if (typeof i == "number" && this.isAmbiguous(i))
        return !0;
    }
    return !1;
  }
  getPrimaryConfusable(t) {
    return this.confusableDictionary.get(t);
  }
  getConfusableCodePoints() {
    return new Set(this.confusableDictionary.keys());
  }
};
Ie.ambiguousCharacterData = new Ti(() => JSON.parse('{"_common":[8232,32,8233,32,5760,32,8192,32,8193,32,8194,32,8195,32,8196,32,8197,32,8198,32,8200,32,8201,32,8202,32,8287,32,8199,32,8239,32,2042,95,65101,95,65102,95,65103,95,8208,45,8209,45,8210,45,65112,45,1748,45,8259,45,727,45,8722,45,10134,45,11450,45,1549,44,1643,44,8218,44,184,44,42233,44,894,59,2307,58,2691,58,1417,58,1795,58,1796,58,5868,58,65072,58,6147,58,6153,58,8282,58,1475,58,760,58,42889,58,8758,58,720,58,42237,58,451,33,11601,33,660,63,577,63,2429,63,5038,63,42731,63,119149,46,8228,46,1793,46,1794,46,42510,46,68176,46,1632,46,1776,46,42232,46,1373,96,65287,96,8219,96,8242,96,1370,96,1523,96,8175,96,65344,96,900,96,8189,96,8125,96,8127,96,8190,96,697,96,884,96,712,96,714,96,715,96,756,96,699,96,701,96,700,96,702,96,42892,96,1497,96,2036,96,2037,96,5194,96,5836,96,94033,96,94034,96,65339,91,10088,40,10098,40,12308,40,64830,40,65341,93,10089,41,10099,41,12309,41,64831,41,10100,123,119060,123,10101,125,65342,94,8270,42,1645,42,8727,42,66335,42,5941,47,8257,47,8725,47,8260,47,9585,47,10187,47,10744,47,119354,47,12755,47,12339,47,11462,47,20031,47,12035,47,65340,92,65128,92,8726,92,10189,92,10741,92,10745,92,119311,92,119355,92,12756,92,20022,92,12034,92,42872,38,708,94,710,94,5869,43,10133,43,66203,43,8249,60,10094,60,706,60,119350,60,5176,60,5810,60,5120,61,11840,61,12448,61,42239,61,8250,62,10095,62,707,62,119351,62,5171,62,94015,62,8275,126,732,126,8128,126,8764,126,65372,124,65293,45,120784,50,120794,50,120804,50,120814,50,120824,50,130034,50,42842,50,423,50,1000,50,42564,50,5311,50,42735,50,119302,51,120785,51,120795,51,120805,51,120815,51,120825,51,130035,51,42923,51,540,51,439,51,42858,51,11468,51,1248,51,94011,51,71882,51,120786,52,120796,52,120806,52,120816,52,120826,52,130036,52,5070,52,71855,52,120787,53,120797,53,120807,53,120817,53,120827,53,130037,53,444,53,71867,53,120788,54,120798,54,120808,54,120818,54,120828,54,130038,54,11474,54,5102,54,71893,54,119314,55,120789,55,120799,55,120809,55,120819,55,120829,55,130039,55,66770,55,71878,55,2819,56,2538,56,2666,56,125131,56,120790,56,120800,56,120810,56,120820,56,120830,56,130040,56,547,56,546,56,66330,56,2663,57,2920,57,2541,57,3437,57,120791,57,120801,57,120811,57,120821,57,120831,57,130041,57,42862,57,11466,57,71884,57,71852,57,71894,57,9082,97,65345,97,119834,97,119886,97,119938,97,119990,97,120042,97,120094,97,120146,97,120198,97,120250,97,120302,97,120354,97,120406,97,120458,97,593,97,945,97,120514,97,120572,97,120630,97,120688,97,120746,97,65313,65,119808,65,119860,65,119912,65,119964,65,120016,65,120068,65,120120,65,120172,65,120224,65,120276,65,120328,65,120380,65,120432,65,913,65,120488,65,120546,65,120604,65,120662,65,120720,65,5034,65,5573,65,42222,65,94016,65,66208,65,119835,98,119887,98,119939,98,119991,98,120043,98,120095,98,120147,98,120199,98,120251,98,120303,98,120355,98,120407,98,120459,98,388,98,5071,98,5234,98,5551,98,65314,66,8492,66,119809,66,119861,66,119913,66,120017,66,120069,66,120121,66,120173,66,120225,66,120277,66,120329,66,120381,66,120433,66,42932,66,914,66,120489,66,120547,66,120605,66,120663,66,120721,66,5108,66,5623,66,42192,66,66178,66,66209,66,66305,66,65347,99,8573,99,119836,99,119888,99,119940,99,119992,99,120044,99,120096,99,120148,99,120200,99,120252,99,120304,99,120356,99,120408,99,120460,99,7428,99,1010,99,11429,99,43951,99,66621,99,128844,67,71922,67,71913,67,65315,67,8557,67,8450,67,8493,67,119810,67,119862,67,119914,67,119966,67,120018,67,120174,67,120226,67,120278,67,120330,67,120382,67,120434,67,1017,67,11428,67,5087,67,42202,67,66210,67,66306,67,66581,67,66844,67,8574,100,8518,100,119837,100,119889,100,119941,100,119993,100,120045,100,120097,100,120149,100,120201,100,120253,100,120305,100,120357,100,120409,100,120461,100,1281,100,5095,100,5231,100,42194,100,8558,68,8517,68,119811,68,119863,68,119915,68,119967,68,120019,68,120071,68,120123,68,120175,68,120227,68,120279,68,120331,68,120383,68,120435,68,5024,68,5598,68,5610,68,42195,68,8494,101,65349,101,8495,101,8519,101,119838,101,119890,101,119942,101,120046,101,120098,101,120150,101,120202,101,120254,101,120306,101,120358,101,120410,101,120462,101,43826,101,1213,101,8959,69,65317,69,8496,69,119812,69,119864,69,119916,69,120020,69,120072,69,120124,69,120176,69,120228,69,120280,69,120332,69,120384,69,120436,69,917,69,120492,69,120550,69,120608,69,120666,69,120724,69,11577,69,5036,69,42224,69,71846,69,71854,69,66182,69,119839,102,119891,102,119943,102,119995,102,120047,102,120099,102,120151,102,120203,102,120255,102,120307,102,120359,102,120411,102,120463,102,43829,102,42905,102,383,102,7837,102,1412,102,119315,70,8497,70,119813,70,119865,70,119917,70,120021,70,120073,70,120125,70,120177,70,120229,70,120281,70,120333,70,120385,70,120437,70,42904,70,988,70,120778,70,5556,70,42205,70,71874,70,71842,70,66183,70,66213,70,66853,70,65351,103,8458,103,119840,103,119892,103,119944,103,120048,103,120100,103,120152,103,120204,103,120256,103,120308,103,120360,103,120412,103,120464,103,609,103,7555,103,397,103,1409,103,119814,71,119866,71,119918,71,119970,71,120022,71,120074,71,120126,71,120178,71,120230,71,120282,71,120334,71,120386,71,120438,71,1292,71,5056,71,5107,71,42198,71,65352,104,8462,104,119841,104,119945,104,119997,104,120049,104,120101,104,120153,104,120205,104,120257,104,120309,104,120361,104,120413,104,120465,104,1211,104,1392,104,5058,104,65320,72,8459,72,8460,72,8461,72,119815,72,119867,72,119919,72,120023,72,120179,72,120231,72,120283,72,120335,72,120387,72,120439,72,919,72,120494,72,120552,72,120610,72,120668,72,120726,72,11406,72,5051,72,5500,72,42215,72,66255,72,731,105,9075,105,65353,105,8560,105,8505,105,8520,105,119842,105,119894,105,119946,105,119998,105,120050,105,120102,105,120154,105,120206,105,120258,105,120310,105,120362,105,120414,105,120466,105,120484,105,618,105,617,105,953,105,8126,105,890,105,120522,105,120580,105,120638,105,120696,105,120754,105,1110,105,42567,105,1231,105,43893,105,5029,105,71875,105,65354,106,8521,106,119843,106,119895,106,119947,106,119999,106,120051,106,120103,106,120155,106,120207,106,120259,106,120311,106,120363,106,120415,106,120467,106,1011,106,1112,106,65322,74,119817,74,119869,74,119921,74,119973,74,120025,74,120077,74,120129,74,120181,74,120233,74,120285,74,120337,74,120389,74,120441,74,42930,74,895,74,1032,74,5035,74,5261,74,42201,74,119844,107,119896,107,119948,107,120000,107,120052,107,120104,107,120156,107,120208,107,120260,107,120312,107,120364,107,120416,107,120468,107,8490,75,65323,75,119818,75,119870,75,119922,75,119974,75,120026,75,120078,75,120130,75,120182,75,120234,75,120286,75,120338,75,120390,75,120442,75,922,75,120497,75,120555,75,120613,75,120671,75,120729,75,11412,75,5094,75,5845,75,42199,75,66840,75,1472,108,8739,73,9213,73,65512,73,1633,108,1777,73,66336,108,125127,108,120783,73,120793,73,120803,73,120813,73,120823,73,130033,73,65321,73,8544,73,8464,73,8465,73,119816,73,119868,73,119920,73,120024,73,120128,73,120180,73,120232,73,120284,73,120336,73,120388,73,120440,73,65356,108,8572,73,8467,108,119845,108,119897,108,119949,108,120001,108,120053,108,120105,73,120157,73,120209,73,120261,73,120313,73,120365,73,120417,73,120469,73,448,73,120496,73,120554,73,120612,73,120670,73,120728,73,11410,73,1030,73,1216,73,1493,108,1503,108,1575,108,126464,108,126592,108,65166,108,65165,108,1994,108,11599,73,5825,73,42226,73,93992,73,66186,124,66313,124,119338,76,8556,76,8466,76,119819,76,119871,76,119923,76,120027,76,120079,76,120131,76,120183,76,120235,76,120287,76,120339,76,120391,76,120443,76,11472,76,5086,76,5290,76,42209,76,93974,76,71843,76,71858,76,66587,76,66854,76,65325,77,8559,77,8499,77,119820,77,119872,77,119924,77,120028,77,120080,77,120132,77,120184,77,120236,77,120288,77,120340,77,120392,77,120444,77,924,77,120499,77,120557,77,120615,77,120673,77,120731,77,1018,77,11416,77,5047,77,5616,77,5846,77,42207,77,66224,77,66321,77,119847,110,119899,110,119951,110,120003,110,120055,110,120107,110,120159,110,120211,110,120263,110,120315,110,120367,110,120419,110,120471,110,1400,110,1404,110,65326,78,8469,78,119821,78,119873,78,119925,78,119977,78,120029,78,120081,78,120185,78,120237,78,120289,78,120341,78,120393,78,120445,78,925,78,120500,78,120558,78,120616,78,120674,78,120732,78,11418,78,42208,78,66835,78,3074,111,3202,111,3330,111,3458,111,2406,111,2662,111,2790,111,3046,111,3174,111,3302,111,3430,111,3664,111,3792,111,4160,111,1637,111,1781,111,65359,111,8500,111,119848,111,119900,111,119952,111,120056,111,120108,111,120160,111,120212,111,120264,111,120316,111,120368,111,120420,111,120472,111,7439,111,7441,111,43837,111,959,111,120528,111,120586,111,120644,111,120702,111,120760,111,963,111,120532,111,120590,111,120648,111,120706,111,120764,111,11423,111,4351,111,1413,111,1505,111,1607,111,126500,111,126564,111,126596,111,65259,111,65260,111,65258,111,65257,111,1726,111,64428,111,64429,111,64427,111,64426,111,1729,111,64424,111,64425,111,64423,111,64422,111,1749,111,3360,111,4125,111,66794,111,71880,111,71895,111,66604,111,1984,79,2534,79,2918,79,12295,79,70864,79,71904,79,120782,79,120792,79,120802,79,120812,79,120822,79,130032,79,65327,79,119822,79,119874,79,119926,79,119978,79,120030,79,120082,79,120134,79,120186,79,120238,79,120290,79,120342,79,120394,79,120446,79,927,79,120502,79,120560,79,120618,79,120676,79,120734,79,11422,79,1365,79,11604,79,4816,79,2848,79,66754,79,42227,79,71861,79,66194,79,66219,79,66564,79,66838,79,9076,112,65360,112,119849,112,119901,112,119953,112,120005,112,120057,112,120109,112,120161,112,120213,112,120265,112,120317,112,120369,112,120421,112,120473,112,961,112,120530,112,120544,112,120588,112,120602,112,120646,112,120660,112,120704,112,120718,112,120762,112,120776,112,11427,112,65328,80,8473,80,119823,80,119875,80,119927,80,119979,80,120031,80,120083,80,120187,80,120239,80,120291,80,120343,80,120395,80,120447,80,929,80,120504,80,120562,80,120620,80,120678,80,120736,80,11426,80,5090,80,5229,80,42193,80,66197,80,119850,113,119902,113,119954,113,120006,113,120058,113,120110,113,120162,113,120214,113,120266,113,120318,113,120370,113,120422,113,120474,113,1307,113,1379,113,1382,113,8474,81,119824,81,119876,81,119928,81,119980,81,120032,81,120084,81,120188,81,120240,81,120292,81,120344,81,120396,81,120448,81,11605,81,119851,114,119903,114,119955,114,120007,114,120059,114,120111,114,120163,114,120215,114,120267,114,120319,114,120371,114,120423,114,120475,114,43847,114,43848,114,7462,114,11397,114,43905,114,119318,82,8475,82,8476,82,8477,82,119825,82,119877,82,119929,82,120033,82,120189,82,120241,82,120293,82,120345,82,120397,82,120449,82,422,82,5025,82,5074,82,66740,82,5511,82,42211,82,94005,82,65363,115,119852,115,119904,115,119956,115,120008,115,120060,115,120112,115,120164,115,120216,115,120268,115,120320,115,120372,115,120424,115,120476,115,42801,115,445,115,1109,115,43946,115,71873,115,66632,115,65331,83,119826,83,119878,83,119930,83,119982,83,120034,83,120086,83,120138,83,120190,83,120242,83,120294,83,120346,83,120398,83,120450,83,1029,83,1359,83,5077,83,5082,83,42210,83,94010,83,66198,83,66592,83,119853,116,119905,116,119957,116,120009,116,120061,116,120113,116,120165,116,120217,116,120269,116,120321,116,120373,116,120425,116,120477,116,8868,84,10201,84,128872,84,65332,84,119827,84,119879,84,119931,84,119983,84,120035,84,120087,84,120139,84,120191,84,120243,84,120295,84,120347,84,120399,84,120451,84,932,84,120507,84,120565,84,120623,84,120681,84,120739,84,11430,84,5026,84,42196,84,93962,84,71868,84,66199,84,66225,84,66325,84,119854,117,119906,117,119958,117,120010,117,120062,117,120114,117,120166,117,120218,117,120270,117,120322,117,120374,117,120426,117,120478,117,42911,117,7452,117,43854,117,43858,117,651,117,965,117,120534,117,120592,117,120650,117,120708,117,120766,117,1405,117,66806,117,71896,117,8746,85,8899,85,119828,85,119880,85,119932,85,119984,85,120036,85,120088,85,120140,85,120192,85,120244,85,120296,85,120348,85,120400,85,120452,85,1357,85,4608,85,66766,85,5196,85,42228,85,94018,85,71864,85,8744,118,8897,118,65366,118,8564,118,119855,118,119907,118,119959,118,120011,118,120063,118,120115,118,120167,118,120219,118,120271,118,120323,118,120375,118,120427,118,120479,118,7456,118,957,118,120526,118,120584,118,120642,118,120700,118,120758,118,1141,118,1496,118,71430,118,43945,118,71872,118,119309,86,1639,86,1783,86,8548,86,119829,86,119881,86,119933,86,119985,86,120037,86,120089,86,120141,86,120193,86,120245,86,120297,86,120349,86,120401,86,120453,86,1140,86,11576,86,5081,86,5167,86,42719,86,42214,86,93960,86,71840,86,66845,86,623,119,119856,119,119908,119,119960,119,120012,119,120064,119,120116,119,120168,119,120220,119,120272,119,120324,119,120376,119,120428,119,120480,119,7457,119,1121,119,1309,119,1377,119,71434,119,71438,119,71439,119,43907,119,71919,87,71910,87,119830,87,119882,87,119934,87,119986,87,120038,87,120090,87,120142,87,120194,87,120246,87,120298,87,120350,87,120402,87,120454,87,1308,87,5043,87,5076,87,42218,87,5742,120,10539,120,10540,120,10799,120,65368,120,8569,120,119857,120,119909,120,119961,120,120013,120,120065,120,120117,120,120169,120,120221,120,120273,120,120325,120,120377,120,120429,120,120481,120,5441,120,5501,120,5741,88,9587,88,66338,88,71916,88,65336,88,8553,88,119831,88,119883,88,119935,88,119987,88,120039,88,120091,88,120143,88,120195,88,120247,88,120299,88,120351,88,120403,88,120455,88,42931,88,935,88,120510,88,120568,88,120626,88,120684,88,120742,88,11436,88,11613,88,5815,88,42219,88,66192,88,66228,88,66327,88,66855,88,611,121,7564,121,65369,121,119858,121,119910,121,119962,121,120014,121,120066,121,120118,121,120170,121,120222,121,120274,121,120326,121,120378,121,120430,121,120482,121,655,121,7935,121,43866,121,947,121,8509,121,120516,121,120574,121,120632,121,120690,121,120748,121,1199,121,4327,121,71900,121,65337,89,119832,89,119884,89,119936,89,119988,89,120040,89,120092,89,120144,89,120196,89,120248,89,120300,89,120352,89,120404,89,120456,89,933,89,978,89,120508,89,120566,89,120624,89,120682,89,120740,89,11432,89,1198,89,5033,89,5053,89,42220,89,94019,89,71844,89,66226,89,119859,122,119911,122,119963,122,120015,122,120067,122,120119,122,120171,122,120223,122,120275,122,120327,122,120379,122,120431,122,120483,122,7458,122,43923,122,71876,122,66293,90,71909,90,65338,90,8484,90,8488,90,119833,90,119885,90,119937,90,119989,90,120041,90,120197,90,120249,90,120301,90,120353,90,120405,90,120457,90,918,90,120493,90,120551,90,120609,90,120667,90,120725,90,5059,90,42204,90,71849,90,65282,34,65284,36,65285,37,65286,38,65290,42,65291,43,65294,46,65295,47,65296,48,65297,49,65298,50,65299,51,65300,52,65301,53,65302,54,65303,55,65304,56,65305,57,65308,60,65309,61,65310,62,65312,64,65316,68,65318,70,65319,71,65324,76,65329,81,65330,82,65333,85,65334,86,65335,87,65343,95,65346,98,65348,100,65350,102,65355,107,65357,109,65358,110,65361,113,65362,114,65364,116,65365,117,65367,119,65370,122,65371,123,65373,125,119846,109],"_default":[160,32,8211,45,65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"cs":[65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"de":[65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"es":[8211,45,65374,126,65306,58,65281,33,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"fr":[65374,126,65306,58,65281,33,8216,96,8245,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"it":[160,32,8211,45,65374,126,65306,58,65281,33,8216,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"ja":[8211,45,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65292,44,65307,59],"ko":[8211,45,65374,126,65306,58,65281,33,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"pl":[65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"pt-BR":[65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"qps-ploc":[160,32,8211,45,65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"ru":[65374,126,65306,58,65281,33,8216,96,8217,96,8245,96,180,96,12494,47,305,105,921,73,1009,112,215,120,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"tr":[160,32,8211,45,65374,126,65306,58,65281,33,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65288,40,65289,41,65292,44,65307,59,65311,63],"zh-hans":[65374,126,65306,58,65281,33,8245,96,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65288,40,65289,41],"zh-hant":[8211,45,65374,126,180,96,12494,47,1047,51,1073,54,1072,97,1040,65,1068,98,1042,66,1089,99,1057,67,1077,101,1045,69,1053,72,305,105,1050,75,921,73,1052,77,1086,111,1054,79,1009,112,1088,112,1056,80,1075,114,1058,84,215,120,1093,120,1061,88,1091,121,1059,89,65283,35,65307,59]}')), Ie.cache = new pa({ getCacheKey: JSON.stringify }, (t) => {
  function n(h) {
    const f = /* @__PURE__ */ new Map();
    for (let _ = 0; _ < h.length; _ += 2)
      f.set(h[_], h[_ + 1]);
    return f;
  }
  function i(h, f) {
    const _ = new Map(h);
    for (const [p, d] of f)
      _.set(p, d);
    return _;
  }
  function r(h, f) {
    if (!h)
      return f;
    const _ = /* @__PURE__ */ new Map();
    for (const [p, d] of h)
      f.has(p) && _.set(p, d);
    return _;
  }
  const s = Ie.ambiguousCharacterData.value;
  let a = t.filter((h) => !h.startsWith("_") && h in s);
  a.length === 0 && (a = ["_default"]);
  let u;
  for (const h of a) {
    const f = n(s[h]);
    u = r(u, f);
  }
  const o = n(s._common), c = i(o, u);
  return new Ie(c);
}), Ie._locales = new Ti(() => Object.keys(Ie.ambiguousCharacterData.value).filter((t) => !t.startsWith("_")));
let Yt = Ie;
const it = class it {
  static getRawData() {
    return JSON.parse("[9,10,11,12,13,32,127,160,173,847,1564,4447,4448,6068,6069,6155,6156,6157,6158,7355,7356,8192,8193,8194,8195,8196,8197,8198,8199,8200,8201,8202,8203,8204,8205,8206,8207,8234,8235,8236,8237,8238,8239,8287,8288,8289,8290,8291,8292,8293,8294,8295,8296,8297,8298,8299,8300,8301,8302,8303,10240,12288,12644,65024,65025,65026,65027,65028,65029,65030,65031,65032,65033,65034,65035,65036,65037,65038,65039,65279,65440,65520,65521,65522,65523,65524,65525,65526,65527,65528,65532,78844,119155,119156,119157,119158,119159,119160,119161,119162,917504,917505,917506,917507,917508,917509,917510,917511,917512,917513,917514,917515,917516,917517,917518,917519,917520,917521,917522,917523,917524,917525,917526,917527,917528,917529,917530,917531,917532,917533,917534,917535,917536,917537,917538,917539,917540,917541,917542,917543,917544,917545,917546,917547,917548,917549,917550,917551,917552,917553,917554,917555,917556,917557,917558,917559,917560,917561,917562,917563,917564,917565,917566,917567,917568,917569,917570,917571,917572,917573,917574,917575,917576,917577,917578,917579,917580,917581,917582,917583,917584,917585,917586,917587,917588,917589,917590,917591,917592,917593,917594,917595,917596,917597,917598,917599,917600,917601,917602,917603,917604,917605,917606,917607,917608,917609,917610,917611,917612,917613,917614,917615,917616,917617,917618,917619,917620,917621,917622,917623,917624,917625,917626,917627,917628,917629,917630,917631,917760,917761,917762,917763,917764,917765,917766,917767,917768,917769,917770,917771,917772,917773,917774,917775,917776,917777,917778,917779,917780,917781,917782,917783,917784,917785,917786,917787,917788,917789,917790,917791,917792,917793,917794,917795,917796,917797,917798,917799,917800,917801,917802,917803,917804,917805,917806,917807,917808,917809,917810,917811,917812,917813,917814,917815,917816,917817,917818,917819,917820,917821,917822,917823,917824,917825,917826,917827,917828,917829,917830,917831,917832,917833,917834,917835,917836,917837,917838,917839,917840,917841,917842,917843,917844,917845,917846,917847,917848,917849,917850,917851,917852,917853,917854,917855,917856,917857,917858,917859,917860,917861,917862,917863,917864,917865,917866,917867,917868,917869,917870,917871,917872,917873,917874,917875,917876,917877,917878,917879,917880,917881,917882,917883,917884,917885,917886,917887,917888,917889,917890,917891,917892,917893,917894,917895,917896,917897,917898,917899,917900,917901,917902,917903,917904,917905,917906,917907,917908,917909,917910,917911,917912,917913,917914,917915,917916,917917,917918,917919,917920,917921,917922,917923,917924,917925,917926,917927,917928,917929,917930,917931,917932,917933,917934,917935,917936,917937,917938,917939,917940,917941,917942,917943,917944,917945,917946,917947,917948,917949,917950,917951,917952,917953,917954,917955,917956,917957,917958,917959,917960,917961,917962,917963,917964,917965,917966,917967,917968,917969,917970,917971,917972,917973,917974,917975,917976,917977,917978,917979,917980,917981,917982,917983,917984,917985,917986,917987,917988,917989,917990,917991,917992,917993,917994,917995,917996,917997,917998,917999]");
  }
  static getData() {
    return this._data || (this._data = new Set(it.getRawData())), this._data;
  }
  static isInvisibleCharacter(t) {
    return it.getData().has(t);
  }
  static containsInvisibleCharacter(t) {
    for (let n = 0; n < t.length; n++) {
      const i = t.codePointAt(n);
      if (typeof i == "number" && it.isInvisibleCharacter(i))
        return !0;
    }
    return !1;
  }
  static get codePoints() {
    return it.getData();
  }
};
it._data = void 0;
let Ot = it;
const Fn = "default", Ia = "$initialize";
var pe;
(function(e) {
  e[e.Request = 0] = "Request", e[e.Reply = 1] = "Reply", e[e.SubscribeEvent = 2] = "SubscribeEvent", e[e.Event = 3] = "Event", e[e.UnsubscribeEvent = 4] = "UnsubscribeEvent";
})(pe || (pe = {}));
class Sa {
  constructor(t, n, i, r, s) {
    this.vsWorker = t, this.req = n, this.channel = i, this.method = r, this.args = s, this.type = pe.Request;
  }
}
class Ii {
  constructor(t, n, i, r) {
    this.vsWorker = t, this.seq = n, this.res = i, this.err = r, this.type = pe.Reply;
  }
}
class Pa {
  constructor(t, n, i, r, s) {
    this.vsWorker = t, this.req = n, this.channel = i, this.eventName = r, this.arg = s, this.type = pe.SubscribeEvent;
  }
}
class ya {
  constructor(t, n, i) {
    this.vsWorker = t, this.req = n, this.event = i, this.type = pe.Event;
  }
}
class Ba {
  constructor(t, n) {
    this.vsWorker = t, this.req = n, this.type = pe.UnsubscribeEvent;
  }
}
class Oa {
  constructor(t) {
    this._workerId = -1, this._handler = t, this._lastSentReq = 0, this._pendingReplies = /* @__PURE__ */ Object.create(null), this._pendingEmitters = /* @__PURE__ */ new Map(), this._pendingEvents = /* @__PURE__ */ new Map();
  }
  setWorkerId(t) {
    this._workerId = t;
  }
  sendMessage(t, n, i) {
    const r = String(++this._lastSentReq);
    return new Promise((s, a) => {
      this._pendingReplies[r] = {
        resolve: s,
        reject: a
      }, this._send(new Sa(this._workerId, r, t, n, i));
    });
  }
  listen(t, n, i) {
    let r = null;
    const s = new Ae({
      onWillAddFirstListener: () => {
        r = String(++this._lastSentReq), this._pendingEmitters.set(r, s), this._send(new Pa(this._workerId, r, t, n, i));
      },
      onDidRemoveLastListener: () => {
        this._pendingEmitters.delete(r), this._send(new Ba(this._workerId, r)), r = null;
      }
    });
    return s.event;
  }
  handleMessage(t) {
    !t || !t.vsWorker || this._workerId !== -1 && t.vsWorker !== this._workerId || this._handleMessage(t);
  }
  createProxyToRemoteChannel(t, n) {
    const i = {
      get: (r, s) => (typeof s == "string" && !r[s] && (us(s) ? r[s] = (a) => this.listen(t, s, a) : ls(s) ? r[s] = this.listen(t, s, void 0) : s.charCodeAt(0) === L.DollarSign && (r[s] = async (...a) => (await (n == null ? void 0 : n()), this.sendMessage(t, s, a)))), r[s])
    };
    return new Proxy(/* @__PURE__ */ Object.create(null), i);
  }
  _handleMessage(t) {
    switch (t.type) {
      case pe.Reply:
        return this._handleReplyMessage(t);
      case pe.Request:
        return this._handleRequestMessage(t);
      case pe.SubscribeEvent:
        return this._handleSubscribeEventMessage(t);
      case pe.Event:
        return this._handleEventMessage(t);
      case pe.UnsubscribeEvent:
        return this._handleUnsubscribeEventMessage(t);
    }
  }
  _handleReplyMessage(t) {
    if (!this._pendingReplies[t.seq]) {
      console.warn("Got reply to unknown seq");
      return;
    }
    const n = this._pendingReplies[t.seq];
    if (delete this._pendingReplies[t.seq], t.err) {
      let i = t.err;
      t.err.$isError && (i = new Error(), i.name = t.err.name, i.message = t.err.message, i.stack = t.err.stack), n.reject(i);
      return;
    }
    n.resolve(t.res);
  }
  _handleRequestMessage(t) {
    const n = t.req;
    this._handler.handleMessage(t.channel, t.method, t.args).then((r) => {
      this._send(new Ii(this._workerId, n, r, void 0));
    }, (r) => {
      r.detail instanceof Error && (r.detail = On(r.detail)), this._send(new Ii(this._workerId, n, void 0, On(r)));
    });
  }
  _handleSubscribeEventMessage(t) {
    const n = t.req, i = this._handler.handleEvent(t.channel, t.eventName, t.arg)((r) => {
      this._send(new ya(this._workerId, n, r));
    });
    this._pendingEvents.set(n, i);
  }
  _handleEventMessage(t) {
    if (!this._pendingEmitters.has(t.req)) {
      console.warn("Got event for unknown req");
      return;
    }
    this._pendingEmitters.get(t.req).fire(t.event);
  }
  _handleUnsubscribeEventMessage(t) {
    if (!this._pendingEvents.has(t.req)) {
      console.warn("Got unsubscribe for unknown req");
      return;
    }
    this._pendingEvents.get(t.req).dispose(), this._pendingEvents.delete(t.req);
  }
  _send(t) {
    const n = [];
    if (t.type === pe.Request)
      for (let i = 0; i < t.args.length; i++)
        t.args[i] instanceof ArrayBuffer && n.push(t.args[i]);
    else t.type === pe.Reply && t.res instanceof ArrayBuffer && n.push(t.res);
    this._handler.sendMessage(t, n);
  }
}
function ls(e) {
  return e[0] === "o" && e[1] === "n" && ss(e.charCodeAt(2));
}
function us(e) {
  return /^onDynamic/.test(e) && ss(e.charCodeAt(9));
}
class Va {
  constructor(t, n) {
    this._localChannels = /* @__PURE__ */ new Map(), this._remoteChannels = /* @__PURE__ */ new Map(), this._requestHandlerFactory = n, this._requestHandler = null, this._protocol = new Oa({
      sendMessage: (i, r) => {
        t(i, r);
      },
      handleMessage: (i, r, s) => this._handleMessage(i, r, s),
      handleEvent: (i, r, s) => this._handleEvent(i, r, s)
    });
  }
  onmessage(t) {
    this._protocol.handleMessage(t);
  }
  _handleMessage(t, n, i) {
    if (t === Fn && n === Ia)
      return this.initialize(i[0], i[1], i[2]);
    const r = t === Fn ? this._requestHandler : this._localChannels.get(t);
    if (!r)
      return Promise.reject(new Error(`Missing channel ${t} on worker thread`));
    if (typeof r[n] != "function")
      return Promise.reject(new Error(`Missing method ${n} on worker thread channel ${t}`));
    try {
      return Promise.resolve(r[n].apply(r, i));
    } catch (s) {
      return Promise.reject(s);
    }
  }
  _handleEvent(t, n, i) {
    const r = t === Fn ? this._requestHandler : this._localChannels.get(t);
    if (!r)
      throw new Error(`Missing channel ${t} on worker thread`);
    if (us(n)) {
      const s = r[n].call(r, i);
      if (typeof s != "function")
        throw new Error(`Missing dynamic event ${n} on request handler.`);
      return s;
    }
    if (ls(n)) {
      const s = r[n];
      if (typeof s != "function")
        throw new Error(`Missing event ${n} on request handler.`);
      return s;
    }
    throw new Error(`Malformed event name ${n}`);
  }
  setChannel(t, n) {
    this._localChannels.set(t, n);
  }
  getChannel(t) {
    if (!this._remoteChannels.has(t)) {
      const n = this._protocol.createProxyToRemoteChannel(t);
      this._remoteChannels.set(t, n);
    }
    return this._remoteChannels.get(t);
  }
  async initialize(t, n, i) {
    if (this._protocol.setWorkerId(t), this._requestHandlerFactory) {
      this._requestHandler = this._requestHandlerFactory(this);
      return;
    }
    return n && (typeof n.baseUrl < "u" && delete n.baseUrl, typeof n.paths < "u" && typeof n.paths.vs < "u" && delete n.paths.vs, typeof n.trustedTypesPolicy < "u" && delete n.trustedTypesPolicy, n.catchError = !0, globalThis.require.config(n)), Promise.reject(new Error("Unexpected usage"));
  }
}
class je {
  constructor(t, n, i, r) {
    this.originalStart = t, this.originalLength = n, this.modifiedStart = i, this.modifiedLength = r;
  }
  getOriginalEnd() {
    return this.originalStart + this.originalLength;
  }
  getModifiedEnd() {
    return this.modifiedStart + this.modifiedLength;
  }
}
function Si(e, t) {
  return (t << 5) - t + e | 0;
}
function qa(e, t) {
  t = Si(149417, t);
  for (let n = 0, i = e.length; n < i; n++)
    t = Si(e.charCodeAt(n), t);
  return t;
}
var Ee;
(function(e) {
  e[e.BLOCK_SIZE = 64] = "BLOCK_SIZE", e[e.UNICODE_REPLACEMENT = 65533] = "UNICODE_REPLACEMENT";
})(Ee || (Ee = {}));
function In(e, t, n = 32) {
  const i = n - t, r = ~((1 << i) - 1);
  return (e << t | (r & e) >>> i) >>> 0;
}
function Mt(e, t = 32) {
  return e instanceof ArrayBuffer ? Array.from(new Uint8Array(e)).map((n) => n.toString(16).padStart(2, "0")).join("") : (e >>> 0).toString(16).padStart(t / 4, "0");
}
const Rn = class Rn {
  constructor() {
    this._h0 = 1732584193, this._h1 = 4023233417, this._h2 = 2562383102, this._h3 = 271733878, this._h4 = 3285377520, this._buff = new Uint8Array(Ee.BLOCK_SIZE + 3), this._buffDV = new DataView(this._buff.buffer), this._buffLen = 0, this._totalLen = 0, this._leftoverHighSurrogate = 0, this._finished = !1;
  }
  update(t) {
    const n = t.length;
    if (n === 0)
      return;
    const i = this._buff;
    let r = this._buffLen, s = this._leftoverHighSurrogate, a, u;
    for (s !== 0 ? (a = s, u = -1, s = 0) : (a = t.charCodeAt(0), u = 0); ; ) {
      let o = a;
      if (gn(a))
        if (u + 1 < n) {
          const c = t.charCodeAt(u + 1);
          zn(c) ? (u++, o = as(a, c)) : o = Ee.UNICODE_REPLACEMENT;
        } else {
          s = a;
          break;
        }
      else zn(a) && (o = Ee.UNICODE_REPLACEMENT);
      if (r = this._push(i, r, o), u++, u < n)
        a = t.charCodeAt(u);
      else
        break;
    }
    this._buffLen = r, this._leftoverHighSurrogate = s;
  }
  _push(t, n, i) {
    return i < 128 ? t[n++] = i : i < 2048 ? (t[n++] = 192 | (i & 1984) >>> 6, t[n++] = 128 | (i & 63) >>> 0) : i < 65536 ? (t[n++] = 224 | (i & 61440) >>> 12, t[n++] = 128 | (i & 4032) >>> 6, t[n++] = 128 | (i & 63) >>> 0) : (t[n++] = 240 | (i & 1835008) >>> 18, t[n++] = 128 | (i & 258048) >>> 12, t[n++] = 128 | (i & 4032) >>> 6, t[n++] = 128 | (i & 63) >>> 0), n >= Ee.BLOCK_SIZE && (this._step(), n -= Ee.BLOCK_SIZE, this._totalLen += Ee.BLOCK_SIZE, t[0] = t[Ee.BLOCK_SIZE + 0], t[1] = t[Ee.BLOCK_SIZE + 1], t[2] = t[Ee.BLOCK_SIZE + 2]), n;
  }
  digest() {
    return this._finished || (this._finished = !0, this._leftoverHighSurrogate && (this._leftoverHighSurrogate = 0, this._buffLen = this._push(this._buff, this._buffLen, Ee.UNICODE_REPLACEMENT)), this._totalLen += this._buffLen, this._wrapUp()), Mt(this._h0) + Mt(this._h1) + Mt(this._h2) + Mt(this._h3) + Mt(this._h4);
  }
  _wrapUp() {
    this._buff[this._buffLen++] = 128, this._buff.subarray(this._buffLen).fill(0), this._buffLen > 56 && (this._step(), this._buff.fill(0));
    const t = 8 * this._totalLen;
    this._buffDV.setUint32(56, Math.floor(t / 4294967296), !1), this._buffDV.setUint32(60, t % 4294967296, !1), this._step();
  }
  _step() {
    const t = Rn._bigBlock32, n = this._buffDV;
    for (let f = 0; f < 64; f += 4)
      t.setUint32(f, n.getUint32(f, !1), !1);
    for (let f = 64; f < 320; f += 4)
      t.setUint32(f, In(t.getUint32(f - 12, !1) ^ t.getUint32(f - 32, !1) ^ t.getUint32(f - 56, !1) ^ t.getUint32(f - 64, !1), 1), !1);
    let i = this._h0, r = this._h1, s = this._h2, a = this._h3, u = this._h4, o, c, h;
    for (let f = 0; f < 80; f++)
      f < 20 ? (o = r & s | ~r & a, c = 1518500249) : f < 40 ? (o = r ^ s ^ a, c = 1859775393) : f < 60 ? (o = r & s | r & a | s & a, c = 2400959708) : (o = r ^ s ^ a, c = 3395469782), h = In(i, 5) + o + u + c + t.getUint32(f * 4, !1) & 4294967295, u = a, a = s, s = In(r, 30), r = i, i = h;
    this._h0 = this._h0 + i & 4294967295, this._h1 = this._h1 + r & 4294967295, this._h2 = this._h2 + s & 4294967295, this._h3 = this._h3 + a & 4294967295, this._h4 = this._h4 + u & 4294967295;
  }
};
Rn._bigBlock32 = new DataView(new ArrayBuffer(320));
let Pi = Rn;
class yi {
  constructor(t) {
    this.source = t;
  }
  getElements() {
    const t = this.source, n = new Int32Array(t.length);
    for (let i = 0, r = t.length; i < r; i++)
      n[i] = t.charCodeAt(i);
    return n;
  }
}
function Ha(e, t, n) {
  return new Ye(new yi(e), new yi(t)).ComputeDiff(n).changes;
}
class ut {
  static Assert(t, n) {
    if (!t)
      throw new Error(n);
  }
}
class ot {
  static Copy(t, n, i, r, s) {
    for (let a = 0; a < s; a++)
      i[r + a] = t[n + a];
  }
  static Copy2(t, n, i, r, s) {
    for (let a = 0; a < s; a++)
      i[r + a] = t[n + a];
  }
}
var Be;
(function(e) {
  e[e.MaxDifferencesHistory = 1447] = "MaxDifferencesHistory";
})(Be || (Be = {}));
class Bi {
  constructor() {
    this.m_changes = [], this.m_originalStart = Ue.MAX_SAFE_SMALL_INTEGER, this.m_modifiedStart = Ue.MAX_SAFE_SMALL_INTEGER, this.m_originalCount = 0, this.m_modifiedCount = 0;
  }
  MarkNextChange() {
    (this.m_originalCount > 0 || this.m_modifiedCount > 0) && this.m_changes.push(new je(
      this.m_originalStart,
      this.m_originalCount,
      this.m_modifiedStart,
      this.m_modifiedCount
    )), this.m_originalCount = 0, this.m_modifiedCount = 0, this.m_originalStart = Ue.MAX_SAFE_SMALL_INTEGER, this.m_modifiedStart = Ue.MAX_SAFE_SMALL_INTEGER;
  }
  AddOriginalElement(t, n) {
    this.m_originalStart = Math.min(this.m_originalStart, t), this.m_modifiedStart = Math.min(this.m_modifiedStart, n), this.m_originalCount++;
  }
  AddModifiedElement(t, n) {
    this.m_originalStart = Math.min(this.m_originalStart, t), this.m_modifiedStart = Math.min(this.m_modifiedStart, n), this.m_modifiedCount++;
  }
  getChanges() {
    return (this.m_originalCount > 0 || this.m_modifiedCount > 0) && this.MarkNextChange(), this.m_changes;
  }
  getReverseChanges() {
    return (this.m_originalCount > 0 || this.m_modifiedCount > 0) && this.MarkNextChange(), this.m_changes.reverse(), this.m_changes;
  }
}
class Ye {
  constructor(t, n, i = null) {
    this.ContinueProcessingPredicate = i, this._originalSequence = t, this._modifiedSequence = n;
    const [r, s, a] = Ye._getElements(t), [u, o, c] = Ye._getElements(n);
    this._hasStrings = a && c, this._originalStringElements = r, this._originalElementsOrHash = s, this._modifiedStringElements = u, this._modifiedElementsOrHash = o, this.m_forwardHistory = [], this.m_reverseHistory = [];
  }
  static _isStringArray(t) {
    return t.length > 0 && typeof t[0] == "string";
  }
  static _getElements(t) {
    const n = t.getElements();
    if (Ye._isStringArray(n)) {
      const i = new Int32Array(n.length);
      for (let r = 0, s = n.length; r < s; r++)
        i[r] = qa(n[r], 0);
      return [n, i, !0];
    }
    return n instanceof Int32Array ? [[], n, !1] : [[], new Int32Array(n), !1];
  }
  ElementsAreEqual(t, n) {
    return this._originalElementsOrHash[t] !== this._modifiedElementsOrHash[n] ? !1 : this._hasStrings ? this._originalStringElements[t] === this._modifiedStringElements[n] : !0;
  }
  ElementsAreStrictEqual(t, n) {
    if (!this.ElementsAreEqual(t, n))
      return !1;
    const i = Ye._getStrictElement(this._originalSequence, t), r = Ye._getStrictElement(this._modifiedSequence, n);
    return i === r;
  }
  static _getStrictElement(t, n) {
    return typeof t.getStrictElement == "function" ? t.getStrictElement(n) : null;
  }
  OriginalElementsAreEqual(t, n) {
    return this._originalElementsOrHash[t] !== this._originalElementsOrHash[n] ? !1 : this._hasStrings ? this._originalStringElements[t] === this._originalStringElements[n] : !0;
  }
  ModifiedElementsAreEqual(t, n) {
    return this._modifiedElementsOrHash[t] !== this._modifiedElementsOrHash[n] ? !1 : this._hasStrings ? this._modifiedStringElements[t] === this._modifiedStringElements[n] : !0;
  }
  ComputeDiff(t) {
    return this._ComputeDiff(0, this._originalElementsOrHash.length - 1, 0, this._modifiedElementsOrHash.length - 1, t);
  }
  _ComputeDiff(t, n, i, r, s) {
    const a = [!1];
    let u = this.ComputeDiffRecursive(t, n, i, r, a);
    return s && (u = this.PrettifyChanges(u)), {
      quitEarly: a[0],
      changes: u
    };
  }
  ComputeDiffRecursive(t, n, i, r, s) {
    for (s[0] = !1; t <= n && i <= r && this.ElementsAreEqual(t, i); )
      t++, i++;
    for (; n >= t && r >= i && this.ElementsAreEqual(n, r); )
      n--, r--;
    if (t > n || i > r) {
      let f;
      return i <= r ? (ut.Assert(t === n + 1, "originalStart should only be one more than originalEnd"), f = [
        new je(t, 0, i, r - i + 1)
      ]) : t <= n ? (ut.Assert(i === r + 1, "modifiedStart should only be one more than modifiedEnd"), f = [
        new je(t, n - t + 1, i, 0)
      ]) : (ut.Assert(t === n + 1, "originalStart should only be one more than originalEnd"), ut.Assert(i === r + 1, "modifiedStart should only be one more than modifiedEnd"), f = []), f;
    }
    const a = [0], u = [0], o = this.ComputeRecursionPoint(t, n, i, r, a, u, s), c = a[0], h = u[0];
    if (o !== null)
      return o;
    if (!s[0]) {
      const f = this.ComputeDiffRecursive(t, c, i, h, s);
      let _ = [];
      return s[0] ? _ = [
        new je(
          c + 1,
          n - (c + 1) + 1,
          h + 1,
          r - (h + 1) + 1
        )
      ] : _ = this.ComputeDiffRecursive(c + 1, n, h + 1, r, s), this.ConcatenateChanges(f, _);
    }
    return [
      new je(
        t,
        n - t + 1,
        i,
        r - i + 1
      )
    ];
  }
  WALKTRACE(t, n, i, r, s, a, u, o, c, h, f, _, p, d, b, A, v, x) {
    let R = null, N = null, E = new Bi(), U = n, D = i, S = p[0] - A[0] - r, X = Ue.MIN_SAFE_SMALL_INTEGER, ie = this.m_forwardHistory.length - 1;
    do {
      const Y = S + t;
      Y === U || Y < D && c[Y - 1] < c[Y + 1] ? (f = c[Y + 1], d = f - S - r, f < X && E.MarkNextChange(), X = f, E.AddModifiedElement(f + 1, d), S = Y + 1 - t) : (f = c[Y - 1] + 1, d = f - S - r, f < X && E.MarkNextChange(), X = f - 1, E.AddOriginalElement(f, d + 1), S = Y - 1 - t), ie >= 0 && (c = this.m_forwardHistory[ie], t = c[0], U = 1, D = c.length - 1);
    } while (--ie >= -1);
    if (R = E.getReverseChanges(), x[0]) {
      let Y = p[0] + 1, H = A[0] + 1;
      if (R !== null && R.length > 0) {
        const I = R[R.length - 1];
        Y = Math.max(Y, I.getOriginalEnd()), H = Math.max(H, I.getModifiedEnd());
      }
      N = [
        new je(
          Y,
          _ - Y + 1,
          H,
          b - H + 1
        )
      ];
    } else {
      E = new Bi(), U = a, D = u, S = p[0] - A[0] - o, X = Ue.MAX_SAFE_SMALL_INTEGER, ie = v ? this.m_reverseHistory.length - 1 : this.m_reverseHistory.length - 2;
      do {
        const Y = S + s;
        Y === U || Y < D && h[Y - 1] >= h[Y + 1] ? (f = h[Y + 1] - 1, d = f - S - o, f > X && E.MarkNextChange(), X = f + 1, E.AddOriginalElement(f + 1, d + 1), S = Y + 1 - s) : (f = h[Y - 1], d = f - S - o, f > X && E.MarkNextChange(), X = f, E.AddModifiedElement(f + 1, d + 1), S = Y - 1 - s), ie >= 0 && (h = this.m_reverseHistory[ie], s = h[0], U = 1, D = h.length - 1);
      } while (--ie >= -1);
      N = E.getChanges();
    }
    return this.ConcatenateChanges(R, N);
  }
  ComputeRecursionPoint(t, n, i, r, s, a, u) {
    let o = 0, c = 0, h = 0, f = 0, _ = 0, p = 0;
    t--, i--, s[0] = 0, a[0] = 0, this.m_forwardHistory = [], this.m_reverseHistory = [];
    const d = n - t + (r - i), b = d + 1, A = new Int32Array(b), v = new Int32Array(b), x = r - i, R = n - t, N = t - i, E = n - r, D = (R - x) % 2 === 0;
    A[x] = t, v[R] = n, u[0] = !1;
    for (let S = 1; S <= d / 2 + 1; S++) {
      let X = 0, ie = 0;
      h = this.ClipDiagonalBound(x - S, S, x, b), f = this.ClipDiagonalBound(x + S, S, x, b);
      for (let H = h; H <= f; H += 2) {
        H === h || H < f && A[H - 1] < A[H + 1] ? o = A[H + 1] : o = A[H - 1] + 1, c = o - (H - x) - N;
        const I = o;
        for (; o < n && c < r && this.ElementsAreEqual(o + 1, c + 1); )
          o++, c++;
        if (A[H] = o, o + c > X + ie && (X = o, ie = c), !D && Math.abs(H - R) <= S - 1 && o >= v[H])
          return s[0] = o, a[0] = c, I <= v[H] && Be.MaxDifferencesHistory > 0 && S <= Be.MaxDifferencesHistory + 1 ? this.WALKTRACE(x, h, f, N, R, _, p, E, A, v, o, n, s, c, r, a, D, u) : null;
      }
      const Y = (X - t + (ie - i) - S) / 2;
      if (this.ContinueProcessingPredicate !== null && !this.ContinueProcessingPredicate(X, Y))
        return u[0] = !0, s[0] = X, a[0] = ie, Y > 0 && Be.MaxDifferencesHistory > 0 && S <= Be.MaxDifferencesHistory + 1 ? this.WALKTRACE(x, h, f, N, R, _, p, E, A, v, o, n, s, c, r, a, D, u) : (t++, i++, [
          new je(
            t,
            n - t + 1,
            i,
            r - i + 1
          )
        ]);
      _ = this.ClipDiagonalBound(R - S, S, R, b), p = this.ClipDiagonalBound(R + S, S, R, b);
      for (let H = _; H <= p; H += 2) {
        H === _ || H < p && v[H - 1] >= v[H + 1] ? o = v[H + 1] - 1 : o = v[H - 1], c = o - (H - R) - E;
        const I = o;
        for (; o > t && c > i && this.ElementsAreEqual(o, c); )
          o--, c--;
        if (v[H] = o, D && Math.abs(H - x) <= S && o <= A[H])
          return s[0] = o, a[0] = c, I >= A[H] && Be.MaxDifferencesHistory > 0 && S <= Be.MaxDifferencesHistory + 1 ? this.WALKTRACE(x, h, f, N, R, _, p, E, A, v, o, n, s, c, r, a, D, u) : null;
      }
      if (S <= Be.MaxDifferencesHistory) {
        let H = new Int32Array(f - h + 2);
        H[0] = x - h + 1, ot.Copy2(A, h, H, 1, f - h + 1), this.m_forwardHistory.push(H), H = new Int32Array(p - _ + 2), H[0] = R - _ + 1, ot.Copy2(v, _, H, 1, p - _ + 1), this.m_reverseHistory.push(H);
      }
    }
    return this.WALKTRACE(x, h, f, N, R, _, p, E, A, v, o, n, s, c, r, a, D, u);
  }
  PrettifyChanges(t) {
    for (let n = 0; n < t.length; n++) {
      const i = t[n], r = n < t.length - 1 ? t[n + 1].originalStart : this._originalElementsOrHash.length, s = n < t.length - 1 ? t[n + 1].modifiedStart : this._modifiedElementsOrHash.length, a = i.originalLength > 0, u = i.modifiedLength > 0;
      for (; i.originalStart + i.originalLength < r && i.modifiedStart + i.modifiedLength < s && (!a || this.OriginalElementsAreEqual(i.originalStart, i.originalStart + i.originalLength)) && (!u || this.ModifiedElementsAreEqual(i.modifiedStart, i.modifiedStart + i.modifiedLength)); ) {
        const c = this.ElementsAreStrictEqual(i.originalStart, i.modifiedStart);
        if (this.ElementsAreStrictEqual(i.originalStart + i.originalLength, i.modifiedStart + i.modifiedLength) && !c)
          break;
        i.originalStart++, i.modifiedStart++;
      }
      const o = [null];
      if (n < t.length - 1 && this.ChangesOverlap(t[n], t[n + 1], o)) {
        t[n] = o[0], t.splice(n + 1, 1), n--;
        continue;
      }
    }
    for (let n = t.length - 1; n >= 0; n--) {
      const i = t[n];
      let r = 0, s = 0;
      if (n > 0) {
        const f = t[n - 1];
        r = f.originalStart + f.originalLength, s = f.modifiedStart + f.modifiedLength;
      }
      const a = i.originalLength > 0, u = i.modifiedLength > 0;
      let o = 0, c = this._boundaryScore(i.originalStart, i.originalLength, i.modifiedStart, i.modifiedLength);
      for (let f = 1; ; f++) {
        const _ = i.originalStart - f, p = i.modifiedStart - f;
        if (_ < r || p < s || a && !this.OriginalElementsAreEqual(_, _ + i.originalLength) || u && !this.ModifiedElementsAreEqual(p, p + i.modifiedLength))
          break;
        const b = (_ === r && p === s ? 5 : 0) + this._boundaryScore(_, i.originalLength, p, i.modifiedLength);
        b > c && (c = b, o = f);
      }
      i.originalStart -= o, i.modifiedStart -= o;
      const h = [null];
      if (n > 0 && this.ChangesOverlap(t[n - 1], t[n], h)) {
        t[n - 1] = h[0], t.splice(n, 1), n++;
        continue;
      }
    }
    if (this._hasStrings)
      for (let n = 1, i = t.length; n < i; n++) {
        const r = t[n - 1], s = t[n], a = s.originalStart - r.originalStart - r.originalLength, u = r.originalStart, o = s.originalStart + s.originalLength, c = o - u, h = r.modifiedStart, f = s.modifiedStart + s.modifiedLength, _ = f - h;
        if (a < 5 && c < 20 && _ < 20) {
          const p = this._findBetterContiguousSequence(u, c, h, _, a);
          if (p) {
            const [d, b] = p;
            (d !== r.originalStart + r.originalLength || b !== r.modifiedStart + r.modifiedLength) && (r.originalLength = d - r.originalStart, r.modifiedLength = b - r.modifiedStart, s.originalStart = d + a, s.modifiedStart = b + a, s.originalLength = o - s.originalStart, s.modifiedLength = f - s.modifiedStart);
          }
        }
      }
    return t;
  }
  _findBetterContiguousSequence(t, n, i, r, s) {
    if (n < s || r < s)
      return null;
    const a = t + n - s + 1, u = i + r - s + 1;
    let o = 0, c = 0, h = 0;
    for (let f = t; f < a; f++)
      for (let _ = i; _ < u; _++) {
        const p = this._contiguousSequenceScore(f, _, s);
        p > 0 && p > o && (o = p, c = f, h = _);
      }
    return o > 0 ? [c, h] : null;
  }
  _contiguousSequenceScore(t, n, i) {
    let r = 0;
    for (let s = 0; s < i; s++) {
      if (!this.ElementsAreEqual(t + s, n + s))
        return 0;
      r += this._originalStringElements[t + s].length;
    }
    return r;
  }
  _OriginalIsBoundary(t) {
    return t <= 0 || t >= this._originalElementsOrHash.length - 1 ? !0 : this._hasStrings && /^\s*$/.test(this._originalStringElements[t]);
  }
  _OriginalRegionIsBoundary(t, n) {
    if (this._OriginalIsBoundary(t) || this._OriginalIsBoundary(t - 1))
      return !0;
    if (n > 0) {
      const i = t + n;
      if (this._OriginalIsBoundary(i - 1) || this._OriginalIsBoundary(i))
        return !0;
    }
    return !1;
  }
  _ModifiedIsBoundary(t) {
    return t <= 0 || t >= this._modifiedElementsOrHash.length - 1 ? !0 : this._hasStrings && /^\s*$/.test(this._modifiedStringElements[t]);
  }
  _ModifiedRegionIsBoundary(t, n) {
    if (this._ModifiedIsBoundary(t) || this._ModifiedIsBoundary(t - 1))
      return !0;
    if (n > 0) {
      const i = t + n;
      if (this._ModifiedIsBoundary(i - 1) || this._ModifiedIsBoundary(i))
        return !0;
    }
    return !1;
  }
  _boundaryScore(t, n, i, r) {
    const s = this._OriginalRegionIsBoundary(t, n) ? 1 : 0, a = this._ModifiedRegionIsBoundary(i, r) ? 1 : 0;
    return s + a;
  }
  ConcatenateChanges(t, n) {
    const i = [];
    if (t.length === 0 || n.length === 0)
      return n.length > 0 ? n : t;
    if (this.ChangesOverlap(t[t.length - 1], n[0], i)) {
      const r = new Array(t.length + n.length - 1);
      return ot.Copy(t, 0, r, 0, t.length - 1), r[t.length - 1] = i[0], ot.Copy(n, 1, r, t.length, n.length - 1), r;
    } else {
      const r = new Array(t.length + n.length);
      return ot.Copy(t, 0, r, 0, t.length), ot.Copy(n, 0, r, t.length, n.length), r;
    }
  }
  ChangesOverlap(t, n, i) {
    if (ut.Assert(t.originalStart <= n.originalStart, "Left change is not less than or equal to right change"), ut.Assert(t.modifiedStart <= n.modifiedStart, "Left change is not less than or equal to right change"), t.originalStart + t.originalLength >= n.originalStart || t.modifiedStart + t.modifiedLength >= n.modifiedStart) {
      const r = t.originalStart;
      let s = t.originalLength;
      const a = t.modifiedStart;
      let u = t.modifiedLength;
      return t.originalStart + t.originalLength >= n.originalStart && (s = n.originalStart + n.originalLength - t.originalStart), t.modifiedStart + t.modifiedLength >= n.modifiedStart && (u = n.modifiedStart + n.modifiedLength - t.modifiedStart), i[0] = new je(r, s, a, u), !0;
    } else
      return i[0] = null, !1;
  }
  ClipDiagonalBound(t, n, i, r) {
    if (t >= 0 && t < r)
      return t;
    const s = i, a = r - i - 1, u = n % 2 === 0;
    if (t < 0) {
      const o = s % 2 === 0;
      return u === o ? 0 : 1;
    } else {
      const o = a % 2 === 0;
      return u === o ? r - 1 : r - 2;
    }
  }
}
class W {
  constructor(t, n) {
    this.lineNumber = t, this.column = n;
  }
  with(t = this.lineNumber, n = this.column) {
    return t === this.lineNumber && n === this.column ? this : new W(t, n);
  }
  delta(t = 0, n = 0) {
    return this.with(Math.max(1, this.lineNumber + t), Math.max(1, this.column + n));
  }
  equals(t) {
    return W.equals(this, t);
  }
  static equals(t, n) {
    return !t && !n ? !0 : !!t && !!n && t.lineNumber === n.lineNumber && t.column === n.column;
  }
  isBefore(t) {
    return W.isBefore(this, t);
  }
  static isBefore(t, n) {
    return t.lineNumber < n.lineNumber ? !0 : n.lineNumber < t.lineNumber ? !1 : t.column < n.column;
  }
  isBeforeOrEqual(t) {
    return W.isBeforeOrEqual(this, t);
  }
  static isBeforeOrEqual(t, n) {
    return t.lineNumber < n.lineNumber ? !0 : n.lineNumber < t.lineNumber ? !1 : t.column <= n.column;
  }
  static compare(t, n) {
    const i = t.lineNumber | 0, r = n.lineNumber | 0;
    if (i === r) {
      const s = t.column | 0, a = n.column | 0;
      return s - a;
    }
    return i - r;
  }
  clone() {
    return new W(this.lineNumber, this.column);
  }
  toString() {
    return "(" + this.lineNumber + "," + this.column + ")";
  }
  static lift(t) {
    return new W(t.lineNumber, t.column);
  }
  static isIPosition(t) {
    return t && typeof t.lineNumber == "number" && typeof t.column == "number";
  }
  toJSON() {
    return {
      lineNumber: this.lineNumber,
      column: this.column
    };
  }
}
class F {
  constructor(t, n, i, r) {
    t > i || t === i && n > r ? (this.startLineNumber = i, this.startColumn = r, this.endLineNumber = t, this.endColumn = n) : (this.startLineNumber = t, this.startColumn = n, this.endLineNumber = i, this.endColumn = r);
  }
  isEmpty() {
    return F.isEmpty(this);
  }
  static isEmpty(t) {
    return t.startLineNumber === t.endLineNumber && t.startColumn === t.endColumn;
  }
  containsPosition(t) {
    return F.containsPosition(this, t);
  }
  static containsPosition(t, n) {
    return !(n.lineNumber < t.startLineNumber || n.lineNumber > t.endLineNumber || n.lineNumber === t.startLineNumber && n.column < t.startColumn || n.lineNumber === t.endLineNumber && n.column > t.endColumn);
  }
  static strictContainsPosition(t, n) {
    return !(n.lineNumber < t.startLineNumber || n.lineNumber > t.endLineNumber || n.lineNumber === t.startLineNumber && n.column <= t.startColumn || n.lineNumber === t.endLineNumber && n.column >= t.endColumn);
  }
  containsRange(t) {
    return F.containsRange(this, t);
  }
  static containsRange(t, n) {
    return !(n.startLineNumber < t.startLineNumber || n.endLineNumber < t.startLineNumber || n.startLineNumber > t.endLineNumber || n.endLineNumber > t.endLineNumber || n.startLineNumber === t.startLineNumber && n.startColumn < t.startColumn || n.endLineNumber === t.endLineNumber && n.endColumn > t.endColumn);
  }
  strictContainsRange(t) {
    return F.strictContainsRange(this, t);
  }
  static strictContainsRange(t, n) {
    return !(n.startLineNumber < t.startLineNumber || n.endLineNumber < t.startLineNumber || n.startLineNumber > t.endLineNumber || n.endLineNumber > t.endLineNumber || n.startLineNumber === t.startLineNumber && n.startColumn <= t.startColumn || n.endLineNumber === t.endLineNumber && n.endColumn >= t.endColumn);
  }
  plusRange(t) {
    return F.plusRange(this, t);
  }
  static plusRange(t, n) {
    let i, r, s, a;
    return n.startLineNumber < t.startLineNumber ? (i = n.startLineNumber, r = n.startColumn) : n.startLineNumber === t.startLineNumber ? (i = n.startLineNumber, r = Math.min(n.startColumn, t.startColumn)) : (i = t.startLineNumber, r = t.startColumn), n.endLineNumber > t.endLineNumber ? (s = n.endLineNumber, a = n.endColumn) : n.endLineNumber === t.endLineNumber ? (s = n.endLineNumber, a = Math.max(n.endColumn, t.endColumn)) : (s = t.endLineNumber, a = t.endColumn), new F(i, r, s, a);
  }
  intersectRanges(t) {
    return F.intersectRanges(this, t);
  }
  static intersectRanges(t, n) {
    let i = t.startLineNumber, r = t.startColumn, s = t.endLineNumber, a = t.endColumn;
    const u = n.startLineNumber, o = n.startColumn, c = n.endLineNumber, h = n.endColumn;
    return i < u ? (i = u, r = o) : i === u && (r = Math.max(r, o)), s > c ? (s = c, a = h) : s === c && (a = Math.min(a, h)), i > s || i === s && r > a ? null : new F(
      i,
      r,
      s,
      a
    );
  }
  equalsRange(t) {
    return F.equalsRange(this, t);
  }
  static equalsRange(t, n) {
    return !t && !n ? !0 : !!t && !!n && t.startLineNumber === n.startLineNumber && t.startColumn === n.startColumn && t.endLineNumber === n.endLineNumber && t.endColumn === n.endColumn;
  }
  getEndPosition() {
    return F.getEndPosition(this);
  }
  static getEndPosition(t) {
    return new W(t.endLineNumber, t.endColumn);
  }
  getStartPosition() {
    return F.getStartPosition(this);
  }
  static getStartPosition(t) {
    return new W(t.startLineNumber, t.startColumn);
  }
  toString() {
    return "[" + this.startLineNumber + "," + this.startColumn + " -> " + this.endLineNumber + "," + this.endColumn + "]";
  }
  setEndPosition(t, n) {
    return new F(this.startLineNumber, this.startColumn, t, n);
  }
  setStartPosition(t, n) {
    return new F(t, n, this.endLineNumber, this.endColumn);
  }
  collapseToStart() {
    return F.collapseToStart(this);
  }
  static collapseToStart(t) {
    return new F(
      t.startLineNumber,
      t.startColumn,
      t.startLineNumber,
      t.startColumn
    );
  }
  collapseToEnd() {
    return F.collapseToEnd(this);
  }
  static collapseToEnd(t) {
    return new F(t.endLineNumber, t.endColumn, t.endLineNumber, t.endColumn);
  }
  delta(t) {
    return new F(
      this.startLineNumber + t,
      this.startColumn,
      this.endLineNumber + t,
      this.endColumn
    );
  }
  isSingleLine() {
    return this.startLineNumber === this.endLineNumber;
  }
  static fromPositions(t, n = t) {
    return new F(t.lineNumber, t.column, n.lineNumber, n.column);
  }
  static lift(t) {
    return t ? new F(
      t.startLineNumber,
      t.startColumn,
      t.endLineNumber,
      t.endColumn
    ) : null;
  }
  static isIRange(t) {
    return t && typeof t.startLineNumber == "number" && typeof t.startColumn == "number" && typeof t.endLineNumber == "number" && typeof t.endColumn == "number";
  }
  static areIntersectingOrTouching(t, n) {
    return !(t.endLineNumber < n.startLineNumber || t.endLineNumber === n.startLineNumber && t.endColumn < n.startColumn || n.endLineNumber < t.startLineNumber || n.endLineNumber === t.startLineNumber && n.endColumn < t.startColumn);
  }
  static areIntersecting(t, n) {
    return !(t.endLineNumber < n.startLineNumber || t.endLineNumber === n.startLineNumber && t.endColumn <= n.startColumn || n.endLineNumber < t.startLineNumber || n.endLineNumber === t.startLineNumber && n.endColumn <= t.startColumn);
  }
  static compareRangesUsingStarts(t, n) {
    if (t && n) {
      const s = t.startLineNumber | 0, a = n.startLineNumber | 0;
      if (s === a) {
        const u = t.startColumn | 0, o = n.startColumn | 0;
        if (u === o) {
          const c = t.endLineNumber | 0, h = n.endLineNumber | 0;
          if (c === h) {
            const f = t.endColumn | 0, _ = n.endColumn | 0;
            return f - _;
          }
          return c - h;
        }
        return u - o;
      }
      return s - a;
    }
    return (t ? 1 : 0) - (n ? 1 : 0);
  }
  static compareRangesUsingEnds(t, n) {
    return t.endLineNumber === n.endLineNumber ? t.endColumn === n.endColumn ? t.startLineNumber === n.startLineNumber ? t.startColumn - n.startColumn : t.startLineNumber - n.startLineNumber : t.endColumn - n.endColumn : t.endLineNumber - n.endLineNumber;
  }
  static spansMultipleLines(t) {
    return t.endLineNumber > t.startLineNumber;
  }
  toJSON() {
    return this;
  }
}
class gi {
  constructor(t) {
    const n = Ui(t);
    this._defaultValue = n, this._asciiMap = gi._createAsciiMap(n), this._map = /* @__PURE__ */ new Map();
  }
  static _createAsciiMap(t) {
    const n = new Uint8Array(256);
    return n.fill(t), n;
  }
  set(t, n) {
    const i = Ui(n);
    t >= 0 && t < 256 ? this._asciiMap[t] = i : this._map.set(t, i);
  }
  get(t) {
    return t >= 0 && t < 256 ? this._asciiMap[t] : this._map.get(t) || this._defaultValue;
  }
  clear() {
    this._asciiMap.fill(this._defaultValue), this._map.clear();
  }
}
var Oi;
(function(e) {
  e[e.False = 0] = "False", e[e.True = 1] = "True";
})(Oi || (Oi = {}));
var O;
(function(e) {
  e[e.Invalid = 0] = "Invalid", e[e.Start = 1] = "Start", e[e.H = 2] = "H", e[e.HT = 3] = "HT", e[e.HTT = 4] = "HTT", e[e.HTTP = 5] = "HTTP", e[e.F = 6] = "F", e[e.FI = 7] = "FI", e[e.FIL = 8] = "FIL", e[e.BeforeColon = 9] = "BeforeColon", e[e.AfterColon = 10] = "AfterColon", e[e.AlmostThere = 11] = "AlmostThere", e[e.End = 12] = "End", e[e.Accept = 13] = "Accept", e[e.LastKnownState = 14] = "LastKnownState";
})(O || (O = {}));
class Wa {
  constructor(t, n, i) {
    const r = new Uint8Array(t * n);
    for (let s = 0, a = t * n; s < a; s++)
      r[s] = i;
    this._data = r, this.rows = t, this.cols = n;
  }
  get(t, n) {
    return this._data[t * this.cols + n];
  }
  set(t, n, i) {
    this._data[t * this.cols + n] = i;
  }
}
class Ga {
  constructor(t) {
    let n = 0, i = O.Invalid;
    for (let s = 0, a = t.length; s < a; s++) {
      const [u, o, c] = t[s];
      o > n && (n = o), u > i && (i = u), c > i && (i = c);
    }
    n++, i++;
    const r = new Wa(i, n, O.Invalid);
    for (let s = 0, a = t.length; s < a; s++) {
      const [u, o, c] = t[s];
      r.set(u, o, c);
    }
    this._states = r, this._maxCharCode = n;
  }
  nextState(t, n) {
    return n < 0 || n >= this._maxCharCode ? O.Invalid : this._states.get(t, n);
  }
}
let Sn = null;
function $a() {
  return Sn === null && (Sn = new Ga([
    [O.Start, L.h, O.H],
    [O.Start, L.H, O.H],
    [O.Start, L.f, O.F],
    [O.Start, L.F, O.F],
    [O.H, L.t, O.HT],
    [O.H, L.T, O.HT],
    [O.HT, L.t, O.HTT],
    [O.HT, L.T, O.HTT],
    [O.HTT, L.p, O.HTTP],
    [O.HTT, L.P, O.HTTP],
    [O.HTTP, L.s, O.BeforeColon],
    [O.HTTP, L.S, O.BeforeColon],
    [O.HTTP, L.Colon, O.AfterColon],
    [O.F, L.i, O.FI],
    [O.F, L.I, O.FI],
    [O.FI, L.l, O.FIL],
    [O.FI, L.L, O.FIL],
    [O.FIL, L.e, O.BeforeColon],
    [O.FIL, L.E, O.BeforeColon],
    [O.BeforeColon, L.Colon, O.AfterColon],
    [O.AfterColon, L.Slash, O.AlmostThere],
    [O.AlmostThere, L.Slash, O.End]
  ])), Sn;
}
var K;
(function(e) {
  e[e.None = 0] = "None", e[e.ForceTermination = 1] = "ForceTermination", e[e.CannotEndIn = 2] = "CannotEndIn";
})(K || (K = {}));
let Dt = null;
function za() {
  if (Dt === null) {
    Dt = new gi(K.None);
    const e = ` 	<>'"、。｡､，．：；‘〈「『〔（［｛｢｣｝］）〕』」〉’｀～…`;
    for (let n = 0; n < e.length; n++)
      Dt.set(e.charCodeAt(n), K.ForceTermination);
    const t = ".,;:";
    for (let n = 0; n < t.length; n++)
      Dt.set(t.charCodeAt(n), K.CannotEndIn);
  }
  return Dt;
}
class _n {
  static _createLink(t, n, i, r, s) {
    let a = s - 1;
    do {
      const u = n.charCodeAt(a);
      if (t.get(u) !== K.CannotEndIn)
        break;
      a--;
    } while (a > r);
    if (r > 0) {
      const u = n.charCodeAt(r - 1), o = n.charCodeAt(a);
      (u === L.OpenParen && o === L.CloseParen || u === L.OpenSquareBracket && o === L.CloseSquareBracket || u === L.OpenCurlyBrace && o === L.CloseCurlyBrace) && a--;
    }
    return {
      range: {
        startLineNumber: i,
        startColumn: r + 1,
        endLineNumber: i,
        endColumn: a + 2
      },
      url: n.substring(r, a + 1)
    };
  }
  static computeLinks(t, n = $a()) {
    const i = za(), r = [];
    for (let s = 1, a = t.getLineCount(); s <= a; s++) {
      const u = t.getLineContent(s), o = u.length;
      let c = 0, h = 0, f = 0, _ = O.Start, p = !1, d = !1, b = !1, A = !1;
      for (; c < o; ) {
        let v = !1;
        const x = u.charCodeAt(c);
        if (_ === O.Accept) {
          let R;
          switch (x) {
            case L.OpenParen:
              p = !0, R = K.None;
              break;
            case L.CloseParen:
              R = p ? K.None : K.ForceTermination;
              break;
            case L.OpenSquareBracket:
              b = !0, d = !0, R = K.None;
              break;
            case L.CloseSquareBracket:
              b = !1, R = d ? K.None : K.ForceTermination;
              break;
            case L.OpenCurlyBrace:
              A = !0, R = K.None;
              break;
            case L.CloseCurlyBrace:
              R = A ? K.None : K.ForceTermination;
              break;
            case L.SingleQuote:
            case L.DoubleQuote:
            case L.BackTick:
              f === x ? R = K.ForceTermination : f === L.SingleQuote || f === L.DoubleQuote || f === L.BackTick ? R = K.None : R = K.ForceTermination;
              break;
            case L.Asterisk:
              R = f === L.Asterisk ? K.ForceTermination : K.None;
              break;
            case L.Pipe:
              R = f === L.Pipe ? K.ForceTermination : K.None;
              break;
            case L.Space:
              R = b ? K.None : K.ForceTermination;
              break;
            default:
              R = i.get(x);
          }
          R === K.ForceTermination && (r.push(_n._createLink(i, u, s, h, c)), v = !0);
        } else if (_ === O.End) {
          let R;
          x === L.OpenSquareBracket ? (d = !0, R = K.None) : R = i.get(x), R === K.ForceTermination ? v = !0 : _ = O.Accept;
        } else
          _ = n.nextState(_, x), _ === O.Invalid && (v = !0);
        v && (_ = O.Start, p = !1, d = !1, A = !1, h = c + 1, f = x), c++;
      }
      _ === O.Accept && r.push(_n._createLink(i, u, s, h, o));
    }
    return r;
  }
}
function ja(e) {
  return !e || typeof e.getLineCount != "function" || typeof e.getLineContent != "function" ? [] : _n.computeLinks(e);
}
const Tn = class Tn {
  constructor() {
    this._defaultValueSet = [
      ["true", "false"],
      ["True", "False"],
      ["Private", "Public", "Friend", "ReadOnly", "Partial", "Protected", "WriteOnly"],
      ["public", "protected", "private"]
    ];
  }
  navigateValueSet(t, n, i, r, s) {
    if (t && n) {
      const a = this.doNavigateValueSet(n, s);
      if (a)
        return {
          range: t,
          value: a
        };
    }
    if (i && r) {
      const a = this.doNavigateValueSet(r, s);
      if (a)
        return {
          range: i,
          value: a
        };
    }
    return null;
  }
  doNavigateValueSet(t, n) {
    const i = this.numberReplace(t, n);
    return i !== null ? i : this.textReplace(t, n);
  }
  numberReplace(t, n) {
    const i = Math.pow(10, t.length - (t.lastIndexOf(".") + 1));
    let r = Number(t);
    const s = parseFloat(t);
    return !isNaN(r) && !isNaN(s) && r === s ? r === 0 && !n ? null : (r = Math.floor(r * i), r += n ? i : -i, String(r / i)) : null;
  }
  textReplace(t, n) {
    return this.valueSetsReplace(this._defaultValueSet, t, n);
  }
  valueSetsReplace(t, n, i) {
    let r = null;
    for (let s = 0, a = t.length; r === null && s < a; s++)
      r = this.valueSetReplace(t[s], n, i);
    return r;
  }
  valueSetReplace(t, n, i) {
    let r = t.indexOf(n);
    return r >= 0 ? (r += i ? 1 : -1, r < 0 ? r = t.length - 1 : r %= t.length, t[r]) : null;
  }
};
Tn.INSTANCE = new Tn();
let jn = Tn;
var m;
(function(e) {
  e[e.DependsOnKbLayout = -1] = "DependsOnKbLayout", e[e.Unknown = 0] = "Unknown", e[e.Backspace = 1] = "Backspace", e[e.Tab = 2] = "Tab", e[e.Enter = 3] = "Enter", e[e.Shift = 4] = "Shift", e[e.Ctrl = 5] = "Ctrl", e[e.Alt = 6] = "Alt", e[e.PauseBreak = 7] = "PauseBreak", e[e.CapsLock = 8] = "CapsLock", e[e.Escape = 9] = "Escape", e[e.Space = 10] = "Space", e[e.PageUp = 11] = "PageUp", e[e.PageDown = 12] = "PageDown", e[e.End = 13] = "End", e[e.Home = 14] = "Home", e[e.LeftArrow = 15] = "LeftArrow", e[e.UpArrow = 16] = "UpArrow", e[e.RightArrow = 17] = "RightArrow", e[e.DownArrow = 18] = "DownArrow", e[e.Insert = 19] = "Insert", e[e.Delete = 20] = "Delete", e[e.Digit0 = 21] = "Digit0", e[e.Digit1 = 22] = "Digit1", e[e.Digit2 = 23] = "Digit2", e[e.Digit3 = 24] = "Digit3", e[e.Digit4 = 25] = "Digit4", e[e.Digit5 = 26] = "Digit5", e[e.Digit6 = 27] = "Digit6", e[e.Digit7 = 28] = "Digit7", e[e.Digit8 = 29] = "Digit8", e[e.Digit9 = 30] = "Digit9", e[e.KeyA = 31] = "KeyA", e[e.KeyB = 32] = "KeyB", e[e.KeyC = 33] = "KeyC", e[e.KeyD = 34] = "KeyD", e[e.KeyE = 35] = "KeyE", e[e.KeyF = 36] = "KeyF", e[e.KeyG = 37] = "KeyG", e[e.KeyH = 38] = "KeyH", e[e.KeyI = 39] = "KeyI", e[e.KeyJ = 40] = "KeyJ", e[e.KeyK = 41] = "KeyK", e[e.KeyL = 42] = "KeyL", e[e.KeyM = 43] = "KeyM", e[e.KeyN = 44] = "KeyN", e[e.KeyO = 45] = "KeyO", e[e.KeyP = 46] = "KeyP", e[e.KeyQ = 47] = "KeyQ", e[e.KeyR = 48] = "KeyR", e[e.KeyS = 49] = "KeyS", e[e.KeyT = 50] = "KeyT", e[e.KeyU = 51] = "KeyU", e[e.KeyV = 52] = "KeyV", e[e.KeyW = 53] = "KeyW", e[e.KeyX = 54] = "KeyX", e[e.KeyY = 55] = "KeyY", e[e.KeyZ = 56] = "KeyZ", e[e.Meta = 57] = "Meta", e[e.ContextMenu = 58] = "ContextMenu", e[e.F1 = 59] = "F1", e[e.F2 = 60] = "F2", e[e.F3 = 61] = "F3", e[e.F4 = 62] = "F4", e[e.F5 = 63] = "F5", e[e.F6 = 64] = "F6", e[e.F7 = 65] = "F7", e[e.F8 = 66] = "F8", e[e.F9 = 67] = "F9", e[e.F10 = 68] = "F10", e[e.F11 = 69] = "F11", e[e.F12 = 70] = "F12", e[e.F13 = 71] = "F13", e[e.F14 = 72] = "F14", e[e.F15 = 73] = "F15", e[e.F16 = 74] = "F16", e[e.F17 = 75] = "F17", e[e.F18 = 76] = "F18", e[e.F19 = 77] = "F19", e[e.F20 = 78] = "F20", e[e.F21 = 79] = "F21", e[e.F22 = 80] = "F22", e[e.F23 = 81] = "F23", e[e.F24 = 82] = "F24", e[e.NumLock = 83] = "NumLock", e[e.ScrollLock = 84] = "ScrollLock", e[e.Semicolon = 85] = "Semicolon", e[e.Equal = 86] = "Equal", e[e.Comma = 87] = "Comma", e[e.Minus = 88] = "Minus", e[e.Period = 89] = "Period", e[e.Slash = 90] = "Slash", e[e.Backquote = 91] = "Backquote", e[e.BracketLeft = 92] = "BracketLeft", e[e.Backslash = 93] = "Backslash", e[e.BracketRight = 94] = "BracketRight", e[e.Quote = 95] = "Quote", e[e.OEM_8 = 96] = "OEM_8", e[e.IntlBackslash = 97] = "IntlBackslash", e[e.Numpad0 = 98] = "Numpad0", e[e.Numpad1 = 99] = "Numpad1", e[e.Numpad2 = 100] = "Numpad2", e[e.Numpad3 = 101] = "Numpad3", e[e.Numpad4 = 102] = "Numpad4", e[e.Numpad5 = 103] = "Numpad5", e[e.Numpad6 = 104] = "Numpad6", e[e.Numpad7 = 105] = "Numpad7", e[e.Numpad8 = 106] = "Numpad8", e[e.Numpad9 = 107] = "Numpad9", e[e.NumpadMultiply = 108] = "NumpadMultiply", e[e.NumpadAdd = 109] = "NumpadAdd", e[e.NUMPAD_SEPARATOR = 110] = "NUMPAD_SEPARATOR", e[e.NumpadSubtract = 111] = "NumpadSubtract", e[e.NumpadDecimal = 112] = "NumpadDecimal", e[e.NumpadDivide = 113] = "NumpadDivide", e[e.KEY_IN_COMPOSITION = 114] = "KEY_IN_COMPOSITION", e[e.ABNT_C1 = 115] = "ABNT_C1", e[e.ABNT_C2 = 116] = "ABNT_C2", e[e.AudioVolumeMute = 117] = "AudioVolumeMute", e[e.AudioVolumeUp = 118] = "AudioVolumeUp", e[e.AudioVolumeDown = 119] = "AudioVolumeDown", e[e.BrowserSearch = 120] = "BrowserSearch", e[e.BrowserHome = 121] = "BrowserHome", e[e.BrowserBack = 122] = "BrowserBack", e[e.BrowserForward = 123] = "BrowserForward", e[e.MediaTrackNext = 124] = "MediaTrackNext", e[e.MediaTrackPrevious = 125] = "MediaTrackPrevious", e[e.MediaStop = 126] = "MediaStop", e[e.MediaPlayPause = 127] = "MediaPlayPause", e[e.LaunchMediaPlayer = 128] = "LaunchMediaPlayer", e[e.LaunchMail = 129] = "LaunchMail", e[e.LaunchApp2 = 130] = "LaunchApp2", e[e.Clear = 131] = "Clear", e[e.MAX_VALUE = 132] = "MAX_VALUE";
})(m || (m = {}));
var g;
(function(e) {
  e[e.DependsOnKbLayout = -1] = "DependsOnKbLayout", e[e.None = 0] = "None", e[e.Hyper = 1] = "Hyper", e[e.Super = 2] = "Super", e[e.Fn = 3] = "Fn", e[e.FnLock = 4] = "FnLock", e[e.Suspend = 5] = "Suspend", e[e.Resume = 6] = "Resume", e[e.Turbo = 7] = "Turbo", e[e.Sleep = 8] = "Sleep", e[e.WakeUp = 9] = "WakeUp", e[e.KeyA = 10] = "KeyA", e[e.KeyB = 11] = "KeyB", e[e.KeyC = 12] = "KeyC", e[e.KeyD = 13] = "KeyD", e[e.KeyE = 14] = "KeyE", e[e.KeyF = 15] = "KeyF", e[e.KeyG = 16] = "KeyG", e[e.KeyH = 17] = "KeyH", e[e.KeyI = 18] = "KeyI", e[e.KeyJ = 19] = "KeyJ", e[e.KeyK = 20] = "KeyK", e[e.KeyL = 21] = "KeyL", e[e.KeyM = 22] = "KeyM", e[e.KeyN = 23] = "KeyN", e[e.KeyO = 24] = "KeyO", e[e.KeyP = 25] = "KeyP", e[e.KeyQ = 26] = "KeyQ", e[e.KeyR = 27] = "KeyR", e[e.KeyS = 28] = "KeyS", e[e.KeyT = 29] = "KeyT", e[e.KeyU = 30] = "KeyU", e[e.KeyV = 31] = "KeyV", e[e.KeyW = 32] = "KeyW", e[e.KeyX = 33] = "KeyX", e[e.KeyY = 34] = "KeyY", e[e.KeyZ = 35] = "KeyZ", e[e.Digit1 = 36] = "Digit1", e[e.Digit2 = 37] = "Digit2", e[e.Digit3 = 38] = "Digit3", e[e.Digit4 = 39] = "Digit4", e[e.Digit5 = 40] = "Digit5", e[e.Digit6 = 41] = "Digit6", e[e.Digit7 = 42] = "Digit7", e[e.Digit8 = 43] = "Digit8", e[e.Digit9 = 44] = "Digit9", e[e.Digit0 = 45] = "Digit0", e[e.Enter = 46] = "Enter", e[e.Escape = 47] = "Escape", e[e.Backspace = 48] = "Backspace", e[e.Tab = 49] = "Tab", e[e.Space = 50] = "Space", e[e.Minus = 51] = "Minus", e[e.Equal = 52] = "Equal", e[e.BracketLeft = 53] = "BracketLeft", e[e.BracketRight = 54] = "BracketRight", e[e.Backslash = 55] = "Backslash", e[e.IntlHash = 56] = "IntlHash", e[e.Semicolon = 57] = "Semicolon", e[e.Quote = 58] = "Quote", e[e.Backquote = 59] = "Backquote", e[e.Comma = 60] = "Comma", e[e.Period = 61] = "Period", e[e.Slash = 62] = "Slash", e[e.CapsLock = 63] = "CapsLock", e[e.F1 = 64] = "F1", e[e.F2 = 65] = "F2", e[e.F3 = 66] = "F3", e[e.F4 = 67] = "F4", e[e.F5 = 68] = "F5", e[e.F6 = 69] = "F6", e[e.F7 = 70] = "F7", e[e.F8 = 71] = "F8", e[e.F9 = 72] = "F9", e[e.F10 = 73] = "F10", e[e.F11 = 74] = "F11", e[e.F12 = 75] = "F12", e[e.PrintScreen = 76] = "PrintScreen", e[e.ScrollLock = 77] = "ScrollLock", e[e.Pause = 78] = "Pause", e[e.Insert = 79] = "Insert", e[e.Home = 80] = "Home", e[e.PageUp = 81] = "PageUp", e[e.Delete = 82] = "Delete", e[e.End = 83] = "End", e[e.PageDown = 84] = "PageDown", e[e.ArrowRight = 85] = "ArrowRight", e[e.ArrowLeft = 86] = "ArrowLeft", e[e.ArrowDown = 87] = "ArrowDown", e[e.ArrowUp = 88] = "ArrowUp", e[e.NumLock = 89] = "NumLock", e[e.NumpadDivide = 90] = "NumpadDivide", e[e.NumpadMultiply = 91] = "NumpadMultiply", e[e.NumpadSubtract = 92] = "NumpadSubtract", e[e.NumpadAdd = 93] = "NumpadAdd", e[e.NumpadEnter = 94] = "NumpadEnter", e[e.Numpad1 = 95] = "Numpad1", e[e.Numpad2 = 96] = "Numpad2", e[e.Numpad3 = 97] = "Numpad3", e[e.Numpad4 = 98] = "Numpad4", e[e.Numpad5 = 99] = "Numpad5", e[e.Numpad6 = 100] = "Numpad6", e[e.Numpad7 = 101] = "Numpad7", e[e.Numpad8 = 102] = "Numpad8", e[e.Numpad9 = 103] = "Numpad9", e[e.Numpad0 = 104] = "Numpad0", e[e.NumpadDecimal = 105] = "NumpadDecimal", e[e.IntlBackslash = 106] = "IntlBackslash", e[e.ContextMenu = 107] = "ContextMenu", e[e.Power = 108] = "Power", e[e.NumpadEqual = 109] = "NumpadEqual", e[e.F13 = 110] = "F13", e[e.F14 = 111] = "F14", e[e.F15 = 112] = "F15", e[e.F16 = 113] = "F16", e[e.F17 = 114] = "F17", e[e.F18 = 115] = "F18", e[e.F19 = 116] = "F19", e[e.F20 = 117] = "F20", e[e.F21 = 118] = "F21", e[e.F22 = 119] = "F22", e[e.F23 = 120] = "F23", e[e.F24 = 121] = "F24", e[e.Open = 122] = "Open", e[e.Help = 123] = "Help", e[e.Select = 124] = "Select", e[e.Again = 125] = "Again", e[e.Undo = 126] = "Undo", e[e.Cut = 127] = "Cut", e[e.Copy = 128] = "Copy", e[e.Paste = 129] = "Paste", e[e.Find = 130] = "Find", e[e.AudioVolumeMute = 131] = "AudioVolumeMute", e[e.AudioVolumeUp = 132] = "AudioVolumeUp", e[e.AudioVolumeDown = 133] = "AudioVolumeDown", e[e.NumpadComma = 134] = "NumpadComma", e[e.IntlRo = 135] = "IntlRo", e[e.KanaMode = 136] = "KanaMode", e[e.IntlYen = 137] = "IntlYen", e[e.Convert = 138] = "Convert", e[e.NonConvert = 139] = "NonConvert", e[e.Lang1 = 140] = "Lang1", e[e.Lang2 = 141] = "Lang2", e[e.Lang3 = 142] = "Lang3", e[e.Lang4 = 143] = "Lang4", e[e.Lang5 = 144] = "Lang5", e[e.Abort = 145] = "Abort", e[e.Props = 146] = "Props", e[e.NumpadParenLeft = 147] = "NumpadParenLeft", e[e.NumpadParenRight = 148] = "NumpadParenRight", e[e.NumpadBackspace = 149] = "NumpadBackspace", e[e.NumpadMemoryStore = 150] = "NumpadMemoryStore", e[e.NumpadMemoryRecall = 151] = "NumpadMemoryRecall", e[e.NumpadMemoryClear = 152] = "NumpadMemoryClear", e[e.NumpadMemoryAdd = 153] = "NumpadMemoryAdd", e[e.NumpadMemorySubtract = 154] = "NumpadMemorySubtract", e[e.NumpadClear = 155] = "NumpadClear", e[e.NumpadClearEntry = 156] = "NumpadClearEntry", e[e.ControlLeft = 157] = "ControlLeft", e[e.ShiftLeft = 158] = "ShiftLeft", e[e.AltLeft = 159] = "AltLeft", e[e.MetaLeft = 160] = "MetaLeft", e[e.ControlRight = 161] = "ControlRight", e[e.ShiftRight = 162] = "ShiftRight", e[e.AltRight = 163] = "AltRight", e[e.MetaRight = 164] = "MetaRight", e[e.BrightnessUp = 165] = "BrightnessUp", e[e.BrightnessDown = 166] = "BrightnessDown", e[e.MediaPlay = 167] = "MediaPlay", e[e.MediaRecord = 168] = "MediaRecord", e[e.MediaFastForward = 169] = "MediaFastForward", e[e.MediaRewind = 170] = "MediaRewind", e[e.MediaTrackNext = 171] = "MediaTrackNext", e[e.MediaTrackPrevious = 172] = "MediaTrackPrevious", e[e.MediaStop = 173] = "MediaStop", e[e.Eject = 174] = "Eject", e[e.MediaPlayPause = 175] = "MediaPlayPause", e[e.MediaSelect = 176] = "MediaSelect", e[e.LaunchMail = 177] = "LaunchMail", e[e.LaunchApp2 = 178] = "LaunchApp2", e[e.LaunchApp1 = 179] = "LaunchApp1", e[e.SelectTask = 180] = "SelectTask", e[e.LaunchScreenSaver = 181] = "LaunchScreenSaver", e[e.BrowserSearch = 182] = "BrowserSearch", e[e.BrowserHome = 183] = "BrowserHome", e[e.BrowserBack = 184] = "BrowserBack", e[e.BrowserForward = 185] = "BrowserForward", e[e.BrowserStop = 186] = "BrowserStop", e[e.BrowserRefresh = 187] = "BrowserRefresh", e[e.BrowserFavorites = 188] = "BrowserFavorites", e[e.ZoomToggle = 189] = "ZoomToggle", e[e.MailReply = 190] = "MailReply", e[e.MailForward = 191] = "MailForward", e[e.MailSend = 192] = "MailSend", e[e.MAX_VALUE = 193] = "MAX_VALUE";
})(g || (g = {}));
class _i {
  constructor() {
    this._keyCodeToStr = [], this._strToKeyCode = /* @__PURE__ */ Object.create(null);
  }
  define(t, n) {
    this._keyCodeToStr[t] = n, this._strToKeyCode[n.toLowerCase()] = t;
  }
  keyCodeToStr(t) {
    return this._keyCodeToStr[t];
  }
  strToKeyCode(t) {
    return this._strToKeyCode[t.toLowerCase()] || m.Unknown;
  }
}
const ln = new _i(), Xn = new _i(), Yn = new _i(), Xa = new Array(230), Ya = /* @__PURE__ */ Object.create(null), Qa = /* @__PURE__ */ Object.create(null), Qn = [];
for (let e = 0; e <= g.MAX_VALUE; e++)
  m.DependsOnKbLayout;
for (let e = 0; e <= m.MAX_VALUE; e++)
  Qn[e] = g.DependsOnKbLayout;
(function() {
  const e = "", t = [
    [1, g.None, "None", m.Unknown, "unknown", 0, "VK_UNKNOWN", e, e],
    [1, g.Hyper, "Hyper", m.Unknown, e, 0, e, e, e],
    [1, g.Super, "Super", m.Unknown, e, 0, e, e, e],
    [1, g.Fn, "Fn", m.Unknown, e, 0, e, e, e],
    [1, g.FnLock, "FnLock", m.Unknown, e, 0, e, e, e],
    [1, g.Suspend, "Suspend", m.Unknown, e, 0, e, e, e],
    [1, g.Resume, "Resume", m.Unknown, e, 0, e, e, e],
    [1, g.Turbo, "Turbo", m.Unknown, e, 0, e, e, e],
    [1, g.Sleep, "Sleep", m.Unknown, e, 0, "VK_SLEEP", e, e],
    [1, g.WakeUp, "WakeUp", m.Unknown, e, 0, e, e, e],
    [0, g.KeyA, "KeyA", m.KeyA, "A", 65, "VK_A", e, e],
    [0, g.KeyB, "KeyB", m.KeyB, "B", 66, "VK_B", e, e],
    [0, g.KeyC, "KeyC", m.KeyC, "C", 67, "VK_C", e, e],
    [0, g.KeyD, "KeyD", m.KeyD, "D", 68, "VK_D", e, e],
    [0, g.KeyE, "KeyE", m.KeyE, "E", 69, "VK_E", e, e],
    [0, g.KeyF, "KeyF", m.KeyF, "F", 70, "VK_F", e, e],
    [0, g.KeyG, "KeyG", m.KeyG, "G", 71, "VK_G", e, e],
    [0, g.KeyH, "KeyH", m.KeyH, "H", 72, "VK_H", e, e],
    [0, g.KeyI, "KeyI", m.KeyI, "I", 73, "VK_I", e, e],
    [0, g.KeyJ, "KeyJ", m.KeyJ, "J", 74, "VK_J", e, e],
    [0, g.KeyK, "KeyK", m.KeyK, "K", 75, "VK_K", e, e],
    [0, g.KeyL, "KeyL", m.KeyL, "L", 76, "VK_L", e, e],
    [0, g.KeyM, "KeyM", m.KeyM, "M", 77, "VK_M", e, e],
    [0, g.KeyN, "KeyN", m.KeyN, "N", 78, "VK_N", e, e],
    [0, g.KeyO, "KeyO", m.KeyO, "O", 79, "VK_O", e, e],
    [0, g.KeyP, "KeyP", m.KeyP, "P", 80, "VK_P", e, e],
    [0, g.KeyQ, "KeyQ", m.KeyQ, "Q", 81, "VK_Q", e, e],
    [0, g.KeyR, "KeyR", m.KeyR, "R", 82, "VK_R", e, e],
    [0, g.KeyS, "KeyS", m.KeyS, "S", 83, "VK_S", e, e],
    [0, g.KeyT, "KeyT", m.KeyT, "T", 84, "VK_T", e, e],
    [0, g.KeyU, "KeyU", m.KeyU, "U", 85, "VK_U", e, e],
    [0, g.KeyV, "KeyV", m.KeyV, "V", 86, "VK_V", e, e],
    [0, g.KeyW, "KeyW", m.KeyW, "W", 87, "VK_W", e, e],
    [0, g.KeyX, "KeyX", m.KeyX, "X", 88, "VK_X", e, e],
    [0, g.KeyY, "KeyY", m.KeyY, "Y", 89, "VK_Y", e, e],
    [0, g.KeyZ, "KeyZ", m.KeyZ, "Z", 90, "VK_Z", e, e],
    [0, g.Digit1, "Digit1", m.Digit1, "1", 49, "VK_1", e, e],
    [0, g.Digit2, "Digit2", m.Digit2, "2", 50, "VK_2", e, e],
    [0, g.Digit3, "Digit3", m.Digit3, "3", 51, "VK_3", e, e],
    [0, g.Digit4, "Digit4", m.Digit4, "4", 52, "VK_4", e, e],
    [0, g.Digit5, "Digit5", m.Digit5, "5", 53, "VK_5", e, e],
    [0, g.Digit6, "Digit6", m.Digit6, "6", 54, "VK_6", e, e],
    [0, g.Digit7, "Digit7", m.Digit7, "7", 55, "VK_7", e, e],
    [0, g.Digit8, "Digit8", m.Digit8, "8", 56, "VK_8", e, e],
    [0, g.Digit9, "Digit9", m.Digit9, "9", 57, "VK_9", e, e],
    [0, g.Digit0, "Digit0", m.Digit0, "0", 48, "VK_0", e, e],
    [1, g.Enter, "Enter", m.Enter, "Enter", 13, "VK_RETURN", e, e],
    [1, g.Escape, "Escape", m.Escape, "Escape", 27, "VK_ESCAPE", e, e],
    [1, g.Backspace, "Backspace", m.Backspace, "Backspace", 8, "VK_BACK", e, e],
    [1, g.Tab, "Tab", m.Tab, "Tab", 9, "VK_TAB", e, e],
    [1, g.Space, "Space", m.Space, "Space", 32, "VK_SPACE", e, e],
    [0, g.Minus, "Minus", m.Minus, "-", 189, "VK_OEM_MINUS", "-", "OEM_MINUS"],
    [0, g.Equal, "Equal", m.Equal, "=", 187, "VK_OEM_PLUS", "=", "OEM_PLUS"],
    [0, g.BracketLeft, "BracketLeft", m.BracketLeft, "[", 219, "VK_OEM_4", "[", "OEM_4"],
    [0, g.BracketRight, "BracketRight", m.BracketRight, "]", 221, "VK_OEM_6", "]", "OEM_6"],
    [0, g.Backslash, "Backslash", m.Backslash, "\\", 220, "VK_OEM_5", "\\", "OEM_5"],
    [0, g.IntlHash, "IntlHash", m.Unknown, e, 0, e, e, e],
    [0, g.Semicolon, "Semicolon", m.Semicolon, ";", 186, "VK_OEM_1", ";", "OEM_1"],
    [0, g.Quote, "Quote", m.Quote, "'", 222, "VK_OEM_7", "'", "OEM_7"],
    [0, g.Backquote, "Backquote", m.Backquote, "`", 192, "VK_OEM_3", "`", "OEM_3"],
    [0, g.Comma, "Comma", m.Comma, ",", 188, "VK_OEM_COMMA", ",", "OEM_COMMA"],
    [0, g.Period, "Period", m.Period, ".", 190, "VK_OEM_PERIOD", ".", "OEM_PERIOD"],
    [0, g.Slash, "Slash", m.Slash, "/", 191, "VK_OEM_2", "/", "OEM_2"],
    [1, g.CapsLock, "CapsLock", m.CapsLock, "CapsLock", 20, "VK_CAPITAL", e, e],
    [1, g.F1, "F1", m.F1, "F1", 112, "VK_F1", e, e],
    [1, g.F2, "F2", m.F2, "F2", 113, "VK_F2", e, e],
    [1, g.F3, "F3", m.F3, "F3", 114, "VK_F3", e, e],
    [1, g.F4, "F4", m.F4, "F4", 115, "VK_F4", e, e],
    [1, g.F5, "F5", m.F5, "F5", 116, "VK_F5", e, e],
    [1, g.F6, "F6", m.F6, "F6", 117, "VK_F6", e, e],
    [1, g.F7, "F7", m.F7, "F7", 118, "VK_F7", e, e],
    [1, g.F8, "F8", m.F8, "F8", 119, "VK_F8", e, e],
    [1, g.F9, "F9", m.F9, "F9", 120, "VK_F9", e, e],
    [1, g.F10, "F10", m.F10, "F10", 121, "VK_F10", e, e],
    [1, g.F11, "F11", m.F11, "F11", 122, "VK_F11", e, e],
    [1, g.F12, "F12", m.F12, "F12", 123, "VK_F12", e, e],
    [1, g.PrintScreen, "PrintScreen", m.Unknown, e, 0, e, e, e],
    [1, g.ScrollLock, "ScrollLock", m.ScrollLock, "ScrollLock", 145, "VK_SCROLL", e, e],
    [1, g.Pause, "Pause", m.PauseBreak, "PauseBreak", 19, "VK_PAUSE", e, e],
    [1, g.Insert, "Insert", m.Insert, "Insert", 45, "VK_INSERT", e, e],
    [1, g.Home, "Home", m.Home, "Home", 36, "VK_HOME", e, e],
    [1, g.PageUp, "PageUp", m.PageUp, "PageUp", 33, "VK_PRIOR", e, e],
    [1, g.Delete, "Delete", m.Delete, "Delete", 46, "VK_DELETE", e, e],
    [1, g.End, "End", m.End, "End", 35, "VK_END", e, e],
    [1, g.PageDown, "PageDown", m.PageDown, "PageDown", 34, "VK_NEXT", e, e],
    [1, g.ArrowRight, "ArrowRight", m.RightArrow, "RightArrow", 39, "VK_RIGHT", "Right", e],
    [1, g.ArrowLeft, "ArrowLeft", m.LeftArrow, "LeftArrow", 37, "VK_LEFT", "Left", e],
    [1, g.ArrowDown, "ArrowDown", m.DownArrow, "DownArrow", 40, "VK_DOWN", "Down", e],
    [1, g.ArrowUp, "ArrowUp", m.UpArrow, "UpArrow", 38, "VK_UP", "Up", e],
    [1, g.NumLock, "NumLock", m.NumLock, "NumLock", 144, "VK_NUMLOCK", e, e],
    [1, g.NumpadDivide, "NumpadDivide", m.NumpadDivide, "NumPad_Divide", 111, "VK_DIVIDE", e, e],
    [1, g.NumpadMultiply, "NumpadMultiply", m.NumpadMultiply, "NumPad_Multiply", 106, "VK_MULTIPLY", e, e],
    [1, g.NumpadSubtract, "NumpadSubtract", m.NumpadSubtract, "NumPad_Subtract", 109, "VK_SUBTRACT", e, e],
    [1, g.NumpadAdd, "NumpadAdd", m.NumpadAdd, "NumPad_Add", 107, "VK_ADD", e, e],
    [1, g.NumpadEnter, "NumpadEnter", m.Enter, e, 0, e, e, e],
    [1, g.Numpad1, "Numpad1", m.Numpad1, "NumPad1", 97, "VK_NUMPAD1", e, e],
    [1, g.Numpad2, "Numpad2", m.Numpad2, "NumPad2", 98, "VK_NUMPAD2", e, e],
    [1, g.Numpad3, "Numpad3", m.Numpad3, "NumPad3", 99, "VK_NUMPAD3", e, e],
    [1, g.Numpad4, "Numpad4", m.Numpad4, "NumPad4", 100, "VK_NUMPAD4", e, e],
    [1, g.Numpad5, "Numpad5", m.Numpad5, "NumPad5", 101, "VK_NUMPAD5", e, e],
    [1, g.Numpad6, "Numpad6", m.Numpad6, "NumPad6", 102, "VK_NUMPAD6", e, e],
    [1, g.Numpad7, "Numpad7", m.Numpad7, "NumPad7", 103, "VK_NUMPAD7", e, e],
    [1, g.Numpad8, "Numpad8", m.Numpad8, "NumPad8", 104, "VK_NUMPAD8", e, e],
    [1, g.Numpad9, "Numpad9", m.Numpad9, "NumPad9", 105, "VK_NUMPAD9", e, e],
    [1, g.Numpad0, "Numpad0", m.Numpad0, "NumPad0", 96, "VK_NUMPAD0", e, e],
    [1, g.NumpadDecimal, "NumpadDecimal", m.NumpadDecimal, "NumPad_Decimal", 110, "VK_DECIMAL", e, e],
    [0, g.IntlBackslash, "IntlBackslash", m.IntlBackslash, "OEM_102", 226, "VK_OEM_102", e, e],
    [1, g.ContextMenu, "ContextMenu", m.ContextMenu, "ContextMenu", 93, e, e, e],
    [1, g.Power, "Power", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadEqual, "NumpadEqual", m.Unknown, e, 0, e, e, e],
    [1, g.F13, "F13", m.F13, "F13", 124, "VK_F13", e, e],
    [1, g.F14, "F14", m.F14, "F14", 125, "VK_F14", e, e],
    [1, g.F15, "F15", m.F15, "F15", 126, "VK_F15", e, e],
    [1, g.F16, "F16", m.F16, "F16", 127, "VK_F16", e, e],
    [1, g.F17, "F17", m.F17, "F17", 128, "VK_F17", e, e],
    [1, g.F18, "F18", m.F18, "F18", 129, "VK_F18", e, e],
    [1, g.F19, "F19", m.F19, "F19", 130, "VK_F19", e, e],
    [1, g.F20, "F20", m.F20, "F20", 131, "VK_F20", e, e],
    [1, g.F21, "F21", m.F21, "F21", 132, "VK_F21", e, e],
    [1, g.F22, "F22", m.F22, "F22", 133, "VK_F22", e, e],
    [1, g.F23, "F23", m.F23, "F23", 134, "VK_F23", e, e],
    [1, g.F24, "F24", m.F24, "F24", 135, "VK_F24", e, e],
    [1, g.Open, "Open", m.Unknown, e, 0, e, e, e],
    [1, g.Help, "Help", m.Unknown, e, 0, e, e, e],
    [1, g.Select, "Select", m.Unknown, e, 0, e, e, e],
    [1, g.Again, "Again", m.Unknown, e, 0, e, e, e],
    [1, g.Undo, "Undo", m.Unknown, e, 0, e, e, e],
    [1, g.Cut, "Cut", m.Unknown, e, 0, e, e, e],
    [1, g.Copy, "Copy", m.Unknown, e, 0, e, e, e],
    [1, g.Paste, "Paste", m.Unknown, e, 0, e, e, e],
    [1, g.Find, "Find", m.Unknown, e, 0, e, e, e],
    [1, g.AudioVolumeMute, "AudioVolumeMute", m.AudioVolumeMute, "AudioVolumeMute", 173, "VK_VOLUME_MUTE", e, e],
    [1, g.AudioVolumeUp, "AudioVolumeUp", m.AudioVolumeUp, "AudioVolumeUp", 175, "VK_VOLUME_UP", e, e],
    [1, g.AudioVolumeDown, "AudioVolumeDown", m.AudioVolumeDown, "AudioVolumeDown", 174, "VK_VOLUME_DOWN", e, e],
    [1, g.NumpadComma, "NumpadComma", m.NUMPAD_SEPARATOR, "NumPad_Separator", 108, "VK_SEPARATOR", e, e],
    [0, g.IntlRo, "IntlRo", m.ABNT_C1, "ABNT_C1", 193, "VK_ABNT_C1", e, e],
    [1, g.KanaMode, "KanaMode", m.Unknown, e, 0, e, e, e],
    [0, g.IntlYen, "IntlYen", m.Unknown, e, 0, e, e, e],
    [1, g.Convert, "Convert", m.Unknown, e, 0, e, e, e],
    [1, g.NonConvert, "NonConvert", m.Unknown, e, 0, e, e, e],
    [1, g.Lang1, "Lang1", m.Unknown, e, 0, e, e, e],
    [1, g.Lang2, "Lang2", m.Unknown, e, 0, e, e, e],
    [1, g.Lang3, "Lang3", m.Unknown, e, 0, e, e, e],
    [1, g.Lang4, "Lang4", m.Unknown, e, 0, e, e, e],
    [1, g.Lang5, "Lang5", m.Unknown, e, 0, e, e, e],
    [1, g.Abort, "Abort", m.Unknown, e, 0, e, e, e],
    [1, g.Props, "Props", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadParenLeft, "NumpadParenLeft", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadParenRight, "NumpadParenRight", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadBackspace, "NumpadBackspace", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadMemoryStore, "NumpadMemoryStore", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadMemoryRecall, "NumpadMemoryRecall", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadMemoryClear, "NumpadMemoryClear", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadMemoryAdd, "NumpadMemoryAdd", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadMemorySubtract, "NumpadMemorySubtract", m.Unknown, e, 0, e, e, e],
    [1, g.NumpadClear, "NumpadClear", m.Clear, "Clear", 12, "VK_CLEAR", e, e],
    [1, g.NumpadClearEntry, "NumpadClearEntry", m.Unknown, e, 0, e, e, e],
    [1, g.None, e, m.Ctrl, "Ctrl", 17, "VK_CONTROL", e, e],
    [1, g.None, e, m.Shift, "Shift", 16, "VK_SHIFT", e, e],
    [1, g.None, e, m.Alt, "Alt", 18, "VK_MENU", e, e],
    [1, g.None, e, m.Meta, "Meta", 91, "VK_COMMAND", e, e],
    [1, g.ControlLeft, "ControlLeft", m.Ctrl, e, 0, "VK_LCONTROL", e, e],
    [1, g.ShiftLeft, "ShiftLeft", m.Shift, e, 0, "VK_LSHIFT", e, e],
    [1, g.AltLeft, "AltLeft", m.Alt, e, 0, "VK_LMENU", e, e],
    [1, g.MetaLeft, "MetaLeft", m.Meta, e, 0, "VK_LWIN", e, e],
    [1, g.ControlRight, "ControlRight", m.Ctrl, e, 0, "VK_RCONTROL", e, e],
    [1, g.ShiftRight, "ShiftRight", m.Shift, e, 0, "VK_RSHIFT", e, e],
    [1, g.AltRight, "AltRight", m.Alt, e, 0, "VK_RMENU", e, e],
    [1, g.MetaRight, "MetaRight", m.Meta, e, 0, "VK_RWIN", e, e],
    [1, g.BrightnessUp, "BrightnessUp", m.Unknown, e, 0, e, e, e],
    [1, g.BrightnessDown, "BrightnessDown", m.Unknown, e, 0, e, e, e],
    [1, g.MediaPlay, "MediaPlay", m.Unknown, e, 0, e, e, e],
    [1, g.MediaRecord, "MediaRecord", m.Unknown, e, 0, e, e, e],
    [1, g.MediaFastForward, "MediaFastForward", m.Unknown, e, 0, e, e, e],
    [1, g.MediaRewind, "MediaRewind", m.Unknown, e, 0, e, e, e],
    [1, g.MediaTrackNext, "MediaTrackNext", m.MediaTrackNext, "MediaTrackNext", 176, "VK_MEDIA_NEXT_TRACK", e, e],
    [1, g.MediaTrackPrevious, "MediaTrackPrevious", m.MediaTrackPrevious, "MediaTrackPrevious", 177, "VK_MEDIA_PREV_TRACK", e, e],
    [1, g.MediaStop, "MediaStop", m.MediaStop, "MediaStop", 178, "VK_MEDIA_STOP", e, e],
    [1, g.Eject, "Eject", m.Unknown, e, 0, e, e, e],
    [1, g.MediaPlayPause, "MediaPlayPause", m.MediaPlayPause, "MediaPlayPause", 179, "VK_MEDIA_PLAY_PAUSE", e, e],
    [1, g.MediaSelect, "MediaSelect", m.LaunchMediaPlayer, "LaunchMediaPlayer", 181, "VK_MEDIA_LAUNCH_MEDIA_SELECT", e, e],
    [1, g.LaunchMail, "LaunchMail", m.LaunchMail, "LaunchMail", 180, "VK_MEDIA_LAUNCH_MAIL", e, e],
    [1, g.LaunchApp2, "LaunchApp2", m.LaunchApp2, "LaunchApp2", 183, "VK_MEDIA_LAUNCH_APP2", e, e],
    [1, g.LaunchApp1, "LaunchApp1", m.Unknown, e, 0, "VK_MEDIA_LAUNCH_APP1", e, e],
    [1, g.SelectTask, "SelectTask", m.Unknown, e, 0, e, e, e],
    [1, g.LaunchScreenSaver, "LaunchScreenSaver", m.Unknown, e, 0, e, e, e],
    [1, g.BrowserSearch, "BrowserSearch", m.BrowserSearch, "BrowserSearch", 170, "VK_BROWSER_SEARCH", e, e],
    [1, g.BrowserHome, "BrowserHome", m.BrowserHome, "BrowserHome", 172, "VK_BROWSER_HOME", e, e],
    [1, g.BrowserBack, "BrowserBack", m.BrowserBack, "BrowserBack", 166, "VK_BROWSER_BACK", e, e],
    [1, g.BrowserForward, "BrowserForward", m.BrowserForward, "BrowserForward", 167, "VK_BROWSER_FORWARD", e, e],
    [1, g.BrowserStop, "BrowserStop", m.Unknown, e, 0, "VK_BROWSER_STOP", e, e],
    [1, g.BrowserRefresh, "BrowserRefresh", m.Unknown, e, 0, "VK_BROWSER_REFRESH", e, e],
    [1, g.BrowserFavorites, "BrowserFavorites", m.Unknown, e, 0, "VK_BROWSER_FAVORITES", e, e],
    [1, g.ZoomToggle, "ZoomToggle", m.Unknown, e, 0, e, e, e],
    [1, g.MailReply, "MailReply", m.Unknown, e, 0, e, e, e],
    [1, g.MailForward, "MailForward", m.Unknown, e, 0, e, e, e],
    [1, g.MailSend, "MailSend", m.Unknown, e, 0, e, e, e],
    [1, g.None, e, m.KEY_IN_COMPOSITION, "KeyInComposition", 229, e, e, e],
    [1, g.None, e, m.ABNT_C2, "ABNT_C2", 194, "VK_ABNT_C2", e, e],
    [1, g.None, e, m.OEM_8, "OEM_8", 223, "VK_OEM_8", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_KANA", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_HANGUL", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_JUNJA", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_FINAL", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_HANJA", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_KANJI", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_CONVERT", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_NONCONVERT", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_ACCEPT", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_MODECHANGE", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_SELECT", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_PRINT", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_EXECUTE", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_SNAPSHOT", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_HELP", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_APPS", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_PROCESSKEY", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_PACKET", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_DBE_SBCSCHAR", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_DBE_DBCSCHAR", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_ATTN", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_CRSEL", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_EXSEL", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_EREOF", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_PLAY", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_ZOOM", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_NONAME", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_PA1", e, e],
    [1, g.None, e, m.Unknown, e, 0, "VK_OEM_CLEAR", e, e]
  ], n = [], i = [];
  for (const r of t) {
    const [s, a, u, o, c, h, f, _, p] = r;
    if (i[a] || (i[a] = !0, Ya[u] = a, Qa[u.toLowerCase()] = a, s && o !== m.Unknown && o !== m.Enter && o !== m.Ctrl && o !== m.Shift && o !== m.Alt && o !== m.Meta && (Qn[o] = a)), !n[o]) {
      if (n[o] = !0, !c)
        throw new Error(
          `String representation missing for key code ${o} around scan code ${u}`
        );
      ln.define(o, c), Xn.define(o, _ || c), Yn.define(o, p || _ || c);
    }
    h && (Xa[h] = o);
  }
  Qn[m.Enter] = g.Enter;
})();
var Vi;
(function(e) {
  function t(u) {
    return ln.keyCodeToStr(u);
  }
  e.toString = t;
  function n(u) {
    return ln.strToKeyCode(u);
  }
  e.fromString = n;
  function i(u) {
    return Xn.keyCodeToStr(u);
  }
  e.toUserSettingsUS = i;
  function r(u) {
    return Yn.keyCodeToStr(u);
  }
  e.toUserSettingsGeneral = r;
  function s(u) {
    return Xn.strToKeyCode(u) || Yn.strToKeyCode(u);
  }
  e.fromUserSettings = s;
  function a(u) {
    if (u >= m.Numpad0 && u <= m.NumpadDivide)
      return null;
    switch (u) {
      case m.UpArrow:
        return "Up";
      case m.DownArrow:
        return "Down";
      case m.LeftArrow:
        return "Left";
      case m.RightArrow:
        return "Right";
    }
    return ln.keyCodeToStr(u);
  }
  e.toElectronAccelerator = a;
})(Vi || (Vi = {}));
var gt;
(function(e) {
  e[e.CtrlCmd = 2048] = "CtrlCmd", e[e.Shift = 1024] = "Shift", e[e.Alt = 512] = "Alt", e[e.WinCtrl = 256] = "WinCtrl";
})(gt || (gt = {}));
function Za(e, t) {
  const n = (t & 65535) << 16 >>> 0;
  return (e | n) >>> 0;
}
var Zn;
(function(e) {
  e[e.Uri = 1] = "Uri", e[e.Regexp = 2] = "Regexp", e[e.ScmResource = 3] = "ScmResource", e[e.ScmResourceGroup = 4] = "ScmResourceGroup", e[e.ScmProvider = 5] = "ScmProvider", e[e.CommentController = 6] = "CommentController", e[e.CommentThread = 7] = "CommentThread", e[e.CommentThreadInstance = 8] = "CommentThreadInstance", e[e.CommentThreadReply = 9] = "CommentThreadReply", e[e.CommentNode = 10] = "CommentNode", e[e.CommentThreadNode = 11] = "CommentThreadNode", e[e.TimelineActionContext = 12] = "TimelineActionContext", e[e.NotebookCellActionContext = 13] = "NotebookCellActionContext", e[e.NotebookActionContext = 14] = "NotebookActionContext", e[e.TerminalContext = 15] = "TerminalContext", e[e.TestItemContext = 16] = "TestItemContext", e[e.Date = 17] = "Date", e[e.TestMessageMenuArgs = 18] = "TestMessageMenuArgs", e[e.ChatViewContext = 19] = "ChatViewContext", e[e.LanguageModelToolResult = 20] = "LanguageModelToolResult", e[e.LanguageModelTextPart = 21] = "LanguageModelTextPart", e[e.LanguageModelPromptTsxPart = 22] = "LanguageModelPromptTsxPart";
})(Zn || (Zn = {}));
let st;
const Pn = globalThis.vscode;
var Qr;
if (typeof Pn < "u" && typeof Pn.process < "u") {
  const e = Pn.process;
  st = {
    get platform() {
      return e.platform;
    },
    get arch() {
      return e.arch;
    },
    get env() {
      return e.env;
    },
    cwd() {
      return e.cwd();
    }
  };
} else typeof process < "u" && typeof ((Qr = process == null ? void 0 : process.versions) == null ? void 0 : Qr.node) == "string" ? st = {
  get platform() {
    return process.platform;
  },
  get arch() {
    return process.arch;
  },
  get env() {
    return process.env;
  },
  cwd() {
    return process.env.VSCODE_CWD || process.cwd();
  }
} : st = {
  get platform() {
    return Tt ? "win32" : ha ? "darwin" : "linux";
  },
  get arch() {
  },
  get env() {
    return {};
  },
  cwd() {
    return "/";
  }
};
const bn = st.cwd, Ja = st.env, Ka = st.platform;
st.arch;
const Ca = 65, el = 97, tl = 90, nl = 122, Qe = 46, ue = 47, we = 92, Ge = 58, il = 63;
class os extends Error {
  constructor(t, n, i) {
    let r;
    typeof n == "string" && n.indexOf("not ") === 0 ? (r = "must not be", n = n.replace(/^not /, "")) : r = "must be";
    const s = t.indexOf(".") !== -1 ? "property" : "argument";
    let a = `The "${t}" ${s} ${r} of type ${n}`;
    a += `. Received type ${typeof i}`, super(a), this.code = "ERR_INVALID_ARG_TYPE";
  }
}
function rl(e, t) {
  if (e === null || typeof e != "object")
    throw new os(t, "Object", e);
}
function se(e, t) {
  if (typeof e != "string")
    throw new os(t, "string", e);
}
const Fe = Ka === "win32";
function G(e) {
  return e === ue || e === we;
}
function Jn(e) {
  return e === ue;
}
function $e(e) {
  return e >= Ca && e <= tl || e >= el && e <= nl;
}
function dn(e, t, n, i) {
  let r = "", s = 0, a = -1, u = 0, o = 0;
  for (let c = 0; c <= e.length; ++c) {
    if (c < e.length)
      o = e.charCodeAt(c);
    else {
      if (i(o))
        break;
      o = ue;
    }
    if (i(o)) {
      if (!(a === c - 1 || u === 1)) if (u === 2) {
        if (r.length < 2 || s !== 2 || r.charCodeAt(r.length - 1) !== Qe || r.charCodeAt(r.length - 2) !== Qe) {
          if (r.length > 2) {
            const h = r.lastIndexOf(n);
            h === -1 ? (r = "", s = 0) : (r = r.slice(0, h), s = r.length - 1 - r.lastIndexOf(n)), a = c, u = 0;
            continue;
          } else if (r.length !== 0) {
            r = "", s = 0, a = c, u = 0;
            continue;
          }
        }
        t && (r += r.length > 0 ? `${n}..` : "..", s = 2);
      } else
        r.length > 0 ? r += `${n}${e.slice(a + 1, c)}` : r = e.slice(a + 1, c), s = c - a - 1;
      a = c, u = 0;
    } else o === Qe && u !== -1 ? ++u : u = -1;
  }
  return r;
}
function sl(e) {
  return e ? `${e[0] === "." ? "" : "."}${e}` : "";
}
function cs(e, t) {
  rl(t, "pathObject");
  const n = t.dir || t.root, i = t.base || `${t.name || ""}${sl(t.ext)}`;
  return n ? n === t.root ? `${n}${i}` : `${n}${e}${i}` : i;
}
const ce = {
  resolve(...e) {
    let t = "", n = "", i = !1;
    for (let r = e.length - 1; r >= -1; r--) {
      let s;
      if (r >= 0) {
        if (s = e[r], se(s, `paths[${r}]`), s.length === 0)
          continue;
      } else t.length === 0 ? s = bn() : (s = Ja[`=${t}`] || bn(), (s === void 0 || s.slice(0, 2).toLowerCase() !== t.toLowerCase() && s.charCodeAt(2) === we) && (s = `${t}\\`));
      const a = s.length;
      let u = 0, o = "", c = !1;
      const h = s.charCodeAt(0);
      if (a === 1)
        G(h) && (u = 1, c = !0);
      else if (G(h))
        if (c = !0, G(s.charCodeAt(1))) {
          let f = 2, _ = f;
          for (; f < a && !G(s.charCodeAt(f)); )
            f++;
          if (f < a && f !== _) {
            const p = s.slice(_, f);
            for (_ = f; f < a && G(s.charCodeAt(f)); )
              f++;
            if (f < a && f !== _) {
              for (_ = f; f < a && !G(s.charCodeAt(f)); )
                f++;
              (f === a || f !== _) && (o = `\\\\${p}\\${s.slice(_, f)}`, u = f);
            }
          }
        } else
          u = 1;
      else $e(h) && s.charCodeAt(1) === Ge && (o = s.slice(0, 2), u = 2, a > 2 && G(s.charCodeAt(2)) && (c = !0, u = 3));
      if (o.length > 0)
        if (t.length > 0) {
          if (o.toLowerCase() !== t.toLowerCase())
            continue;
        } else
          t = o;
      if (i) {
        if (t.length > 0)
          break;
      } else if (n = `${s.slice(u)}\\${n}`, i = c, c && t.length > 0)
        break;
    }
    return n = dn(n, !i, "\\", G), i ? `${t}\\${n}` : `${t}${n}` || ".";
  },
  normalize(e) {
    se(e, "path");
    const t = e.length;
    if (t === 0)
      return ".";
    let n = 0, i, r = !1;
    const s = e.charCodeAt(0);
    if (t === 1)
      return Jn(s) ? "\\" : e;
    if (G(s))
      if (r = !0, G(e.charCodeAt(1))) {
        let u = 2, o = u;
        for (; u < t && !G(e.charCodeAt(u)); )
          u++;
        if (u < t && u !== o) {
          const c = e.slice(o, u);
          for (o = u; u < t && G(e.charCodeAt(u)); )
            u++;
          if (u < t && u !== o) {
            for (o = u; u < t && !G(e.charCodeAt(u)); )
              u++;
            if (u === t)
              return `\\\\${c}\\${e.slice(o)}\\`;
            u !== o && (i = `\\\\${c}\\${e.slice(o, u)}`, n = u);
          }
        }
      } else
        n = 1;
    else $e(s) && e.charCodeAt(1) === Ge && (i = e.slice(0, 2), n = 2, t > 2 && G(e.charCodeAt(2)) && (r = !0, n = 3));
    let a = n < t ? dn(e.slice(n), !r, "\\", G) : "";
    return a.length === 0 && !r && (a = "."), a.length > 0 && G(e.charCodeAt(t - 1)) && (a += "\\"), i === void 0 ? r ? `\\${a}` : a : r ? `${i}\\${a}` : `${i}${a}`;
  },
  isAbsolute(e) {
    se(e, "path");
    const t = e.length;
    if (t === 0)
      return !1;
    const n = e.charCodeAt(0);
    return G(n) || t > 2 && $e(n) && e.charCodeAt(1) === Ge && G(e.charCodeAt(2));
  },
  join(...e) {
    if (e.length === 0)
      return ".";
    let t, n;
    for (let s = 0; s < e.length; ++s) {
      const a = e[s];
      se(a, "path"), a.length > 0 && (t === void 0 ? t = n = a : t += `\\${a}`);
    }
    if (t === void 0)
      return ".";
    let i = !0, r = 0;
    if (typeof n == "string" && G(n.charCodeAt(0))) {
      ++r;
      const s = n.length;
      s > 1 && G(n.charCodeAt(1)) && (++r, s > 2 && (G(n.charCodeAt(2)) ? ++r : i = !1));
    }
    if (i) {
      for (; r < t.length && G(t.charCodeAt(r)); )
        r++;
      r >= 2 && (t = `\\${t.slice(r)}`);
    }
    return ce.normalize(t);
  },
  relative(e, t) {
    if (se(e, "from"), se(t, "to"), e === t)
      return "";
    const n = ce.resolve(e), i = ce.resolve(t);
    if (n === i || (e = n.toLowerCase(), t = i.toLowerCase(), e === t))
      return "";
    let r = 0;
    for (; r < e.length && e.charCodeAt(r) === we; )
      r++;
    let s = e.length;
    for (; s - 1 > r && e.charCodeAt(s - 1) === we; )
      s--;
    const a = s - r;
    let u = 0;
    for (; u < t.length && t.charCodeAt(u) === we; )
      u++;
    let o = t.length;
    for (; o - 1 > u && t.charCodeAt(o - 1) === we; )
      o--;
    const c = o - u, h = a < c ? a : c;
    let f = -1, _ = 0;
    for (; _ < h; _++) {
      const d = e.charCodeAt(r + _);
      if (d !== t.charCodeAt(u + _))
        break;
      d === we && (f = _);
    }
    if (_ !== h) {
      if (f === -1)
        return i;
    } else {
      if (c > h) {
        if (t.charCodeAt(u + _) === we)
          return i.slice(u + _ + 1);
        if (_ === 2)
          return i.slice(u + _);
      }
      a > h && (e.charCodeAt(r + _) === we ? f = _ : _ === 2 && (f = 3)), f === -1 && (f = 0);
    }
    let p = "";
    for (_ = r + f + 1; _ <= s; ++_)
      (_ === s || e.charCodeAt(_) === we) && (p += p.length === 0 ? ".." : "\\..");
    return u += f, p.length > 0 ? `${p}${i.slice(u, o)}` : (i.charCodeAt(u) === we && ++u, i.slice(u, o));
  },
  toNamespacedPath(e) {
    if (typeof e != "string" || e.length === 0)
      return e;
    const t = ce.resolve(e);
    if (t.length <= 2)
      return e;
    if (t.charCodeAt(0) === we) {
      if (t.charCodeAt(1) === we) {
        const n = t.charCodeAt(2);
        if (n !== il && n !== Qe)
          return `\\\\?\\UNC\\${t.slice(2)}`;
      }
    } else if ($e(t.charCodeAt(0)) && t.charCodeAt(1) === Ge && t.charCodeAt(2) === we)
      return `\\\\?\\${t}`;
    return e;
  },
  dirname(e) {
    se(e, "path");
    const t = e.length;
    if (t === 0)
      return ".";
    let n = -1, i = 0;
    const r = e.charCodeAt(0);
    if (t === 1)
      return G(r) ? e : ".";
    if (G(r)) {
      if (n = i = 1, G(e.charCodeAt(1))) {
        let u = 2, o = u;
        for (; u < t && !G(e.charCodeAt(u)); )
          u++;
        if (u < t && u !== o) {
          for (o = u; u < t && G(e.charCodeAt(u)); )
            u++;
          if (u < t && u !== o) {
            for (o = u; u < t && !G(e.charCodeAt(u)); )
              u++;
            if (u === t)
              return e;
            u !== o && (n = i = u + 1);
          }
        }
      }
    } else $e(r) && e.charCodeAt(1) === Ge && (n = t > 2 && G(e.charCodeAt(2)) ? 3 : 2, i = n);
    let s = -1, a = !0;
    for (let u = t - 1; u >= i; --u)
      if (G(e.charCodeAt(u))) {
        if (!a) {
          s = u;
          break;
        }
      } else
        a = !1;
    if (s === -1) {
      if (n === -1)
        return ".";
      s = n;
    }
    return e.slice(0, s);
  },
  basename(e, t) {
    t !== void 0 && se(t, "suffix"), se(e, "path");
    let n = 0, i = -1, r = !0, s;
    if (e.length >= 2 && $e(e.charCodeAt(0)) && e.charCodeAt(1) === Ge && (n = 2), t !== void 0 && t.length > 0 && t.length <= e.length) {
      if (t === e)
        return "";
      let a = t.length - 1, u = -1;
      for (s = e.length - 1; s >= n; --s) {
        const o = e.charCodeAt(s);
        if (G(o)) {
          if (!r) {
            n = s + 1;
            break;
          }
        } else
          u === -1 && (r = !1, u = s + 1), a >= 0 && (o === t.charCodeAt(a) ? --a === -1 && (i = s) : (a = -1, i = u));
      }
      return n === i ? i = u : i === -1 && (i = e.length), e.slice(n, i);
    }
    for (s = e.length - 1; s >= n; --s)
      if (G(e.charCodeAt(s))) {
        if (!r) {
          n = s + 1;
          break;
        }
      } else i === -1 && (r = !1, i = s + 1);
    return i === -1 ? "" : e.slice(n, i);
  },
  extname(e) {
    se(e, "path");
    let t = 0, n = -1, i = 0, r = -1, s = !0, a = 0;
    e.length >= 2 && e.charCodeAt(1) === Ge && $e(e.charCodeAt(0)) && (t = i = 2);
    for (let u = e.length - 1; u >= t; --u) {
      const o = e.charCodeAt(u);
      if (G(o)) {
        if (!s) {
          i = u + 1;
          break;
        }
        continue;
      }
      r === -1 && (s = !1, r = u + 1), o === Qe ? n === -1 ? n = u : a !== 1 && (a = 1) : n !== -1 && (a = -1);
    }
    return n === -1 || r === -1 || a === 0 || a === 1 && n === r - 1 && n === i + 1 ? "" : e.slice(n, r);
  },
  format: cs.bind(null, "\\"),
  parse(e) {
    se(e, "path");
    const t = { root: "", dir: "", base: "", ext: "", name: "" };
    if (e.length === 0)
      return t;
    const n = e.length;
    let i = 0, r = e.charCodeAt(0);
    if (n === 1)
      return G(r) ? (t.root = t.dir = e, t) : (t.base = t.name = e, t);
    if (G(r)) {
      if (i = 1, G(e.charCodeAt(1))) {
        let f = 2, _ = f;
        for (; f < n && !G(e.charCodeAt(f)); )
          f++;
        if (f < n && f !== _) {
          for (_ = f; f < n && G(e.charCodeAt(f)); )
            f++;
          if (f < n && f !== _) {
            for (_ = f; f < n && !G(e.charCodeAt(f)); )
              f++;
            f === n ? i = f : f !== _ && (i = f + 1);
          }
        }
      }
    } else if ($e(r) && e.charCodeAt(1) === Ge) {
      if (n <= 2)
        return t.root = t.dir = e, t;
      if (i = 2, G(e.charCodeAt(2))) {
        if (n === 3)
          return t.root = t.dir = e, t;
        i = 3;
      }
    }
    i > 0 && (t.root = e.slice(0, i));
    let s = -1, a = i, u = -1, o = !0, c = e.length - 1, h = 0;
    for (; c >= i; --c) {
      if (r = e.charCodeAt(c), G(r)) {
        if (!o) {
          a = c + 1;
          break;
        }
        continue;
      }
      u === -1 && (o = !1, u = c + 1), r === Qe ? s === -1 ? s = c : h !== 1 && (h = 1) : s !== -1 && (h = -1);
    }
    return u !== -1 && (s === -1 || h === 0 || h === 1 && s === u - 1 && s === a + 1 ? t.base = t.name = e.slice(a, u) : (t.name = e.slice(a, s), t.base = e.slice(a, u), t.ext = e.slice(s, u))), a > 0 && a !== i ? t.dir = e.slice(0, a - 1) : t.dir = t.root, t;
  },
  sep: "\\",
  delimiter: ";",
  win32: null,
  posix: null
}, al = (() => {
  if (Fe) {
    const e = /\\/g;
    return () => {
      const t = bn().replace(e, "/");
      return t.slice(t.indexOf("/"));
    };
  }
  return () => bn();
})(), C = {
  resolve(...e) {
    let t = "", n = !1;
    for (let i = e.length - 1; i >= -1 && !n; i--) {
      const r = i >= 0 ? e[i] : al();
      se(r, `paths[${i}]`), r.length !== 0 && (t = `${r}/${t}`, n = r.charCodeAt(0) === ue);
    }
    return t = dn(t, !n, "/", Jn), n ? `/${t}` : t.length > 0 ? t : ".";
  },
  normalize(e) {
    if (se(e, "path"), e.length === 0)
      return ".";
    const t = e.charCodeAt(0) === ue, n = e.charCodeAt(e.length - 1) === ue;
    return e = dn(e, !t, "/", Jn), e.length === 0 ? t ? "/" : n ? "./" : "." : (n && (e += "/"), t ? `/${e}` : e);
  },
  isAbsolute(e) {
    return se(e, "path"), e.length > 0 && e.charCodeAt(0) === ue;
  },
  join(...e) {
    if (e.length === 0)
      return ".";
    let t;
    for (let n = 0; n < e.length; ++n) {
      const i = e[n];
      se(i, "path"), i.length > 0 && (t === void 0 ? t = i : t += `/${i}`);
    }
    return t === void 0 ? "." : C.normalize(t);
  },
  relative(e, t) {
    if (se(e, "from"), se(t, "to"), e === t || (e = C.resolve(e), t = C.resolve(t), e === t))
      return "";
    const n = 1, i = e.length, r = i - n, s = 1, a = t.length - s, u = r < a ? r : a;
    let o = -1, c = 0;
    for (; c < u; c++) {
      const f = e.charCodeAt(n + c);
      if (f !== t.charCodeAt(s + c))
        break;
      f === ue && (o = c);
    }
    if (c === u)
      if (a > u) {
        if (t.charCodeAt(s + c) === ue)
          return t.slice(s + c + 1);
        if (c === 0)
          return t.slice(s + c);
      } else r > u && (e.charCodeAt(n + c) === ue ? o = c : c === 0 && (o = 0));
    let h = "";
    for (c = n + o + 1; c <= i; ++c)
      (c === i || e.charCodeAt(c) === ue) && (h += h.length === 0 ? ".." : "/..");
    return `${h}${t.slice(s + o)}`;
  },
  toNamespacedPath(e) {
    return e;
  },
  dirname(e) {
    if (se(e, "path"), e.length === 0)
      return ".";
    const t = e.charCodeAt(0) === ue;
    let n = -1, i = !0;
    for (let r = e.length - 1; r >= 1; --r)
      if (e.charCodeAt(r) === ue) {
        if (!i) {
          n = r;
          break;
        }
      } else
        i = !1;
    return n === -1 ? t ? "/" : "." : t && n === 1 ? "//" : e.slice(0, n);
  },
  basename(e, t) {
    t !== void 0 && se(t, "ext"), se(e, "path");
    let n = 0, i = -1, r = !0, s;
    if (t !== void 0 && t.length > 0 && t.length <= e.length) {
      if (t === e)
        return "";
      let a = t.length - 1, u = -1;
      for (s = e.length - 1; s >= 0; --s) {
        const o = e.charCodeAt(s);
        if (o === ue) {
          if (!r) {
            n = s + 1;
            break;
          }
        } else
          u === -1 && (r = !1, u = s + 1), a >= 0 && (o === t.charCodeAt(a) ? --a === -1 && (i = s) : (a = -1, i = u));
      }
      return n === i ? i = u : i === -1 && (i = e.length), e.slice(n, i);
    }
    for (s = e.length - 1; s >= 0; --s)
      if (e.charCodeAt(s) === ue) {
        if (!r) {
          n = s + 1;
          break;
        }
      } else i === -1 && (r = !1, i = s + 1);
    return i === -1 ? "" : e.slice(n, i);
  },
  extname(e) {
    se(e, "path");
    let t = -1, n = 0, i = -1, r = !0, s = 0;
    for (let a = e.length - 1; a >= 0; --a) {
      const u = e.charCodeAt(a);
      if (u === ue) {
        if (!r) {
          n = a + 1;
          break;
        }
        continue;
      }
      i === -1 && (r = !1, i = a + 1), u === Qe ? t === -1 ? t = a : s !== 1 && (s = 1) : t !== -1 && (s = -1);
    }
    return t === -1 || i === -1 || s === 0 || s === 1 && t === i - 1 && t === n + 1 ? "" : e.slice(t, i);
  },
  format: cs.bind(null, "/"),
  parse(e) {
    se(e, "path");
    const t = { root: "", dir: "", base: "", ext: "", name: "" };
    if (e.length === 0)
      return t;
    const n = e.charCodeAt(0) === ue;
    let i;
    n ? (t.root = "/", i = 1) : i = 0;
    let r = -1, s = 0, a = -1, u = !0, o = e.length - 1, c = 0;
    for (; o >= i; --o) {
      const h = e.charCodeAt(o);
      if (h === ue) {
        if (!u) {
          s = o + 1;
          break;
        }
        continue;
      }
      a === -1 && (u = !1, a = o + 1), h === Qe ? r === -1 ? r = o : c !== 1 && (c = 1) : r !== -1 && (c = -1);
    }
    if (a !== -1) {
      const h = s === 0 && n ? 1 : s;
      r === -1 || c === 0 || c === 1 && r === a - 1 && r === s + 1 ? t.base = t.name = e.slice(h, a) : (t.name = e.slice(h, r), t.base = e.slice(h, a), t.ext = e.slice(r, a));
    }
    return s > 0 ? t.dir = e.slice(0, s - 1) : n && (t.dir = "/"), t;
  },
  sep: "/",
  delimiter: ":",
  win32: null,
  posix: null
};
C.win32 = ce.win32 = ce;
C.posix = ce.posix = C;
const ll = Fe ? ce.normalize : C.normalize;
Fe ? ce.isAbsolute : C.isAbsolute;
const ul = Fe ? ce.join : C.join, ol = Fe ? ce.resolve : C.resolve, cl = Fe ? ce.relative : C.relative, hl = Fe ? ce.dirname : C.dirname;
Fe ? ce.basename : C.basename;
Fe ? ce.extname : C.extname;
Fe ? ce.parse : C.parse;
const un = Fe ? ce.sep : C.sep, fl = /^\w[\w\d+.-]*$/, ml = /^\//, gl = /^\/\//;
function _l(e, t) {
  if (!e.scheme && t)
    throw new Error(
      `[UriError]: Scheme is missing: {scheme: "", authority: "${e.authority}", path: "${e.path}", query: "${e.query}", fragment: "${e.fragment}"}`
    );
  if (e.scheme && !fl.test(e.scheme))
    throw new Error("[UriError]: Scheme contains illegal characters.");
  if (e.path) {
    if (e.authority) {
      if (!ml.test(e.path))
        throw new Error(
          '[UriError]: If a URI contains an authority component, then the path component must either be empty or begin with a slash ("/") character'
        );
    } else if (gl.test(e.path))
      throw new Error(
        '[UriError]: If a URI does not contain an authority component, then the path cannot begin with two slash characters ("//")'
      );
  }
}
function bl(e, t) {
  return !e && !t ? "file" : e;
}
function dl(e, t) {
  switch (e) {
    case "https":
    case "http":
    case "file":
      t ? t[0] !== ke && (t = ke + t) : t = ke;
      break;
  }
  return t;
}
const J = "", ke = "/", wl = /^(([^:/?#]+?):)?(\/\/([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?/;
class oe {
  static isUri(t) {
    return t instanceof oe ? !0 : t ? typeof t.authority == "string" && typeof t.fragment == "string" && typeof t.path == "string" && typeof t.query == "string" && typeof t.scheme == "string" && typeof t.fsPath == "string" && typeof t.with == "function" && typeof t.toString == "function" : !1;
  }
  constructor(t, n, i, r, s, a = !1) {
    typeof t == "object" ? (this.scheme = t.scheme || J, this.authority = t.authority || J, this.path = t.path || J, this.query = t.query || J, this.fragment = t.fragment || J) : (this.scheme = bl(t, a), this.authority = n || J, this.path = dl(this.scheme, i || J), this.query = r || J, this.fragment = s || J, _l(this, a));
  }
  get fsPath() {
    return wn(this, !1);
  }
  with(t) {
    if (!t)
      return this;
    let { scheme: n, authority: i, path: r, query: s, fragment: a } = t;
    return n === void 0 ? n = this.scheme : n === null && (n = J), i === void 0 ? i = this.authority : i === null && (i = J), r === void 0 ? r = this.path : r === null && (r = J), s === void 0 ? s = this.query : s === null && (s = J), a === void 0 ? a = this.fragment : a === null && (a = J), n === this.scheme && i === this.authority && r === this.path && s === this.query && a === this.fragment ? this : new ct(n, i, r, s, a);
  }
  static parse(t, n = !1) {
    const i = wl.exec(t);
    return i ? new ct(
      i[2] || J,
      en(i[4] || J),
      en(i[5] || J),
      en(i[7] || J),
      en(i[9] || J),
      n
    ) : new ct(J, J, J, J, J);
  }
  static file(t) {
    let n = J;
    if (Tt && (t = t.replace(/\\/g, ke)), t[0] === ke && t[1] === ke) {
      const i = t.indexOf(ke, 2);
      i === -1 ? (n = t.substring(2), t = ke) : (n = t.substring(2, i), t = t.substring(i) || ke);
    }
    return new ct("file", n, t, J, J);
  }
  static from(t, n) {
    return new ct(
      t.scheme,
      t.authority,
      t.path,
      t.query,
      t.fragment,
      n
    );
  }
  static joinPath(t, ...n) {
    if (!t.path)
      throw new Error("[UriError]: cannot call joinPath on URI without path");
    let i;
    return Tt && t.scheme === "file" ? i = oe.file(ce.join(wn(t, !0), ...n)).path : i = C.join(t.path, ...n), t.with({ path: i });
  }
  toString(t = !1) {
    return Kn(this, t);
  }
  toJSON() {
    return this;
  }
  static revive(t) {
    if (t) {
      if (t instanceof oe)
        return t;
      {
        const n = new ct(t);
        return n._formatted = t.external ?? null, n._fsPath = t._sep === hs ? t.fsPath ?? null : null, n;
      }
    } else return t;
  }
  [Symbol.for("debug.description")]() {
    return `URI(${this.toString()})`;
  }
}
const hs = Tt ? 1 : void 0;
class ct extends oe {
  constructor() {
    super(...arguments), this._formatted = null, this._fsPath = null;
  }
  get fsPath() {
    return this._fsPath || (this._fsPath = wn(this, !1)), this._fsPath;
  }
  toString(t = !1) {
    return t ? Kn(this, !0) : (this._formatted || (this._formatted = Kn(this, !1)), this._formatted);
  }
  toJSON() {
    const t = {
      $mid: Zn.Uri
    };
    return this._fsPath && (t.fsPath = this._fsPath, t._sep = hs), this._formatted && (t.external = this._formatted), this.path && (t.path = this.path), this.scheme && (t.scheme = this.scheme), this.authority && (t.authority = this.authority), this.query && (t.query = this.query), this.fragment && (t.fragment = this.fragment), t;
  }
}
const fs = {
  [L.Colon]: "%3A",
  [L.Slash]: "%2F",
  [L.QuestionMark]: "%3F",
  [L.Hash]: "%23",
  [L.OpenSquareBracket]: "%5B",
  [L.CloseSquareBracket]: "%5D",
  [L.AtSign]: "%40",
  [L.ExclamationMark]: "%21",
  [L.DollarSign]: "%24",
  [L.Ampersand]: "%26",
  [L.SingleQuote]: "%27",
  [L.OpenParen]: "%28",
  [L.CloseParen]: "%29",
  [L.Asterisk]: "%2A",
  [L.Plus]: "%2B",
  [L.Comma]: "%2C",
  [L.Semicolon]: "%3B",
  [L.Equals]: "%3D",
  [L.Space]: "%20"
};
function qi(e, t, n) {
  let i, r = -1;
  for (let s = 0; s < e.length; s++) {
    const a = e.charCodeAt(s);
    if (a >= L.a && a <= L.z || a >= L.A && a <= L.Z || a >= L.Digit0 && a <= L.Digit9 || a === L.Dash || a === L.Period || a === L.Underline || a === L.Tilde || t && a === L.Slash || n && a === L.OpenSquareBracket || n && a === L.CloseSquareBracket || n && a === L.Colon)
      r !== -1 && (i += encodeURIComponent(e.substring(r, s)), r = -1), i !== void 0 && (i += e.charAt(s));
    else {
      i === void 0 && (i = e.substr(0, s));
      const u = fs[a];
      u !== void 0 ? (r !== -1 && (i += encodeURIComponent(e.substring(r, s)), r = -1), i += u) : r === -1 && (r = s);
    }
  }
  return r !== -1 && (i += encodeURIComponent(e.substring(r))), i !== void 0 ? i : e;
}
function Ll(e) {
  let t;
  for (let n = 0; n < e.length; n++) {
    const i = e.charCodeAt(n);
    i === L.Hash || i === L.QuestionMark ? (t === void 0 && (t = e.substr(0, n)), t += fs[i]) : t !== void 0 && (t += e[n]);
  }
  return t !== void 0 ? t : e;
}
function wn(e, t) {
  let n;
  return e.authority && e.path.length > 1 && e.scheme === "file" ? n = `//${e.authority}${e.path}` : e.path.charCodeAt(0) === L.Slash && (e.path.charCodeAt(1) >= L.A && e.path.charCodeAt(1) <= L.Z || e.path.charCodeAt(1) >= L.a && e.path.charCodeAt(1) <= L.z) && e.path.charCodeAt(2) === L.Colon ? t ? n = e.path.substr(1) : n = e.path[1].toLowerCase() + e.path.substr(2) : n = e.path, Tt && (n = n.replace(/\//g, "\\")), n;
}
function Kn(e, t) {
  const n = t ? Ll : qi;
  let i = "", { scheme: r, authority: s, path: a, query: u, fragment: o } = e;
  if (r && (i += r, i += ":"), (s || r === "file") && (i += ke, i += ke), s) {
    let c = s.indexOf("@");
    if (c !== -1) {
      const h = s.substr(0, c);
      s = s.substr(c + 1), c = h.lastIndexOf(":"), c === -1 ? i += n(h, !1, !1) : (i += n(h.substr(0, c), !1, !1), i += ":", i += n(h.substr(c + 1), !1, !0)), i += "@";
    }
    s = s.toLowerCase(), c = s.lastIndexOf(":"), c === -1 ? i += n(s, !1, !0) : (i += n(s.substr(0, c), !1, !0), i += s.substr(c));
  }
  if (a) {
    if (a.length >= 3 && a.charCodeAt(0) === L.Slash && a.charCodeAt(2) === L.Colon) {
      const c = a.charCodeAt(1);
      c >= L.A && c <= L.Z && (a = `/${String.fromCharCode(c + 32)}:${a.substr(3)}`);
    } else if (a.length >= 2 && a.charCodeAt(1) === L.Colon) {
      const c = a.charCodeAt(0);
      c >= L.A && c <= L.Z && (a = `${String.fromCharCode(c + 32)}:${a.substr(2)}`);
    }
    i += n(a, !0, !1);
  }
  return u && (i += "?", i += n(u, !1, !1)), o && (i += "#", i += t ? o : qi(o, !1, !1)), i;
}
function ms(e) {
  try {
    return decodeURIComponent(e);
  } catch {
    return e.length > 3 ? e.substr(0, 3) + ms(e.substr(3)) : e;
  }
}
const Hi = /(%[0-9A-Za-z][0-9A-Za-z])+/g;
function en(e) {
  return e.match(Hi) ? e.replace(Hi, (t) => ms(t)) : e;
}
var Xe;
(function(e) {
  e[e.LTR = 0] = "LTR", e[e.RTL = 1] = "RTL";
})(Xe || (Xe = {}));
class Ne extends F {
  constructor(t, n, i, r) {
    super(t, n, i, r), this.selectionStartLineNumber = t, this.selectionStartColumn = n, this.positionLineNumber = i, this.positionColumn = r;
  }
  toString() {
    return "[" + this.selectionStartLineNumber + "," + this.selectionStartColumn + " -> " + this.positionLineNumber + "," + this.positionColumn + "]";
  }
  equalsSelection(t) {
    return Ne.selectionsEqual(this, t);
  }
  static selectionsEqual(t, n) {
    return t.selectionStartLineNumber === n.selectionStartLineNumber && t.selectionStartColumn === n.selectionStartColumn && t.positionLineNumber === n.positionLineNumber && t.positionColumn === n.positionColumn;
  }
  getDirection() {
    return this.selectionStartLineNumber === this.startLineNumber && this.selectionStartColumn === this.startColumn ? Xe.LTR : Xe.RTL;
  }
  setEndPosition(t, n) {
    return this.getDirection() === Xe.LTR ? new Ne(this.startLineNumber, this.startColumn, t, n) : new Ne(t, n, this.startLineNumber, this.startColumn);
  }
  getPosition() {
    return new W(this.positionLineNumber, this.positionColumn);
  }
  getSelectionStart() {
    return new W(this.selectionStartLineNumber, this.selectionStartColumn);
  }
  setStartPosition(t, n) {
    return this.getDirection() === Xe.LTR ? new Ne(t, n, this.endLineNumber, this.endColumn) : new Ne(this.endLineNumber, this.endColumn, t, n);
  }
  static fromPositions(t, n = t) {
    return new Ne(t.lineNumber, t.column, n.lineNumber, n.column);
  }
  static fromRange(t, n) {
    return n === Xe.LTR ? new Ne(
      t.startLineNumber,
      t.startColumn,
      t.endLineNumber,
      t.endColumn
    ) : new Ne(
      t.endLineNumber,
      t.endColumn,
      t.startLineNumber,
      t.startColumn
    );
  }
  static liftSelection(t) {
    return new Ne(
      t.selectionStartLineNumber,
      t.selectionStartColumn,
      t.positionLineNumber,
      t.positionColumn
    );
  }
  static selectionsArrEqual(t, n) {
    if (t && !n || !t && n)
      return !1;
    if (!t && !n)
      return !0;
    if (t.length !== n.length)
      return !1;
    for (let i = 0, r = t.length; i < r; i++)
      if (!this.selectionsEqual(t[i], n[i]))
        return !1;
    return !0;
  }
  static isISelection(t) {
    return t && typeof t.selectionStartLineNumber == "number" && typeof t.selectionStartColumn == "number" && typeof t.positionLineNumber == "number" && typeof t.positionColumn == "number";
  }
  static createWithDirection(t, n, i, r, s) {
    return s === Xe.LTR ? new Ne(t, n, i, r) : new Ne(i, r, t, n);
  }
}
const Wi = /* @__PURE__ */ Object.create(null);
function l(e, t) {
  if (Ys(t)) {
    const n = Wi[t];
    if (n === void 0)
      throw new Error(`${e} references an unknown codicon: ${t}`);
    t = n;
  }
  return Wi[e] = t, { id: e };
}
const pl = {
  add: l("add", 6e4),
  plus: l("plus", 6e4),
  gistNew: l("gist-new", 6e4),
  repoCreate: l("repo-create", 6e4),
  lightbulb: l("lightbulb", 60001),
  lightBulb: l("light-bulb", 60001),
  repo: l("repo", 60002),
  repoDelete: l("repo-delete", 60002),
  gistFork: l("gist-fork", 60003),
  repoForked: l("repo-forked", 60003),
  gitPullRequest: l("git-pull-request", 60004),
  gitPullRequestAbandoned: l("git-pull-request-abandoned", 60004),
  recordKeys: l("record-keys", 60005),
  keyboard: l("keyboard", 60005),
  tag: l("tag", 60006),
  gitPullRequestLabel: l("git-pull-request-label", 60006),
  tagAdd: l("tag-add", 60006),
  tagRemove: l("tag-remove", 60006),
  person: l("person", 60007),
  personFollow: l("person-follow", 60007),
  personOutline: l("person-outline", 60007),
  personFilled: l("person-filled", 60007),
  gitBranch: l("git-branch", 60008),
  gitBranchCreate: l("git-branch-create", 60008),
  gitBranchDelete: l("git-branch-delete", 60008),
  sourceControl: l("source-control", 60008),
  mirror: l("mirror", 60009),
  mirrorPublic: l("mirror-public", 60009),
  star: l("star", 60010),
  starAdd: l("star-add", 60010),
  starDelete: l("star-delete", 60010),
  starEmpty: l("star-empty", 60010),
  comment: l("comment", 60011),
  commentAdd: l("comment-add", 60011),
  alert: l("alert", 60012),
  warning: l("warning", 60012),
  search: l("search", 60013),
  searchSave: l("search-save", 60013),
  logOut: l("log-out", 60014),
  signOut: l("sign-out", 60014),
  logIn: l("log-in", 60015),
  signIn: l("sign-in", 60015),
  eye: l("eye", 60016),
  eyeUnwatch: l("eye-unwatch", 60016),
  eyeWatch: l("eye-watch", 60016),
  circleFilled: l("circle-filled", 60017),
  primitiveDot: l("primitive-dot", 60017),
  closeDirty: l("close-dirty", 60017),
  debugBreakpoint: l("debug-breakpoint", 60017),
  debugBreakpointDisabled: l("debug-breakpoint-disabled", 60017),
  debugHint: l("debug-hint", 60017),
  terminalDecorationSuccess: l("terminal-decoration-success", 60017),
  primitiveSquare: l("primitive-square", 60018),
  edit: l("edit", 60019),
  pencil: l("pencil", 60019),
  info: l("info", 60020),
  issueOpened: l("issue-opened", 60020),
  gistPrivate: l("gist-private", 60021),
  gitForkPrivate: l("git-fork-private", 60021),
  lock: l("lock", 60021),
  mirrorPrivate: l("mirror-private", 60021),
  close: l("close", 60022),
  removeClose: l("remove-close", 60022),
  x: l("x", 60022),
  repoSync: l("repo-sync", 60023),
  sync: l("sync", 60023),
  clone: l("clone", 60024),
  desktopDownload: l("desktop-download", 60024),
  beaker: l("beaker", 60025),
  microscope: l("microscope", 60025),
  vm: l("vm", 60026),
  deviceDesktop: l("device-desktop", 60026),
  file: l("file", 60027),
  fileText: l("file-text", 60027),
  more: l("more", 60028),
  ellipsis: l("ellipsis", 60028),
  kebabHorizontal: l("kebab-horizontal", 60028),
  mailReply: l("mail-reply", 60029),
  reply: l("reply", 60029),
  organization: l("organization", 60030),
  organizationFilled: l("organization-filled", 60030),
  organizationOutline: l("organization-outline", 60030),
  newFile: l("new-file", 60031),
  fileAdd: l("file-add", 60031),
  newFolder: l("new-folder", 60032),
  fileDirectoryCreate: l("file-directory-create", 60032),
  trash: l("trash", 60033),
  trashcan: l("trashcan", 60033),
  history: l("history", 60034),
  clock: l("clock", 60034),
  folder: l("folder", 60035),
  fileDirectory: l("file-directory", 60035),
  symbolFolder: l("symbol-folder", 60035),
  logoGithub: l("logo-github", 60036),
  markGithub: l("mark-github", 60036),
  github: l("github", 60036),
  terminal: l("terminal", 60037),
  console: l("console", 60037),
  repl: l("repl", 60037),
  zap: l("zap", 60038),
  symbolEvent: l("symbol-event", 60038),
  error: l("error", 60039),
  stop: l("stop", 60039),
  variable: l("variable", 60040),
  symbolVariable: l("symbol-variable", 60040),
  array: l("array", 60042),
  symbolArray: l("symbol-array", 60042),
  symbolModule: l("symbol-module", 60043),
  symbolPackage: l("symbol-package", 60043),
  symbolNamespace: l("symbol-namespace", 60043),
  symbolObject: l("symbol-object", 60043),
  symbolMethod: l("symbol-method", 60044),
  symbolFunction: l("symbol-function", 60044),
  symbolConstructor: l("symbol-constructor", 60044),
  symbolBoolean: l("symbol-boolean", 60047),
  symbolNull: l("symbol-null", 60047),
  symbolNumeric: l("symbol-numeric", 60048),
  symbolNumber: l("symbol-number", 60048),
  symbolStructure: l("symbol-structure", 60049),
  symbolStruct: l("symbol-struct", 60049),
  symbolParameter: l("symbol-parameter", 60050),
  symbolTypeParameter: l("symbol-type-parameter", 60050),
  symbolKey: l("symbol-key", 60051),
  symbolText: l("symbol-text", 60051),
  symbolReference: l("symbol-reference", 60052),
  goToFile: l("go-to-file", 60052),
  symbolEnum: l("symbol-enum", 60053),
  symbolValue: l("symbol-value", 60053),
  symbolRuler: l("symbol-ruler", 60054),
  symbolUnit: l("symbol-unit", 60054),
  activateBreakpoints: l("activate-breakpoints", 60055),
  archive: l("archive", 60056),
  arrowBoth: l("arrow-both", 60057),
  arrowDown: l("arrow-down", 60058),
  arrowLeft: l("arrow-left", 60059),
  arrowRight: l("arrow-right", 60060),
  arrowSmallDown: l("arrow-small-down", 60061),
  arrowSmallLeft: l("arrow-small-left", 60062),
  arrowSmallRight: l("arrow-small-right", 60063),
  arrowSmallUp: l("arrow-small-up", 60064),
  arrowUp: l("arrow-up", 60065),
  bell: l("bell", 60066),
  bold: l("bold", 60067),
  book: l("book", 60068),
  bookmark: l("bookmark", 60069),
  debugBreakpointConditionalUnverified: l("debug-breakpoint-conditional-unverified", 60070),
  debugBreakpointConditional: l("debug-breakpoint-conditional", 60071),
  debugBreakpointConditionalDisabled: l("debug-breakpoint-conditional-disabled", 60071),
  debugBreakpointDataUnverified: l("debug-breakpoint-data-unverified", 60072),
  debugBreakpointData: l("debug-breakpoint-data", 60073),
  debugBreakpointDataDisabled: l("debug-breakpoint-data-disabled", 60073),
  debugBreakpointLogUnverified: l("debug-breakpoint-log-unverified", 60074),
  debugBreakpointLog: l("debug-breakpoint-log", 60075),
  debugBreakpointLogDisabled: l("debug-breakpoint-log-disabled", 60075),
  briefcase: l("briefcase", 60076),
  broadcast: l("broadcast", 60077),
  browser: l("browser", 60078),
  bug: l("bug", 60079),
  calendar: l("calendar", 60080),
  caseSensitive: l("case-sensitive", 60081),
  check: l("check", 60082),
  checklist: l("checklist", 60083),
  chevronDown: l("chevron-down", 60084),
  chevronLeft: l("chevron-left", 60085),
  chevronRight: l("chevron-right", 60086),
  chevronUp: l("chevron-up", 60087),
  chromeClose: l("chrome-close", 60088),
  chromeMaximize: l("chrome-maximize", 60089),
  chromeMinimize: l("chrome-minimize", 60090),
  chromeRestore: l("chrome-restore", 60091),
  circleOutline: l("circle-outline", 60092),
  circle: l("circle", 60092),
  debugBreakpointUnverified: l("debug-breakpoint-unverified", 60092),
  terminalDecorationIncomplete: l("terminal-decoration-incomplete", 60092),
  circleSlash: l("circle-slash", 60093),
  circuitBoard: l("circuit-board", 60094),
  clearAll: l("clear-all", 60095),
  clippy: l("clippy", 60096),
  closeAll: l("close-all", 60097),
  cloudDownload: l("cloud-download", 60098),
  cloudUpload: l("cloud-upload", 60099),
  code: l("code", 60100),
  collapseAll: l("collapse-all", 60101),
  colorMode: l("color-mode", 60102),
  commentDiscussion: l("comment-discussion", 60103),
  creditCard: l("credit-card", 60105),
  dash: l("dash", 60108),
  dashboard: l("dashboard", 60109),
  database: l("database", 60110),
  debugContinue: l("debug-continue", 60111),
  debugDisconnect: l("debug-disconnect", 60112),
  debugPause: l("debug-pause", 60113),
  debugRestart: l("debug-restart", 60114),
  debugStart: l("debug-start", 60115),
  debugStepInto: l("debug-step-into", 60116),
  debugStepOut: l("debug-step-out", 60117),
  debugStepOver: l("debug-step-over", 60118),
  debugStop: l("debug-stop", 60119),
  debug: l("debug", 60120),
  deviceCameraVideo: l("device-camera-video", 60121),
  deviceCamera: l("device-camera", 60122),
  deviceMobile: l("device-mobile", 60123),
  diffAdded: l("diff-added", 60124),
  diffIgnored: l("diff-ignored", 60125),
  diffModified: l("diff-modified", 60126),
  diffRemoved: l("diff-removed", 60127),
  diffRenamed: l("diff-renamed", 60128),
  diff: l("diff", 60129),
  diffSidebyside: l("diff-sidebyside", 60129),
  discard: l("discard", 60130),
  editorLayout: l("editor-layout", 60131),
  emptyWindow: l("empty-window", 60132),
  exclude: l("exclude", 60133),
  extensions: l("extensions", 60134),
  eyeClosed: l("eye-closed", 60135),
  fileBinary: l("file-binary", 60136),
  fileCode: l("file-code", 60137),
  fileMedia: l("file-media", 60138),
  filePdf: l("file-pdf", 60139),
  fileSubmodule: l("file-submodule", 60140),
  fileSymlinkDirectory: l("file-symlink-directory", 60141),
  fileSymlinkFile: l("file-symlink-file", 60142),
  fileZip: l("file-zip", 60143),
  files: l("files", 60144),
  filter: l("filter", 60145),
  flame: l("flame", 60146),
  foldDown: l("fold-down", 60147),
  foldUp: l("fold-up", 60148),
  fold: l("fold", 60149),
  folderActive: l("folder-active", 60150),
  folderOpened: l("folder-opened", 60151),
  gear: l("gear", 60152),
  gift: l("gift", 60153),
  gistSecret: l("gist-secret", 60154),
  gist: l("gist", 60155),
  gitCommit: l("git-commit", 60156),
  gitCompare: l("git-compare", 60157),
  compareChanges: l("compare-changes", 60157),
  gitMerge: l("git-merge", 60158),
  githubAction: l("github-action", 60159),
  githubAlt: l("github-alt", 60160),
  globe: l("globe", 60161),
  grabber: l("grabber", 60162),
  graph: l("graph", 60163),
  gripper: l("gripper", 60164),
  heart: l("heart", 60165),
  home: l("home", 60166),
  horizontalRule: l("horizontal-rule", 60167),
  hubot: l("hubot", 60168),
  inbox: l("inbox", 60169),
  issueReopened: l("issue-reopened", 60171),
  issues: l("issues", 60172),
  italic: l("italic", 60173),
  jersey: l("jersey", 60174),
  json: l("json", 60175),
  kebabVertical: l("kebab-vertical", 60176),
  key: l("key", 60177),
  law: l("law", 60178),
  lightbulbAutofix: l("lightbulb-autofix", 60179),
  linkExternal: l("link-external", 60180),
  link: l("link", 60181),
  listOrdered: l("list-ordered", 60182),
  listUnordered: l("list-unordered", 60183),
  liveShare: l("live-share", 60184),
  loading: l("loading", 60185),
  location: l("location", 60186),
  mailRead: l("mail-read", 60187),
  mail: l("mail", 60188),
  markdown: l("markdown", 60189),
  megaphone: l("megaphone", 60190),
  mention: l("mention", 60191),
  milestone: l("milestone", 60192),
  gitPullRequestMilestone: l("git-pull-request-milestone", 60192),
  mortarBoard: l("mortar-board", 60193),
  move: l("move", 60194),
  multipleWindows: l("multiple-windows", 60195),
  mute: l("mute", 60196),
  noNewline: l("no-newline", 60197),
  note: l("note", 60198),
  octoface: l("octoface", 60199),
  openPreview: l("open-preview", 60200),
  package: l("package", 60201),
  paintcan: l("paintcan", 60202),
  pin: l("pin", 60203),
  play: l("play", 60204),
  run: l("run", 60204),
  plug: l("plug", 60205),
  preserveCase: l("preserve-case", 60206),
  preview: l("preview", 60207),
  project: l("project", 60208),
  pulse: l("pulse", 60209),
  question: l("question", 60210),
  quote: l("quote", 60211),
  radioTower: l("radio-tower", 60212),
  reactions: l("reactions", 60213),
  references: l("references", 60214),
  refresh: l("refresh", 60215),
  regex: l("regex", 60216),
  remoteExplorer: l("remote-explorer", 60217),
  remote: l("remote", 60218),
  remove: l("remove", 60219),
  replaceAll: l("replace-all", 60220),
  replace: l("replace", 60221),
  repoClone: l("repo-clone", 60222),
  repoForcePush: l("repo-force-push", 60223),
  repoPull: l("repo-pull", 60224),
  repoPush: l("repo-push", 60225),
  report: l("report", 60226),
  requestChanges: l("request-changes", 60227),
  rocket: l("rocket", 60228),
  rootFolderOpened: l("root-folder-opened", 60229),
  rootFolder: l("root-folder", 60230),
  rss: l("rss", 60231),
  ruby: l("ruby", 60232),
  saveAll: l("save-all", 60233),
  saveAs: l("save-as", 60234),
  save: l("save", 60235),
  screenFull: l("screen-full", 60236),
  screenNormal: l("screen-normal", 60237),
  searchStop: l("search-stop", 60238),
  server: l("server", 60240),
  settingsGear: l("settings-gear", 60241),
  settings: l("settings", 60242),
  shield: l("shield", 60243),
  smiley: l("smiley", 60244),
  sortPrecedence: l("sort-precedence", 60245),
  splitHorizontal: l("split-horizontal", 60246),
  splitVertical: l("split-vertical", 60247),
  squirrel: l("squirrel", 60248),
  starFull: l("star-full", 60249),
  starHalf: l("star-half", 60250),
  symbolClass: l("symbol-class", 60251),
  symbolColor: l("symbol-color", 60252),
  symbolConstant: l("symbol-constant", 60253),
  symbolEnumMember: l("symbol-enum-member", 60254),
  symbolField: l("symbol-field", 60255),
  symbolFile: l("symbol-file", 60256),
  symbolInterface: l("symbol-interface", 60257),
  symbolKeyword: l("symbol-keyword", 60258),
  symbolMisc: l("symbol-misc", 60259),
  symbolOperator: l("symbol-operator", 60260),
  symbolProperty: l("symbol-property", 60261),
  wrench: l("wrench", 60261),
  wrenchSubaction: l("wrench-subaction", 60261),
  symbolSnippet: l("symbol-snippet", 60262),
  tasklist: l("tasklist", 60263),
  telescope: l("telescope", 60264),
  textSize: l("text-size", 60265),
  threeBars: l("three-bars", 60266),
  thumbsdown: l("thumbsdown", 60267),
  thumbsup: l("thumbsup", 60268),
  tools: l("tools", 60269),
  triangleDown: l("triangle-down", 60270),
  triangleLeft: l("triangle-left", 60271),
  triangleRight: l("triangle-right", 60272),
  triangleUp: l("triangle-up", 60273),
  twitter: l("twitter", 60274),
  unfold: l("unfold", 60275),
  unlock: l("unlock", 60276),
  unmute: l("unmute", 60277),
  unverified: l("unverified", 60278),
  verified: l("verified", 60279),
  versions: l("versions", 60280),
  vmActive: l("vm-active", 60281),
  vmOutline: l("vm-outline", 60282),
  vmRunning: l("vm-running", 60283),
  watch: l("watch", 60284),
  whitespace: l("whitespace", 60285),
  wholeWord: l("whole-word", 60286),
  window: l("window", 60287),
  wordWrap: l("word-wrap", 60288),
  zoomIn: l("zoom-in", 60289),
  zoomOut: l("zoom-out", 60290),
  listFilter: l("list-filter", 60291),
  listFlat: l("list-flat", 60292),
  listSelection: l("list-selection", 60293),
  selection: l("selection", 60293),
  listTree: l("list-tree", 60294),
  debugBreakpointFunctionUnverified: l("debug-breakpoint-function-unverified", 60295),
  debugBreakpointFunction: l("debug-breakpoint-function", 60296),
  debugBreakpointFunctionDisabled: l("debug-breakpoint-function-disabled", 60296),
  debugStackframeActive: l("debug-stackframe-active", 60297),
  circleSmallFilled: l("circle-small-filled", 60298),
  debugStackframeDot: l("debug-stackframe-dot", 60298),
  terminalDecorationMark: l("terminal-decoration-mark", 60298),
  debugStackframe: l("debug-stackframe", 60299),
  debugStackframeFocused: l("debug-stackframe-focused", 60299),
  debugBreakpointUnsupported: l("debug-breakpoint-unsupported", 60300),
  symbolString: l("symbol-string", 60301),
  debugReverseContinue: l("debug-reverse-continue", 60302),
  debugStepBack: l("debug-step-back", 60303),
  debugRestartFrame: l("debug-restart-frame", 60304),
  debugAlt: l("debug-alt", 60305),
  callIncoming: l("call-incoming", 60306),
  callOutgoing: l("call-outgoing", 60307),
  menu: l("menu", 60308),
  expandAll: l("expand-all", 60309),
  feedback: l("feedback", 60310),
  gitPullRequestReviewer: l("git-pull-request-reviewer", 60310),
  groupByRefType: l("group-by-ref-type", 60311),
  ungroupByRefType: l("ungroup-by-ref-type", 60312),
  account: l("account", 60313),
  gitPullRequestAssignee: l("git-pull-request-assignee", 60313),
  bellDot: l("bell-dot", 60314),
  debugConsole: l("debug-console", 60315),
  library: l("library", 60316),
  output: l("output", 60317),
  runAll: l("run-all", 60318),
  syncIgnored: l("sync-ignored", 60319),
  pinned: l("pinned", 60320),
  githubInverted: l("github-inverted", 60321),
  serverProcess: l("server-process", 60322),
  serverEnvironment: l("server-environment", 60323),
  pass: l("pass", 60324),
  issueClosed: l("issue-closed", 60324),
  stopCircle: l("stop-circle", 60325),
  playCircle: l("play-circle", 60326),
  record: l("record", 60327),
  debugAltSmall: l("debug-alt-small", 60328),
  vmConnect: l("vm-connect", 60329),
  cloud: l("cloud", 60330),
  merge: l("merge", 60331),
  export: l("export", 60332),
  graphLeft: l("graph-left", 60333),
  magnet: l("magnet", 60334),
  notebook: l("notebook", 60335),
  redo: l("redo", 60336),
  checkAll: l("check-all", 60337),
  pinnedDirty: l("pinned-dirty", 60338),
  passFilled: l("pass-filled", 60339),
  circleLargeFilled: l("circle-large-filled", 60340),
  circleLarge: l("circle-large", 60341),
  circleLargeOutline: l("circle-large-outline", 60341),
  combine: l("combine", 60342),
  gather: l("gather", 60342),
  table: l("table", 60343),
  variableGroup: l("variable-group", 60344),
  typeHierarchy: l("type-hierarchy", 60345),
  typeHierarchySub: l("type-hierarchy-sub", 60346),
  typeHierarchySuper: l("type-hierarchy-super", 60347),
  gitPullRequestCreate: l("git-pull-request-create", 60348),
  runAbove: l("run-above", 60349),
  runBelow: l("run-below", 60350),
  notebookTemplate: l("notebook-template", 60351),
  debugRerun: l("debug-rerun", 60352),
  workspaceTrusted: l("workspace-trusted", 60353),
  workspaceUntrusted: l("workspace-untrusted", 60354),
  workspaceUnknown: l("workspace-unknown", 60355),
  terminalCmd: l("terminal-cmd", 60356),
  terminalDebian: l("terminal-debian", 60357),
  terminalLinux: l("terminal-linux", 60358),
  terminalPowershell: l("terminal-powershell", 60359),
  terminalTmux: l("terminal-tmux", 60360),
  terminalUbuntu: l("terminal-ubuntu", 60361),
  terminalBash: l("terminal-bash", 60362),
  arrowSwap: l("arrow-swap", 60363),
  copy: l("copy", 60364),
  personAdd: l("person-add", 60365),
  filterFilled: l("filter-filled", 60366),
  wand: l("wand", 60367),
  debugLineByLine: l("debug-line-by-line", 60368),
  inspect: l("inspect", 60369),
  layers: l("layers", 60370),
  layersDot: l("layers-dot", 60371),
  layersActive: l("layers-active", 60372),
  compass: l("compass", 60373),
  compassDot: l("compass-dot", 60374),
  compassActive: l("compass-active", 60375),
  azure: l("azure", 60376),
  issueDraft: l("issue-draft", 60377),
  gitPullRequestClosed: l("git-pull-request-closed", 60378),
  gitPullRequestDraft: l("git-pull-request-draft", 60379),
  debugAll: l("debug-all", 60380),
  debugCoverage: l("debug-coverage", 60381),
  runErrors: l("run-errors", 60382),
  folderLibrary: l("folder-library", 60383),
  debugContinueSmall: l("debug-continue-small", 60384),
  beakerStop: l("beaker-stop", 60385),
  graphLine: l("graph-line", 60386),
  graphScatter: l("graph-scatter", 60387),
  pieChart: l("pie-chart", 60388),
  bracket: l("bracket", 60175),
  bracketDot: l("bracket-dot", 60389),
  bracketError: l("bracket-error", 60390),
  lockSmall: l("lock-small", 60391),
  azureDevops: l("azure-devops", 60392),
  verifiedFilled: l("verified-filled", 60393),
  newline: l("newline", 60394),
  layout: l("layout", 60395),
  layoutActivitybarLeft: l("layout-activitybar-left", 60396),
  layoutActivitybarRight: l("layout-activitybar-right", 60397),
  layoutPanelLeft: l("layout-panel-left", 60398),
  layoutPanelCenter: l("layout-panel-center", 60399),
  layoutPanelJustify: l("layout-panel-justify", 60400),
  layoutPanelRight: l("layout-panel-right", 60401),
  layoutPanel: l("layout-panel", 60402),
  layoutSidebarLeft: l("layout-sidebar-left", 60403),
  layoutSidebarRight: l("layout-sidebar-right", 60404),
  layoutStatusbar: l("layout-statusbar", 60405),
  layoutMenubar: l("layout-menubar", 60406),
  layoutCentered: l("layout-centered", 60407),
  target: l("target", 60408),
  indent: l("indent", 60409),
  recordSmall: l("record-small", 60410),
  errorSmall: l("error-small", 60411),
  terminalDecorationError: l("terminal-decoration-error", 60411),
  arrowCircleDown: l("arrow-circle-down", 60412),
  arrowCircleLeft: l("arrow-circle-left", 60413),
  arrowCircleRight: l("arrow-circle-right", 60414),
  arrowCircleUp: l("arrow-circle-up", 60415),
  layoutSidebarRightOff: l("layout-sidebar-right-off", 60416),
  layoutPanelOff: l("layout-panel-off", 60417),
  layoutSidebarLeftOff: l("layout-sidebar-left-off", 60418),
  blank: l("blank", 60419),
  heartFilled: l("heart-filled", 60420),
  map: l("map", 60421),
  mapHorizontal: l("map-horizontal", 60421),
  foldHorizontal: l("fold-horizontal", 60421),
  mapFilled: l("map-filled", 60422),
  mapHorizontalFilled: l("map-horizontal-filled", 60422),
  foldHorizontalFilled: l("fold-horizontal-filled", 60422),
  circleSmall: l("circle-small", 60423),
  bellSlash: l("bell-slash", 60424),
  bellSlashDot: l("bell-slash-dot", 60425),
  commentUnresolved: l("comment-unresolved", 60426),
  gitPullRequestGoToChanges: l("git-pull-request-go-to-changes", 60427),
  gitPullRequestNewChanges: l("git-pull-request-new-changes", 60428),
  searchFuzzy: l("search-fuzzy", 60429),
  commentDraft: l("comment-draft", 60430),
  send: l("send", 60431),
  sparkle: l("sparkle", 60432),
  insert: l("insert", 60433),
  mic: l("mic", 60434),
  thumbsdownFilled: l("thumbsdown-filled", 60435),
  thumbsupFilled: l("thumbsup-filled", 60436),
  coffee: l("coffee", 60437),
  snake: l("snake", 60438),
  game: l("game", 60439),
  vr: l("vr", 60440),
  chip: l("chip", 60441),
  piano: l("piano", 60442),
  music: l("music", 60443),
  micFilled: l("mic-filled", 60444),
  repoFetch: l("repo-fetch", 60445),
  copilot: l("copilot", 60446),
  lightbulbSparkle: l("lightbulb-sparkle", 60447),
  robot: l("robot", 60448),
  sparkleFilled: l("sparkle-filled", 60449),
  diffSingle: l("diff-single", 60450),
  diffMultiple: l("diff-multiple", 60451),
  surroundWith: l("surround-with", 60452),
  share: l("share", 60453),
  gitStash: l("git-stash", 60454),
  gitStashApply: l("git-stash-apply", 60455),
  gitStashPop: l("git-stash-pop", 60456),
  vscode: l("vscode", 60457),
  vscodeInsiders: l("vscode-insiders", 60458),
  codeOss: l("code-oss", 60459),
  runCoverage: l("run-coverage", 60460),
  runAllCoverage: l("run-all-coverage", 60461),
  coverage: l("coverage", 60462),
  githubProject: l("github-project", 60463),
  mapVertical: l("map-vertical", 60464),
  foldVertical: l("fold-vertical", 60464),
  mapVerticalFilled: l("map-vertical-filled", 60465),
  foldVerticalFilled: l("fold-vertical-filled", 60465),
  goToSearch: l("go-to-search", 60466),
  percentage: l("percentage", 60467),
  sortPercentage: l("sort-percentage", 60467),
  attach: l("attach", 60468),
  goToEditingSession: l("go-to-editing-session", 60469),
  editSession: l("edit-session", 60470),
  codeReview: l("code-review", 60471),
  copilotWarning: l("copilot-warning", 60472),
  python: l("python", 60473),
  copilotLarge: l("copilot-large", 60474),
  copilotWarningLarge: l("copilot-warning-large", 60475),
  keyboardTab: l("keyboard-tab", 60476)
}, Nl = {
  dialogError: l("dialog-error", "error"),
  dialogWarning: l("dialog-warning", "warning"),
  dialogInfo: l("dialog-info", "info"),
  dialogClose: l("dialog-close", "close"),
  treeItemExpanded: l("tree-item-expanded", "chevron-down"),
  treeFilterOnTypeOn: l("tree-filter-on-type-on", "list-filter"),
  treeFilterOnTypeOff: l("tree-filter-on-type-off", "list-selection"),
  treeFilterClear: l("tree-filter-clear", "close"),
  treeItemLoading: l("tree-item-loading", "loading"),
  menuSelection: l("menu-selection", "check"),
  menuSubmenu: l("menu-submenu", "chevron-right"),
  menuBarMore: l("menubar-more", "more"),
  scrollbarButtonLeft: l("scrollbar-button-left", "triangle-left"),
  scrollbarButtonRight: l("scrollbar-button-right", "triangle-right"),
  scrollbarButtonUp: l("scrollbar-button-up", "triangle-up"),
  scrollbarButtonDown: l("scrollbar-button-down", "triangle-down"),
  toolBarMore: l("toolbar-more", "more"),
  quickInputBack: l("quick-input-back", "arrow-left"),
  dropDownButton: l("drop-down-button", 60084),
  symbolCustomColor: l("symbol-customcolor", 60252),
  exportIcon: l("export", 60332),
  workspaceUnspecified: l("workspace-unspecified", 60355),
  newLine: l("newline", 60394),
  thumbsDownFilled: l("thumbsdown-filled", 60435),
  thumbsUpFilled: l("thumbsup-filled", 60436),
  gitFetch: l("git-fetch", 60445),
  lightbulbSparkleAutofix: l("lightbulb-sparkle-autofix", 60447),
  debugBreakpointPending: l("debug-breakpoint-pending", 60377)
}, B = {
  ...pl,
  ...Nl
};
var Gi;
(function(e) {
  e[e.Null = 0] = "Null", e[e.PlainText = 1] = "PlainText";
})(Gi || (Gi = {}));
var $i;
(function(e) {
  e[e.NotSet = -1] = "NotSet", e[e.None = 0] = "None", e[e.Italic = 1] = "Italic", e[e.Bold = 2] = "Bold", e[e.Underline = 4] = "Underline", e[e.Strikethrough = 8] = "Strikethrough";
})($i || ($i = {}));
var Ln;
(function(e) {
  e[e.None = 0] = "None", e[e.DefaultForeground = 1] = "DefaultForeground", e[e.DefaultBackground = 2] = "DefaultBackground";
})(Ln || (Ln = {}));
var zi;
(function(e) {
  e[e.Other = 0] = "Other", e[e.Comment = 1] = "Comment", e[e.String = 2] = "String", e[e.RegEx = 3] = "RegEx";
})(zi || (zi = {}));
var ji;
(function(e) {
  e[e.LANGUAGEID_MASK = 255] = "LANGUAGEID_MASK", e[e.TOKEN_TYPE_MASK = 768] = "TOKEN_TYPE_MASK", e[e.BALANCED_BRACKETS_MASK = 1024] = "BALANCED_BRACKETS_MASK", e[e.FONT_STYLE_MASK = 30720] = "FONT_STYLE_MASK", e[e.FOREGROUND_MASK = 16744448] = "FOREGROUND_MASK", e[e.BACKGROUND_MASK = 4278190080] = "BACKGROUND_MASK", e[e.ITALIC_MASK = 2048] = "ITALIC_MASK", e[e.BOLD_MASK = 4096] = "BOLD_MASK", e[e.UNDERLINE_MASK = 8192] = "UNDERLINE_MASK", e[e.STRIKETHROUGH_MASK = 16384] = "STRIKETHROUGH_MASK", e[e.SEMANTIC_USE_ITALIC = 1] = "SEMANTIC_USE_ITALIC", e[e.SEMANTIC_USE_BOLD = 2] = "SEMANTIC_USE_BOLD", e[e.SEMANTIC_USE_UNDERLINE = 4] = "SEMANTIC_USE_UNDERLINE", e[e.SEMANTIC_USE_STRIKETHROUGH = 8] = "SEMANTIC_USE_STRIKETHROUGH", e[e.SEMANTIC_USE_FOREGROUND = 16] = "SEMANTIC_USE_FOREGROUND", e[e.SEMANTIC_USE_BACKGROUND = 32] = "SEMANTIC_USE_BACKGROUND", e[e.LANGUAGEID_OFFSET = 0] = "LANGUAGEID_OFFSET", e[e.TOKEN_TYPE_OFFSET = 8] = "TOKEN_TYPE_OFFSET", e[e.BALANCED_BRACKETS_OFFSET = 10] = "BALANCED_BRACKETS_OFFSET", e[e.FONT_STYLE_OFFSET = 11] = "FONT_STYLE_OFFSET", e[e.FOREGROUND_OFFSET = 15] = "FOREGROUND_OFFSET", e[e.BACKGROUND_OFFSET = 24] = "BACKGROUND_OFFSET";
})(ji || (ji = {}));
class gs {
  constructor() {
    this._tokenizationSupports = /* @__PURE__ */ new Map(), this._factories = /* @__PURE__ */ new Map(), this._onDidChange = new Ae(), this.onDidChange = this._onDidChange.event, this._colorMap = null;
  }
  handleChange(t) {
    this._onDidChange.fire({
      changedLanguages: t,
      changedColorMap: !1
    });
  }
  register(t, n) {
    return this._tokenizationSupports.set(t, n), this.handleChange([t]), $t(() => {
      this._tokenizationSupports.get(t) === n && (this._tokenizationSupports.delete(t), this.handleChange([t]));
    });
  }
  get(t) {
    return this._tokenizationSupports.get(t) || null;
  }
  registerFactory(t, n) {
    var r;
    (r = this._factories.get(t)) == null || r.dispose();
    const i = new El(this, t, n);
    return this._factories.set(t, i), $t(() => {
      const s = this._factories.get(t);
      !s || s !== i || (this._factories.delete(t), s.dispose());
    });
  }
  async getOrCreate(t) {
    const n = this.get(t);
    if (n)
      return n;
    const i = this._factories.get(t);
    return !i || i.isResolved ? null : (await i.resolve(), this.get(t));
  }
  isResolved(t) {
    if (this.get(t))
      return !0;
    const i = this._factories.get(t);
    return !!(!i || i.isResolved);
  }
  setColorMap(t) {
    this._colorMap = t, this._onDidChange.fire({
      changedLanguages: Array.from(this._tokenizationSupports.keys()),
      changedColorMap: !0
    });
  }
  getColorMap() {
    return this._colorMap;
  }
  getDefaultBackground() {
    return this._colorMap && this._colorMap.length > Ln.DefaultBackground ? this._colorMap[Ln.DefaultBackground] : null;
  }
}
class El extends Rt {
  get isResolved() {
    return this._isResolved;
  }
  constructor(t, n, i) {
    super(), this._registry = t, this._languageId = n, this._factory = i, this._isDisposed = !1, this._resolvePromise = null, this._isResolved = !1;
  }
  dispose() {
    this._isDisposed = !0, super.dispose();
  }
  async resolve() {
    return this._resolvePromise || (this._resolvePromise = this._create()), this._resolvePromise;
  }
  async _create() {
    const t = await this._factory.tokenizationSupport;
    this._isResolved = !0, t && !this._isDisposed && this._register(this._registry.register(this._languageId, t));
  }
}
class xl {
  constructor(t, n, i) {
    this.offset = t, this.type = n, this.language = i, this._tokenBrand = void 0;
  }
  toString() {
    return "(" + this.offset + ", " + this.type + ")";
  }
}
var Xi;
(function(e) {
  e[e.Increase = 0] = "Increase", e[e.Decrease = 1] = "Decrease";
})(Xi || (Xi = {}));
var T;
(function(e) {
  e[e.Method = 0] = "Method", e[e.Function = 1] = "Function", e[e.Constructor = 2] = "Constructor", e[e.Field = 3] = "Field", e[e.Variable = 4] = "Variable", e[e.Class = 5] = "Class", e[e.Struct = 6] = "Struct", e[e.Interface = 7] = "Interface", e[e.Module = 8] = "Module", e[e.Property = 9] = "Property", e[e.Event = 10] = "Event", e[e.Operator = 11] = "Operator", e[e.Unit = 12] = "Unit", e[e.Value = 13] = "Value", e[e.Constant = 14] = "Constant", e[e.Enum = 15] = "Enum", e[e.EnumMember = 16] = "EnumMember", e[e.Keyword = 17] = "Keyword", e[e.Text = 18] = "Text", e[e.Color = 19] = "Color", e[e.File = 20] = "File", e[e.Reference = 21] = "Reference", e[e.Customcolor = 22] = "Customcolor", e[e.Folder = 23] = "Folder", e[e.TypeParameter = 24] = "TypeParameter", e[e.User = 25] = "User", e[e.Issue = 26] = "Issue", e[e.Snippet = 27] = "Snippet";
})(T || (T = {}));
var Yi;
(function(e) {
  const t = /* @__PURE__ */ new Map();
  t.set(T.Method, B.symbolMethod), t.set(T.Function, B.symbolFunction), t.set(T.Constructor, B.symbolConstructor), t.set(T.Field, B.symbolField), t.set(T.Variable, B.symbolVariable), t.set(T.Class, B.symbolClass), t.set(T.Struct, B.symbolStruct), t.set(T.Interface, B.symbolInterface), t.set(T.Module, B.symbolModule), t.set(T.Property, B.symbolProperty), t.set(T.Event, B.symbolEvent), t.set(T.Operator, B.symbolOperator), t.set(T.Unit, B.symbolUnit), t.set(T.Value, B.symbolValue), t.set(T.Enum, B.symbolEnum), t.set(T.Constant, B.symbolConstant), t.set(T.Enum, B.symbolEnum), t.set(T.EnumMember, B.symbolEnumMember), t.set(T.Keyword, B.symbolKeyword), t.set(T.Snippet, B.symbolSnippet), t.set(T.Text, B.symbolText), t.set(T.Color, B.symbolColor), t.set(T.File, B.symbolFile), t.set(T.Reference, B.symbolReference), t.set(T.Customcolor, B.symbolCustomColor), t.set(T.Folder, B.symbolFolder), t.set(T.TypeParameter, B.symbolTypeParameter), t.set(T.User, B.account), t.set(T.Issue, B.issues);
  function n(s) {
    let a = t.get(s);
    return a || (console.info("No codicon found for CompletionItemKind " + s), a = B.symbolProperty), a;
  }
  e.toIcon = n;
  const i = /* @__PURE__ */ new Map();
  i.set("method", T.Method), i.set("function", T.Function), i.set("constructor", T.Constructor), i.set("field", T.Field), i.set("variable", T.Variable), i.set("class", T.Class), i.set("struct", T.Struct), i.set("interface", T.Interface), i.set("module", T.Module), i.set("property", T.Property), i.set("event", T.Event), i.set("operator", T.Operator), i.set("unit", T.Unit), i.set("value", T.Value), i.set("constant", T.Constant), i.set("enum", T.Enum), i.set("enum-member", T.EnumMember), i.set("enumMember", T.EnumMember), i.set("keyword", T.Keyword), i.set("snippet", T.Snippet), i.set("text", T.Text), i.set("color", T.Color), i.set("file", T.File), i.set("reference", T.Reference), i.set("customcolor", T.Customcolor), i.set("folder", T.Folder), i.set("type-parameter", T.TypeParameter), i.set("typeParameter", T.TypeParameter), i.set("account", T.User), i.set("issue", T.Issue);
  function r(s, a) {
    let u = i.get(s);
    return typeof u > "u" && !a && (u = T.Property), u;
  }
  e.fromString = r;
})(Yi || (Yi = {}));
var Qi;
(function(e) {
  e[e.Deprecated = 1] = "Deprecated";
})(Qi || (Qi = {}));
var Zi;
(function(e) {
  e[e.None = 0] = "None", e[e.KeepWhitespace = 1] = "KeepWhitespace", e[e.InsertAsSnippet = 4] = "InsertAsSnippet";
})(Zi || (Zi = {}));
var Ji;
(function(e) {
  e[e.Word = 0] = "Word", e[e.Line = 1] = "Line", e[e.Suggest = 2] = "Suggest";
})(Ji || (Ji = {}));
var Ki;
(function(e) {
  e[e.Invoke = 0] = "Invoke", e[e.TriggerCharacter = 1] = "TriggerCharacter", e[e.TriggerForIncompleteCompletions = 2] = "TriggerForIncompleteCompletions";
})(Ki || (Ki = {}));
var Ci;
(function(e) {
  e[e.Automatic = 0] = "Automatic", e[e.Explicit = 1] = "Explicit";
})(Ci || (Ci = {}));
var e1;
(function(e) {
  e[e.Invoke = 1] = "Invoke", e[e.Auto = 2] = "Auto";
})(e1 || (e1 = {}));
var t1;
(function(e) {
  e[e.Automatic = 0] = "Automatic", e[e.PasteAs = 1] = "PasteAs";
})(t1 || (t1 = {}));
var n1;
(function(e) {
  e[e.Invoke = 1] = "Invoke", e[e.TriggerCharacter = 2] = "TriggerCharacter", e[e.ContentChange = 3] = "ContentChange";
})(n1 || (n1 = {}));
var i1;
(function(e) {
  e[e.Text = 0] = "Text", e[e.Read = 1] = "Read", e[e.Write = 2] = "Write";
})(i1 || (i1 = {}));
var k;
(function(e) {
  e[e.File = 0] = "File", e[e.Module = 1] = "Module", e[e.Namespace = 2] = "Namespace", e[e.Package = 3] = "Package", e[e.Class = 4] = "Class", e[e.Method = 5] = "Method", e[e.Property = 6] = "Property", e[e.Field = 7] = "Field", e[e.Constructor = 8] = "Constructor", e[e.Enum = 9] = "Enum", e[e.Interface = 10] = "Interface", e[e.Function = 11] = "Function", e[e.Variable = 12] = "Variable", e[e.Constant = 13] = "Constant", e[e.String = 14] = "String", e[e.Number = 15] = "Number", e[e.Boolean = 16] = "Boolean", e[e.Array = 17] = "Array", e[e.Object = 18] = "Object", e[e.Key = 19] = "Key", e[e.Null = 20] = "Null", e[e.EnumMember = 21] = "EnumMember", e[e.Struct = 22] = "Struct", e[e.Event = 23] = "Event", e[e.Operator = 24] = "Operator", e[e.TypeParameter = 25] = "TypeParameter";
})(k || (k = {}));
k.Array + "", ee(758, "array"), k.Boolean + "", ee(759, "boolean"), k.Class + "", ee(760, "class"), k.Constant + "", ee(761, "constant"), k.Constructor + "", ee(762, "constructor"), k.Enum + "", ee(763, "enumeration"), k.EnumMember + "", ee(764, "enumeration member"), k.Event + "", ee(765, "event"), k.Field + "", ee(766, "field"), k.File + "", ee(767, "file"), k.Function + "", ee(768, "function"), k.Interface + "", ee(769, "interface"), k.Key + "", ee(770, "key"), k.Method + "", ee(771, "method"), k.Module + "", ee(772, "module"), k.Namespace + "", ee(773, "namespace"), k.Null + "", ee(774, "null"), k.Number + "", ee(775, "number"), k.Object + "", ee(776, "object"), k.Operator + "", ee(777, "operator"), k.Package + "", ee(778, "package"), k.Property + "", ee(779, "property"), k.String + "", ee(780, "string"), k.Struct + "", ee(781, "struct"), k.TypeParameter + "", ee(782, "type parameter"), k.Variable + "", ee(783, "variable");
var r1;
(function(e) {
  e[e.Deprecated = 1] = "Deprecated";
})(r1 || (r1 = {}));
var s1;
(function(e) {
  const t = /* @__PURE__ */ new Map();
  t.set(k.File, B.symbolFile), t.set(k.Module, B.symbolModule), t.set(k.Namespace, B.symbolNamespace), t.set(k.Package, B.symbolPackage), t.set(k.Class, B.symbolClass), t.set(k.Method, B.symbolMethod), t.set(k.Property, B.symbolProperty), t.set(k.Field, B.symbolField), t.set(k.Constructor, B.symbolConstructor), t.set(k.Enum, B.symbolEnum), t.set(k.Interface, B.symbolInterface), t.set(k.Function, B.symbolFunction), t.set(k.Variable, B.symbolVariable), t.set(k.Constant, B.symbolConstant), t.set(k.String, B.symbolString), t.set(k.Number, B.symbolNumber), t.set(k.Boolean, B.symbolBoolean), t.set(k.Array, B.symbolArray), t.set(k.Object, B.symbolObject), t.set(k.Key, B.symbolKey), t.set(k.Null, B.symbolNull), t.set(k.EnumMember, B.symbolEnumMember), t.set(k.Struct, B.symbolStruct), t.set(k.Event, B.symbolEvent), t.set(k.Operator, B.symbolOperator), t.set(k.TypeParameter, B.symbolTypeParameter);
  function n(s) {
    let a = t.get(s);
    return a || (console.info("No codicon found for SymbolKind " + s), a = B.symbolProperty), a;
  }
  e.toIcon = n;
  const i = /* @__PURE__ */ new Map();
  i.set(k.File, T.File), i.set(k.Module, T.Module), i.set(k.Namespace, T.Module), i.set(k.Package, T.Module), i.set(k.Class, T.Class), i.set(k.Method, T.Method), i.set(k.Property, T.Property), i.set(k.Field, T.Field), i.set(k.Constructor, T.Constructor), i.set(k.Enum, T.Enum), i.set(k.Interface, T.Interface), i.set(k.Function, T.Function), i.set(k.Variable, T.Variable), i.set(k.Constant, T.Constant), i.set(k.String, T.Text), i.set(k.Number, T.Value), i.set(k.Boolean, T.Value), i.set(k.Array, T.Value), i.set(k.Object, T.Value), i.set(k.Key, T.Keyword), i.set(k.Null, T.Value), i.set(k.EnumMember, T.EnumMember), i.set(k.Struct, T.Struct), i.set(k.Event, T.Event), i.set(k.Operator, T.Operator), i.set(k.TypeParameter, T.TypeParameter);
  function r(s) {
    let a = i.get(s);
    return a === void 0 && (console.info("No completion kind found for SymbolKind " + s), a = T.File), a;
  }
  e.toCompletionKind = r;
})(s1 || (s1 = {}));
const xe = class xe {
  static fromValue(t) {
    switch (t) {
      case "comment":
        return xe.Comment;
      case "imports":
        return xe.Imports;
      case "region":
        return xe.Region;
    }
    return new xe(t);
  }
  constructor(t) {
    this.value = t;
  }
};
xe.Comment = new xe("comment"), xe.Imports = new xe("imports"), xe.Region = new xe("region");
let a1 = xe;
var l1;
(function(e) {
  e[e.AIGenerated = 1] = "AIGenerated";
})(l1 || (l1 = {}));
var u1;
(function(e) {
  e[e.Invoke = 0] = "Invoke", e[e.Automatic = 1] = "Automatic";
})(u1 || (u1 = {}));
var o1;
(function(e) {
  function t(n) {
    return !n || typeof n != "object" ? !1 : typeof n.id == "string" && typeof n.title == "string";
  }
  e.is = t;
})(o1 || (o1 = {}));
var c1;
(function(e) {
  e[e.Collapsed = 0] = "Collapsed", e[e.Expanded = 1] = "Expanded";
})(c1 || (c1 = {}));
var h1;
(function(e) {
  e[e.Unresolved = 0] = "Unresolved", e[e.Resolved = 1] = "Resolved";
})(h1 || (h1 = {}));
var f1;
(function(e) {
  e[e.Current = 0] = "Current", e[e.Outdated = 1] = "Outdated";
})(f1 || (f1 = {}));
var m1;
(function(e) {
  e[e.Editing = 0] = "Editing", e[e.Preview = 1] = "Preview";
})(m1 || (m1 = {}));
var g1;
(function(e) {
  e[e.Published = 0] = "Published", e[e.Draft = 1] = "Draft";
})(g1 || (g1 = {}));
var _1;
(function(e) {
  e[e.Type = 1] = "Type", e[e.Parameter = 2] = "Parameter";
})(_1 || (_1 = {}));
new gs();
new gs();
var b1;
(function(e) {
  e[e.None = 0] = "None", e[e.Option = 1] = "Option", e[e.Default = 2] = "Default", e[e.Preferred = 3] = "Preferred";
})(b1 || (b1 = {}));
var d1;
(function(e) {
  e[e.Invoke = 0] = "Invoke", e[e.Automatic = 1] = "Automatic";
})(d1 || (d1 = {}));
var w1;
(function(e) {
  e[e.Unknown = 0] = "Unknown", e[e.Disabled = 1] = "Disabled", e[e.Enabled = 2] = "Enabled";
})(w1 || (w1 = {}));
var L1;
(function(e) {
  e[e.Invoke = 1] = "Invoke", e[e.Auto = 2] = "Auto";
})(L1 || (L1 = {}));
var p1;
(function(e) {
  e[e.None = 0] = "None", e[e.KeepWhitespace = 1] = "KeepWhitespace", e[e.InsertAsSnippet = 4] = "InsertAsSnippet";
})(p1 || (p1 = {}));
var N1;
(function(e) {
  e[e.Method = 0] = "Method", e[e.Function = 1] = "Function", e[e.Constructor = 2] = "Constructor", e[e.Field = 3] = "Field", e[e.Variable = 4] = "Variable", e[e.Class = 5] = "Class", e[e.Struct = 6] = "Struct", e[e.Interface = 7] = "Interface", e[e.Module = 8] = "Module", e[e.Property = 9] = "Property", e[e.Event = 10] = "Event", e[e.Operator = 11] = "Operator", e[e.Unit = 12] = "Unit", e[e.Value = 13] = "Value", e[e.Constant = 14] = "Constant", e[e.Enum = 15] = "Enum", e[e.EnumMember = 16] = "EnumMember", e[e.Keyword = 17] = "Keyword", e[e.Text = 18] = "Text", e[e.Color = 19] = "Color", e[e.File = 20] = "File", e[e.Reference = 21] = "Reference", e[e.Customcolor = 22] = "Customcolor", e[e.Folder = 23] = "Folder", e[e.TypeParameter = 24] = "TypeParameter", e[e.User = 25] = "User", e[e.Issue = 26] = "Issue", e[e.Snippet = 27] = "Snippet";
})(N1 || (N1 = {}));
var E1;
(function(e) {
  e[e.Deprecated = 1] = "Deprecated";
})(E1 || (E1 = {}));
var x1;
(function(e) {
  e[e.Invoke = 0] = "Invoke", e[e.TriggerCharacter = 1] = "TriggerCharacter", e[e.TriggerForIncompleteCompletions = 2] = "TriggerForIncompleteCompletions";
})(x1 || (x1 = {}));
var A1;
(function(e) {
  e[e.EXACT = 0] = "EXACT", e[e.ABOVE = 1] = "ABOVE", e[e.BELOW = 2] = "BELOW";
})(A1 || (A1 = {}));
var v1;
(function(e) {
  e[e.NotSet = 0] = "NotSet", e[e.ContentFlush = 1] = "ContentFlush", e[e.RecoverFromMarkers = 2] = "RecoverFromMarkers", e[e.Explicit = 3] = "Explicit", e[e.Paste = 4] = "Paste", e[e.Undo = 5] = "Undo", e[e.Redo = 6] = "Redo";
})(v1 || (v1 = {}));
var R1;
(function(e) {
  e[e.LF = 1] = "LF", e[e.CRLF = 2] = "CRLF";
})(R1 || (R1 = {}));
var T1;
(function(e) {
  e[e.Text = 0] = "Text", e[e.Read = 1] = "Read", e[e.Write = 2] = "Write";
})(T1 || (T1 = {}));
var U1;
(function(e) {
  e[e.None = 0] = "None", e[e.Keep = 1] = "Keep", e[e.Brackets = 2] = "Brackets", e[e.Advanced = 3] = "Advanced", e[e.Full = 4] = "Full";
})(U1 || (U1 = {}));
var M1;
(function(e) {
  e[e.acceptSuggestionOnCommitCharacter = 0] = "acceptSuggestionOnCommitCharacter", e[e.acceptSuggestionOnEnter = 1] = "acceptSuggestionOnEnter", e[e.accessibilitySupport = 2] = "accessibilitySupport", e[e.accessibilityPageSize = 3] = "accessibilityPageSize", e[e.ariaLabel = 4] = "ariaLabel", e[e.ariaRequired = 5] = "ariaRequired", e[e.autoClosingBrackets = 6] = "autoClosingBrackets", e[e.autoClosingComments = 7] = "autoClosingComments", e[e.screenReaderAnnounceInlineSuggestion = 8] = "screenReaderAnnounceInlineSuggestion", e[e.autoClosingDelete = 9] = "autoClosingDelete", e[e.autoClosingOvertype = 10] = "autoClosingOvertype", e[e.autoClosingQuotes = 11] = "autoClosingQuotes", e[e.autoIndent = 12] = "autoIndent", e[e.automaticLayout = 13] = "automaticLayout", e[e.autoSurround = 14] = "autoSurround", e[e.bracketPairColorization = 15] = "bracketPairColorization", e[e.guides = 16] = "guides", e[e.codeLens = 17] = "codeLens", e[e.codeLensFontFamily = 18] = "codeLensFontFamily", e[e.codeLensFontSize = 19] = "codeLensFontSize", e[e.colorDecorators = 20] = "colorDecorators", e[e.colorDecoratorsLimit = 21] = "colorDecoratorsLimit", e[e.columnSelection = 22] = "columnSelection", e[e.comments = 23] = "comments", e[e.contextmenu = 24] = "contextmenu", e[e.copyWithSyntaxHighlighting = 25] = "copyWithSyntaxHighlighting", e[e.cursorBlinking = 26] = "cursorBlinking", e[e.cursorSmoothCaretAnimation = 27] = "cursorSmoothCaretAnimation", e[e.cursorStyle = 28] = "cursorStyle", e[e.cursorSurroundingLines = 29] = "cursorSurroundingLines", e[e.cursorSurroundingLinesStyle = 30] = "cursorSurroundingLinesStyle", e[e.cursorWidth = 31] = "cursorWidth", e[e.disableLayerHinting = 32] = "disableLayerHinting", e[e.disableMonospaceOptimizations = 33] = "disableMonospaceOptimizations", e[e.domReadOnly = 34] = "domReadOnly", e[e.dragAndDrop = 35] = "dragAndDrop", e[e.dropIntoEditor = 36] = "dropIntoEditor", e[e.experimentalEditContextEnabled = 37] = "experimentalEditContextEnabled", e[e.emptySelectionClipboard = 38] = "emptySelectionClipboard", e[e.experimentalGpuAcceleration = 39] = "experimentalGpuAcceleration", e[e.experimentalWhitespaceRendering = 40] = "experimentalWhitespaceRendering", e[e.extraEditorClassName = 41] = "extraEditorClassName", e[e.fastScrollSensitivity = 42] = "fastScrollSensitivity", e[e.find = 43] = "find", e[e.fixedOverflowWidgets = 44] = "fixedOverflowWidgets", e[e.folding = 45] = "folding", e[e.foldingStrategy = 46] = "foldingStrategy", e[e.foldingHighlight = 47] = "foldingHighlight", e[e.foldingImportsByDefault = 48] = "foldingImportsByDefault", e[e.foldingMaximumRegions = 49] = "foldingMaximumRegions", e[e.unfoldOnClickAfterEndOfLine = 50] = "unfoldOnClickAfterEndOfLine", e[e.fontFamily = 51] = "fontFamily", e[e.fontInfo = 52] = "fontInfo", e[e.fontLigatures = 53] = "fontLigatures", e[e.fontSize = 54] = "fontSize", e[e.fontWeight = 55] = "fontWeight", e[e.fontVariations = 56] = "fontVariations", e[e.formatOnPaste = 57] = "formatOnPaste", e[e.formatOnType = 58] = "formatOnType", e[e.glyphMargin = 59] = "glyphMargin", e[e.gotoLocation = 60] = "gotoLocation", e[e.hideCursorInOverviewRuler = 61] = "hideCursorInOverviewRuler", e[e.hover = 62] = "hover", e[e.inDiffEditor = 63] = "inDiffEditor", e[e.inlineSuggest = 64] = "inlineSuggest", e[e.letterSpacing = 65] = "letterSpacing", e[e.lightbulb = 66] = "lightbulb", e[e.lineDecorationsWidth = 67] = "lineDecorationsWidth", e[e.lineHeight = 68] = "lineHeight", e[e.lineNumbers = 69] = "lineNumbers", e[e.lineNumbersMinChars = 70] = "lineNumbersMinChars", e[e.linkedEditing = 71] = "linkedEditing", e[e.links = 72] = "links", e[e.matchBrackets = 73] = "matchBrackets", e[e.minimap = 74] = "minimap", e[e.mouseStyle = 75] = "mouseStyle", e[e.mouseWheelScrollSensitivity = 76] = "mouseWheelScrollSensitivity", e[e.mouseWheelZoom = 77] = "mouseWheelZoom", e[e.multiCursorMergeOverlapping = 78] = "multiCursorMergeOverlapping", e[e.multiCursorModifier = 79] = "multiCursorModifier", e[e.multiCursorPaste = 80] = "multiCursorPaste", e[e.multiCursorLimit = 81] = "multiCursorLimit", e[e.occurrencesHighlight = 82] = "occurrencesHighlight", e[e.occurrencesHighlightDelay = 83] = "occurrencesHighlightDelay", e[e.overtypeCursorStyle = 84] = "overtypeCursorStyle", e[e.overtypeOnPaste = 85] = "overtypeOnPaste", e[e.overviewRulerBorder = 86] = "overviewRulerBorder", e[e.overviewRulerLanes = 87] = "overviewRulerLanes", e[e.padding = 88] = "padding", e[e.pasteAs = 89] = "pasteAs", e[e.parameterHints = 90] = "parameterHints", e[e.peekWidgetDefaultFocus = 91] = "peekWidgetDefaultFocus", e[e.placeholder = 92] = "placeholder", e[e.definitionLinkOpensInPeek = 93] = "definitionLinkOpensInPeek", e[e.quickSuggestions = 94] = "quickSuggestions", e[e.quickSuggestionsDelay = 95] = "quickSuggestionsDelay", e[e.readOnly = 96] = "readOnly", e[e.readOnlyMessage = 97] = "readOnlyMessage", e[e.renameOnType = 98] = "renameOnType", e[e.renderControlCharacters = 99] = "renderControlCharacters", e[e.renderFinalNewline = 100] = "renderFinalNewline", e[e.renderLineHighlight = 101] = "renderLineHighlight", e[e.renderLineHighlightOnlyWhenFocus = 102] = "renderLineHighlightOnlyWhenFocus", e[e.renderValidationDecorations = 103] = "renderValidationDecorations", e[e.renderWhitespace = 104] = "renderWhitespace", e[e.revealHorizontalRightPadding = 105] = "revealHorizontalRightPadding", e[e.roundedSelection = 106] = "roundedSelection", e[e.rulers = 107] = "rulers", e[e.scrollbar = 108] = "scrollbar", e[e.scrollBeyondLastColumn = 109] = "scrollBeyondLastColumn", e[e.scrollBeyondLastLine = 110] = "scrollBeyondLastLine", e[e.scrollPredominantAxis = 111] = "scrollPredominantAxis", e[e.selectionClipboard = 112] = "selectionClipboard", e[e.selectionHighlight = 113] = "selectionHighlight", e[e.selectOnLineNumbers = 114] = "selectOnLineNumbers", e[e.showFoldingControls = 115] = "showFoldingControls", e[e.showUnused = 116] = "showUnused", e[e.snippetSuggestions = 117] = "snippetSuggestions", e[e.smartSelect = 118] = "smartSelect", e[e.smoothScrolling = 119] = "smoothScrolling", e[e.stickyScroll = 120] = "stickyScroll", e[e.stickyTabStops = 121] = "stickyTabStops", e[e.stopRenderingLineAfter = 122] = "stopRenderingLineAfter", e[e.suggest = 123] = "suggest", e[e.suggestFontSize = 124] = "suggestFontSize", e[e.suggestLineHeight = 125] = "suggestLineHeight", e[e.suggestOnTriggerCharacters = 126] = "suggestOnTriggerCharacters", e[e.suggestSelection = 127] = "suggestSelection", e[e.tabCompletion = 128] = "tabCompletion", e[e.tabIndex = 129] = "tabIndex", e[e.unicodeHighlighting = 130] = "unicodeHighlighting", e[e.unusualLineTerminators = 131] = "unusualLineTerminators", e[e.useShadowDOM = 132] = "useShadowDOM", e[e.useTabStops = 133] = "useTabStops", e[e.wordBreak = 134] = "wordBreak", e[e.wordSegmenterLocales = 135] = "wordSegmenterLocales", e[e.wordSeparators = 136] = "wordSeparators", e[e.wordWrap = 137] = "wordWrap", e[e.wordWrapBreakAfterCharacters = 138] = "wordWrapBreakAfterCharacters", e[e.wordWrapBreakBeforeCharacters = 139] = "wordWrapBreakBeforeCharacters", e[e.wordWrapColumn = 140] = "wordWrapColumn", e[e.wordWrapOverride1 = 141] = "wordWrapOverride1", e[e.wordWrapOverride2 = 142] = "wordWrapOverride2", e[e.wrappingIndent = 143] = "wrappingIndent", e[e.wrappingStrategy = 144] = "wrappingStrategy", e[e.showDeprecated = 145] = "showDeprecated", e[e.inlayHints = 146] = "inlayHints", e[e.effectiveCursorStyle = 147] = "effectiveCursorStyle", e[e.editorClassName = 148] = "editorClassName", e[e.pixelRatio = 149] = "pixelRatio", e[e.tabFocusMode = 150] = "tabFocusMode", e[e.layoutInfo = 151] = "layoutInfo", e[e.wrappingInfo = 152] = "wrappingInfo", e[e.defaultColorDecorators = 153] = "defaultColorDecorators", e[e.colorDecoratorsActivatedOn = 154] = "colorDecoratorsActivatedOn", e[e.inlineCompletionsAccessibilityVerbose = 155] = "inlineCompletionsAccessibilityVerbose";
})(M1 || (M1 = {}));
var D1;
(function(e) {
  e[e.TextDefined = 0] = "TextDefined", e[e.LF = 1] = "LF", e[e.CRLF = 2] = "CRLF";
})(D1 || (D1 = {}));
var k1;
(function(e) {
  e[e.LF = 0] = "LF", e[e.CRLF = 1] = "CRLF";
})(k1 || (k1 = {}));
var F1;
(function(e) {
  e[e.Left = 1] = "Left", e[e.Center = 2] = "Center", e[e.Right = 3] = "Right";
})(F1 || (F1 = {}));
var I1;
(function(e) {
  e[e.Increase = 0] = "Increase", e[e.Decrease = 1] = "Decrease";
})(I1 || (I1 = {}));
var S1;
(function(e) {
  e[e.None = 0] = "None", e[e.Indent = 1] = "Indent", e[e.IndentOutdent = 2] = "IndentOutdent", e[e.Outdent = 3] = "Outdent";
})(S1 || (S1 = {}));
var P1;
(function(e) {
  e[e.Both = 0] = "Both", e[e.Right = 1] = "Right", e[e.Left = 2] = "Left", e[e.None = 3] = "None";
})(P1 || (P1 = {}));
var y1;
(function(e) {
  e[e.Type = 1] = "Type", e[e.Parameter = 2] = "Parameter";
})(y1 || (y1 = {}));
var B1;
(function(e) {
  e[e.Automatic = 0] = "Automatic", e[e.Explicit = 1] = "Explicit";
})(B1 || (B1 = {}));
var O1;
(function(e) {
  e[e.Invoke = 0] = "Invoke", e[e.Automatic = 1] = "Automatic";
})(O1 || (O1 = {}));
var Cn;
(function(e) {
  e[e.DependsOnKbLayout = -1] = "DependsOnKbLayout", e[e.Unknown = 0] = "Unknown", e[e.Backspace = 1] = "Backspace", e[e.Tab = 2] = "Tab", e[e.Enter = 3] = "Enter", e[e.Shift = 4] = "Shift", e[e.Ctrl = 5] = "Ctrl", e[e.Alt = 6] = "Alt", e[e.PauseBreak = 7] = "PauseBreak", e[e.CapsLock = 8] = "CapsLock", e[e.Escape = 9] = "Escape", e[e.Space = 10] = "Space", e[e.PageUp = 11] = "PageUp", e[e.PageDown = 12] = "PageDown", e[e.End = 13] = "End", e[e.Home = 14] = "Home", e[e.LeftArrow = 15] = "LeftArrow", e[e.UpArrow = 16] = "UpArrow", e[e.RightArrow = 17] = "RightArrow", e[e.DownArrow = 18] = "DownArrow", e[e.Insert = 19] = "Insert", e[e.Delete = 20] = "Delete", e[e.Digit0 = 21] = "Digit0", e[e.Digit1 = 22] = "Digit1", e[e.Digit2 = 23] = "Digit2", e[e.Digit3 = 24] = "Digit3", e[e.Digit4 = 25] = "Digit4", e[e.Digit5 = 26] = "Digit5", e[e.Digit6 = 27] = "Digit6", e[e.Digit7 = 28] = "Digit7", e[e.Digit8 = 29] = "Digit8", e[e.Digit9 = 30] = "Digit9", e[e.KeyA = 31] = "KeyA", e[e.KeyB = 32] = "KeyB", e[e.KeyC = 33] = "KeyC", e[e.KeyD = 34] = "KeyD", e[e.KeyE = 35] = "KeyE", e[e.KeyF = 36] = "KeyF", e[e.KeyG = 37] = "KeyG", e[e.KeyH = 38] = "KeyH", e[e.KeyI = 39] = "KeyI", e[e.KeyJ = 40] = "KeyJ", e[e.KeyK = 41] = "KeyK", e[e.KeyL = 42] = "KeyL", e[e.KeyM = 43] = "KeyM", e[e.KeyN = 44] = "KeyN", e[e.KeyO = 45] = "KeyO", e[e.KeyP = 46] = "KeyP", e[e.KeyQ = 47] = "KeyQ", e[e.KeyR = 48] = "KeyR", e[e.KeyS = 49] = "KeyS", e[e.KeyT = 50] = "KeyT", e[e.KeyU = 51] = "KeyU", e[e.KeyV = 52] = "KeyV", e[e.KeyW = 53] = "KeyW", e[e.KeyX = 54] = "KeyX", e[e.KeyY = 55] = "KeyY", e[e.KeyZ = 56] = "KeyZ", e[e.Meta = 57] = "Meta", e[e.ContextMenu = 58] = "ContextMenu", e[e.F1 = 59] = "F1", e[e.F2 = 60] = "F2", e[e.F3 = 61] = "F3", e[e.F4 = 62] = "F4", e[e.F5 = 63] = "F5", e[e.F6 = 64] = "F6", e[e.F7 = 65] = "F7", e[e.F8 = 66] = "F8", e[e.F9 = 67] = "F9", e[e.F10 = 68] = "F10", e[e.F11 = 69] = "F11", e[e.F12 = 70] = "F12", e[e.F13 = 71] = "F13", e[e.F14 = 72] = "F14", e[e.F15 = 73] = "F15", e[e.F16 = 74] = "F16", e[e.F17 = 75] = "F17", e[e.F18 = 76] = "F18", e[e.F19 = 77] = "F19", e[e.F20 = 78] = "F20", e[e.F21 = 79] = "F21", e[e.F22 = 80] = "F22", e[e.F23 = 81] = "F23", e[e.F24 = 82] = "F24", e[e.NumLock = 83] = "NumLock", e[e.ScrollLock = 84] = "ScrollLock", e[e.Semicolon = 85] = "Semicolon", e[e.Equal = 86] = "Equal", e[e.Comma = 87] = "Comma", e[e.Minus = 88] = "Minus", e[e.Period = 89] = "Period", e[e.Slash = 90] = "Slash", e[e.Backquote = 91] = "Backquote", e[e.BracketLeft = 92] = "BracketLeft", e[e.Backslash = 93] = "Backslash", e[e.BracketRight = 94] = "BracketRight", e[e.Quote = 95] = "Quote", e[e.OEM_8 = 96] = "OEM_8", e[e.IntlBackslash = 97] = "IntlBackslash", e[e.Numpad0 = 98] = "Numpad0", e[e.Numpad1 = 99] = "Numpad1", e[e.Numpad2 = 100] = "Numpad2", e[e.Numpad3 = 101] = "Numpad3", e[e.Numpad4 = 102] = "Numpad4", e[e.Numpad5 = 103] = "Numpad5", e[e.Numpad6 = 104] = "Numpad6", e[e.Numpad7 = 105] = "Numpad7", e[e.Numpad8 = 106] = "Numpad8", e[e.Numpad9 = 107] = "Numpad9", e[e.NumpadMultiply = 108] = "NumpadMultiply", e[e.NumpadAdd = 109] = "NumpadAdd", e[e.NUMPAD_SEPARATOR = 110] = "NUMPAD_SEPARATOR", e[e.NumpadSubtract = 111] = "NumpadSubtract", e[e.NumpadDecimal = 112] = "NumpadDecimal", e[e.NumpadDivide = 113] = "NumpadDivide", e[e.KEY_IN_COMPOSITION = 114] = "KEY_IN_COMPOSITION", e[e.ABNT_C1 = 115] = "ABNT_C1", e[e.ABNT_C2 = 116] = "ABNT_C2", e[e.AudioVolumeMute = 117] = "AudioVolumeMute", e[e.AudioVolumeUp = 118] = "AudioVolumeUp", e[e.AudioVolumeDown = 119] = "AudioVolumeDown", e[e.BrowserSearch = 120] = "BrowserSearch", e[e.BrowserHome = 121] = "BrowserHome", e[e.BrowserBack = 122] = "BrowserBack", e[e.BrowserForward = 123] = "BrowserForward", e[e.MediaTrackNext = 124] = "MediaTrackNext", e[e.MediaTrackPrevious = 125] = "MediaTrackPrevious", e[e.MediaStop = 126] = "MediaStop", e[e.MediaPlayPause = 127] = "MediaPlayPause", e[e.LaunchMediaPlayer = 128] = "LaunchMediaPlayer", e[e.LaunchMail = 129] = "LaunchMail", e[e.LaunchApp2 = 130] = "LaunchApp2", e[e.Clear = 131] = "Clear", e[e.MAX_VALUE = 132] = "MAX_VALUE";
})(Cn || (Cn = {}));
var ei;
(function(e) {
  e[e.Hint = 1] = "Hint", e[e.Info = 2] = "Info", e[e.Warning = 4] = "Warning", e[e.Error = 8] = "Error";
})(ei || (ei = {}));
var ti;
(function(e) {
  e[e.Unnecessary = 1] = "Unnecessary", e[e.Deprecated = 2] = "Deprecated";
})(ti || (ti = {}));
var V1;
(function(e) {
  e[e.Inline = 1] = "Inline", e[e.Gutter = 2] = "Gutter";
})(V1 || (V1 = {}));
var q1;
(function(e) {
  e[e.Normal = 1] = "Normal", e[e.Underlined = 2] = "Underlined";
})(q1 || (q1 = {}));
var H1;
(function(e) {
  e[e.UNKNOWN = 0] = "UNKNOWN", e[e.TEXTAREA = 1] = "TEXTAREA", e[e.GUTTER_GLYPH_MARGIN = 2] = "GUTTER_GLYPH_MARGIN", e[e.GUTTER_LINE_NUMBERS = 3] = "GUTTER_LINE_NUMBERS", e[e.GUTTER_LINE_DECORATIONS = 4] = "GUTTER_LINE_DECORATIONS", e[e.GUTTER_VIEW_ZONE = 5] = "GUTTER_VIEW_ZONE", e[e.CONTENT_TEXT = 6] = "CONTENT_TEXT", e[e.CONTENT_EMPTY = 7] = "CONTENT_EMPTY", e[e.CONTENT_VIEW_ZONE = 8] = "CONTENT_VIEW_ZONE", e[e.CONTENT_WIDGET = 9] = "CONTENT_WIDGET", e[e.OVERVIEW_RULER = 10] = "OVERVIEW_RULER", e[e.SCROLLBAR = 11] = "SCROLLBAR", e[e.OVERLAY_WIDGET = 12] = "OVERLAY_WIDGET", e[e.OUTSIDE_EDITOR = 13] = "OUTSIDE_EDITOR";
})(H1 || (H1 = {}));
var W1;
(function(e) {
  e[e.AIGenerated = 1] = "AIGenerated";
})(W1 || (W1 = {}));
var G1;
(function(e) {
  e[e.Invoke = 0] = "Invoke", e[e.Automatic = 1] = "Automatic";
})(G1 || (G1 = {}));
var $1;
(function(e) {
  e[e.TOP_RIGHT_CORNER = 0] = "TOP_RIGHT_CORNER", e[e.BOTTOM_RIGHT_CORNER = 1] = "BOTTOM_RIGHT_CORNER", e[e.TOP_CENTER = 2] = "TOP_CENTER";
})($1 || ($1 = {}));
var z1;
(function(e) {
  e[e.Left = 1] = "Left", e[e.Center = 2] = "Center", e[e.Right = 4] = "Right", e[e.Full = 7] = "Full";
})(z1 || (z1 = {}));
var j1;
(function(e) {
  e[e.Word = 0] = "Word", e[e.Line = 1] = "Line", e[e.Suggest = 2] = "Suggest";
})(j1 || (j1 = {}));
var X1;
(function(e) {
  e[e.Left = 0] = "Left", e[e.Right = 1] = "Right", e[e.None = 2] = "None", e[e.LeftOfInjectedText = 3] = "LeftOfInjectedText", e[e.RightOfInjectedText = 4] = "RightOfInjectedText";
})(X1 || (X1 = {}));
var Y1;
(function(e) {
  e[e.Off = 0] = "Off", e[e.On = 1] = "On", e[e.Relative = 2] = "Relative", e[e.Interval = 3] = "Interval", e[e.Custom = 4] = "Custom";
})(Y1 || (Y1 = {}));
var Q1;
(function(e) {
  e[e.None = 0] = "None", e[e.Text = 1] = "Text", e[e.Blocks = 2] = "Blocks";
})(Q1 || (Q1 = {}));
var Z1;
(function(e) {
  e[e.Smooth = 0] = "Smooth", e[e.Immediate = 1] = "Immediate";
})(Z1 || (Z1 = {}));
var J1;
(function(e) {
  e[e.Auto = 1] = "Auto", e[e.Hidden = 2] = "Hidden", e[e.Visible = 3] = "Visible";
})(J1 || (J1 = {}));
var ni;
(function(e) {
  e[e.LTR = 0] = "LTR", e[e.RTL = 1] = "RTL";
})(ni || (ni = {}));
var K1;
(function(e) {
  e.Off = "off", e.OnCode = "onCode", e.On = "on";
})(K1 || (K1 = {}));
var C1;
(function(e) {
  e[e.Invoke = 1] = "Invoke", e[e.TriggerCharacter = 2] = "TriggerCharacter", e[e.ContentChange = 3] = "ContentChange";
})(C1 || (C1 = {}));
var er;
(function(e) {
  e[e.File = 0] = "File", e[e.Module = 1] = "Module", e[e.Namespace = 2] = "Namespace", e[e.Package = 3] = "Package", e[e.Class = 4] = "Class", e[e.Method = 5] = "Method", e[e.Property = 6] = "Property", e[e.Field = 7] = "Field", e[e.Constructor = 8] = "Constructor", e[e.Enum = 9] = "Enum", e[e.Interface = 10] = "Interface", e[e.Function = 11] = "Function", e[e.Variable = 12] = "Variable", e[e.Constant = 13] = "Constant", e[e.String = 14] = "String", e[e.Number = 15] = "Number", e[e.Boolean = 16] = "Boolean", e[e.Array = 17] = "Array", e[e.Object = 18] = "Object", e[e.Key = 19] = "Key", e[e.Null = 20] = "Null", e[e.EnumMember = 21] = "EnumMember", e[e.Struct = 22] = "Struct", e[e.Event = 23] = "Event", e[e.Operator = 24] = "Operator", e[e.TypeParameter = 25] = "TypeParameter";
})(er || (er = {}));
var tr;
(function(e) {
  e[e.Deprecated = 1] = "Deprecated";
})(tr || (tr = {}));
var nr;
(function(e) {
  e[e.Hidden = 0] = "Hidden", e[e.Blink = 1] = "Blink", e[e.Smooth = 2] = "Smooth", e[e.Phase = 3] = "Phase", e[e.Expand = 4] = "Expand", e[e.Solid = 5] = "Solid";
})(nr || (nr = {}));
var ir;
(function(e) {
  e[e.Line = 1] = "Line", e[e.Block = 2] = "Block", e[e.Underline = 3] = "Underline", e[e.LineThin = 4] = "LineThin", e[e.BlockOutline = 5] = "BlockOutline", e[e.UnderlineThin = 6] = "UnderlineThin";
})(ir || (ir = {}));
var rr;
(function(e) {
  e[e.AlwaysGrowsWhenTypingAtEdges = 0] = "AlwaysGrowsWhenTypingAtEdges", e[e.NeverGrowsWhenTypingAtEdges = 1] = "NeverGrowsWhenTypingAtEdges", e[e.GrowsOnlyWhenTypingBefore = 2] = "GrowsOnlyWhenTypingBefore", e[e.GrowsOnlyWhenTypingAfter = 3] = "GrowsOnlyWhenTypingAfter";
})(rr || (rr = {}));
var sr;
(function(e) {
  e[e.None = 0] = "None", e[e.Same = 1] = "Same", e[e.Indent = 2] = "Indent", e[e.DeepIndent = 3] = "DeepIndent";
})(sr || (sr = {}));
const Lt = class Lt {
  static chord(t, n) {
    return Za(t, n);
  }
};
Lt.CtrlCmd = gt.CtrlCmd, Lt.Shift = gt.Shift, Lt.Alt = gt.Alt, Lt.WinCtrl = gt.WinCtrl;
let ii = Lt;
function Al() {
  return {
    editor: void 0,
    languages: void 0,
    CancellationTokenSource: wa,
    Emitter: Ae,
    KeyCode: Cn,
    KeyMod: ii,
    Position: W,
    Range: F,
    Selection: Ne,
    SelectionDirection: ni,
    MarkerSeverity: ei,
    MarkerTag: ti,
    Uri: oe,
    Token: xl
  };
}
const Ht = class Ht {
  static getChannel(t) {
    return t.getChannel(Ht.CHANNEL_NAME);
  }
  static setChannel(t, n) {
    t.setChannel(Ht.CHANNEL_NAME, n);
  }
};
Ht.CHANNEL_NAME = "editorWorkerHost";
let ri = Ht;
var Ut;
(function(e) {
  e[e.Regular = 0] = "Regular", e[e.Whitespace = 1] = "Whitespace", e[e.WordSeparator = 2] = "WordSeparator";
})(Ut || (Ut = {}));
new zs(10);
function vl(e) {
  let t = [];
  for (; Object.prototype !== e; )
    t = t.concat(Object.getOwnPropertyNames(e)), e = Object.getPrototypeOf(e);
  return t;
}
function Rl(e) {
  const t = [];
  for (const n of vl(e))
    typeof e[n] == "function" && t.push(n);
  return t;
}
function Tl(e, t) {
  const n = (r) => function() {
    const s = Array.prototype.slice.call(arguments, 0);
    return t(r, s);
  }, i = {};
  for (const r of e)
    i[r] = n(r);
  return i;
}
var ar;
(function(e) {
  e[e.Left = 1] = "Left", e[e.Center = 2] = "Center", e[e.Right = 4] = "Right", e[e.Full = 7] = "Full";
})(ar || (ar = {}));
var lr;
(function(e) {
  e[e.Left = 1] = "Left", e[e.Center = 2] = "Center", e[e.Right = 3] = "Right";
})(lr || (lr = {}));
var ur;
(function(e) {
  e[e.Inline = 1] = "Inline", e[e.Gutter = 2] = "Gutter";
})(ur || (ur = {}));
var or;
(function(e) {
  e[e.Normal = 1] = "Normal", e[e.Underlined = 2] = "Underlined";
})(or || (or = {}));
var cr;
(function(e) {
  e[e.Both = 0] = "Both", e[e.Right = 1] = "Right", e[e.Left = 2] = "Left", e[e.None = 3] = "None";
})(cr || (cr = {}));
var hr;
(function(e) {
  e[e.TextDefined = 0] = "TextDefined", e[e.LF = 1] = "LF", e[e.CRLF = 2] = "CRLF";
})(hr || (hr = {}));
var fr;
(function(e) {
  e[e.LF = 1] = "LF", e[e.CRLF = 2] = "CRLF";
})(fr || (fr = {}));
var mr;
(function(e) {
  e[e.LF = 0] = "LF", e[e.CRLF = 1] = "CRLF";
})(mr || (mr = {}));
var gr;
(function(e) {
  e[e.AlwaysGrowsWhenTypingAtEdges = 0] = "AlwaysGrowsWhenTypingAtEdges", e[e.NeverGrowsWhenTypingAtEdges = 1] = "NeverGrowsWhenTypingAtEdges", e[e.GrowsOnlyWhenTypingBefore = 2] = "GrowsOnlyWhenTypingBefore", e[e.GrowsOnlyWhenTypingAfter = 3] = "GrowsOnlyWhenTypingAfter";
})(gr || (gr = {}));
var _r;
(function(e) {
  e[e.Left = 0] = "Left", e[e.Right = 1] = "Right", e[e.None = 2] = "None", e[e.LeftOfInjectedText = 3] = "LeftOfInjectedText", e[e.RightOfInjectedText = 4] = "RightOfInjectedText";
})(_r || (_r = {}));
var br;
(function(e) {
  e[e.FIRST_LINE_DETECTION_LENGTH_LIMIT = 1e3] = "FIRST_LINE_DETECTION_LENGTH_LIMIT";
})(br || (br = {}));
function Ul(e, t, n, i, r) {
  if (i === 0)
    return !0;
  const s = t.charCodeAt(i - 1);
  if (e.get(s) !== Ut.Regular || s === L.CarriageReturn || s === L.LineFeed)
    return !0;
  if (r > 0) {
    const a = t.charCodeAt(i);
    if (e.get(a) !== Ut.Regular)
      return !0;
  }
  return !1;
}
function Ml(e, t, n, i, r) {
  if (i + r === n)
    return !0;
  const s = t.charCodeAt(i + r);
  if (e.get(s) !== Ut.Regular || s === L.CarriageReturn || s === L.LineFeed)
    return !0;
  if (r > 0) {
    const a = t.charCodeAt(i + r - 1);
    if (e.get(a) !== Ut.Regular)
      return !0;
  }
  return !1;
}
function Dl(e, t, n, i, r) {
  return Ul(e, t, n, i, r) && Ml(e, t, n, i, r);
}
class kl {
  constructor(t, n) {
    this._wordSeparators = t, this._searchRegex = n, this._prevMatchStartIndex = -1, this._prevMatchLength = 0;
  }
  reset(t) {
    this._searchRegex.lastIndex = t, this._prevMatchStartIndex = -1, this._prevMatchLength = 0;
  }
  next(t) {
    const n = t.length;
    let i;
    do {
      if (this._prevMatchStartIndex + this._prevMatchLength === n || (i = this._searchRegex.exec(t), !i))
        return null;
      const r = i.index, s = i[0].length;
      if (r === this._prevMatchStartIndex && s === this._prevMatchLength) {
        if (s === 0) {
          Ma(t, n, this._searchRegex.lastIndex) > 65535 ? this._searchRegex.lastIndex += 2 : this._searchRegex.lastIndex += 1;
          continue;
        }
        return null;
      }
      if (this._prevMatchStartIndex = r, this._prevMatchLength = s, !this._wordSeparators || Dl(this._wordSeparators, t, n, r, s))
        return i;
    } while (i);
    return null;
  }
}
const Fl = "`~!@#$%^&*()-=+[{]}\\|;:'\",.<>/?";
function Il(e = "") {
  let t = "(-?\\d*\\.\\d\\w*)|([^";
  for (const n of Fl)
    e.indexOf(n) >= 0 || (t += "\\" + n);
  return t += "\\s]+)", new RegExp(t, "g");
}
const _s = Il();
function bs(e) {
  let t = _s;
  if (e && e instanceof RegExp)
    if (e.global)
      t = e;
    else {
      let n = "g";
      e.ignoreCase && (n += "i"), e.multiline && (n += "m"), e.unicode && (n += "u"), t = new RegExp(e.source, n);
    }
  return t.lastIndex = 0, t;
}
const ds = new Js();
ds.unshift({
  maxLen: 1e3,
  windowSize: 15,
  timeBudget: 150
});
function bi(e, t, n, i, r) {
  if (t = bs(t), r || (r = hn.first(ds)), n.length > r.maxLen) {
    let c = e - r.maxLen / 2;
    return c < 0 ? c = 0 : i += c, n = n.substring(c, e + r.maxLen / 2), bi(e, t, n, i, r);
  }
  const s = Date.now(), a = e - 1 - i;
  let u = -1, o = null;
  for (let c = 1; !(Date.now() - s >= r.timeBudget); c++) {
    const h = a - r.windowSize * c;
    t.lastIndex = Math.max(0, h);
    const f = Sl(t, n, a, u);
    if (!f && o || (o = f, h <= 0))
      break;
    u = h;
  }
  if (o) {
    const c = {
      word: o[0],
      startColumn: i + 1 + o.index,
      endColumn: i + 1 + o.index + o[0].length
    };
    return t.lastIndex = 0, c;
  }
  return null;
}
function Sl(e, t, n, i) {
  let r;
  for (; r = e.exec(t); ) {
    const s = r.index || 0;
    if (s <= n && e.lastIndex >= n)
      return r;
    if (i > 0 && s > i)
      return null;
  }
  return null;
}
class Pl {
  static computeUnicodeHighlights(t, n, i) {
    const r = i ? i.startLineNumber : 1, s = i ? i.endLineNumber : t.getLineCount(), a = new dr(n), u = a.getCandidateCodePoints();
    let o;
    u === "allNonBasicAscii" ? o = new RegExp("[^\\t\\n\\r\\x20-\\x7E]", "g") : o = new RegExp(`${yl(Array.from(u))}`, "g");
    const c = new kl(null, o), h = [];
    let f = !1, _, p = 0, d = 0, b = 0;
    e: for (let A = r, v = s; A <= v; A++) {
      const x = t.getLineContent(A), R = x.length;
      c.reset(0);
      do
        if (_ = c.next(x), _) {
          let N = _.index, E = _.index + _[0].length;
          if (N > 0) {
            const X = x.charCodeAt(N - 1);
            gn(X) && N--;
          }
          if (E + 1 < R) {
            const X = x.charCodeAt(E - 1);
            gn(X) && E++;
          }
          const U = x.substring(N, E);
          let D = bi(N + 1, _s, x, 0);
          D && D.endColumn <= N + 1 && (D = null);
          const S = a.shouldHighlightNonBasicASCII(U, D ? D.word : null);
          if (S !== _e.None) {
            if (S === _e.Ambiguous ? p++ : S === _e.Invisible ? d++ : S === _e.NonBasicASCII ? b++ : js(), h.length >= 1e3) {
              f = !0;
              break e;
            }
            h.push(new F(A, N + 1, A, E + 1));
          }
        }
      while (_);
    }
    return {
      ranges: h,
      hasMore: f,
      ambiguousCharacterCount: p,
      invisibleCharacterCount: d,
      nonBasicAsciiCharacterCount: b
    };
  }
  static computeUnicodeHighlightReason(t, n) {
    const i = new dr(n);
    switch (i.shouldHighlightNonBasicASCII(t, null)) {
      case _e.None:
        return null;
      case _e.Invisible:
        return { kind: Vt.Invisible };
      case _e.Ambiguous: {
        const s = t.codePointAt(0), a = i.ambiguousCharacters.getPrimaryConfusable(s), u = Yt.getLocales().filter((o) => !Yt.getInstance(/* @__PURE__ */ new Set([...n.allowedLocales, o])).isAmbiguous(s));
        return { kind: Vt.Ambiguous, confusableWith: String.fromCodePoint(a), notAmbiguousInLocales: u };
      }
      case _e.NonBasicASCII:
        return { kind: Vt.NonBasicAscii };
    }
  }
}
function yl(e, t) {
  return `[${Na(e.map((i) => String.fromCodePoint(i)).join(""))}]`;
}
var Vt;
(function(e) {
  e[e.Ambiguous = 0] = "Ambiguous", e[e.Invisible = 1] = "Invisible", e[e.NonBasicAscii = 2] = "NonBasicAscii";
})(Vt || (Vt = {}));
class dr {
  constructor(t) {
    this.options = t, this.allowedCodePoints = new Set(t.allowedCodePoints), this.ambiguousCharacters = Yt.getInstance(new Set(t.allowedLocales));
  }
  getCandidateCodePoints() {
    if (this.options.nonBasicASCII)
      return "allNonBasicAscii";
    const t = /* @__PURE__ */ new Set();
    if (this.options.invisibleCharacters)
      for (const n of Ot.codePoints)
        wr(String.fromCodePoint(n)) || t.add(n);
    if (this.options.ambiguousCharacters)
      for (const n of this.ambiguousCharacters.getConfusableCodePoints())
        t.add(n);
    for (const n of this.allowedCodePoints)
      t.delete(n);
    return t;
  }
  shouldHighlightNonBasicASCII(t, n) {
    const i = t.codePointAt(0);
    if (this.allowedCodePoints.has(i))
      return _e.None;
    if (this.options.nonBasicASCII)
      return _e.NonBasicASCII;
    let r = !1, s = !1;
    if (n)
      for (const a of n) {
        const u = a.codePointAt(0), o = ka(a);
        r = r || o, !o && !this.ambiguousCharacters.isAmbiguous(u) && !Ot.isInvisibleCharacter(u) && (s = !0);
      }
    return !r && s ? _e.None : this.options.invisibleCharacters && !wr(t) && Ot.isInvisibleCharacter(i) ? _e.Invisible : this.options.ambiguousCharacters && this.ambiguousCharacters.isAmbiguous(i) ? _e.Ambiguous : _e.None;
  }
}
function wr(e) {
  return e === " " || e === `
` || e === "	";
}
var _e;
(function(e) {
  e[e.None = 0] = "None", e[e.NonBasicASCII = 1] = "NonBasicASCII", e[e.Invisible = 2] = "Invisible", e[e.Ambiguous = 3] = "Ambiguous";
})(_e || (_e = {}));
class on {
  constructor(t, n, i) {
    this.changes = t, this.moves = n, this.hitTimeout = i;
  }
}
class di {
  constructor(t, n) {
    this.lineRangeMapping = t, this.changes = n;
  }
  flip() {
    return new di(this.lineRangeMapping.flip(), this.changes.map((t) => t.flip()));
  }
}
class z {
  static fromTo(t, n) {
    return new z(t, n);
  }
  static addRange(t, n) {
    let i = 0;
    for (; i < n.length && n[i].endExclusive < t.start; )
      i++;
    let r = i;
    for (; r < n.length && n[r].start <= t.endExclusive; )
      r++;
    if (i === r)
      n.splice(i, 0, t);
    else {
      const s = Math.min(t.start, n[i].start), a = Math.max(t.endExclusive, n[r - 1].endExclusive);
      n.splice(i, r - i, new z(s, a));
    }
  }
  static tryCreate(t, n) {
    if (!(t > n))
      return new z(t, n);
  }
  static ofLength(t) {
    return new z(0, t);
  }
  static ofStartAndLength(t, n) {
    return new z(t, t + n);
  }
  static emptyAt(t) {
    return new z(t, t);
  }
  constructor(t, n) {
    if (this.start = t, this.endExclusive = n, t > n)
      throw new ae(`Invalid range: ${this.toString()}`);
  }
  get isEmpty() {
    return this.start === this.endExclusive;
  }
  delta(t) {
    return new z(this.start + t, this.endExclusive + t);
  }
  deltaStart(t) {
    return new z(this.start + t, this.endExclusive);
  }
  deltaEnd(t) {
    return new z(this.start, this.endExclusive + t);
  }
  get length() {
    return this.endExclusive - this.start;
  }
  toString() {
    return `[${this.start}, ${this.endExclusive})`;
  }
  equals(t) {
    return this.start === t.start && this.endExclusive === t.endExclusive;
  }
  containsRange(t) {
    return this.start <= t.start && t.endExclusive <= this.endExclusive;
  }
  contains(t) {
    return this.start <= t && t < this.endExclusive;
  }
  join(t) {
    return new z(
      Math.min(this.start, t.start),
      Math.max(this.endExclusive, t.endExclusive)
    );
  }
  intersect(t) {
    const n = Math.max(this.start, t.start), i = Math.min(this.endExclusive, t.endExclusive);
    if (n <= i)
      return new z(n, i);
  }
  intersectionLength(t) {
    const n = Math.max(this.start, t.start), i = Math.min(this.endExclusive, t.endExclusive);
    return Math.max(0, i - n);
  }
  intersects(t) {
    const n = Math.max(this.start, t.start), i = Math.min(this.endExclusive, t.endExclusive);
    return n < i;
  }
  intersectsOrTouches(t) {
    const n = Math.max(this.start, t.start), i = Math.min(this.endExclusive, t.endExclusive);
    return n <= i;
  }
  isBefore(t) {
    return this.endExclusive <= t.start;
  }
  isAfter(t) {
    return this.start >= t.endExclusive;
  }
  slice(t) {
    return t.slice(this.start, this.endExclusive);
  }
  substring(t) {
    return t.substring(this.start, this.endExclusive);
  }
  clip(t) {
    if (this.isEmpty)
      throw new ae(`Invalid clipping range: ${this.toString()}`);
    return Math.max(this.start, Math.min(this.endExclusive - 1, t));
  }
  clipCyclic(t) {
    if (this.isEmpty)
      throw new ae(`Invalid clipping range: ${this.toString()}`);
    return t < this.start ? this.endExclusive - (this.start - t) % this.length : t >= this.endExclusive ? this.start + (t - this.start) % this.length : t;
  }
  map(t) {
    const n = [];
    for (let i = this.start; i < this.endExclusive; i++)
      n.push(t(i));
    return n;
  }
  forEach(t) {
    for (let n = this.start; n < this.endExclusive; n++)
      t(n);
  }
}
class q {
  static fromRange(t) {
    return new q(t.startLineNumber, t.endLineNumber);
  }
  static fromRangeInclusive(t) {
    return new q(t.startLineNumber, t.endLineNumber + 1);
  }
  static subtract(t, n) {
    return n ? t.startLineNumber < n.startLineNumber && n.endLineNumberExclusive < t.endLineNumberExclusive ? [
      new q(t.startLineNumber, n.startLineNumber),
      new q(n.endLineNumberExclusive, t.endLineNumberExclusive)
    ] : n.startLineNumber <= t.startLineNumber && t.endLineNumberExclusive <= n.endLineNumberExclusive ? [] : n.endLineNumberExclusive < t.endLineNumberExclusive ? [new q(
      Math.max(n.endLineNumberExclusive, t.startLineNumber),
      t.endLineNumberExclusive
    )] : [new q(t.startLineNumber, Math.min(n.startLineNumber, t.endLineNumberExclusive))] : [t];
  }
  static joinMany(t) {
    if (t.length === 0)
      return [];
    let n = new Se(t[0].slice());
    for (let i = 1; i < t.length; i++)
      n = n.getUnion(new Se(t[i].slice()));
    return n.ranges;
  }
  static join(t) {
    if (t.length === 0)
      throw new ae("lineRanges cannot be empty");
    let n = t[0].startLineNumber, i = t[0].endLineNumberExclusive;
    for (let r = 1; r < t.length; r++)
      n = Math.min(n, t[r].startLineNumber), i = Math.max(i, t[r].endLineNumberExclusive);
    return new q(n, i);
  }
  static ofLength(t, n) {
    return new q(t, t + n);
  }
  static deserialize(t) {
    return new q(t[0], t[1]);
  }
  constructor(t, n) {
    if (t > n)
      throw new ae(
        `startLineNumber ${t} cannot be after endLineNumberExclusive ${n}`
      );
    this.startLineNumber = t, this.endLineNumberExclusive = n;
  }
  contains(t) {
    return this.startLineNumber <= t && t < this.endLineNumberExclusive;
  }
  get isEmpty() {
    return this.startLineNumber === this.endLineNumberExclusive;
  }
  delta(t) {
    return new q(this.startLineNumber + t, this.endLineNumberExclusive + t);
  }
  deltaLength(t) {
    return new q(this.startLineNumber, this.endLineNumberExclusive + t);
  }
  get length() {
    return this.endLineNumberExclusive - this.startLineNumber;
  }
  join(t) {
    return new q(
      Math.min(this.startLineNumber, t.startLineNumber),
      Math.max(this.endLineNumberExclusive, t.endLineNumberExclusive)
    );
  }
  toString() {
    return `[${this.startLineNumber},${this.endLineNumberExclusive})`;
  }
  intersect(t) {
    const n = Math.max(this.startLineNumber, t.startLineNumber), i = Math.min(this.endLineNumberExclusive, t.endLineNumberExclusive);
    if (n <= i)
      return new q(n, i);
  }
  intersectsStrict(t) {
    return this.startLineNumber < t.endLineNumberExclusive && t.startLineNumber < this.endLineNumberExclusive;
  }
  overlapOrTouch(t) {
    return this.startLineNumber <= t.endLineNumberExclusive && t.startLineNumber <= this.endLineNumberExclusive;
  }
  equals(t) {
    return this.startLineNumber === t.startLineNumber && this.endLineNumberExclusive === t.endLineNumberExclusive;
  }
  toInclusiveRange() {
    return this.isEmpty ? null : new F(
      this.startLineNumber,
      1,
      this.endLineNumberExclusive - 1,
      Number.MAX_SAFE_INTEGER
    );
  }
  toExclusiveRange() {
    return new F(this.startLineNumber, 1, this.endLineNumberExclusive, 1);
  }
  mapToLineArray(t) {
    const n = [];
    for (let i = this.startLineNumber; i < this.endLineNumberExclusive; i++)
      n.push(t(i));
    return n;
  }
  forEach(t) {
    for (let n = this.startLineNumber; n < this.endLineNumberExclusive; n++)
      t(n);
  }
  serialize() {
    return [this.startLineNumber, this.endLineNumberExclusive];
  }
  includes(t) {
    return this.startLineNumber <= t && t < this.endLineNumberExclusive;
  }
  toOffsetRange() {
    return new z(this.startLineNumber - 1, this.endLineNumberExclusive - 1);
  }
  distanceToRange(t) {
    return this.endLineNumberExclusive <= t.startLineNumber ? t.startLineNumber - this.endLineNumberExclusive : t.endLineNumberExclusive <= this.startLineNumber ? this.startLineNumber - t.endLineNumberExclusive : 0;
  }
  distanceToLine(t) {
    return this.contains(t) ? 0 : t < this.startLineNumber ? this.startLineNumber - t : t - this.endLineNumberExclusive;
  }
  addMargin(t, n) {
    return new q(
      this.startLineNumber - t,
      this.endLineNumberExclusive + n
    );
  }
}
class Se {
  constructor(t = []) {
    this._normalizedRanges = t;
  }
  get ranges() {
    return this._normalizedRanges;
  }
  addRange(t) {
    if (t.length === 0)
      return;
    const n = qn(this._normalizedRanges, (r) => r.endLineNumberExclusive >= t.startLineNumber), i = vt(this._normalizedRanges, (r) => r.startLineNumber <= t.endLineNumberExclusive) + 1;
    if (n === i)
      this._normalizedRanges.splice(n, 0, t);
    else if (n === i - 1) {
      const r = this._normalizedRanges[n];
      this._normalizedRanges[n] = r.join(t);
    } else {
      const r = this._normalizedRanges[n].join(this._normalizedRanges[i - 1]).join(t);
      this._normalizedRanges.splice(n, i - n, r);
    }
  }
  contains(t) {
    const n = At(this._normalizedRanges, (i) => i.startLineNumber <= t);
    return !!n && n.endLineNumberExclusive > t;
  }
  intersects(t) {
    const n = At(this._normalizedRanges, (i) => i.startLineNumber < t.endLineNumberExclusive);
    return !!n && n.endLineNumberExclusive > t.startLineNumber;
  }
  getUnion(t) {
    if (this._normalizedRanges.length === 0)
      return t;
    if (t._normalizedRanges.length === 0)
      return this;
    const n = [];
    let i = 0, r = 0, s = null;
    for (; i < this._normalizedRanges.length || r < t._normalizedRanges.length; ) {
      let a = null;
      if (i < this._normalizedRanges.length && r < t._normalizedRanges.length) {
        const u = this._normalizedRanges[i], o = t._normalizedRanges[r];
        u.startLineNumber < o.startLineNumber ? (a = u, i++) : (a = o, r++);
      } else i < this._normalizedRanges.length ? (a = this._normalizedRanges[i], i++) : (a = t._normalizedRanges[r], r++);
      s === null ? s = a : s.endLineNumberExclusive >= a.startLineNumber ? s = new q(
        s.startLineNumber,
        Math.max(s.endLineNumberExclusive, a.endLineNumberExclusive)
      ) : (n.push(s), s = a);
    }
    return s !== null && n.push(s), new Se(n);
  }
  subtractFrom(t) {
    const n = qn(this._normalizedRanges, (a) => a.endLineNumberExclusive >= t.startLineNumber), i = vt(this._normalizedRanges, (a) => a.startLineNumber <= t.endLineNumberExclusive) + 1;
    if (n === i)
      return new Se([t]);
    const r = [];
    let s = t.startLineNumber;
    for (let a = n; a < i; a++) {
      const u = this._normalizedRanges[a];
      u.startLineNumber > s && r.push(new q(s, u.startLineNumber)), s = u.endLineNumberExclusive;
    }
    return s < t.endLineNumberExclusive && r.push(new q(s, t.endLineNumberExclusive)), new Se(r);
  }
  toString() {
    return this._normalizedRanges.map((t) => t.toString()).join(", ");
  }
  getIntersection(t) {
    const n = [];
    let i = 0, r = 0;
    for (; i < this._normalizedRanges.length && r < t._normalizedRanges.length; ) {
      const s = this._normalizedRanges[i], a = t._normalizedRanges[r], u = s.intersect(a);
      u && !u.isEmpty && n.push(u), s.endLineNumberExclusive < a.endLineNumberExclusive ? i++ : r++;
    }
    return new Se(n);
  }
  getWithDelta(t) {
    return new Se(this._normalizedRanges.map((n) => n.delta(t)));
  }
}
const Le = class Le {
  static lengthDiffNonNegative(t, n) {
    return n.isLessThan(t) ? Le.zero : t.lineCount === n.lineCount ? new Le(0, n.columnCount - t.columnCount) : new Le(n.lineCount - t.lineCount, n.columnCount);
  }
  static betweenPositions(t, n) {
    return t.lineNumber === n.lineNumber ? new Le(0, n.column - t.column) : new Le(n.lineNumber - t.lineNumber, n.column - 1);
  }
  static fromPosition(t) {
    return new Le(t.lineNumber - 1, t.column - 1);
  }
  static ofRange(t) {
    return Le.betweenPositions(t.getStartPosition(), t.getEndPosition());
  }
  static ofText(t) {
    let n = 0, i = 0;
    for (const r of t)
      r === `
` ? (n++, i = 0) : i++;
    return new Le(n, i);
  }
  constructor(t, n) {
    this.lineCount = t, this.columnCount = n;
  }
  isZero() {
    return this.lineCount === 0 && this.columnCount === 0;
  }
  isLessThan(t) {
    return this.lineCount !== t.lineCount ? this.lineCount < t.lineCount : this.columnCount < t.columnCount;
  }
  isGreaterThan(t) {
    return this.lineCount !== t.lineCount ? this.lineCount > t.lineCount : this.columnCount > t.columnCount;
  }
  isGreaterThanOrEqualTo(t) {
    return this.lineCount !== t.lineCount ? this.lineCount > t.lineCount : this.columnCount >= t.columnCount;
  }
  equals(t) {
    return this.lineCount === t.lineCount && this.columnCount === t.columnCount;
  }
  compare(t) {
    return this.lineCount !== t.lineCount ? this.lineCount - t.lineCount : this.columnCount - t.columnCount;
  }
  add(t) {
    return t.lineCount === 0 ? new Le(this.lineCount, this.columnCount + t.columnCount) : new Le(this.lineCount + t.lineCount, t.columnCount);
  }
  createRange(t) {
    return this.lineCount === 0 ? new F(
      t.lineNumber,
      t.column,
      t.lineNumber,
      t.column + this.columnCount
    ) : new F(
      t.lineNumber,
      t.column,
      t.lineNumber + this.lineCount,
      this.columnCount + 1
    );
  }
  toRange() {
    return new F(1, 1, this.lineCount + 1, this.columnCount + 1);
  }
  toLineRange() {
    return q.ofLength(1, this.lineCount + 1);
  }
  addToPosition(t) {
    return this.lineCount === 0 ? new W(t.lineNumber, t.column + this.columnCount) : new W(t.lineNumber + this.lineCount, this.columnCount + 1);
  }
  addToRange(t) {
    return F.fromPositions(this.addToPosition(t.getStartPosition()), this.addToPosition(t.getEndPosition()));
  }
  toString() {
    return `${this.lineCount},${this.columnCount}`;
  }
};
Le.zero = new Le(0, 0);
let Je = Le;
class ws {
  constructor(t) {
    this.text = t, this.lineStartOffsetByLineIdx = [], this.lineEndOffsetByLineIdx = [], this.lineStartOffsetByLineIdx.push(0);
    for (let n = 0; n < t.length; n++)
      t.charAt(n) === `
` && (this.lineStartOffsetByLineIdx.push(n + 1), n > 0 && t.charAt(n - 1) === "\r" ? this.lineEndOffsetByLineIdx.push(n - 1) : this.lineEndOffsetByLineIdx.push(n));
    this.lineEndOffsetByLineIdx.push(t.length);
  }
  getOffset(t) {
    const n = this._validatePosition(t);
    return this.lineStartOffsetByLineIdx[n.lineNumber - 1] + n.column - 1;
  }
  _validatePosition(t) {
    if (t.lineNumber < 1)
      return new W(1, 1);
    const n = this.textLength.lineCount + 1;
    if (t.lineNumber > n) {
      const r = this.getLineLength(n);
      return new W(n, r + 1);
    }
    if (t.column < 1)
      return new W(t.lineNumber, 1);
    const i = this.getLineLength(t.lineNumber);
    return t.column - 1 > i ? new W(t.lineNumber, i + 1) : t;
  }
  getOffsetRange(t) {
    return new z(
      this.getOffset(t.getStartPosition()),
      this.getOffset(t.getEndPosition())
    );
  }
  getPosition(t) {
    const n = vt(this.lineStartOffsetByLineIdx, (s) => s <= t), i = n + 1, r = t - this.lineStartOffsetByLineIdx[n] + 1;
    return new W(i, r);
  }
  getRange(t) {
    return F.fromPositions(this.getPosition(t.start), this.getPosition(t.endExclusive));
  }
  getTextLength(t) {
    return Je.ofRange(this.getRange(t));
  }
  get textLength() {
    const t = this.lineStartOffsetByLineIdx.length - 1;
    return new Je(t, this.text.length - this.lineStartOffsetByLineIdx[t]);
  }
  getLineLength(t) {
    return this.lineEndOffsetByLineIdx[t - 1] - this.lineStartOffsetByLineIdx[t - 1];
  }
}
class et {
  static fromOffsetEdit(t, n) {
    const i = t.edits.map((r) => new ve(n.getTransformer().getRange(r.replaceRange), r.newText));
    return new et(i);
  }
  static single(t, n) {
    return new et([new ve(t, n)]);
  }
  static insert(t, n) {
    return new et([new ve(F.fromPositions(t, t), n)]);
  }
  constructor(t) {
    this.edits = t, Gt(() => hi(t, (n, i) => n.range.getEndPosition().isBeforeOrEqual(i.range.getStartPosition())));
  }
  normalize() {
    const t = [];
    for (const n of this.edits)
      if (t.length > 0 && t[t.length - 1].range.getEndPosition().equals(n.range.getStartPosition())) {
        const i = t[t.length - 1];
        t[t.length - 1] = new ve(i.range.plusRange(n.range), i.text + n.text);
      } else n.isEmpty || t.push(n);
    return new et(t);
  }
  mapPosition(t) {
    let n = 0, i = 0, r = 0;
    for (const s of this.edits) {
      const a = s.range.getStartPosition();
      if (t.isBeforeOrEqual(a))
        break;
      const u = s.range.getEndPosition(), o = Je.ofText(s.text);
      if (t.isBefore(u)) {
        const c = new W(
          a.lineNumber + n,
          a.column + (a.lineNumber + n === i ? r : 0)
        ), h = o.addToPosition(c);
        return tn(c, h);
      }
      a.lineNumber + n !== i && (r = 0), n += o.lineCount - (s.range.endLineNumber - s.range.startLineNumber), o.lineCount === 0 ? u.lineNumber !== a.lineNumber ? r += o.columnCount - (u.column - 1) : r += o.columnCount - (u.column - a.column) : r = o.columnCount, i = u.lineNumber + n;
    }
    return new W(
      t.lineNumber + n,
      t.column + (t.lineNumber + n === i ? r : 0)
    );
  }
  mapRange(t) {
    function n(a) {
      return a instanceof W ? a : a.getStartPosition();
    }
    function i(a) {
      return a instanceof W ? a : a.getEndPosition();
    }
    const r = n(this.mapPosition(t.getStartPosition())), s = i(this.mapPosition(t.getEndPosition()));
    return tn(r, s);
  }
  inverseMapPosition(t, n) {
    return this.inverse(n).mapPosition(t);
  }
  inverseMapRange(t, n) {
    return this.inverse(n).mapRange(t);
  }
  apply(t) {
    let n = "", i = new W(1, 1);
    for (const s of this.edits) {
      const a = s.range, u = a.getStartPosition(), o = a.getEndPosition(), c = tn(i, u);
      c.isEmpty() || (n += t.getValueOfRange(c)), n += s.text, i = o;
    }
    const r = tn(i, t.endPositionExclusive);
    return r.isEmpty() || (n += t.getValueOfRange(r)), n;
  }
  applyToString(t) {
    const n = new Ol(t);
    return this.apply(n);
  }
  inverse(t) {
    const n = this.getNewRanges();
    return new et(this.edits.map((i, r) => new ve(n[r], t.getValueOfRange(i.range))));
  }
  getNewRanges() {
    const t = [];
    let n = 0, i = 0, r = 0;
    for (const s of this.edits) {
      const a = Je.ofText(s.text), u = W.lift({
        lineNumber: s.range.startLineNumber + i,
        column: s.range.startColumn + (s.range.startLineNumber === n ? r : 0)
      }), o = a.createRange(u);
      t.push(o), i = o.endLineNumber - s.range.endLineNumber, r = o.endColumn - s.range.endColumn, n = s.range.endLineNumber;
    }
    return t;
  }
  toSingle(t) {
    if (this.edits.length === 0)
      throw new ae();
    if (this.edits.length === 1)
      return this.edits[0];
    const n = this.edits[0].range.getStartPosition(), i = this.edits[this.edits.length - 1].range.getEndPosition();
    let r = "";
    for (let s = 0; s < this.edits.length; s++) {
      const a = this.edits[s];
      if (r += a.text, s < this.edits.length - 1) {
        const u = this.edits[s + 1], o = F.fromPositions(a.range.getEndPosition(), u.range.getStartPosition()), c = t.getValueOfRange(o);
        r += c;
      }
    }
    return new ve(F.fromPositions(n, i), r);
  }
  equals(t) {
    return Zr(this.edits, t.edits, (n, i) => n.equals(i));
  }
}
class ve {
  static joinEdits(t, n) {
    if (t.length === 0)
      throw new ae();
    if (t.length === 1)
      return t[0];
    const i = t[0].range.getStartPosition(), r = t[t.length - 1].range.getEndPosition();
    let s = "";
    for (let a = 0; a < t.length; a++) {
      const u = t[a];
      if (s += u.text, a < t.length - 1) {
        const o = t[a + 1], c = F.fromPositions(u.range.getEndPosition(), o.range.getStartPosition()), h = n.getValueOfRange(c);
        s += h;
      }
    }
    return new ve(F.fromPositions(i, r), s);
  }
  constructor(t, n) {
    this.range = t, this.text = n;
  }
  get isEmpty() {
    return this.range.isEmpty() && this.text.length === 0;
  }
  static equals(t, n) {
    return t.range.equalsRange(n.range) && t.text === n.text;
  }
  toSingleEditOperation() {
    return {
      range: this.range,
      text: this.text
    };
  }
  toEdit() {
    return new et([this]);
  }
  equals(t) {
    return ve.equals(this, t);
  }
  extendToCoverRange(t, n) {
    if (this.range.containsRange(t))
      return this;
    const i = this.range.plusRange(t), r = n.getValueOfRange(F.fromPositions(i.getStartPosition(), this.range.getStartPosition())), s = n.getValueOfRange(F.fromPositions(this.range.getEndPosition(), i.getEndPosition())), a = r + this.text + s;
    return new ve(i, a);
  }
  extendToFullLine(t) {
    const n = new F(
      this.range.startLineNumber,
      1,
      this.range.endLineNumber,
      t.getTransformer().getLineLength(this.range.endLineNumber) + 1
    );
    return this.extendToCoverRange(n, t);
  }
  removeCommonPrefix(t) {
    const n = t.getValueOfRange(this.range).replaceAll(`\r
`, `
`), i = this.text.replaceAll(`\r
`, `
`), r = Di(n, i), s = Je.ofText(n.substring(0, r)).addToPosition(this.range.getStartPosition()), a = i.substring(r), u = F.fromPositions(s, this.range.getEndPosition());
    return new ve(u, a);
  }
  isEffectiveDeletion(t) {
    let n = this.text.replaceAll(`\r
`, `
`), i = t.getValueOfRange(this.range).replaceAll(`\r
`, `
`);
    const r = Di(n, i);
    n = n.substring(r), i = i.substring(r);
    const s = Ua(n, i);
    return n = n.substring(0, n.length - s), i = i.substring(0, i.length - s), n === "";
  }
}
function tn(e, t) {
  if (e.lineNumber === t.lineNumber && e.column === Number.MAX_SAFE_INTEGER)
    return F.fromPositions(t, t);
  if (!e.isBeforeOrEqual(t))
    throw new ae("start must be before end");
  return new F(e.lineNumber, e.column, t.lineNumber, t.column);
}
class Ls {
  constructor() {
    this._transformer = void 0;
  }
  get endPositionExclusive() {
    return this.length.addToPosition(new W(1, 1));
  }
  get lineRange() {
    return this.length.toLineRange();
  }
  getValue() {
    return this.getValueOfRange(this.length.toRange());
  }
  getLineLength(t) {
    return this.getValueOfRange(new F(t, 1, t, Number.MAX_SAFE_INTEGER)).length;
  }
  getTransformer() {
    return this._transformer || (this._transformer = new ws(this.getValue())), this._transformer;
  }
  getLineAt(t) {
    return this.getValueOfRange(new F(t, 1, t, Number.MAX_SAFE_INTEGER));
  }
  getLines() {
    const t = this.getValue();
    return is(t);
  }
}
class Bl extends Ls {
  constructor(t, n) {
    Xs(n >= 1), super(), this._getLineContent = t, this._lineCount = n;
  }
  getValueOfRange(t) {
    if (t.startLineNumber === t.endLineNumber)
      return this._getLineContent(t.startLineNumber).substring(t.startColumn - 1, t.endColumn - 1);
    let n = this._getLineContent(t.startLineNumber).substring(t.startColumn - 1);
    for (let i = t.startLineNumber + 1; i < t.endLineNumber; i++)
      n += `
` + this._getLineContent(i);
    return n += `
` + this._getLineContent(t.endLineNumber).substring(0, t.endColumn - 1), n;
  }
  getLineLength(t) {
    return this._getLineContent(t).length;
  }
  get length() {
    const t = this._getLineContent(this._lineCount);
    return new Je(this._lineCount - 1, t.length);
  }
}
class nn extends Bl {
  constructor(t) {
    super((n) => t[n - 1], t.length);
  }
}
class Ol extends Ls {
  constructor(t) {
    super(), this.value = t, this._t = new ws(this.value);
  }
  getValueOfRange(t) {
    return this._t.getOffsetRange(t).substring(this.value);
  }
  get length() {
    return this._t.textLength;
  }
}
class Te {
  static inverse(t, n, i) {
    const r = [];
    let s = 1, a = 1;
    for (const o of t) {
      const c = new Te(new q(s, o.original.startLineNumber), new q(a, o.modified.startLineNumber));
      c.modified.isEmpty || r.push(c), s = o.original.endLineNumberExclusive, a = o.modified.endLineNumberExclusive;
    }
    const u = new Te(new q(s, n + 1), new q(a, i + 1));
    return u.modified.isEmpty || r.push(u), r;
  }
  static clip(t, n, i) {
    const r = [];
    for (const s of t) {
      const a = s.original.intersect(n), u = s.modified.intersect(i);
      a && !a.isEmpty && u && !u.isEmpty && r.push(new Te(a, u));
    }
    return r;
  }
  constructor(t, n) {
    this.original = t, this.modified = n;
  }
  toString() {
    return `{${this.original.toString()}->${this.modified.toString()}}`;
  }
  flip() {
    return new Te(this.modified, this.original);
  }
  join(t) {
    return new Te(this.original.join(t.original), this.modified.join(t.modified));
  }
  get changedLineCount() {
    return Math.max(this.original.length, this.modified.length);
  }
  toRangeMapping() {
    const t = this.original.toInclusiveRange(), n = this.modified.toInclusiveRange();
    if (t && n)
      return new de(t, n);
    if (this.original.startLineNumber === 1 || this.modified.startLineNumber === 1) {
      if (!(this.modified.startLineNumber === 1 && this.original.startLineNumber === 1))
        throw new ae("not a valid diff");
      return new de(new F(this.original.startLineNumber, 1, this.original.endLineNumberExclusive, 1), new F(this.modified.startLineNumber, 1, this.modified.endLineNumberExclusive, 1));
    } else
      return new de(new F(
        this.original.startLineNumber - 1,
        Number.MAX_SAFE_INTEGER,
        this.original.endLineNumberExclusive - 1,
        Number.MAX_SAFE_INTEGER
      ), new F(
        this.modified.startLineNumber - 1,
        Number.MAX_SAFE_INTEGER,
        this.modified.endLineNumberExclusive - 1,
        Number.MAX_SAFE_INTEGER
      ));
  }
  toRangeMapping2(t, n) {
    if (Lr(this.original.endLineNumberExclusive, t) && Lr(this.modified.endLineNumberExclusive, n))
      return new de(new F(this.original.startLineNumber, 1, this.original.endLineNumberExclusive, 1), new F(this.modified.startLineNumber, 1, this.modified.endLineNumberExclusive, 1));
    if (!this.original.isEmpty && !this.modified.isEmpty)
      return new de(F.fromPositions(new W(this.original.startLineNumber, 1), ht(new W(this.original.endLineNumberExclusive - 1, Number.MAX_SAFE_INTEGER), t)), F.fromPositions(new W(this.modified.startLineNumber, 1), ht(new W(this.modified.endLineNumberExclusive - 1, Number.MAX_SAFE_INTEGER), n)));
    if (this.original.startLineNumber > 1 && this.modified.startLineNumber > 1)
      return new de(F.fromPositions(ht(new W(this.original.startLineNumber - 1, Number.MAX_SAFE_INTEGER), t), ht(new W(this.original.endLineNumberExclusive - 1, Number.MAX_SAFE_INTEGER), t)), F.fromPositions(ht(new W(this.modified.startLineNumber - 1, Number.MAX_SAFE_INTEGER), n), ht(new W(this.modified.endLineNumberExclusive - 1, Number.MAX_SAFE_INTEGER), n)));
    throw new ae();
  }
}
function ht(e, t) {
  if (e.lineNumber < 1)
    return new W(1, 1);
  if (e.lineNumber > t.length)
    return new W(t.length, t[t.length - 1].length + 1);
  const n = t[e.lineNumber - 1];
  return e.column > n.length + 1 ? new W(e.lineNumber, n.length + 1) : e;
}
function Lr(e, t) {
  return e >= 1 && e <= t.length;
}
class qe extends Te {
  static fromRangeMappings(t) {
    const n = q.join(t.map((r) => q.fromRangeInclusive(r.originalRange))), i = q.join(t.map((r) => q.fromRangeInclusive(r.modifiedRange)));
    return new qe(n, i, t);
  }
  constructor(t, n, i) {
    super(t, n), this.innerChanges = i;
  }
  flip() {
    var t;
    return new qe(this.modified, this.original, (t = this.innerChanges) == null ? void 0 : t.map((n) => n.flip()));
  }
  withInnerChangesFromLineRanges() {
    return new qe(this.original, this.modified, [this.toRangeMapping()]);
  }
}
class de {
  static fromEdit(t) {
    const n = t.getNewRanges();
    return t.edits.map((r, s) => new de(r.range, n[s]));
  }
  static fromEditJoin(t) {
    const n = t.getNewRanges(), i = t.edits.map((r, s) => new de(r.range, n[s]));
    return de.join(i);
  }
  static join(t) {
    if (t.length === 0)
      throw new ae("Cannot join an empty list of range mappings");
    let n = t[0];
    for (let i = 1; i < t.length; i++)
      n = n.join(t[i]);
    return n;
  }
  static assertSorted(t) {
    for (let n = 1; n < t.length; n++) {
      const i = t[n - 1], r = t[n];
      if (!(i.originalRange.getEndPosition().isBeforeOrEqual(r.originalRange.getStartPosition()) && i.modifiedRange.getEndPosition().isBeforeOrEqual(r.modifiedRange.getStartPosition())))
        throw new ae("Range mappings must be sorted");
    }
  }
  constructor(t, n) {
    this.originalRange = t, this.modifiedRange = n;
  }
  toString() {
    return `{${this.originalRange.toString()}->${this.modifiedRange.toString()}}`;
  }
  flip() {
    return new de(this.modifiedRange, this.originalRange);
  }
  toTextEdit(t) {
    const n = t.getValueOfRange(this.modifiedRange);
    return new ve(this.originalRange, n);
  }
  join(t) {
    return new de(
      this.originalRange.plusRange(t.originalRange),
      this.modifiedRange.plusRange(t.modifiedRange)
    );
  }
}
function pr(e, t, n, i = !1) {
  const r = [];
  for (const s of ys(e.map((a) => Vl(a, t, n)), (a, u) => a.original.overlapOrTouch(u.original) || a.modified.overlapOrTouch(u.modified))) {
    const a = s[0], u = s[s.length - 1];
    r.push(new qe(
      a.original.join(u.original),
      a.modified.join(u.modified),
      s.map((o) => o.innerChanges[0])
    ));
  }
  return Gt(() => !i && r.length > 0 && (r[0].modified.startLineNumber !== r[0].original.startLineNumber || n.length.lineCount - r[r.length - 1].modified.endLineNumberExclusive !== t.length.lineCount - r[r.length - 1].original.endLineNumberExclusive) ? !1 : hi(r, (s, a) => a.original.startLineNumber - s.original.endLineNumberExclusive === a.modified.startLineNumber - s.modified.endLineNumberExclusive && s.original.endLineNumberExclusive < a.original.startLineNumber && s.modified.endLineNumberExclusive < a.modified.startLineNumber)), r;
}
function Vl(e, t, n) {
  let i = 0, r = 0;
  e.modifiedRange.endColumn === 1 && e.originalRange.endColumn === 1 && e.originalRange.startLineNumber + i <= e.originalRange.endLineNumber && e.modifiedRange.startLineNumber + i <= e.modifiedRange.endLineNumber && (r = -1), e.modifiedRange.startColumn - 1 >= n.getLineLength(e.modifiedRange.startLineNumber) && e.originalRange.startColumn - 1 >= t.getLineLength(e.originalRange.startLineNumber) && e.originalRange.startLineNumber <= e.originalRange.endLineNumber + r && e.modifiedRange.startLineNumber <= e.modifiedRange.endLineNumber + r && (i = 1);
  const s = new q(
    e.originalRange.startLineNumber + i,
    e.originalRange.endLineNumber + 1 + r
  ), a = new q(
    e.modifiedRange.startLineNumber + i,
    e.modifiedRange.endLineNumber + 1 + r
  );
  return new qe(s, a, [e]);
}
const ql = 3;
class Hl {
  computeDiff(t, n, i) {
    var o;
    const s = new Ns(t, n, {
      maxComputationTime: i.maxComputationTimeMs,
      shouldIgnoreTrimWhitespace: i.ignoreTrimWhitespace,
      shouldComputeCharChanges: !0,
      shouldMakePrettyDiff: !0,
      shouldPostProcessCharChanges: !0
    }).computeDiff(), a = [];
    let u = null;
    for (const c of s.changes) {
      let h;
      c.originalEndLineNumber === 0 ? h = new q(c.originalStartLineNumber + 1, c.originalStartLineNumber + 1) : h = new q(c.originalStartLineNumber, c.originalEndLineNumber + 1);
      let f;
      c.modifiedEndLineNumber === 0 ? f = new q(c.modifiedStartLineNumber + 1, c.modifiedStartLineNumber + 1) : f = new q(c.modifiedStartLineNumber, c.modifiedEndLineNumber + 1);
      let _ = new qe(h, f, (o = c.charChanges) == null ? void 0 : o.map((p) => new de(new F(
        p.originalStartLineNumber,
        p.originalStartColumn,
        p.originalEndLineNumber,
        p.originalEndColumn
      ), new F(
        p.modifiedStartLineNumber,
        p.modifiedStartColumn,
        p.modifiedEndLineNumber,
        p.modifiedEndColumn
      ))));
      u && (u.modified.endLineNumberExclusive === _.modified.startLineNumber || u.original.endLineNumberExclusive === _.original.startLineNumber) && (_ = new qe(
        u.original.join(_.original),
        u.modified.join(_.modified),
        u.innerChanges && _.innerChanges ? u.innerChanges.concat(_.innerChanges) : void 0
      ), a.pop()), a.push(_), u = _;
    }
    return Gt(() => hi(a, (c, h) => h.original.startLineNumber - c.original.endLineNumberExclusive === h.modified.startLineNumber - c.modified.endLineNumberExclusive && c.original.endLineNumberExclusive < h.original.startLineNumber && c.modified.endLineNumberExclusive < h.modified.startLineNumber)), new on(a, [], s.quitEarly);
  }
}
function ps(e, t, n, i) {
  return new Ye(e, t, n).ComputeDiff(i);
}
let Nr = class {
  constructor(t) {
    const n = [], i = [];
    for (let r = 0, s = t.length; r < s; r++)
      n[r] = si(t[r], 1), i[r] = ai(t[r], 1);
    this.lines = t, this._startColumns = n, this._endColumns = i;
  }
  getElements() {
    const t = [];
    for (let n = 0, i = this.lines.length; n < i; n++)
      t[n] = this.lines[n].substring(this._startColumns[n] - 1, this._endColumns[n] - 1);
    return t;
  }
  getStrictElement(t) {
    return this.lines[t];
  }
  getStartLineNumber(t) {
    return t + 1;
  }
  getEndLineNumber(t) {
    return t + 1;
  }
  createCharSequence(t, n, i) {
    const r = [], s = [], a = [];
    let u = 0;
    for (let o = n; o <= i; o++) {
      const c = this.lines[o], h = t ? this._startColumns[o] : 1, f = t ? this._endColumns[o] : c.length + 1;
      for (let _ = h; _ < f; _++)
        r[u] = c.charCodeAt(_ - 1), s[u] = o + 1, a[u] = _, u++;
      !t && o < i && (r[u] = L.LineFeed, s[u] = o + 1, a[u] = c.length + 1, u++);
    }
    return new Wl(r, s, a);
  }
};
class Wl {
  constructor(t, n, i) {
    this._charCodes = t, this._lineNumbers = n, this._columns = i;
  }
  toString() {
    return "[" + this._charCodes.map(
      (t, n) => (t === L.LineFeed ? "\\n" : String.fromCharCode(t)) + `-(${this._lineNumbers[n]},${this._columns[n]})`
    ).join(", ") + "]";
  }
  _assertIndex(t, n) {
    if (t < 0 || t >= n.length)
      throw new Error("Illegal index");
  }
  getElements() {
    return this._charCodes;
  }
  getStartLineNumber(t) {
    return t > 0 && t === this._lineNumbers.length ? this.getEndLineNumber(t - 1) : (this._assertIndex(t, this._lineNumbers), this._lineNumbers[t]);
  }
  getEndLineNumber(t) {
    return t === -1 ? this.getStartLineNumber(t + 1) : (this._assertIndex(t, this._lineNumbers), this._charCodes[t] === L.LineFeed ? this._lineNumbers[t] + 1 : this._lineNumbers[t]);
  }
  getStartColumn(t) {
    return t > 0 && t === this._columns.length ? this.getEndColumn(t - 1) : (this._assertIndex(t, this._columns), this._columns[t]);
  }
  getEndColumn(t) {
    return t === -1 ? this.getStartColumn(t + 1) : (this._assertIndex(t, this._columns), this._charCodes[t] === L.LineFeed ? 1 : this._columns[t] + 1);
  }
}
class Et {
  constructor(t, n, i, r, s, a, u, o) {
    this.originalStartLineNumber = t, this.originalStartColumn = n, this.originalEndLineNumber = i, this.originalEndColumn = r, this.modifiedStartLineNumber = s, this.modifiedStartColumn = a, this.modifiedEndLineNumber = u, this.modifiedEndColumn = o;
  }
  static createFromDiffChange(t, n, i) {
    const r = n.getStartLineNumber(t.originalStart), s = n.getStartColumn(t.originalStart), a = n.getEndLineNumber(t.originalStart + t.originalLength - 1), u = n.getEndColumn(t.originalStart + t.originalLength - 1), o = i.getStartLineNumber(t.modifiedStart), c = i.getStartColumn(t.modifiedStart), h = i.getEndLineNumber(t.modifiedStart + t.modifiedLength - 1), f = i.getEndColumn(t.modifiedStart + t.modifiedLength - 1);
    return new Et(
      r,
      s,
      a,
      u,
      o,
      c,
      h,
      f
    );
  }
}
function Gl(e) {
  if (e.length <= 1)
    return e;
  const t = [e[0]];
  let n = t[0];
  for (let i = 1, r = e.length; i < r; i++) {
    const s = e[i], a = s.originalStart - (n.originalStart + n.originalLength), u = s.modifiedStart - (n.modifiedStart + n.modifiedLength);
    Math.min(a, u) < ql ? (n.originalLength = s.originalStart + s.originalLength - n.originalStart, n.modifiedLength = s.modifiedStart + s.modifiedLength - n.modifiedStart) : (t.push(s), n = s);
  }
  return t;
}
class qt {
  constructor(t, n, i, r, s) {
    this.originalStartLineNumber = t, this.originalEndLineNumber = n, this.modifiedStartLineNumber = i, this.modifiedEndLineNumber = r, this.charChanges = s;
  }
  static createFromDiffResult(t, n, i, r, s, a, u) {
    let o, c, h, f, _;
    if (n.originalLength === 0 ? (o = i.getStartLineNumber(n.originalStart) - 1, c = 0) : (o = i.getStartLineNumber(n.originalStart), c = i.getEndLineNumber(n.originalStart + n.originalLength - 1)), n.modifiedLength === 0 ? (h = r.getStartLineNumber(n.modifiedStart) - 1, f = 0) : (h = r.getStartLineNumber(n.modifiedStart), f = r.getEndLineNumber(n.modifiedStart + n.modifiedLength - 1)), a && n.originalLength > 0 && n.originalLength < 20 && n.modifiedLength > 0 && n.modifiedLength < 20 && s()) {
      const p = i.createCharSequence(t, n.originalStart, n.originalStart + n.originalLength - 1), d = r.createCharSequence(t, n.modifiedStart, n.modifiedStart + n.modifiedLength - 1);
      if (p.getElements().length > 0 && d.getElements().length > 0) {
        let b = ps(p, d, s, !0).changes;
        u && (b = Gl(b)), _ = [];
        for (let A = 0, v = b.length; A < v; A++)
          _.push(Et.createFromDiffChange(b[A], p, d));
      }
    }
    return new qt(
      o,
      c,
      h,
      f,
      _
    );
  }
}
class Ns {
  constructor(t, n, i) {
    this.shouldComputeCharChanges = i.shouldComputeCharChanges, this.shouldPostProcessCharChanges = i.shouldPostProcessCharChanges, this.shouldIgnoreTrimWhitespace = i.shouldIgnoreTrimWhitespace, this.shouldMakePrettyDiff = i.shouldMakePrettyDiff, this.originalLines = t, this.modifiedLines = n, this.original = new Nr(t), this.modified = new Nr(n), this.continueLineDiff = Er(i.maxComputationTime), this.continueCharDiff = Er(i.maxComputationTime === 0 ? 0 : Math.min(i.maxComputationTime, 5e3));
  }
  computeDiff() {
    if (this.original.lines.length === 1 && this.original.lines[0].length === 0)
      return this.modified.lines.length === 1 && this.modified.lines[0].length === 0 ? {
        quitEarly: !1,
        changes: []
      } : {
        quitEarly: !1,
        changes: [{
          originalStartLineNumber: 1,
          originalEndLineNumber: 1,
          modifiedStartLineNumber: 1,
          modifiedEndLineNumber: this.modified.lines.length,
          charChanges: void 0
        }]
      };
    if (this.modified.lines.length === 1 && this.modified.lines[0].length === 0)
      return {
        quitEarly: !1,
        changes: [{
          originalStartLineNumber: 1,
          originalEndLineNumber: this.original.lines.length,
          modifiedStartLineNumber: 1,
          modifiedEndLineNumber: 1,
          charChanges: void 0
        }]
      };
    const t = ps(this.original, this.modified, this.continueLineDiff, this.shouldMakePrettyDiff), n = t.changes, i = t.quitEarly;
    if (this.shouldIgnoreTrimWhitespace) {
      const u = [];
      for (let o = 0, c = n.length; o < c; o++)
        u.push(qt.createFromDiffResult(this.shouldIgnoreTrimWhitespace, n[o], this.original, this.modified, this.continueCharDiff, this.shouldComputeCharChanges, this.shouldPostProcessCharChanges));
      return {
        quitEarly: i,
        changes: u
      };
    }
    const r = [];
    let s = 0, a = 0;
    for (let u = -1, o = n.length; u < o; u++) {
      const c = u + 1 < o ? n[u + 1] : null, h = c ? c.originalStart : this.originalLines.length, f = c ? c.modifiedStart : this.modifiedLines.length;
      for (; s < h && a < f; ) {
        const _ = this.originalLines[s], p = this.modifiedLines[a];
        if (_ !== p) {
          {
            let d = si(_, 1), b = si(p, 1);
            for (; d > 1 && b > 1; ) {
              const A = _.charCodeAt(d - 2), v = p.charCodeAt(b - 2);
              if (A !== v)
                break;
              d--, b--;
            }
            (d > 1 || b > 1) && this._pushTrimWhitespaceCharChange(r, s + 1, 1, d, a + 1, 1, b);
          }
          {
            let d = ai(_, 1), b = ai(p, 1);
            const A = _.length + 1, v = p.length + 1;
            for (; d < A && b < v; ) {
              const x = _.charCodeAt(d - 1), R = _.charCodeAt(b - 1);
              if (x !== R)
                break;
              d++, b++;
            }
            (d < A || b < v) && this._pushTrimWhitespaceCharChange(r, s + 1, d, A, a + 1, b, v);
          }
        }
        s++, a++;
      }
      c && (r.push(qt.createFromDiffResult(this.shouldIgnoreTrimWhitespace, c, this.original, this.modified, this.continueCharDiff, this.shouldComputeCharChanges, this.shouldPostProcessCharChanges)), s += c.originalLength, a += c.modifiedLength);
    }
    return {
      quitEarly: i,
      changes: r
    };
  }
  _pushTrimWhitespaceCharChange(t, n, i, r, s, a, u) {
    if (this._mergeTrimWhitespaceCharChange(t, n, i, r, s, a, u))
      return;
    let o;
    this.shouldComputeCharChanges && (o = [new Et(
      n,
      i,
      n,
      r,
      s,
      a,
      s,
      u
    )]), t.push(new qt(
      n,
      n,
      s,
      s,
      o
    ));
  }
  _mergeTrimWhitespaceCharChange(t, n, i, r, s, a, u) {
    const o = t.length;
    if (o === 0)
      return !1;
    const c = t[o - 1];
    return c.originalEndLineNumber === 0 || c.modifiedEndLineNumber === 0 ? !1 : c.originalEndLineNumber === n && c.modifiedEndLineNumber === s ? (this.shouldComputeCharChanges && c.charChanges && c.charChanges.push(new Et(
      n,
      i,
      n,
      r,
      s,
      a,
      s,
      u
    )), !0) : c.originalEndLineNumber + 1 === n && c.modifiedEndLineNumber + 1 === s ? (c.originalEndLineNumber = n, c.modifiedEndLineNumber = s, this.shouldComputeCharChanges && c.charChanges && c.charChanges.push(new Et(
      n,
      i,
      n,
      r,
      s,
      a,
      s,
      u
    )), !0) : !1;
  }
}
function si(e, t) {
  const n = Ea(e);
  return n === -1 ? t : n + 1;
}
function ai(e, t) {
  const n = xa(e);
  return n === -1 ? t : n + 2;
}
function Er(e) {
  if (e === 0)
    return () => !0;
  const t = Date.now();
  return () => Date.now() - t < e;
}
class He {
  static trivial(t, n) {
    return new He([new re(z.ofLength(t.length), z.ofLength(n.length))], !1);
  }
  static trivialTimedOut(t, n) {
    return new He([new re(z.ofLength(t.length), z.ofLength(n.length))], !0);
  }
  constructor(t, n) {
    this.diffs = t, this.hitTimeout = n;
  }
}
class re {
  static invert(t, n) {
    const i = [];
    return Bs(t, (r, s) => {
      i.push(re.fromOffsetPairs(r ? r.getEndExclusives() : Oe.zero, s ? s.getStarts() : new Oe(
        n,
        (r ? r.seq2Range.endExclusive - r.seq1Range.endExclusive : 0) + n
      )));
    }), i;
  }
  static fromOffsetPairs(t, n) {
    return new re(new z(t.offset1, n.offset1), new z(t.offset2, n.offset2));
  }
  static assertSorted(t) {
    let n;
    for (const i of t) {
      if (n && !(n.seq1Range.endExclusive <= i.seq1Range.start && n.seq2Range.endExclusive <= i.seq2Range.start))
        throw new ae("Sequence diffs must be sorted");
      n = i;
    }
  }
  constructor(t, n) {
    this.seq1Range = t, this.seq2Range = n;
  }
  swap() {
    return new re(this.seq2Range, this.seq1Range);
  }
  toString() {
    return `${this.seq1Range} <-> ${this.seq2Range}`;
  }
  join(t) {
    return new re(this.seq1Range.join(t.seq1Range), this.seq2Range.join(t.seq2Range));
  }
  delta(t) {
    return t === 0 ? this : new re(this.seq1Range.delta(t), this.seq2Range.delta(t));
  }
  deltaStart(t) {
    return t === 0 ? this : new re(this.seq1Range.deltaStart(t), this.seq2Range.deltaStart(t));
  }
  deltaEnd(t) {
    return t === 0 ? this : new re(this.seq1Range.deltaEnd(t), this.seq2Range.deltaEnd(t));
  }
  intersectsOrTouches(t) {
    return this.seq1Range.intersectsOrTouches(t.seq1Range) || this.seq2Range.intersectsOrTouches(t.seq2Range);
  }
  intersect(t) {
    const n = this.seq1Range.intersect(t.seq1Range), i = this.seq2Range.intersect(t.seq2Range);
    if (!(!n || !i))
      return new re(n, i);
  }
  getStarts() {
    return new Oe(this.seq1Range.start, this.seq2Range.start);
  }
  getEndExclusives() {
    return new Oe(this.seq1Range.endExclusive, this.seq2Range.endExclusive);
  }
}
const rt = class rt {
  constructor(t, n) {
    this.offset1 = t, this.offset2 = n;
  }
  toString() {
    return `${this.offset1} <-> ${this.offset2}`;
  }
  delta(t) {
    return t === 0 ? this : new rt(this.offset1 + t, this.offset2 + t);
  }
  equals(t) {
    return this.offset1 === t.offset1 && this.offset2 === t.offset2;
  }
};
rt.zero = new rt(0, 0), rt.max = new rt(Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER);
let Oe = rt;
const Un = class Un {
  isValid() {
    return !0;
  }
};
Un.instance = new Un();
let Qt = Un;
class $l {
  constructor(t) {
    if (this.timeout = t, this.startTime = Date.now(), this.valid = !0, t <= 0)
      throw new ae("timeout must be positive");
  }
  isValid() {
    return !(Date.now() - this.startTime < this.timeout) && this.valid && (this.valid = !1), this.valid;
  }
  disable() {
    this.timeout = Number.MAX_SAFE_INTEGER, this.isValid = () => !0, this.valid = !0;
  }
}
class yn {
  constructor(t, n) {
    this.width = t, this.height = n, this.array = [], this.array = new Array(t * n);
  }
  get(t, n) {
    return this.array[t + n * this.width];
  }
  set(t, n, i) {
    this.array[t + n * this.width] = i;
  }
}
function li(e) {
  return e === L.Space || e === L.Tab;
}
const Wt = class Wt {
  static getKey(t) {
    let n = this.chrKeys.get(t);
    return n === void 0 && (n = this.chrKeys.size, this.chrKeys.set(t, n)), n;
  }
  constructor(t, n, i) {
    this.range = t, this.lines = n, this.source = i, this.histogram = [];
    let r = 0;
    for (let s = t.startLineNumber - 1; s < t.endLineNumberExclusive - 1; s++) {
      const a = n[s];
      for (let o = 0; o < a.length; o++) {
        r++;
        const c = a[o], h = Wt.getKey(c);
        this.histogram[h] = (this.histogram[h] || 0) + 1;
      }
      r++;
      const u = Wt.getKey(`
`);
      this.histogram[u] = (this.histogram[u] || 0) + 1;
    }
    this.totalCount = r;
  }
  computeSimilarity(t) {
    let n = 0;
    const i = Math.max(this.histogram.length, t.histogram.length);
    for (let r = 0; r < i; r++)
      n += Math.abs((this.histogram[r] ?? 0) - (t.histogram[r] ?? 0));
    return 1 - n / (this.totalCount + t.totalCount);
  }
};
Wt.chrKeys = /* @__PURE__ */ new Map();
let pn = Wt;
class zl {
  compute(t, n, i = Qt.instance, r) {
    if (t.length === 0 || n.length === 0)
      return He.trivial(t, n);
    const s = new yn(t.length, n.length), a = new yn(t.length, n.length), u = new yn(t.length, n.length);
    for (let d = 0; d < t.length; d++)
      for (let b = 0; b < n.length; b++) {
        if (!i.isValid())
          return He.trivialTimedOut(t, n);
        const A = d === 0 ? 0 : s.get(d - 1, b), v = b === 0 ? 0 : s.get(d, b - 1);
        let x;
        t.getElement(d) === n.getElement(b) ? (d === 0 || b === 0 ? x = 0 : x = s.get(d - 1, b - 1), d > 0 && b > 0 && a.get(d - 1, b - 1) === 3 && (x += u.get(d - 1, b - 1)), x += r ? r(d, b) : 1) : x = -1;
        const R = Math.max(A, v, x);
        if (R === x) {
          const N = d > 0 && b > 0 ? u.get(d - 1, b - 1) : 0;
          u.set(d, b, N + 1), a.set(d, b, 3);
        } else R === A ? (u.set(d, b, 0), a.set(d, b, 1)) : R === v && (u.set(d, b, 0), a.set(d, b, 2));
        s.set(d, b, R);
      }
    const o = [];
    let c = t.length, h = n.length;
    function f(d, b) {
      (d + 1 !== c || b + 1 !== h) && o.push(new re(new z(d + 1, c), new z(b + 1, h))), c = d, h = b;
    }
    let _ = t.length - 1, p = n.length - 1;
    for (; _ >= 0 && p >= 0; )
      a.get(_, p) === 3 ? (f(_, p), _--, p--) : a.get(_, p) === 1 ? _-- : p--;
    return f(-1, -1), o.reverse(), new He(o, !1);
  }
}
class Es {
  compute(t, n, i = Qt.instance) {
    if (t.length === 0 || n.length === 0)
      return He.trivial(t, n);
    const r = t, s = n;
    function a(b, A) {
      for (; b < r.length && A < s.length && r.getElement(b) === s.getElement(A); )
        b++, A++;
      return b;
    }
    let u = 0;
    const o = new jl();
    o.set(0, a(0, 0));
    const c = new Xl();
    c.set(0, o.get(0) === 0 ? null : new xr(null, 0, 0, o.get(0)));
    let h = 0;
    e: for (; ; ) {
      if (u++, !i.isValid())
        return He.trivialTimedOut(r, s);
      const b = -Math.min(u, s.length + u % 2), A = Math.min(u, r.length + u % 2);
      for (h = b; h <= A; h += 2) {
        const v = h === A ? -1 : o.get(h + 1), x = h === b ? -1 : o.get(h - 1) + 1, R = Math.min(Math.max(v, x), r.length), N = R - h;
        if (R > r.length || N > s.length)
          continue;
        const E = a(R, N);
        o.set(h, E);
        const U = R === v ? c.get(h + 1) : c.get(h - 1);
        if (c.set(h, E !== R ? new xr(U, R, N, E - R) : U), o.get(h) === r.length && o.get(h) - h === s.length)
          break e;
      }
    }
    let f = c.get(h);
    const _ = [];
    let p = r.length, d = s.length;
    for (; ; ) {
      const b = f ? f.x + f.length : 0, A = f ? f.y + f.length : 0;
      if ((b !== p || A !== d) && _.push(new re(new z(b, p), new z(A, d))), !f)
        break;
      p = f.x, d = f.y, f = f.prev;
    }
    return _.reverse(), new He(_, !1);
  }
}
class xr {
  constructor(t, n, i, r) {
    this.prev = t, this.x = n, this.y = i, this.length = r;
  }
}
class jl {
  constructor() {
    this.positiveArr = new Int32Array(10), this.negativeArr = new Int32Array(10);
  }
  get(t) {
    return t < 0 ? (t = -t - 1, this.negativeArr[t]) : this.positiveArr[t];
  }
  set(t, n) {
    if (t < 0) {
      if (t = -t - 1, t >= this.negativeArr.length) {
        const i = this.negativeArr;
        this.negativeArr = new Int32Array(i.length * 2), this.negativeArr.set(i);
      }
      this.negativeArr[t] = n;
    } else {
      if (t >= this.positiveArr.length) {
        const i = this.positiveArr;
        this.positiveArr = new Int32Array(i.length * 2), this.positiveArr.set(i);
      }
      this.positiveArr[t] = n;
    }
  }
}
class Xl {
  constructor() {
    this.positiveArr = [], this.negativeArr = [];
  }
  get(t) {
    return t < 0 ? (t = -t - 1, this.negativeArr[t]) : this.positiveArr[t];
  }
  set(t, n) {
    t < 0 ? (t = -t - 1, this.negativeArr[t] = n) : this.positiveArr[t] = n;
  }
}
class Nn {
  constructor(t, n, i) {
    this.lines = t, this.range = n, this.considerWhitespaceChanges = i, this.elements = [], this.firstElementOffsetByLineIdx = [], this.lineStartOffsets = [], this.trimmedWsLengthsByLineIdx = [], this.firstElementOffsetByLineIdx.push(0);
    for (let r = this.range.startLineNumber; r <= this.range.endLineNumber; r++) {
      let s = t[r - 1], a = 0;
      r === this.range.startLineNumber && this.range.startColumn > 1 && (a = this.range.startColumn - 1, s = s.substring(a)), this.lineStartOffsets.push(a);
      let u = 0;
      if (!i) {
        const c = s.trimStart();
        u = s.length - c.length, s = c.trimEnd();
      }
      this.trimmedWsLengthsByLineIdx.push(u);
      const o = r === this.range.endLineNumber ? Math.min(this.range.endColumn - 1 - a - u, s.length) : s.length;
      for (let c = 0; c < o; c++)
        this.elements.push(s.charCodeAt(c));
      r < this.range.endLineNumber && (this.elements.push(10), this.firstElementOffsetByLineIdx.push(this.elements.length));
    }
  }
  toString() {
    return `Slice: "${this.text}"`;
  }
  get text() {
    return this.getText(new z(0, this.length));
  }
  getText(t) {
    return this.elements.slice(t.start, t.endExclusive).map((n) => String.fromCharCode(n)).join("");
  }
  getElement(t) {
    return this.elements[t];
  }
  get length() {
    return this.elements.length;
  }
  getBoundaryScore(t) {
    const n = Rr(t > 0 ? this.elements[t - 1] : -1), i = Rr(t < this.elements.length ? this.elements[t] : -1);
    if (n === ne.LineBreakCR && i === ne.LineBreakLF)
      return 0;
    if (n === ne.LineBreakLF)
      return 150;
    let r = 0;
    return n !== i && (r += 10, n === ne.WordLower && i === ne.WordUpper && (r += 1)), r += vr(n), r += vr(i), r;
  }
  translateOffset(t, n = "right") {
    const i = vt(this.firstElementOffsetByLineIdx, (s) => s <= t), r = t - this.firstElementOffsetByLineIdx[i];
    return new W(
      this.range.startLineNumber + i,
      1 + this.lineStartOffsets[i] + r + (r === 0 && n === "left" ? 0 : this.trimmedWsLengthsByLineIdx[i])
    );
  }
  translateRange(t) {
    const n = this.translateOffset(t.start, "right"), i = this.translateOffset(t.endExclusive, "left");
    return i.isBefore(n) ? F.fromPositions(i, i) : F.fromPositions(n, i);
  }
  findWordContaining(t) {
    if (t < 0 || t >= this.elements.length || !ft(this.elements[t]))
      return;
    let n = t;
    for (; n > 0 && ft(this.elements[n - 1]); )
      n--;
    let i = t;
    for (; i < this.elements.length && ft(this.elements[i]); )
      i++;
    return new z(n, i);
  }
  findSubWordContaining(t) {
    if (t < 0 || t >= this.elements.length || !ft(this.elements[t]))
      return;
    let n = t;
    for (; n > 0 && ft(this.elements[n - 1]) && !Ar(this.elements[n]); )
      n--;
    let i = t;
    for (; i < this.elements.length && ft(this.elements[i]) && !Ar(this.elements[i]); )
      i++;
    return new z(n, i);
  }
  countLinesIn(t) {
    return this.translateOffset(t.endExclusive).lineNumber - this.translateOffset(t.start).lineNumber;
  }
  isStronglyEqual(t, n) {
    return this.elements[t] === this.elements[n];
  }
  extendToFullLines(t) {
    const n = At(this.firstElementOffsetByLineIdx, (r) => r <= t.start) ?? 0, i = Ps(this.firstElementOffsetByLineIdx, (r) => t.endExclusive <= r) ?? this.elements.length;
    return new z(n, i);
  }
}
function ft(e) {
  return e >= L.a && e <= L.z || e >= L.A && e <= L.Z || e >= L.Digit0 && e <= L.Digit9;
}
function Ar(e) {
  return e >= L.A && e <= L.Z;
}
var ne;
(function(e) {
  e[e.WordLower = 0] = "WordLower", e[e.WordUpper = 1] = "WordUpper", e[e.WordNumber = 2] = "WordNumber", e[e.End = 3] = "End", e[e.Other = 4] = "Other", e[e.Separator = 5] = "Separator", e[e.Space = 6] = "Space", e[e.LineBreakCR = 7] = "LineBreakCR", e[e.LineBreakLF = 8] = "LineBreakLF";
})(ne || (ne = {}));
const Yl = {
  [ne.WordLower]: 0,
  [ne.WordUpper]: 0,
  [ne.WordNumber]: 0,
  [ne.End]: 10,
  [ne.Other]: 2,
  [ne.Separator]: 30,
  [ne.Space]: 3,
  [ne.LineBreakCR]: 10,
  [ne.LineBreakLF]: 10
};
function vr(e) {
  return Yl[e];
}
function Rr(e) {
  return e === L.LineFeed ? ne.LineBreakLF : e === L.CarriageReturn ? ne.LineBreakCR : li(e) ? ne.Space : e >= L.a && e <= L.z ? ne.WordLower : e >= L.A && e <= L.Z ? ne.WordUpper : e >= L.Digit0 && e <= L.Digit9 ? ne.WordNumber : e === -1 ? ne.End : e === L.Comma || e === L.Semicolon ? ne.Separator : ne.Other;
}
function Ql(e, t, n, i, r, s) {
  let { moves: a, excludedChanges: u } = Jl(e, t, n, s);
  if (!s.isValid())
    return [];
  const o = e.filter((h) => !u.has(h)), c = Kl(o, i, r, t, n, s);
  return Vs(a, c), a = Cl(a), a = a.filter((h) => {
    const f = h.original.toOffsetRange().slice(t).map((p) => p.trim());
    return f.join(`
`).length >= 15 && Zl(f, (p) => p.length >= 2) >= 2;
  }), a = eu(e, a), a;
}
function Zl(e, t) {
  let n = 0;
  for (const i of e)
    t(i) && n++;
  return n;
}
function Jl(e, t, n, i) {
  const r = [], s = e.filter((o) => o.modified.isEmpty && o.original.length >= 3).map((o) => new pn(o.original, t, o)), a = new Set(e.filter((o) => o.original.isEmpty && o.modified.length >= 3).map((o) => new pn(o.modified, n, o))), u = /* @__PURE__ */ new Set();
  for (const o of s) {
    let c = -1, h;
    for (const f of a) {
      const _ = o.computeSimilarity(f);
      _ > c && (c = _, h = f);
    }
    if (c > 0.9 && h && (a.delete(h), r.push(new Te(o.range, h.range)), u.add(o.source), u.add(h.source)), !i.isValid())
      return { moves: r, excludedChanges: u };
  }
  return { moves: r, excludedChanges: u };
}
function Kl(e, t, n, i, r, s) {
  const a = [], u = new Jr();
  for (const _ of e)
    for (let p = _.original.startLineNumber; p < _.original.endLineNumberExclusive - 2; p++) {
      const d = `${t[p - 1]}:${t[p + 1 - 1]}:${t[p + 2 - 1]}`;
      u.add(d, { range: new q(p, p + 3) });
    }
  const o = [];
  e.sort(Pt((_) => _.modified.startLineNumber, yt));
  for (const _ of e) {
    let p = [];
    for (let d = _.modified.startLineNumber; d < _.modified.endLineNumberExclusive - 2; d++) {
      const b = `${n[d - 1]}:${n[d + 1 - 1]}:${n[d + 2 - 1]}`, A = new q(d, d + 3), v = [];
      u.forEach(b, ({ range: x }) => {
        for (const N of p)
          if (N.originalLineRange.endLineNumberExclusive + 1 === x.endLineNumberExclusive && N.modifiedLineRange.endLineNumberExclusive + 1 === A.endLineNumberExclusive) {
            N.originalLineRange = new q(
              N.originalLineRange.startLineNumber,
              x.endLineNumberExclusive
            ), N.modifiedLineRange = new q(
              N.modifiedLineRange.startLineNumber,
              A.endLineNumberExclusive
            ), v.push(N);
            return;
          }
        const R = {
          modifiedLineRange: A,
          originalLineRange: x
        };
        o.push(R), v.push(R);
      }), p = v;
    }
    if (!s.isValid())
      return [];
  }
  o.sort(qs(Pt((_) => _.modifiedLineRange.length, yt)));
  const c = new Se(), h = new Se();
  for (const _ of o) {
    const p = _.modifiedLineRange.startLineNumber - _.originalLineRange.startLineNumber, d = c.subtractFrom(_.modifiedLineRange), b = h.subtractFrom(_.originalLineRange).getWithDelta(p), A = d.getIntersection(b);
    for (const v of A.ranges) {
      if (v.length < 3)
        continue;
      const x = v, R = v.delta(-p);
      a.push(new Te(R, x)), c.addRange(x), h.addRange(R);
    }
  }
  a.sort(Pt((_) => _.original.startLineNumber, yt));
  const f = new cn(e);
  for (let _ = 0; _ < a.length; _++) {
    const p = a[_], d = f.findLastMonotonous((U) => U.original.startLineNumber <= p.original.startLineNumber), b = At(e, (U) => U.modified.startLineNumber <= p.modified.startLineNumber), A = Math.max(p.original.startLineNumber - d.original.startLineNumber, p.modified.startLineNumber - b.modified.startLineNumber), v = f.findLastMonotonous((U) => U.original.startLineNumber < p.original.endLineNumberExclusive), x = At(e, (U) => U.modified.startLineNumber < p.modified.endLineNumberExclusive), R = Math.max(v.original.endLineNumberExclusive - p.original.endLineNumberExclusive, x.modified.endLineNumberExclusive - p.modified.endLineNumberExclusive);
    let N;
    for (N = 0; N < A; N++) {
      const U = p.original.startLineNumber - N - 1, D = p.modified.startLineNumber - N - 1;
      if (U > i.length || D > r.length || c.contains(D) || h.contains(U) || !Tr(i[U - 1], r[D - 1], s))
        break;
    }
    N > 0 && (h.addRange(new q(p.original.startLineNumber - N, p.original.startLineNumber)), c.addRange(new q(p.modified.startLineNumber - N, p.modified.startLineNumber)));
    let E;
    for (E = 0; E < R; E++) {
      const U = p.original.endLineNumberExclusive + E, D = p.modified.endLineNumberExclusive + E;
      if (U > i.length || D > r.length || c.contains(D) || h.contains(U) || !Tr(i[U - 1], r[D - 1], s))
        break;
    }
    E > 0 && (h.addRange(new q(
      p.original.endLineNumberExclusive,
      p.original.endLineNumberExclusive + E
    )), c.addRange(new q(
      p.modified.endLineNumberExclusive,
      p.modified.endLineNumberExclusive + E
    ))), (N > 0 || E > 0) && (a[_] = new Te(new q(
      p.original.startLineNumber - N,
      p.original.endLineNumberExclusive + E
    ), new q(
      p.modified.startLineNumber - N,
      p.modified.endLineNumberExclusive + E
    )));
  }
  return a;
}
function Tr(e, t, n) {
  if (e.trim() === t.trim())
    return !0;
  if (e.length > 300 && t.length > 300)
    return !1;
  const r = new Es().compute(new Nn([e], new F(1, 1, 1, e.length), !1), new Nn([t], new F(1, 1, 1, t.length), !1), n);
  let s = 0;
  const a = re.invert(r.diffs, e.length);
  for (const h of a)
    h.seq1Range.forEach((f) => {
      li(e.charCodeAt(f)) || s++;
    });
  function u(h) {
    let f = 0;
    for (let _ = 0; _ < e.length; _++)
      li(h.charCodeAt(_)) || f++;
    return f;
  }
  const o = u(e.length > t.length ? e : t);
  return s / o > 0.6 && o > 10;
}
function Cl(e) {
  if (e.length === 0)
    return e;
  e.sort(Pt((n) => n.original.startLineNumber, yt));
  const t = [e[0]];
  for (let n = 1; n < e.length; n++) {
    const i = t[t.length - 1], r = e[n], s = r.original.startLineNumber - i.original.endLineNumberExclusive, a = r.modified.startLineNumber - i.modified.endLineNumberExclusive;
    if (s >= 0 && a >= 0 && s + a <= 2) {
      t[t.length - 1] = i.join(r);
      continue;
    }
    t.push(r);
  }
  return t;
}
function eu(e, t) {
  const n = new cn(e);
  return t = t.filter((i) => {
    const r = n.findLastMonotonous((u) => u.original.startLineNumber < i.original.endLineNumberExclusive) || new Te(new q(1, 1), new q(1, 1)), s = At(e, (u) => u.modified.startLineNumber < i.modified.endLineNumberExclusive);
    return r !== s;
  }), t;
}
function Ur(e, t, n) {
  let i = n;
  return i = Mr(e, t, i), i = Mr(e, t, i), i = tu(e, t, i), i;
}
function Mr(e, t, n) {
  if (n.length === 0)
    return n;
  const i = [];
  i.push(n[0]);
  for (let s = 1; s < n.length; s++) {
    const a = i[i.length - 1];
    let u = n[s];
    if (u.seq1Range.isEmpty || u.seq2Range.isEmpty) {
      const o = u.seq1Range.start - a.seq1Range.endExclusive;
      let c;
      for (c = 1; c <= o && !(e.getElement(u.seq1Range.start - c) !== e.getElement(u.seq1Range.endExclusive - c) || t.getElement(u.seq2Range.start - c) !== t.getElement(u.seq2Range.endExclusive - c)); c++)
        ;
      if (c--, c === o) {
        i[i.length - 1] = new re(new z(a.seq1Range.start, u.seq1Range.endExclusive - o), new z(a.seq2Range.start, u.seq2Range.endExclusive - o));
        continue;
      }
      u = u.delta(-c);
    }
    i.push(u);
  }
  const r = [];
  for (let s = 0; s < i.length - 1; s++) {
    const a = i[s + 1];
    let u = i[s];
    if (u.seq1Range.isEmpty || u.seq2Range.isEmpty) {
      const o = a.seq1Range.start - u.seq1Range.endExclusive;
      let c;
      for (c = 0; c < o && !(!e.isStronglyEqual(u.seq1Range.start + c, u.seq1Range.endExclusive + c) || !t.isStronglyEqual(u.seq2Range.start + c, u.seq2Range.endExclusive + c)); c++)
        ;
      if (c === o) {
        i[s + 1] = new re(new z(u.seq1Range.start + o, a.seq1Range.endExclusive), new z(u.seq2Range.start + o, a.seq2Range.endExclusive));
        continue;
      }
      c > 0 && (u = u.delta(c));
    }
    r.push(u);
  }
  return i.length > 0 && r.push(i[i.length - 1]), r;
}
function tu(e, t, n) {
  if (!e.getBoundaryScore || !t.getBoundaryScore)
    return n;
  for (let i = 0; i < n.length; i++) {
    const r = i > 0 ? n[i - 1] : void 0, s = n[i], a = i + 1 < n.length ? n[i + 1] : void 0, u = new z(
      r ? r.seq1Range.endExclusive + 1 : 0,
      a ? a.seq1Range.start - 1 : e.length
    ), o = new z(
      r ? r.seq2Range.endExclusive + 1 : 0,
      a ? a.seq2Range.start - 1 : t.length
    );
    s.seq1Range.isEmpty ? n[i] = Dr(s, e, t, u, o) : s.seq2Range.isEmpty && (n[i] = Dr(s.swap(), t, e, o, u).swap());
  }
  return n;
}
function Dr(e, t, n, i, r) {
  let a = 1;
  for (; e.seq1Range.start - a >= i.start && e.seq2Range.start - a >= r.start && n.isStronglyEqual(e.seq2Range.start - a, e.seq2Range.endExclusive - a) && a < 100; )
    a++;
  a--;
  let u = 0;
  for (; e.seq1Range.start + u < i.endExclusive && e.seq2Range.endExclusive + u < r.endExclusive && n.isStronglyEqual(e.seq2Range.start + u, e.seq2Range.endExclusive + u) && u < 100; )
    u++;
  if (a === 0 && u === 0)
    return e;
  let o = 0, c = -1;
  for (let h = -a; h <= u; h++) {
    const f = e.seq2Range.start + h, _ = e.seq2Range.endExclusive + h, p = e.seq1Range.start + h, d = t.getBoundaryScore(p) + n.getBoundaryScore(f) + n.getBoundaryScore(_);
    d > c && (c = d, o = h);
  }
  return e.delta(o);
}
function nu(e, t, n) {
  const i = [];
  for (const r of n) {
    const s = i[i.length - 1];
    if (!s) {
      i.push(r);
      continue;
    }
    r.seq1Range.start - s.seq1Range.endExclusive <= 2 || r.seq2Range.start - s.seq2Range.endExclusive <= 2 ? i[i.length - 1] = new re(s.seq1Range.join(r.seq1Range), s.seq2Range.join(r.seq2Range)) : i.push(r);
  }
  return i;
}
function kr(e, t, n, i, r = !1) {
  const s = re.invert(n, e.length), a = [];
  let u = new Oe(0, 0);
  function o(h, f) {
    if (h.offset1 < u.offset1 || h.offset2 < u.offset2)
      return;
    const _ = i(e, h.offset1), p = i(t, h.offset2);
    if (!_ || !p)
      return;
    let d = new re(_, p);
    const b = d.intersect(f);
    let A = b.seq1Range.length, v = b.seq2Range.length;
    for (; s.length > 0; ) {
      const x = s[0];
      if (!(x.seq1Range.intersects(d.seq1Range) || x.seq2Range.intersects(d.seq2Range)))
        break;
      const N = i(e, x.seq1Range.start), E = i(t, x.seq2Range.start), U = new re(N, E), D = U.intersect(x);
      if (A += D.seq1Range.length, v += D.seq2Range.length, d = d.join(U), d.seq1Range.endExclusive >= x.seq1Range.endExclusive)
        s.shift();
      else
        break;
    }
    (r && A + v < d.seq1Range.length + d.seq2Range.length || A + v < (d.seq1Range.length + d.seq2Range.length) * 2 / 3) && a.push(d), u = d.getEndExclusives();
  }
  for (; s.length > 0; ) {
    const h = s.shift();
    h.seq1Range.isEmpty || (o(h.getStarts(), h), o(h.getEndExclusives().delta(-1), h));
  }
  return iu(n, a);
}
function iu(e, t) {
  const n = [];
  for (; e.length > 0 || t.length > 0; ) {
    const i = e[0], r = t[0];
    let s;
    i && (!r || i.seq1Range.start < r.seq1Range.start) ? s = e.shift() : s = t.shift(), n.length > 0 && n[n.length - 1].seq1Range.endExclusive >= s.seq1Range.start ? n[n.length - 1] = n[n.length - 1].join(s) : n.push(s);
  }
  return n;
}
function ru(e, t, n) {
  let i = n;
  if (i.length === 0)
    return i;
  let r = 0, s;
  do {
    s = !1;
    const a = [
      i[0]
    ];
    for (let u = 1; u < i.length; u++) {
      let h = function(_, p) {
        const d = new z(c.seq1Range.endExclusive, o.seq1Range.start);
        return e.getText(d).replace(/\s/g, "").length <= 4 && (_.seq1Range.length + _.seq2Range.length > 5 || p.seq1Range.length + p.seq2Range.length > 5);
      };
      const o = i[u], c = a[a.length - 1];
      h(c, o) ? (s = !0, a[a.length - 1] = a[a.length - 1].join(o)) : a.push(o);
    }
    i = a;
  } while (r++ < 10 && s);
  return i;
}
function su(e, t, n) {
  let i = n;
  if (i.length === 0)
    return i;
  let r = 0, s;
  do {
    s = !1;
    const u = [
      i[0]
    ];
    for (let o = 1; o < i.length; o++) {
      let f = function(p, d) {
        const b = new z(h.seq1Range.endExclusive, c.seq1Range.start);
        if (e.countLinesIn(b) > 5 || b.length > 500)
          return !1;
        const v = e.getText(b).trim();
        if (v.length > 20 || v.split(/\r\n|\r|\n/).length > 1)
          return !1;
        const x = e.countLinesIn(p.seq1Range), R = p.seq1Range.length, N = t.countLinesIn(p.seq2Range), E = p.seq2Range.length, U = e.countLinesIn(d.seq1Range), D = d.seq1Range.length, S = t.countLinesIn(d.seq2Range), X = d.seq2Range.length, ie = 2 * 40 + 50;
        function Y(H) {
          return Math.min(H, ie);
        }
        return Math.pow(Math.pow(Y(x * 40 + R), 1.5) + Math.pow(Y(N * 40 + E), 1.5), 1.5) + Math.pow(Math.pow(Y(U * 40 + D), 1.5) + Math.pow(Y(S * 40 + X), 1.5), 1.5) > (ie ** 1.5) ** 1.5 * 1.3;
      };
      const c = i[o], h = u[u.length - 1];
      f(h, c) ? (s = !0, u[u.length - 1] = u[u.length - 1].join(c)) : u.push(c);
    }
    i = u;
  } while (r++ < 10 && s);
  const a = [];
  return Os(i, (u, o, c) => {
    let h = o;
    function f(v) {
      return v.length > 0 && v.trim().length <= 3 && o.seq1Range.length + o.seq2Range.length > 100;
    }
    const _ = e.extendToFullLines(o.seq1Range), p = e.getText(new z(_.start, o.seq1Range.start));
    f(p) && (h = h.deltaStart(-p.length));
    const d = e.getText(new z(o.seq1Range.endExclusive, _.endExclusive));
    f(d) && (h = h.deltaEnd(d.length));
    const b = re.fromOffsetPairs(u ? u.getEndExclusives() : Oe.zero, c ? c.getStarts() : Oe.max), A = h.intersect(b);
    a.length > 0 && A.getStarts().equals(a[a.length - 1].getEndExclusives()) ? a[a.length - 1] = a[a.length - 1].join(A) : a.push(A);
  }), a;
}
class Fr {
  constructor(t, n) {
    this.trimmedHash = t, this.lines = n;
  }
  getElement(t) {
    return this.trimmedHash[t];
  }
  get length() {
    return this.trimmedHash.length;
  }
  getBoundaryScore(t) {
    const n = t === 0 ? 0 : Ir(this.lines[t - 1]), i = t === this.lines.length ? 0 : Ir(this.lines[t]);
    return 1e3 - (n + i);
  }
  getText(t) {
    return this.lines.slice(t.start, t.endExclusive).join(`
`);
  }
  isStronglyEqual(t, n) {
    return this.lines[t] === this.lines[n];
  }
}
function Ir(e) {
  let t = 0;
  for (; t < e.length && (e.charCodeAt(t) === L.Space || e.charCodeAt(t) === L.Tab); )
    t++;
  return t;
}
class au {
  constructor() {
    this.dynamicProgrammingDiffing = new zl(), this.myersDiffingAlgorithm = new Es();
  }
  computeDiff(t, n, i) {
    if (t.length <= 1 && Zr(t, n, (E, U) => E === U))
      return new on([], [], !1);
    if (t.length === 1 && t[0].length === 0 || n.length === 1 && n[0].length === 0)
      return new on([
        new qe(new q(1, t.length + 1), new q(1, n.length + 1), [
          new de(new F(
            1,
            1,
            t.length,
            t[t.length - 1].length + 1
          ), new F(
            1,
            1,
            n.length,
            n[n.length - 1].length + 1
          ))
        ])
      ], [], !1);
    const r = i.maxComputationTimeMs === 0 ? Qt.instance : new $l(i.maxComputationTimeMs), s = !i.ignoreTrimWhitespace, a = /* @__PURE__ */ new Map();
    function u(E) {
      let U = a.get(E);
      return U === void 0 && (U = a.size, a.set(E, U)), U;
    }
    const o = t.map((E) => u(E.trim())), c = n.map((E) => u(E.trim())), h = new Fr(o, t), f = new Fr(c, n), _ = h.length + f.length < 1700 ? this.dynamicProgrammingDiffing.compute(h, f, r, (E, U) => t[E] === n[U] ? n[U].length === 0 ? 0.1 : 1 + Math.log(1 + n[U].length) : 0.99) : this.myersDiffingAlgorithm.compute(h, f, r);
    let p = _.diffs, d = _.hitTimeout;
    p = Ur(h, f, p), p = ru(h, f, p);
    const b = [], A = (E) => {
      if (s)
        for (let U = 0; U < E; U++) {
          const D = v + U, S = x + U;
          if (t[D] !== n[S]) {
            const X = this.refineDiff(t, n, new re(new z(D, D + 1), new z(S, S + 1)), r, s, i);
            for (const ie of X.mappings)
              b.push(ie);
            X.hitTimeout && (d = !0);
          }
        }
    };
    let v = 0, x = 0;
    for (const E of p) {
      Gt(() => E.seq1Range.start - v === E.seq2Range.start - x);
      const U = E.seq1Range.start - v;
      A(U), v = E.seq1Range.endExclusive, x = E.seq2Range.endExclusive;
      const D = this.refineDiff(t, n, E, r, s, i);
      D.hitTimeout && (d = !0);
      for (const S of D.mappings)
        b.push(S);
    }
    A(t.length - v);
    const R = pr(b, new nn(t), new nn(n));
    let N = [];
    return i.computeMoves && (N = this.computeMoves(R, t, n, o, c, r, s, i)), Gt(() => {
      function E(D, S) {
        if (D.lineNumber < 1 || D.lineNumber > S.length)
          return !1;
        const X = S[D.lineNumber - 1];
        return !(D.column < 1 || D.column > X.length + 1);
      }
      function U(D, S) {
        return !(D.startLineNumber < 1 || D.startLineNumber > S.length + 1 || D.endLineNumberExclusive < 1 || D.endLineNumberExclusive > S.length + 1);
      }
      for (const D of R) {
        if (!D.innerChanges)
          return !1;
        for (const S of D.innerChanges)
          if (!(E(S.modifiedRange.getStartPosition(), n) && E(S.modifiedRange.getEndPosition(), n) && E(S.originalRange.getStartPosition(), t) && E(S.originalRange.getEndPosition(), t)))
            return !1;
        if (!U(D.modified, n) || !U(D.original, t))
          return !1;
      }
      return !0;
    }), new on(R, N, d);
  }
  computeMoves(t, n, i, r, s, a, u, o) {
    return Ql(t, n, i, r, s, a).map((f) => {
      const _ = this.refineDiff(n, i, new re(f.original.toOffsetRange(), f.modified.toOffsetRange()), a, u, o), p = pr(_.mappings, new nn(n), new nn(i), !0);
      return new di(f, p);
    });
  }
  refineDiff(t, n, i, r, s, a) {
    const o = lu(i).toRangeMapping2(t, n), c = new Nn(t, o.originalRange, s), h = new Nn(n, o.modifiedRange, s), f = c.length + h.length < 500 ? this.dynamicProgrammingDiffing.compute(c, h, r) : this.myersDiffingAlgorithm.compute(c, h, r);
    let _ = f.diffs;
    return _ = Ur(c, h, _), _ = kr(c, h, _, (d, b) => d.findWordContaining(b)), a.extendToSubwords && (_ = kr(c, h, _, (d, b) => d.findSubWordContaining(b), !0)), _ = nu(c, h, _), _ = su(c, h, _), {
      mappings: _.map((d) => new de(c.translateRange(d.seq1Range), h.translateRange(d.seq2Range))),
      hitTimeout: f.hitTimeout
    };
  }
}
function lu(e) {
  return new Te(new q(e.seq1Range.start + 1, e.seq1Range.endExclusive + 1), new q(e.seq2Range.start + 1, e.seq2Range.endExclusive + 1));
}
const Bn = {
  getLegacy: () => new Hl(),
  getDefault: () => new au()
};
function Ze(e, t) {
  const n = Math.pow(10, t);
  return Math.round(e * n) / n;
}
class w {
  constructor(t, n, i, r = 1) {
    this._rgbaBrand = void 0, this.r = Math.min(255, Math.max(0, t)) | 0, this.g = Math.min(255, Math.max(0, n)) | 0, this.b = Math.min(255, Math.max(0, i)) | 0, this.a = Ze(Math.max(Math.min(1, r), 0), 3);
  }
  static equals(t, n) {
    return t.r === n.r && t.g === n.g && t.b === n.b && t.a === n.a;
  }
}
class Re {
  constructor(t, n, i, r) {
    this._hslaBrand = void 0, this.h = Math.max(Math.min(360, t), 0) | 0, this.s = Ze(Math.max(Math.min(1, n), 0), 3), this.l = Ze(Math.max(Math.min(1, i), 0), 3), this.a = Ze(Math.max(Math.min(1, r), 0), 3);
  }
  static equals(t, n) {
    return t.h === n.h && t.s === n.s && t.l === n.l && t.a === n.a;
  }
  static fromRGBA(t) {
    const n = t.r / 255, i = t.g / 255, r = t.b / 255, s = t.a, a = Math.max(n, i, r), u = Math.min(n, i, r);
    let o = 0, c = 0;
    const h = (u + a) / 2, f = a - u;
    if (f > 0) {
      switch (c = Math.min(h <= 0.5 ? f / (2 * h) : f / (2 - 2 * h), 1), a) {
        case n:
          o = (i - r) / f + (i < r ? 6 : 0);
          break;
        case i:
          o = (r - n) / f + 2;
          break;
        case r:
          o = (n - i) / f + 4;
          break;
      }
      o *= 60, o = Math.round(o);
    }
    return new Re(o, c, h, s);
  }
  static _hue2rgb(t, n, i) {
    return i < 0 && (i += 1), i > 1 && (i -= 1), i < 1 / 6 ? t + (n - t) * 6 * i : i < 1 / 2 ? n : i < 2 / 3 ? t + (n - t) * (2 / 3 - i) * 6 : t;
  }
  static toRGBA(t) {
    const n = t.h / 360, { s: i, l: r, a: s } = t;
    let a, u, o;
    if (i === 0)
      a = u = o = r;
    else {
      const c = r < 0.5 ? r * (1 + i) : r + i - r * i, h = 2 * r - c;
      a = Re._hue2rgb(h, c, n + 1 / 3), u = Re._hue2rgb(h, c, n), o = Re._hue2rgb(h, c, n - 1 / 3);
    }
    return new w(Math.round(a * 255), Math.round(u * 255), Math.round(o * 255), s);
  }
}
class _t {
  constructor(t, n, i, r) {
    this._hsvaBrand = void 0, this.h = Math.max(Math.min(360, t), 0) | 0, this.s = Ze(Math.max(Math.min(1, n), 0), 3), this.v = Ze(Math.max(Math.min(1, i), 0), 3), this.a = Ze(Math.max(Math.min(1, r), 0), 3);
  }
  static equals(t, n) {
    return t.h === n.h && t.s === n.s && t.v === n.v && t.a === n.a;
  }
  static fromRGBA(t) {
    const n = t.r / 255, i = t.g / 255, r = t.b / 255, s = Math.max(n, i, r), a = Math.min(n, i, r), u = s - a, o = s === 0 ? 0 : u / s;
    let c;
    return u === 0 ? c = 0 : s === n ? c = ((i - r) / u % 6 + 6) % 6 : s === i ? c = (r - n) / u + 2 : c = (n - i) / u + 4, new _t(Math.round(c * 60), o, s, t.a);
  }
  static toRGBA(t) {
    const { h: n, s: i, v: r, a: s } = t, a = r * i, u = a * (1 - Math.abs(n / 60 % 2 - 1)), o = r - a;
    let [c, h, f] = [0, 0, 0];
    return n < 60 ? (c = a, h = u) : n < 120 ? (c = u, h = a) : n < 180 ? (h = a, f = u) : n < 240 ? (h = u, f = a) : n < 300 ? (c = u, f = a) : n <= 360 && (c = a, f = u), c = Math.round((c + o) * 255), h = Math.round((h + o) * 255), f = Math.round((f + o) * 255), new w(c, h, f, s);
  }
}
const j = class j {
  static fromHex(t) {
    return j.Format.CSS.parseHex(t) || j.red;
  }
  static equals(t, n) {
    return !t && !n ? !0 : !t || !n ? !1 : t.equals(n);
  }
  get hsla() {
    return this._hsla ? this._hsla : Re.fromRGBA(this.rgba);
  }
  get hsva() {
    return this._hsva ? this._hsva : _t.fromRGBA(this.rgba);
  }
  constructor(t) {
    if (t)
      if (t instanceof w)
        this.rgba = t;
      else if (t instanceof Re)
        this._hsla = t, this.rgba = Re.toRGBA(t);
      else if (t instanceof _t)
        this._hsva = t, this.rgba = _t.toRGBA(t);
      else
        throw new Error("Invalid color ctor argument");
    else throw new Error("Color needs a value");
  }
  equals(t) {
    return !!t && w.equals(this.rgba, t.rgba) && Re.equals(this.hsla, t.hsla) && _t.equals(this.hsva, t.hsva);
  }
  getRelativeLuminance() {
    const t = j._relativeLuminanceForComponent(this.rgba.r), n = j._relativeLuminanceForComponent(this.rgba.g), i = j._relativeLuminanceForComponent(this.rgba.b), r = 0.2126 * t + 0.7152 * n + 0.0722 * i;
    return Ze(r, 4);
  }
  reduceRelativeLuminace(t, n) {
    let { r: i, g: r, b: s } = t.rgba, a = this.getContrastRatio(t);
    for (; a < n && (i > 0 || r > 0 || s > 0); )
      i -= Math.max(0, Math.ceil(i * 0.1)), r -= Math.max(0, Math.ceil(r * 0.1)), s -= Math.max(0, Math.ceil(s * 0.1)), a = this.getContrastRatio(new j(new w(i, r, s)));
    return new j(new w(i, r, s));
  }
  increaseRelativeLuminace(t, n) {
    let { r: i, g: r, b: s } = t.rgba, a = this.getContrastRatio(t);
    for (; a < n && (i < 255 || r < 255 || s < 255); )
      i = Math.min(255, i + Math.ceil((255 - i) * 0.1)), r = Math.min(255, r + Math.ceil((255 - r) * 0.1)), s = Math.min(255, s + Math.ceil((255 - s) * 0.1)), a = this.getContrastRatio(new j(new w(i, r, s)));
    return new j(new w(i, r, s));
  }
  static _relativeLuminanceForComponent(t) {
    const n = t / 255;
    return n <= 0.03928 ? n / 12.92 : Math.pow((n + 0.055) / 1.055, 2.4);
  }
  getContrastRatio(t) {
    const n = this.getRelativeLuminance(), i = t.getRelativeLuminance();
    return n > i ? (n + 0.05) / (i + 0.05) : (i + 0.05) / (n + 0.05);
  }
  isDarker() {
    return (this.rgba.r * 299 + this.rgba.g * 587 + this.rgba.b * 114) / 1e3 < 128;
  }
  isLighter() {
    return (this.rgba.r * 299 + this.rgba.g * 587 + this.rgba.b * 114) / 1e3 >= 128;
  }
  isLighterThan(t) {
    const n = this.getRelativeLuminance(), i = t.getRelativeLuminance();
    return n > i;
  }
  isDarkerThan(t) {
    const n = this.getRelativeLuminance(), i = t.getRelativeLuminance();
    return n < i;
  }
  ensureConstrast(t, n) {
    const i = this.getRelativeLuminance(), r = t.getRelativeLuminance();
    if (this.getContrastRatio(t) < n) {
      if (r < i) {
        const o = this.reduceRelativeLuminace(t, n), c = this.getContrastRatio(o);
        if (c < n) {
          const h = this.increaseRelativeLuminace(t, n), f = this.getContrastRatio(h);
          return c > f ? o : h;
        }
        return o;
      }
      const a = this.increaseRelativeLuminace(t, n), u = this.getContrastRatio(a);
      if (u < n) {
        const o = this.reduceRelativeLuminace(t, n), c = this.getContrastRatio(o);
        return u > c ? a : o;
      }
      return a;
    }
    return t;
  }
  lighten(t) {
    return new j(new Re(this.hsla.h, this.hsla.s, this.hsla.l + this.hsla.l * t, this.hsla.a));
  }
  darken(t) {
    return new j(new Re(this.hsla.h, this.hsla.s, this.hsla.l - this.hsla.l * t, this.hsla.a));
  }
  transparent(t) {
    const { r: n, g: i, b: r, a: s } = this.rgba;
    return new j(new w(n, i, r, s * t));
  }
  isTransparent() {
    return this.rgba.a === 0;
  }
  isOpaque() {
    return this.rgba.a === 1;
  }
  opposite() {
    return new j(new w(255 - this.rgba.r, 255 - this.rgba.g, 255 - this.rgba.b, this.rgba.a));
  }
  blend(t) {
    const n = t.rgba, i = this.rgba.a, r = n.a, s = i + r * (1 - i);
    if (s < 1e-6)
      return j.transparent;
    const a = this.rgba.r * i / s + n.r * r * (1 - i) / s, u = this.rgba.g * i / s + n.g * r * (1 - i) / s, o = this.rgba.b * i / s + n.b * r * (1 - i) / s;
    return new j(new w(a, u, o, s));
  }
  makeOpaque(t) {
    if (this.isOpaque() || t.rgba.a !== 1)
      return this;
    const { r: n, g: i, b: r, a: s } = this.rgba;
    return new j(new w(
      t.rgba.r - s * (t.rgba.r - n),
      t.rgba.g - s * (t.rgba.g - i),
      t.rgba.b - s * (t.rgba.b - r),
      1
    ));
  }
  flatten(...t) {
    const n = t.reduceRight((i, r) => j._flatten(r, i));
    return j._flatten(this, n);
  }
  static _flatten(t, n) {
    const i = 1 - t.rgba.a;
    return new j(new w(
      i * n.rgba.r + t.rgba.a * t.rgba.r,
      i * n.rgba.g + t.rgba.a * t.rgba.g,
      i * n.rgba.b + t.rgba.a * t.rgba.b
    ));
  }
  toString() {
    return this._toString || (this._toString = j.Format.CSS.format(this)), this._toString;
  }
  toNumber32Bit() {
    return this._toNumber32Bit || (this._toNumber32Bit = (this.rgba.r << 24 | this.rgba.g << 16 | this.rgba.b << 8 | this.rgba.a * 255 << 0) >>> 0), this._toNumber32Bit;
  }
  static getLighterColor(t, n, i) {
    if (t.isLighterThan(n))
      return t;
    i = i || 0.5;
    const r = t.getRelativeLuminance(), s = n.getRelativeLuminance();
    return i = i * (s - r) / s, t.lighten(i);
  }
  static getDarkerColor(t, n, i) {
    if (t.isDarkerThan(n))
      return t;
    i = i || 0.5;
    const r = t.getRelativeLuminance(), s = n.getRelativeLuminance();
    return i = i * (r - s) / r, t.darken(i);
  }
};
j.white = new j(new w(255, 255, 255, 1)), j.black = new j(new w(0, 0, 0, 1)), j.red = new j(new w(255, 0, 0, 1)), j.blue = new j(new w(0, 0, 255, 1)), j.green = new j(new w(0, 255, 0, 1)), j.cyan = new j(new w(0, 255, 255, 1)), j.lightgrey = new j(new w(211, 211, 211, 1)), j.transparent = new j(new w(0, 0, 0, 0));
let Zt = j;
(function(e) {
  (function(t) {
    (function(n) {
      function i(b) {
        return b.rgba.a === 1 ? `rgb(${b.rgba.r}, ${b.rgba.g}, ${b.rgba.b})` : e.Format.CSS.formatRGBA(b);
      }
      n.formatRGB = i;
      function r(b) {
        return `rgba(${b.rgba.r}, ${b.rgba.g}, ${b.rgba.b}, ${+b.rgba.a.toFixed(2)})`;
      }
      n.formatRGBA = r;
      function s(b) {
        return b.hsla.a === 1 ? `hsl(${b.hsla.h}, ${(b.hsla.s * 100).toFixed(2)}%, ${(b.hsla.l * 100).toFixed(2)}%)` : e.Format.CSS.formatHSLA(b);
      }
      n.formatHSL = s;
      function a(b) {
        return `hsla(${b.hsla.h}, ${(b.hsla.s * 100).toFixed(2)}%, ${(b.hsla.l * 100).toFixed(2)}%, ${b.hsla.a.toFixed(2)})`;
      }
      n.formatHSLA = a;
      function u(b) {
        const A = b.toString(16);
        return A.length !== 2 ? "0" + A : A;
      }
      function o(b) {
        return `#${u(b.rgba.r)}${u(b.rgba.g)}${u(b.rgba.b)}`;
      }
      n.formatHex = o;
      function c(b, A = !1) {
        return A && b.rgba.a === 1 ? e.Format.CSS.formatHex(b) : `#${u(b.rgba.r)}${u(b.rgba.g)}${u(b.rgba.b)}${u(Math.round(b.rgba.a * 255))}`;
      }
      n.formatHexA = c;
      function h(b) {
        return b.isOpaque() ? e.Format.CSS.formatHex(b) : e.Format.CSS.formatRGBA(b);
      }
      n.format = h;
      function f(b) {
        var A, v, x, R, N, E, U;
        if (b === "transparent")
          return e.transparent;
        if (b.startsWith("#"))
          return p(b);
        if (b.startsWith("rgba(")) {
          const D = b.match(/rgba\((?<r>(?:\+|-)?\d+), *(?<g>(?:\+|-)?\d+), *(?<b>(?:\+|-)?\d+), *(?<a>(?:\+|-)?\d+(\.\d+)?)\)/);
          if (!D)
            throw new Error("Invalid color format " + b);
          const S = parseInt(((A = D.groups) == null ? void 0 : A.r) ?? "0"), X = parseInt(((v = D.groups) == null ? void 0 : v.g) ?? "0"), ie = parseInt(((x = D.groups) == null ? void 0 : x.b) ?? "0"), Y = parseFloat(((R = D.groups) == null ? void 0 : R.a) ?? "0");
          return new e(new w(S, X, ie, Y));
        }
        if (b.startsWith("rgb(")) {
          const D = b.match(/rgb\((?<r>(?:\+|-)?\d+), *(?<g>(?:\+|-)?\d+), *(?<b>(?:\+|-)?\d+)\)/);
          if (!D)
            throw new Error("Invalid color format " + b);
          const S = parseInt(((N = D.groups) == null ? void 0 : N.r) ?? "0"), X = parseInt(((E = D.groups) == null ? void 0 : E.g) ?? "0"), ie = parseInt(((U = D.groups) == null ? void 0 : U.b) ?? "0");
          return new e(new w(S, X, ie));
        }
        return _(b);
      }
      n.parse = f;
      function _(b) {
        switch (b) {
          case "aliceblue":
            return new e(new w(240, 248, 255, 1));
          case "antiquewhite":
            return new e(new w(250, 235, 215, 1));
          case "aqua":
            return new e(new w(0, 255, 255, 1));
          case "aquamarine":
            return new e(new w(127, 255, 212, 1));
          case "azure":
            return new e(new w(240, 255, 255, 1));
          case "beige":
            return new e(new w(245, 245, 220, 1));
          case "bisque":
            return new e(new w(255, 228, 196, 1));
          case "black":
            return new e(new w(0, 0, 0, 1));
          case "blanchedalmond":
            return new e(new w(255, 235, 205, 1));
          case "blue":
            return new e(new w(0, 0, 255, 1));
          case "blueviolet":
            return new e(new w(138, 43, 226, 1));
          case "brown":
            return new e(new w(165, 42, 42, 1));
          case "burlywood":
            return new e(new w(222, 184, 135, 1));
          case "cadetblue":
            return new e(new w(95, 158, 160, 1));
          case "chartreuse":
            return new e(new w(127, 255, 0, 1));
          case "chocolate":
            return new e(new w(210, 105, 30, 1));
          case "coral":
            return new e(new w(255, 127, 80, 1));
          case "cornflowerblue":
            return new e(new w(100, 149, 237, 1));
          case "cornsilk":
            return new e(new w(255, 248, 220, 1));
          case "crimson":
            return new e(new w(220, 20, 60, 1));
          case "cyan":
            return new e(new w(0, 255, 255, 1));
          case "darkblue":
            return new e(new w(0, 0, 139, 1));
          case "darkcyan":
            return new e(new w(0, 139, 139, 1));
          case "darkgoldenrod":
            return new e(new w(184, 134, 11, 1));
          case "darkgray":
            return new e(new w(169, 169, 169, 1));
          case "darkgreen":
            return new e(new w(0, 100, 0, 1));
          case "darkgrey":
            return new e(new w(169, 169, 169, 1));
          case "darkkhaki":
            return new e(new w(189, 183, 107, 1));
          case "darkmagenta":
            return new e(new w(139, 0, 139, 1));
          case "darkolivegreen":
            return new e(new w(85, 107, 47, 1));
          case "darkorange":
            return new e(new w(255, 140, 0, 1));
          case "darkorchid":
            return new e(new w(153, 50, 204, 1));
          case "darkred":
            return new e(new w(139, 0, 0, 1));
          case "darksalmon":
            return new e(new w(233, 150, 122, 1));
          case "darkseagreen":
            return new e(new w(143, 188, 143, 1));
          case "darkslateblue":
            return new e(new w(72, 61, 139, 1));
          case "darkslategray":
            return new e(new w(47, 79, 79, 1));
          case "darkslategrey":
            return new e(new w(47, 79, 79, 1));
          case "darkturquoise":
            return new e(new w(0, 206, 209, 1));
          case "darkviolet":
            return new e(new w(148, 0, 211, 1));
          case "deeppink":
            return new e(new w(255, 20, 147, 1));
          case "deepskyblue":
            return new e(new w(0, 191, 255, 1));
          case "dimgray":
            return new e(new w(105, 105, 105, 1));
          case "dimgrey":
            return new e(new w(105, 105, 105, 1));
          case "dodgerblue":
            return new e(new w(30, 144, 255, 1));
          case "firebrick":
            return new e(new w(178, 34, 34, 1));
          case "floralwhite":
            return new e(new w(255, 250, 240, 1));
          case "forestgreen":
            return new e(new w(34, 139, 34, 1));
          case "fuchsia":
            return new e(new w(255, 0, 255, 1));
          case "gainsboro":
            return new e(new w(220, 220, 220, 1));
          case "ghostwhite":
            return new e(new w(248, 248, 255, 1));
          case "gold":
            return new e(new w(255, 215, 0, 1));
          case "goldenrod":
            return new e(new w(218, 165, 32, 1));
          case "gray":
            return new e(new w(128, 128, 128, 1));
          case "green":
            return new e(new w(0, 128, 0, 1));
          case "greenyellow":
            return new e(new w(173, 255, 47, 1));
          case "grey":
            return new e(new w(128, 128, 128, 1));
          case "honeydew":
            return new e(new w(240, 255, 240, 1));
          case "hotpink":
            return new e(new w(255, 105, 180, 1));
          case "indianred":
            return new e(new w(205, 92, 92, 1));
          case "indigo":
            return new e(new w(75, 0, 130, 1));
          case "ivory":
            return new e(new w(255, 255, 240, 1));
          case "khaki":
            return new e(new w(240, 230, 140, 1));
          case "lavender":
            return new e(new w(230, 230, 250, 1));
          case "lavenderblush":
            return new e(new w(255, 240, 245, 1));
          case "lawngreen":
            return new e(new w(124, 252, 0, 1));
          case "lemonchiffon":
            return new e(new w(255, 250, 205, 1));
          case "lightblue":
            return new e(new w(173, 216, 230, 1));
          case "lightcoral":
            return new e(new w(240, 128, 128, 1));
          case "lightcyan":
            return new e(new w(224, 255, 255, 1));
          case "lightgoldenrodyellow":
            return new e(new w(250, 250, 210, 1));
          case "lightgray":
            return new e(new w(211, 211, 211, 1));
          case "lightgreen":
            return new e(new w(144, 238, 144, 1));
          case "lightgrey":
            return new e(new w(211, 211, 211, 1));
          case "lightpink":
            return new e(new w(255, 182, 193, 1));
          case "lightsalmon":
            return new e(new w(255, 160, 122, 1));
          case "lightseagreen":
            return new e(new w(32, 178, 170, 1));
          case "lightskyblue":
            return new e(new w(135, 206, 250, 1));
          case "lightslategray":
            return new e(new w(119, 136, 153, 1));
          case "lightslategrey":
            return new e(new w(119, 136, 153, 1));
          case "lightsteelblue":
            return new e(new w(176, 196, 222, 1));
          case "lightyellow":
            return new e(new w(255, 255, 224, 1));
          case "lime":
            return new e(new w(0, 255, 0, 1));
          case "limegreen":
            return new e(new w(50, 205, 50, 1));
          case "linen":
            return new e(new w(250, 240, 230, 1));
          case "magenta":
            return new e(new w(255, 0, 255, 1));
          case "maroon":
            return new e(new w(128, 0, 0, 1));
          case "mediumaquamarine":
            return new e(new w(102, 205, 170, 1));
          case "mediumblue":
            return new e(new w(0, 0, 205, 1));
          case "mediumorchid":
            return new e(new w(186, 85, 211, 1));
          case "mediumpurple":
            return new e(new w(147, 112, 219, 1));
          case "mediumseagreen":
            return new e(new w(60, 179, 113, 1));
          case "mediumslateblue":
            return new e(new w(123, 104, 238, 1));
          case "mediumspringgreen":
            return new e(new w(0, 250, 154, 1));
          case "mediumturquoise":
            return new e(new w(72, 209, 204, 1));
          case "mediumvioletred":
            return new e(new w(199, 21, 133, 1));
          case "midnightblue":
            return new e(new w(25, 25, 112, 1));
          case "mintcream":
            return new e(new w(245, 255, 250, 1));
          case "mistyrose":
            return new e(new w(255, 228, 225, 1));
          case "moccasin":
            return new e(new w(255, 228, 181, 1));
          case "navajowhite":
            return new e(new w(255, 222, 173, 1));
          case "navy":
            return new e(new w(0, 0, 128, 1));
          case "oldlace":
            return new e(new w(253, 245, 230, 1));
          case "olive":
            return new e(new w(128, 128, 0, 1));
          case "olivedrab":
            return new e(new w(107, 142, 35, 1));
          case "orange":
            return new e(new w(255, 165, 0, 1));
          case "orangered":
            return new e(new w(255, 69, 0, 1));
          case "orchid":
            return new e(new w(218, 112, 214, 1));
          case "palegoldenrod":
            return new e(new w(238, 232, 170, 1));
          case "palegreen":
            return new e(new w(152, 251, 152, 1));
          case "paleturquoise":
            return new e(new w(175, 238, 238, 1));
          case "palevioletred":
            return new e(new w(219, 112, 147, 1));
          case "papayawhip":
            return new e(new w(255, 239, 213, 1));
          case "peachpuff":
            return new e(new w(255, 218, 185, 1));
          case "peru":
            return new e(new w(205, 133, 63, 1));
          case "pink":
            return new e(new w(255, 192, 203, 1));
          case "plum":
            return new e(new w(221, 160, 221, 1));
          case "powderblue":
            return new e(new w(176, 224, 230, 1));
          case "purple":
            return new e(new w(128, 0, 128, 1));
          case "rebeccapurple":
            return new e(new w(102, 51, 153, 1));
          case "red":
            return new e(new w(255, 0, 0, 1));
          case "rosybrown":
            return new e(new w(188, 143, 143, 1));
          case "royalblue":
            return new e(new w(65, 105, 225, 1));
          case "saddlebrown":
            return new e(new w(139, 69, 19, 1));
          case "salmon":
            return new e(new w(250, 128, 114, 1));
          case "sandybrown":
            return new e(new w(244, 164, 96, 1));
          case "seagreen":
            return new e(new w(46, 139, 87, 1));
          case "seashell":
            return new e(new w(255, 245, 238, 1));
          case "sienna":
            return new e(new w(160, 82, 45, 1));
          case "silver":
            return new e(new w(192, 192, 192, 1));
          case "skyblue":
            return new e(new w(135, 206, 235, 1));
          case "slateblue":
            return new e(new w(106, 90, 205, 1));
          case "slategray":
            return new e(new w(112, 128, 144, 1));
          case "slategrey":
            return new e(new w(112, 128, 144, 1));
          case "snow":
            return new e(new w(255, 250, 250, 1));
          case "springgreen":
            return new e(new w(0, 255, 127, 1));
          case "steelblue":
            return new e(new w(70, 130, 180, 1));
          case "tan":
            return new e(new w(210, 180, 140, 1));
          case "teal":
            return new e(new w(0, 128, 128, 1));
          case "thistle":
            return new e(new w(216, 191, 216, 1));
          case "tomato":
            return new e(new w(255, 99, 71, 1));
          case "turquoise":
            return new e(new w(64, 224, 208, 1));
          case "violet":
            return new e(new w(238, 130, 238, 1));
          case "wheat":
            return new e(new w(245, 222, 179, 1));
          case "white":
            return new e(new w(255, 255, 255, 1));
          case "whitesmoke":
            return new e(new w(245, 245, 245, 1));
          case "yellow":
            return new e(new w(255, 255, 0, 1));
          case "yellowgreen":
            return new e(new w(154, 205, 50, 1));
          default:
            return null;
        }
      }
      function p(b) {
        const A = b.length;
        if (A === 0 || b.charCodeAt(0) !== L.Hash)
          return null;
        if (A === 7) {
          const v = 16 * d(b.charCodeAt(1)) + d(b.charCodeAt(2)), x = 16 * d(b.charCodeAt(3)) + d(b.charCodeAt(4)), R = 16 * d(b.charCodeAt(5)) + d(b.charCodeAt(6));
          return new e(new w(v, x, R, 1));
        }
        if (A === 9) {
          const v = 16 * d(b.charCodeAt(1)) + d(b.charCodeAt(2)), x = 16 * d(b.charCodeAt(3)) + d(b.charCodeAt(4)), R = 16 * d(b.charCodeAt(5)) + d(b.charCodeAt(6)), N = 16 * d(b.charCodeAt(7)) + d(b.charCodeAt(8));
          return new e(new w(v, x, R, N / 255));
        }
        if (A === 4) {
          const v = d(b.charCodeAt(1)), x = d(b.charCodeAt(2)), R = d(b.charCodeAt(3));
          return new e(new w(16 * v + v, 16 * x + x, 16 * R + R));
        }
        if (A === 5) {
          const v = d(b.charCodeAt(1)), x = d(b.charCodeAt(2)), R = d(b.charCodeAt(3)), N = d(b.charCodeAt(4));
          return new e(new w(16 * v + v, 16 * x + x, 16 * R + R, (16 * N + N) / 255));
        }
        return null;
      }
      n.parseHex = p;
      function d(b) {
        switch (b) {
          case L.Digit0:
            return 0;
          case L.Digit1:
            return 1;
          case L.Digit2:
            return 2;
          case L.Digit3:
            return 3;
          case L.Digit4:
            return 4;
          case L.Digit5:
            return 5;
          case L.Digit6:
            return 6;
          case L.Digit7:
            return 7;
          case L.Digit8:
            return 8;
          case L.Digit9:
            return 9;
          case L.a:
            return 10;
          case L.A:
            return 10;
          case L.b:
            return 11;
          case L.B:
            return 11;
          case L.c:
            return 12;
          case L.C:
            return 12;
          case L.d:
            return 13;
          case L.D:
            return 13;
          case L.e:
            return 14;
          case L.E:
            return 14;
          case L.f:
            return 15;
          case L.F:
            return 15;
        }
        return 0;
      }
    })(t.CSS || (t.CSS = {}));
  })(e.Format || (e.Format = {}));
})(Zt);
function xs(e) {
  const t = [];
  for (const n of e) {
    const i = Number(n);
    (i || i === 0 && n.replace(/\s/g, "") !== "") && t.push(i);
  }
  return t;
}
function wi(e, t, n, i) {
  return {
    red: e / 255,
    blue: n / 255,
    green: t / 255,
    alpha: i
  };
}
function kt(e, t) {
  const n = t.index, i = t[0].length;
  if (n === void 0)
    return;
  const r = e.positionAt(n);
  return {
    startLineNumber: r.lineNumber,
    startColumn: r.column,
    endLineNumber: r.lineNumber,
    endColumn: r.column + i
  };
}
function uu(e, t) {
  if (!e)
    return;
  const n = Zt.Format.CSS.parseHex(t);
  if (n)
    return {
      range: e,
      color: wi(n.rgba.r, n.rgba.g, n.rgba.b, n.rgba.a)
    };
}
function Sr(e, t, n) {
  if (!e || t.length !== 1)
    return;
  const r = t[0].values(), s = xs(r);
  return {
    range: e,
    color: wi(s[0], s[1], s[2], n ? s[3] : 1)
  };
}
function Pr(e, t, n) {
  if (!e || t.length !== 1)
    return;
  const r = t[0].values(), s = xs(r), a = new Zt(new Re(
    s[0],
    s[1] / 100,
    s[2] / 100,
    n ? s[3] : 1
  ));
  return {
    range: e,
    color: wi(a.rgba.r, a.rgba.g, a.rgba.b, a.rgba.a)
  };
}
function Ft(e, t) {
  return typeof e == "string" ? [...e.matchAll(t)] : e.findMatches(t);
}
function ou(e) {
  const t = [], i = Ft(e, /\b(rgb|rgba|hsl|hsla)(\([0-9\s,.\%]*\))|\s+(#)([A-Fa-f0-9]{6})\b|\s+(#)([A-Fa-f0-9]{8})\b|^(#)([A-Fa-f0-9]{6})\b|^(#)([A-Fa-f0-9]{8})\b/gm);
  if (i.length > 0)
    for (const r of i) {
      const s = r.filter((c) => c !== void 0), a = s[1], u = s[2];
      if (!u)
        continue;
      let o;
      if (a === "rgb") {
        const c = /^\(\s*(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\s*,\s*(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\s*,\s*(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\s*\)$/gm;
        o = Sr(kt(e, r), Ft(u, c), !1);
      } else if (a === "rgba") {
        const c = /^\(\s*(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\s*,\s*(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\s*,\s*(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\s*,\s*(0[.][0-9]+|[.][0-9]+|[01][.]|[01])\s*\)$/gm;
        o = Sr(kt(e, r), Ft(u, c), !0);
      } else if (a === "hsl") {
        const c = /^\(\s*(36[0]|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9])\s*,\s*(100|\d{1,2}[.]\d*|\d{1,2})%\s*,\s*(100|\d{1,2}[.]\d*|\d{1,2})%\s*\)$/gm;
        o = Pr(kt(e, r), Ft(u, c), !1);
      } else if (a === "hsla") {
        const c = /^\(\s*(36[0]|3[0-5][0-9]|[12][0-9][0-9]|[1-9]?[0-9])\s*,\s*(100|\d{1,2}[.]\d*|\d{1,2})%\s*,\s*(100|\d{1,2}[.]\d*|\d{1,2})%\s*,\s*(0[.][0-9]+|[.][0-9]+|[01][.]|[01])\s*\)$/gm;
        o = Pr(kt(e, r), Ft(u, c), !0);
      } else a === "#" && (o = uu(kt(e, r), a + u));
      o && t.push(o);
    }
  return t;
}
function cu(e) {
  return !e || typeof e.getValue != "function" || typeof e.positionAt != "function" ? [] : ou(e);
}
const yr = new RegExp("\\bMARK:\\s*(.*)$", "d"), hu = /^-+|-+$/g;
function fu(e, t) {
  var i;
  let n = [];
  if (t.findRegionSectionHeaders && ((i = t.foldingRules) != null && i.markers)) {
    const r = mu(e, t);
    n = n.concat(r);
  }
  if (t.findMarkSectionHeaders) {
    const r = gu(e);
    n = n.concat(r);
  }
  return n;
}
function mu(e, t) {
  const n = [], i = e.getLineCount();
  for (let r = 1; r <= i; r++) {
    const s = e.getLineContent(r), a = s.match(t.foldingRules.markers.start);
    if (a) {
      const u = { startLineNumber: r, startColumn: a[0].length + 1, endLineNumber: r, endColumn: s.length + 1 };
      if (u.endColumn > u.startColumn) {
        const o = {
          range: u,
          ...As(s.substring(a[0].length)),
          shouldBeInComments: !1
        };
        (o.text || o.hasSeparatorLine) && n.push(o);
      }
    }
  }
  return n;
}
function gu(e) {
  const t = [], n = e.getLineCount();
  for (let i = 1; i <= n; i++) {
    const r = e.getLineContent(i);
    _u(r, i, t);
  }
  return t;
}
function _u(e, t, n) {
  yr.lastIndex = 0;
  const i = yr.exec(e);
  if (i) {
    const r = i.indices[1][0] + 1, s = i.indices[1][1] + 1, a = { startLineNumber: t, startColumn: r, endLineNumber: t, endColumn: s };
    if (a.endColumn > a.startColumn) {
      const u = {
        range: a,
        ...As(i[1]),
        shouldBeInComments: !0
      };
      (u.text || u.hasSeparatorLine) && n.push(u);
    }
  }
}
function As(e) {
  e = e.trim();
  const t = e.startsWith("-");
  return e = e.replace(hu, ""), { text: e, hasSeparatorLine: t };
}
function ze(e) {
  return e === L.Slash || e === L.Backslash;
}
function vs(e) {
  return e.replace(/[\\/]/g, C.sep);
}
function bu(e) {
  return e.indexOf("/") === -1 && (e = vs(e)), /^[a-zA-Z]:(\/|$)/.test(e) && (e = "/" + e), e;
}
function Br(e, t = C.sep) {
  if (!e)
    return "";
  const n = e.length, i = e.charCodeAt(0);
  if (ze(i)) {
    if (ze(e.charCodeAt(1)) && !ze(e.charCodeAt(2))) {
      let s = 3;
      const a = s;
      for (; s < n && !ze(e.charCodeAt(s)); s++)
        ;
      if (a !== s && !ze(e.charCodeAt(s + 1))) {
        for (s += 1; s < n; s++)
          if (ze(e.charCodeAt(s)))
            return e.slice(0, s + 1).replace(/[\\/]/g, t);
      }
    }
    return t;
  } else if (du(i) && e.charCodeAt(1) === L.Colon)
    return ze(e.charCodeAt(2)) ? e.slice(0, 2) + t : e.slice(0, 2);
  let r = e.indexOf("://");
  if (r !== -1) {
    for (r += 3; r < n; r++)
      if (ze(e.charCodeAt(r)))
        return e.slice(0, r + 1);
  }
  return "";
}
function Or(e, t, n, i = un) {
  if (e === t)
    return !0;
  if (!e || !t || t.length > e.length)
    return !1;
  if (n) {
    if (!Ta(e, t))
      return !1;
    if (t.length === e.length)
      return !0;
    let s = t.length;
    return t.charAt(t.length - 1) === i && s--, e.charAt(s) === i;
  }
  return t.charAt(t.length - 1) !== i && (t += i), e.indexOf(t) === 0;
}
function du(e) {
  return e >= L.A && e <= L.Z || e >= L.a && e <= L.z;
}
var fe;
(function(e) {
  e.inMemory = "inmemory", e.vscode = "vscode", e.internal = "private", e.walkThrough = "walkThrough", e.walkThroughSnippet = "walkThroughSnippet", e.http = "http", e.https = "https", e.file = "file", e.mailto = "mailto", e.untitled = "untitled", e.data = "data", e.command = "command", e.vscodeRemote = "vscode-remote", e.vscodeRemoteResource = "vscode-remote-resource", e.vscodeManagedRemoteResource = "vscode-managed-remote-resource", e.vscodeUserData = "vscode-userdata", e.vscodeCustomEditor = "vscode-custom-editor", e.vscodeNotebookCell = "vscode-notebook-cell", e.vscodeNotebookCellMetadata = "vscode-notebook-cell-metadata", e.vscodeNotebookCellMetadataDiff = "vscode-notebook-cell-metadata-diff", e.vscodeNotebookCellOutput = "vscode-notebook-cell-output", e.vscodeNotebookCellOutputDiff = "vscode-notebook-cell-output-diff", e.vscodeNotebookMetadata = "vscode-notebook-metadata", e.vscodeInteractiveInput = "vscode-interactive-input", e.vscodeSettings = "vscode-settings", e.vscodeWorkspaceTrust = "vscode-workspace-trust", e.vscodeTerminal = "vscode-terminal", e.vscodeChatCodeBlock = "vscode-chat-code-block", e.vscodeChatCodeCompareBlock = "vscode-chat-code-compare-block", e.vscodeChatSesssion = "vscode-chat-editor", e.webviewPanel = "webview-panel", e.vscodeWebview = "vscode-webview", e.extension = "extension", e.vscodeFileResource = "vscode-file", e.tmp = "tmp", e.vsls = "vsls", e.vscodeSourceControl = "vscode-scm", e.commentsInput = "comment", e.codeSetting = "code-setting", e.outputChannel = "output", e.accessibleView = "accessible-view";
})(fe || (fe = {}));
const wu = "tkn";
class Lu {
  constructor() {
    this._hosts = /* @__PURE__ */ Object.create(null), this._ports = /* @__PURE__ */ Object.create(null), this._connectionTokens = /* @__PURE__ */ Object.create(null), this._preferredWebSchema = "http", this._delegate = null, this._serverRootPath = "/";
  }
  setPreferredWebSchema(t) {
    this._preferredWebSchema = t;
  }
  setDelegate(t) {
    this._delegate = t;
  }
  setServerRootPath(t, n) {
    this._serverRootPath = C.join(n ?? "/", Nu(t));
  }
  getServerRootPath() {
    return this._serverRootPath;
  }
  get _remoteResourcesPath() {
    return C.join(this._serverRootPath, fe.vscodeRemoteResource);
  }
  set(t, n, i) {
    this._hosts[t] = n, this._ports[t] = i;
  }
  setConnectionToken(t, n) {
    this._connectionTokens[t] = n;
  }
  getPreferredWebSchema() {
    return this._preferredWebSchema;
  }
  rewrite(t) {
    if (this._delegate)
      try {
        return this._delegate(t);
      } catch (u) {
        return St(u), t;
      }
    const n = t.authority;
    let i = this._hosts[n];
    i && i.indexOf(":") !== -1 && i.indexOf("[") === -1 && (i = `[${i}]`);
    const r = this._ports[n], s = this._connectionTokens[n];
    let a = `path=${encodeURIComponent(t.path)}`;
    return typeof s == "string" && (a += `&${wu}=${encodeURIComponent(s)}`), oe.from({
      scheme: ma ? this._preferredWebSchema : fe.vscodeRemoteResource,
      authority: `${i}:${r}`,
      path: this._remoteResourcesPath,
      query: a
    });
  }
}
const pu = new Lu();
function Nu(e) {
  return `${e.quality ?? "oss"}-${e.commit ?? "dev"}`;
}
const Eu = "vscode-app", pt = class pt {
  constructor() {
    this.staticBrowserUris = new Wn(), this.appResourcePathUrls = /* @__PURE__ */ new Map();
  }
  registerAppResourcePathUrl(t, n) {
    this.appResourcePathUrls.set(t, n);
  }
  toUrl(t) {
    var i;
    let n = this.appResourcePathUrls.get(t);
    return typeof n == "function" && (n = n()), new URL(n ?? t, ((i = globalThis.location) == null ? void 0 : i.href) ?? import.meta.url).toString();
  }
  asBrowserUri(t) {
    const n = this.toUri(t, { toUrl: this.toUrl.bind(this) });
    return this.uriToBrowserUri(n);
  }
  uriToBrowserUri(t) {
    return t.scheme === fe.vscodeRemote ? pu.rewrite(t) : t.scheme === fe.file && (fa || _a === `${fe.vscodeFileResource}://${pt.FALLBACK_AUTHORITY}`) ? t.with({
      scheme: fe.vscodeFileResource,
      authority: t.authority || pt.FALLBACK_AUTHORITY,
      query: null,
      fragment: null
    }) : this.staticBrowserUris.get(t) ?? t;
  }
  asFileUri(t) {
    const n = this.toUri(t, { toUrl: this.toUrl.bind(this) });
    return this.uriToFileUri(n);
  }
  uriToFileUri(t) {
    return t.scheme === fe.vscodeFileResource ? t.with({
      scheme: fe.file,
      authority: t.authority !== pt.FALLBACK_AUTHORITY ? t.authority : null,
      query: null,
      fragment: null
    }) : t;
  }
  toUri(t, n) {
    if (oe.isUri(t))
      return t;
    if (globalThis._VSCODE_FILE_ROOT) {
      const i = globalThis._VSCODE_FILE_ROOT;
      if (/^\w[\w\d+.-]*:\/\//.test(i))
        return oe.joinPath(oe.parse(i, !0), t);
      const r = ul(i, t);
      return oe.file(r);
    }
    return oe.parse(n.toUrl(t));
  }
  registerStaticBrowserUri(t, n) {
    return this.staticBrowserUris.set(t, n), $t(() => {
      this.staticBrowserUris.get(t) === n && this.staticBrowserUris.delete(t);
    });
  }
  getRegisteredBrowserUris() {
    return this.staticBrowserUris.keys();
  }
};
pt.FALLBACK_AUTHORITY = Eu;
let ui = pt;
new ui();
var Vr;
(function(e) {
  const t = /* @__PURE__ */ new Map([
    ["1", { "Cross-Origin-Opener-Policy": "same-origin" }],
    ["2", { "Cross-Origin-Embedder-Policy": "require-corp" }],
    ["3", { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp" }]
  ]);
  e.CoopAndCoep = Object.freeze(t.get("3"));
  const n = "vscode-coi";
  function i(s) {
    let a;
    typeof s == "string" ? a = new URL(s).searchParams : s instanceof URL ? a = s.searchParams : oe.isUri(s) && (a = new URL(s.toString(!0)).searchParams);
    const u = a == null ? void 0 : a.get(n);
    if (u)
      return t.get(u);
  }
  e.getHeadersFromQuery = i;
  function r(s, a, u) {
    if (!globalThis.crossOriginIsolated)
      return;
    const o = a && u ? "3" : u ? "2" : "1";
    s instanceof URLSearchParams ? s.set(n, o) : s[n] = o;
  }
  e.addSearchParam = r;
})(Vr || (Vr = {}));
function ye(e) {
  return wn(e, !0);
}
class xu {
  constructor(t) {
    this._ignorePathCasing = t;
  }
  compare(t, n, i = !1) {
    return t === n ? 0 : Aa(this.getComparisonKey(t, i), this.getComparisonKey(n, i));
  }
  isEqual(t, n, i = !1) {
    return t === n ? !0 : !t || !n ? !1 : this.getComparisonKey(t, i) === this.getComparisonKey(n, i);
  }
  getComparisonKey(t, n = !1) {
    return t.with({
      path: this._ignorePathCasing(t) ? t.path.toLowerCase() : void 0,
      fragment: n ? null : void 0
    }).toString();
  }
  ignorePathCasing(t) {
    return this._ignorePathCasing(t);
  }
  isEqualOrParent(t, n, i = !1) {
    if (t.scheme === n.scheme) {
      if (t.scheme === fe.file)
        return Or(ye(t), ye(n), this._ignorePathCasing(t)) && t.query === n.query && (i || t.fragment === n.fragment);
      if (qr(t.authority, n.authority))
        return Or(t.path, n.path, this._ignorePathCasing(t), "/") && t.query === n.query && (i || t.fragment === n.fragment);
    }
    return !1;
  }
  joinPath(t, ...n) {
    return oe.joinPath(t, ...n);
  }
  basenameOrAuthority(t) {
    return Au(t) || t.authority;
  }
  basename(t) {
    return C.basename(t.path);
  }
  extname(t) {
    return C.extname(t.path);
  }
  dirname(t) {
    if (t.path.length === 0)
      return t;
    let n;
    return t.scheme === fe.file ? n = oe.file(hl(ye(t))).path : (n = C.dirname(t.path), t.authority && n.length && n.charCodeAt(0) !== L.Slash && (console.error(`dirname("${t.toString})) resulted in a relative path`), n = "/")), t.with({
      path: n
    });
  }
  normalizePath(t) {
    if (!t.path.length)
      return t;
    let n;
    return t.scheme === fe.file ? n = oe.file(ll(ye(t))).path : n = C.normalize(t.path), t.with({
      path: n
    });
  }
  relativePath(t, n) {
    if (t.scheme !== n.scheme || !qr(t.authority, n.authority))
      return;
    if (t.scheme === fe.file) {
      const s = cl(ye(t), ye(n));
      return Tt ? vs(s) : s;
    }
    let i = t.path || "/";
    const r = n.path || "/";
    if (this._ignorePathCasing(t)) {
      let s = 0;
      for (const a = Math.min(i.length, r.length); s < a && !(i.charCodeAt(s) !== r.charCodeAt(s) && i.charAt(s).toLowerCase() !== r.charAt(s).toLowerCase()); s++)
        ;
      i = r.substr(0, s) + i.substr(s);
    }
    return C.relative(i, r);
  }
  resolvePath(t, n) {
    if (t.scheme === fe.file) {
      const i = oe.file(ol(ye(t), n));
      return t.with({
        authority: i.authority,
        path: i.path
      });
    }
    return n = bu(n), t.with({
      path: C.resolve(t.path, n)
    });
  }
  isAbsolutePath(t) {
    return !!t.path && t.path[0] === "/";
  }
  isEqualAuthority(t, n) {
    return t === n || t !== void 0 && n !== void 0 && Ra(t, n);
  }
  hasTrailingPathSeparator(t, n = un) {
    if (t.scheme === fe.file) {
      const i = ye(t);
      return i.length > Br(i).length && i[i.length - 1] === n;
    } else {
      const i = t.path;
      return i.length > 1 && i.charCodeAt(i.length - 1) === L.Slash && !/^[a-zA-Z]:(\/$|\\$)/.test(t.fsPath);
    }
  }
  removeTrailingPathSeparator(t, n = un) {
    return Hr(t, n) ? t.with({ path: t.path.substr(0, t.path.length - 1) }) : t;
  }
  addTrailingPathSeparator(t, n = un) {
    let i = !1;
    if (t.scheme === fe.file) {
      const r = ye(t);
      i = r !== void 0 && r.length === Br(r).length && r[r.length - 1] === n;
    } else {
      n = "/";
      const r = t.path;
      i = r.length === 1 && r.charCodeAt(r.length - 1) === L.Slash;
    }
    return !i && !Hr(t, n) ? t.with({ path: t.path + "/" }) : t;
  }
}
const Q = new xu(() => !1);
Q.isEqual.bind(Q);
Q.isEqualOrParent.bind(Q);
Q.getComparisonKey.bind(Q);
Q.basenameOrAuthority.bind(Q);
const Au = Q.basename.bind(Q);
Q.extname.bind(Q);
Q.dirname.bind(Q);
Q.joinPath.bind(Q);
Q.normalizePath.bind(Q);
Q.relativePath.bind(Q);
Q.resolvePath.bind(Q);
Q.isAbsolutePath.bind(Q);
const qr = Q.isEqualAuthority.bind(Q), Hr = Q.hasTrailingPathSeparator.bind(Q);
Q.removeTrailingPathSeparator.bind(Q);
Q.addTrailingPathSeparator.bind(Q);
var Wr;
(function(e) {
  e.META_DATA_LABEL = "label", e.META_DATA_DESCRIPTION = "description", e.META_DATA_SIZE = "size", e.META_DATA_MIME = "mime";
  function t(n) {
    const i = /* @__PURE__ */ new Map();
    n.path.substring(n.path.indexOf(";") + 1, n.path.lastIndexOf(";")).split(";").forEach((a) => {
      const [u, o] = a.split(":");
      u && o && i.set(u, o);
    });
    const s = n.path.substring(0, n.path.indexOf(";"));
    return s && i.set(e.META_DATA_MIME, s), i;
  }
  e.parseMetaData = t;
})(Wr || (Wr = {}));
var Gr;
(function(e) {
  e[e.Resolved = 0] = "Resolved", e[e.Rejected = 1] = "Rejected";
})(Gr || (Gr = {}));
var $r;
(function(e) {
  async function t(i) {
    let r;
    const s = await Promise.all(i.map((a) => a.then((u) => u, (u) => {
      r || (r = u);
    })));
    if (typeof r < "u")
      throw r;
    return s;
  }
  e.settled = t;
  function n(i) {
    return new Promise(async (r, s) => {
      try {
        await i(r, s);
      } catch (a) {
        s(a);
      }
    });
  }
  e.withAsyncBody = n;
})($r || ($r = {}));
var De;
(function(e) {
  e[e.Initial = 0] = "Initial", e[e.DoneOK = 1] = "DoneOK", e[e.DoneError = 2] = "DoneError";
})(De || (De = {}));
const be = class be {
  static fromArray(t) {
    return new be((n) => {
      n.emitMany(t);
    });
  }
  static fromPromise(t) {
    return new be(async (n) => {
      n.emitMany(await t);
    });
  }
  static fromPromisesResolveOrder(t) {
    return new be(async (n) => {
      await Promise.all(t.map(async (i) => n.emitOne(await i)));
    });
  }
  static merge(t) {
    return new be(async (n) => {
      await Promise.all(t.map(async (i) => {
        for await (const r of i)
          n.emitOne(r);
      }));
    });
  }
  constructor(t, n) {
    this._state = De.Initial, this._results = [], this._error = null, this._onReturn = n, this._onStateChanged = new Ae(), queueMicrotask(async () => {
      const i = {
        emitOne: (r) => this.emitOne(r),
        emitMany: (r) => this.emitMany(r),
        reject: (r) => this.reject(r)
      };
      try {
        await Promise.resolve(t(i)), this.resolve();
      } catch (r) {
        this.reject(r);
      } finally {
        i.emitOne = void 0, i.emitMany = void 0, i.reject = void 0;
      }
    });
  }
  [Symbol.asyncIterator]() {
    let t = 0;
    return {
      next: async () => {
        do {
          if (this._state === De.DoneError)
            throw this._error;
          if (t < this._results.length)
            return { done: !1, value: this._results[t++] };
          if (this._state === De.DoneOK)
            return { done: !0, value: void 0 };
          await fn.toPromise(this._onStateChanged.event);
        } while (!0);
      },
      return: async () => {
        var n;
        return (n = this._onReturn) == null || n.call(this), { done: !0, value: void 0 };
      }
    };
  }
  static map(t, n) {
    return new be(async (i) => {
      for await (const r of t)
        i.emitOne(n(r));
    });
  }
  map(t) {
    return be.map(this, t);
  }
  static filter(t, n) {
    return new be(async (i) => {
      for await (const r of t)
        n(r) && i.emitOne(r);
    });
  }
  filter(t) {
    return be.filter(this, t);
  }
  static coalesce(t) {
    return be.filter(t, (n) => !!n);
  }
  coalesce() {
    return be.coalesce(this);
  }
  static async toPromise(t) {
    const n = [];
    for await (const i of t)
      n.push(i);
    return n;
  }
  toPromise() {
    return be.toPromise(this);
  }
  emitOne(t) {
    this._state === De.Initial && (this._results.push(t), this._onStateChanged.fire());
  }
  emitMany(t) {
    this._state === De.Initial && (this._results = this._results.concat(t), this._onStateChanged.fire());
  }
  resolve() {
    this._state === De.Initial && (this._state = De.DoneOK, this._onStateChanged.fire());
  }
  reject(t) {
    this._state === De.Initial && (this._state = De.DoneError, this._error = t, this._onStateChanged.fire());
  }
};
be.EMPTY = be.fromArray([]);
let zr = be;
class vu {
  constructor(t) {
    this.values = t, this.prefixSum = new Uint32Array(t.length), this.prefixSumValidIndex = new Int32Array(1), this.prefixSumValidIndex[0] = -1;
  }
  getCount() {
    return this.values.length;
  }
  insertValues(t, n) {
    t = lt(t);
    const i = this.values, r = this.prefixSum, s = n.length;
    return s === 0 ? !1 : (this.values = new Uint32Array(i.length + s), this.values.set(i.subarray(0, t), 0), this.values.set(i.subarray(t), t + s), this.values.set(n, t), t - 1 < this.prefixSumValidIndex[0] && (this.prefixSumValidIndex[0] = t - 1), this.prefixSum = new Uint32Array(this.values.length), this.prefixSumValidIndex[0] >= 0 && this.prefixSum.set(r.subarray(0, this.prefixSumValidIndex[0] + 1)), !0);
  }
  setValue(t, n) {
    return t = lt(t), n = lt(n), this.values[t] === n ? !1 : (this.values[t] = n, t - 1 < this.prefixSumValidIndex[0] && (this.prefixSumValidIndex[0] = t - 1), !0);
  }
  removeValues(t, n) {
    t = lt(t), n = lt(n);
    const i = this.values, r = this.prefixSum;
    if (t >= i.length)
      return !1;
    const s = i.length - t;
    return n >= s && (n = s), n === 0 ? !1 : (this.values = new Uint32Array(i.length - n), this.values.set(i.subarray(0, t), 0), this.values.set(i.subarray(t + n), t), this.prefixSum = new Uint32Array(this.values.length), t - 1 < this.prefixSumValidIndex[0] && (this.prefixSumValidIndex[0] = t - 1), this.prefixSumValidIndex[0] >= 0 && this.prefixSum.set(r.subarray(0, this.prefixSumValidIndex[0] + 1)), !0);
  }
  getTotalSum() {
    return this.values.length === 0 ? 0 : this._getPrefixSum(this.values.length - 1);
  }
  getPrefixSum(t) {
    return t < 0 ? 0 : (t = lt(t), this._getPrefixSum(t));
  }
  _getPrefixSum(t) {
    if (t <= this.prefixSumValidIndex[0])
      return this.prefixSum[t];
    let n = this.prefixSumValidIndex[0] + 1;
    n === 0 && (this.prefixSum[0] = this.values[0], n++), t >= this.values.length && (t = this.values.length - 1);
    for (let i = n; i <= t; i++)
      this.prefixSum[i] = this.prefixSum[i - 1] + this.values[i];
    return this.prefixSumValidIndex[0] = Math.max(this.prefixSumValidIndex[0], t), this.prefixSum[t];
  }
  getIndexOf(t) {
    t = Math.floor(t), this.getTotalSum();
    let n = 0, i = this.values.length - 1, r = 0, s = 0, a = 0;
    for (; n <= i; )
      if (r = n + (i - n) / 2 | 0, s = this.prefixSum[r], a = s - this.values[r], t < a)
        i = r - 1;
      else if (t >= s)
        n = r + 1;
      else
        break;
    return new Ru(r, t - a);
  }
}
class Ru {
  constructor(t, n) {
    this.index = t, this.remainder = n, this._prefixSumIndexOfResultBrand = void 0, this.index = t, this.remainder = n;
  }
}
class Tu {
  constructor(t, n, i, r) {
    this._uri = t, this._lines = n, this._eol = i, this._versionId = r, this._lineStarts = null, this._cachedTextValue = null;
  }
  dispose() {
    this._lines.length = 0;
  }
  get version() {
    return this._versionId;
  }
  getText() {
    return this._cachedTextValue === null && (this._cachedTextValue = this._lines.join(this._eol)), this._cachedTextValue;
  }
  onEvents(t) {
    t.eol && t.eol !== this._eol && (this._eol = t.eol, this._lineStarts = null);
    const n = t.changes;
    for (const i of n)
      this._acceptDeleteRange(i.range), this._acceptInsertText(new W(i.range.startLineNumber, i.range.startColumn), i.text);
    this._versionId = t.versionId, this._cachedTextValue = null;
  }
  _ensureLineStarts() {
    if (!this._lineStarts) {
      const t = this._eol.length, n = this._lines.length, i = new Uint32Array(n);
      for (let r = 0; r < n; r++)
        i[r] = this._lines[r].length + t;
      this._lineStarts = new vu(i);
    }
  }
  _setLineText(t, n) {
    this._lines[t] = n, this._lineStarts && this._lineStarts.setValue(t, this._lines[t].length + this._eol.length);
  }
  _acceptDeleteRange(t) {
    if (t.startLineNumber === t.endLineNumber) {
      if (t.startColumn === t.endColumn)
        return;
      this._setLineText(t.startLineNumber - 1, this._lines[t.startLineNumber - 1].substring(0, t.startColumn - 1) + this._lines[t.startLineNumber - 1].substring(t.endColumn - 1));
      return;
    }
    this._setLineText(t.startLineNumber - 1, this._lines[t.startLineNumber - 1].substring(0, t.startColumn - 1) + this._lines[t.endLineNumber - 1].substring(t.endColumn - 1)), this._lines.splice(t.startLineNumber, t.endLineNumber - t.startLineNumber), this._lineStarts && this._lineStarts.removeValues(t.startLineNumber, t.endLineNumber - t.startLineNumber);
  }
  _acceptInsertText(t, n) {
    if (n.length === 0)
      return;
    const i = is(n);
    if (i.length === 1) {
      this._setLineText(t.lineNumber - 1, this._lines[t.lineNumber - 1].substring(0, t.column - 1) + i[0] + this._lines[t.lineNumber - 1].substring(t.column - 1));
      return;
    }
    i[i.length - 1] += this._lines[t.lineNumber - 1].substring(t.column - 1), this._setLineText(t.lineNumber - 1, this._lines[t.lineNumber - 1].substring(0, t.column - 1) + i[0]);
    const r = new Uint32Array(i.length - 1);
    for (let s = 1; s < i.length; s++)
      this._lines.splice(t.lineNumber + s - 1, 0, i[s]), r[s - 1] = i[s].length + this._eol.length;
    this._lineStarts && this._lineStarts.insertValues(t.lineNumber, r);
  }
}
const Uu = "workerTextModelSync";
class Mu {
  constructor() {
    this._models = /* @__PURE__ */ Object.create(null);
  }
  bindToServer(t) {
    t.setChannel(Uu, this);
  }
  getModel(t) {
    return this._models[t];
  }
  getModels() {
    const t = [];
    return Object.keys(this._models).forEach((n) => t.push(this._models[n])), t;
  }
  $acceptNewModel(t) {
    this._models[t.url] = new Du(oe.parse(t.url), t.lines, t.EOL, t.versionId);
  }
  $acceptModelChanged(t, n) {
    if (!this._models[t])
      return;
    this._models[t].onEvents(n);
  }
  $acceptRemovedModel(t) {
    this._models[t] && delete this._models[t];
  }
}
class Du extends Tu {
  get uri() {
    return this._uri;
  }
  get eol() {
    return this._eol;
  }
  getValue() {
    return this.getText();
  }
  findMatches(t) {
    const n = [];
    for (let i = 0; i < this._lines.length; i++) {
      const r = this._lines[i], s = this.offsetAt(new W(i + 1, 1)), a = r.matchAll(t);
      for (const u of a)
        (u.index || u.index === 0) && (u.index = u.index + s), n.push(u);
    }
    return n;
  }
  getLinesContent() {
    return this._lines.slice(0);
  }
  getLineCount() {
    return this._lines.length;
  }
  getLineContent(t) {
    return this._lines[t - 1];
  }
  getWordAtPosition(t, n) {
    const i = bi(t.column, bs(n), this._lines[t.lineNumber - 1], 0);
    return i ? new F(
      t.lineNumber,
      i.startColumn,
      t.lineNumber,
      i.endColumn
    ) : null;
  }
  getWordUntilPosition(t, n) {
    const i = this.getWordAtPosition(t, n);
    return i ? {
      word: this._lines[t.lineNumber - 1].substring(i.startColumn - 1, t.column - 1),
      startColumn: i.startColumn,
      endColumn: t.column
    } : {
      word: "",
      startColumn: t.column,
      endColumn: t.column
    };
  }
  words(t) {
    const n = this._lines, i = this._wordenize.bind(this);
    let r = 0, s = "", a = 0, u = [];
    return {
      *[Symbol.iterator]() {
        for (; ; )
          if (a < u.length) {
            const o = s.substring(u[a].start, u[a].end);
            a += 1, yield o;
          } else if (r < n.length)
            s = n[r], u = i(s, t), a = 0, r += 1;
          else
            break;
      }
    };
  }
  getLineWords(t, n) {
    const i = this._lines[t - 1], r = this._wordenize(i, n), s = [];
    for (const a of r)
      s.push({
        word: i.substring(a.start, a.end),
        startColumn: a.start + 1,
        endColumn: a.end + 1
      });
    return s;
  }
  _wordenize(t, n) {
    const i = [];
    let r;
    for (n.lastIndex = 0; (r = n.exec(t)) && r[0].length !== 0; )
      i.push({ start: r.index, end: r.index + r[0].length });
    return i;
  }
  getValueInRange(t) {
    if (t = this._validateRange(t), t.startLineNumber === t.endLineNumber)
      return this._lines[t.startLineNumber - 1].substring(t.startColumn - 1, t.endColumn - 1);
    const n = this._eol, i = t.startLineNumber - 1, r = t.endLineNumber - 1, s = [];
    s.push(this._lines[i].substring(t.startColumn - 1));
    for (let a = i + 1; a < r; a++)
      s.push(this._lines[a]);
    return s.push(this._lines[r].substring(0, t.endColumn - 1)), s.join(n);
  }
  offsetAt(t) {
    return t = this._validatePosition(t), this._ensureLineStarts(), this._lineStarts.getPrefixSum(t.lineNumber - 2) + (t.column - 1);
  }
  positionAt(t) {
    t = Math.floor(t), t = Math.max(0, t), this._ensureLineStarts();
    const n = this._lineStarts.getIndexOf(t), i = this._lines[n.index].length;
    return {
      lineNumber: 1 + n.index,
      column: 1 + Math.min(n.remainder, i)
    };
  }
  _validateRange(t) {
    const n = this._validatePosition({ lineNumber: t.startLineNumber, column: t.startColumn }), i = this._validatePosition({ lineNumber: t.endLineNumber, column: t.endColumn });
    return n.lineNumber !== t.startLineNumber || n.column !== t.startColumn || i.lineNumber !== t.endLineNumber || i.column !== t.endColumn ? {
      startLineNumber: n.lineNumber,
      startColumn: n.column,
      endLineNumber: i.lineNumber,
      endColumn: i.column
    } : t;
  }
  _validatePosition(t) {
    if (!W.isIPosition(t))
      throw new Error("bad position");
    let { lineNumber: n, column: i } = t, r = !1;
    if (n < 1)
      n = 1, i = 1, r = !0;
    else if (n > this._lines.length)
      n = this._lines.length, i = this._lines[n - 1].length + 1, r = !0;
    else {
      const s = this._lines[n - 1].length + 1;
      i < 1 ? (i = 1, r = !0) : i > s && (i = s, r = !0);
    }
    return r ? { lineNumber: n, column: i } : t;
  }
}
const Mn = class Mn {
  constructor() {
    this._workerTextModelSyncServer = new Mu();
  }
  dispose() {
  }
  _getModel(t) {
    return this._workerTextModelSyncServer.getModel(t);
  }
  _getModels() {
    return this._workerTextModelSyncServer.getModels();
  }
  $acceptNewModel(t) {
    this._workerTextModelSyncServer.$acceptNewModel(t);
  }
  $acceptModelChanged(t, n) {
    this._workerTextModelSyncServer.$acceptModelChanged(t, n);
  }
  $acceptRemovedModel(t) {
    this._workerTextModelSyncServer.$acceptRemovedModel(t);
  }
  async $computeUnicodeHighlights(t, n, i) {
    const r = this._getModel(t);
    return r ? Pl.computeUnicodeHighlights(r, n, i) : { ranges: [], hasMore: !1, ambiguousCharacterCount: 0, invisibleCharacterCount: 0, nonBasicAsciiCharacterCount: 0 };
  }
  async $findSectionHeaders(t, n) {
    const i = this._getModel(t);
    return i ? fu(i, n) : [];
  }
  async $computeDiff(t, n, i, r) {
    const s = this._getModel(t), a = this._getModel(n);
    return !s || !a ? null : It.computeDiff(s, a, i, r);
  }
  static computeDiff(t, n, i, r) {
    const s = r === "advanced" ? Bn.getDefault() : Bn.getLegacy(), a = t.getLinesContent(), u = n.getLinesContent(), o = s.computeDiff(a, u, i), c = o.changes.length > 0 ? !1 : this._modelsAreIdentical(t, n);
    function h(f) {
      return f.map(
        (_) => {
          var p;
          return [_.original.startLineNumber, _.original.endLineNumberExclusive, _.modified.startLineNumber, _.modified.endLineNumberExclusive, (p = _.innerChanges) == null ? void 0 : p.map((d) => [
            d.originalRange.startLineNumber,
            d.originalRange.startColumn,
            d.originalRange.endLineNumber,
            d.originalRange.endColumn,
            d.modifiedRange.startLineNumber,
            d.modifiedRange.startColumn,
            d.modifiedRange.endLineNumber,
            d.modifiedRange.endColumn
          ])];
        }
      );
    }
    return {
      identical: c,
      quitEarly: o.hitTimeout,
      changes: h(o.changes),
      moves: o.moves.map((f) => [
        f.lineRangeMapping.original.startLineNumber,
        f.lineRangeMapping.original.endLineNumberExclusive,
        f.lineRangeMapping.modified.startLineNumber,
        f.lineRangeMapping.modified.endLineNumberExclusive,
        h(f.changes)
      ])
    };
  }
  static _modelsAreIdentical(t, n) {
    const i = t.getLineCount(), r = n.getLineCount();
    if (i !== r)
      return !1;
    for (let s = 1; s <= i; s++) {
      const a = t.getLineContent(s), u = n.getLineContent(s);
      if (a !== u)
        return !1;
    }
    return !0;
  }
  async $computeDirtyDiff(t, n, i) {
    const r = this._getModel(t), s = this._getModel(n);
    if (!r || !s)
      return null;
    const a = r.getLinesContent(), u = s.getLinesContent();
    return new Ns(a, u, {
      shouldComputeCharChanges: !1,
      shouldPostProcessCharChanges: !1,
      shouldIgnoreTrimWhitespace: i,
      shouldMakePrettyDiff: !0,
      maxComputationTime: 1e3
    }).computeDiff().changes;
  }
  async $computeMoreMinimalEdits(t, n, i) {
    const r = this._getModel(t);
    if (!r)
      return n;
    const s = [];
    let a;
    n = n.slice(0).sort((o, c) => {
      if (o.range && c.range)
        return F.compareRangesUsingStarts(o.range, c.range);
      const h = o.range ? 0 : 1, f = c.range ? 0 : 1;
      return h - f;
    });
    let u = 0;
    for (let o = 1; o < n.length; o++)
      F.getEndPosition(n[u].range).equals(F.getStartPosition(n[o].range)) ? (n[u].range = F.fromPositions(F.getStartPosition(n[u].range), F.getEndPosition(n[o].range)), n[u].text += n[o].text) : (u++, n[u] = n[o]);
    n.length = u + 1;
    for (let { range: o, text: c, eol: h } of n) {
      if (typeof h == "number" && (a = h), F.isEmpty(o) && !c)
        continue;
      const f = r.getValueInRange(o);
      if (c = c.replace(/\r\n|\n|\r/g, r.eol), f === c)
        continue;
      if (Math.max(c.length, f.length) > It._diffLimit) {
        s.push({ range: o, text: c });
        continue;
      }
      const _ = Ha(f, c, i), p = r.offsetAt(F.lift(o).getStartPosition());
      for (const d of _) {
        const b = r.positionAt(p + d.originalStart), A = r.positionAt(p + d.originalStart + d.originalLength), v = {
          text: c.substr(d.modifiedStart, d.modifiedLength),
          range: { startLineNumber: b.lineNumber, startColumn: b.column, endLineNumber: A.lineNumber, endColumn: A.column }
        };
        r.getValueInRange(v.range) !== v.text && s.push(v);
      }
    }
    return typeof a == "number" && s.push({ eol: a, text: "", range: { startLineNumber: 0, startColumn: 0, endLineNumber: 0, endColumn: 0 } }), s;
  }
  $computeHumanReadableDiff(t, n, i) {
    const r = this._getModel(t);
    if (!r)
      return n;
    const s = [];
    let a;
    n = n.slice(0).sort((u, o) => {
      if (u.range && o.range)
        return F.compareRangesUsingStarts(u.range, o.range);
      const c = u.range ? 0 : 1, h = o.range ? 0 : 1;
      return c - h;
    });
    for (let { range: u, text: o, eol: c } of n) {
      let b = function(v, x) {
        return new W(
          v.lineNumber + x.lineNumber - 1,
          x.lineNumber === 1 ? v.column + x.column - 1 : x.column
        );
      }, A = function(v, x) {
        const R = [];
        for (let N = x.startLineNumber; N <= x.endLineNumber; N++) {
          const E = v[N - 1];
          N === x.startLineNumber && N === x.endLineNumber ? R.push(E.substring(x.startColumn - 1, x.endColumn - 1)) : N === x.startLineNumber ? R.push(E.substring(x.startColumn - 1)) : N === x.endLineNumber ? R.push(E.substring(0, x.endColumn - 1)) : R.push(E);
        }
        return R;
      };
      if (typeof c == "number" && (a = c), F.isEmpty(u) && !o)
        continue;
      const h = r.getValueInRange(u);
      if (o = o.replace(/\r\n|\n|\r/g, r.eol), h === o)
        continue;
      if (Math.max(o.length, h.length) > It._diffLimit) {
        s.push({ range: u, text: o });
        continue;
      }
      const f = h.split(/\r\n|\n|\r/), _ = o.split(/\r\n|\n|\r/), p = Bn.getDefault().computeDiff(f, _, i), d = F.lift(u).getStartPosition();
      for (const v of p.changes)
        if (v.innerChanges)
          for (const x of v.innerChanges)
            s.push({
              range: F.fromPositions(b(d, x.originalRange.getStartPosition()), b(d, x.originalRange.getEndPosition())),
              text: A(_, x.modifiedRange).join(r.eol)
            });
        else
          throw new ae("The experimental diff algorithm always produces inner changes");
    }
    return typeof a == "number" && s.push({ eol: a, text: "", range: { startLineNumber: 0, startColumn: 0, endLineNumber: 0, endColumn: 0 } }), s;
  }
  async $computeLinks(t) {
    const n = this._getModel(t);
    return n ? ja(n) : null;
  }
  async $computeDefaultDocumentColors(t) {
    const n = this._getModel(t);
    return n ? cu(n) : null;
  }
  async $textualSuggest(t, n, i, r) {
    const s = new Dn(), a = new RegExp(i, r), u = /* @__PURE__ */ new Set();
    e: for (const o of t) {
      const c = this._getModel(o);
      if (c) {
        for (const h of c.words(a))
          if (!(h === n || !isNaN(Number(h))) && (u.add(h), u.size > It._suggestionsLimit))
            break e;
      }
    }
    return { words: Array.from(u), duration: s.elapsed() };
  }
  async $computeWordRanges(t, n, i, r) {
    const s = this._getModel(t);
    if (!s)
      return /* @__PURE__ */ Object.create(null);
    const a = new RegExp(i, r), u = /* @__PURE__ */ Object.create(null);
    for (let o = n.startLineNumber; o < n.endLineNumber; o++) {
      const c = s.getLineWords(o, a);
      for (const h of c) {
        if (!isNaN(Number(h.word)))
          continue;
        let f = u[h.word];
        f || (f = [], u[h.word] = f), f.push({
          startLineNumber: o,
          startColumn: h.startColumn,
          endLineNumber: o,
          endColumn: h.endColumn
        });
      }
    }
    return u;
  }
  async $navigateValueSet(t, n, i, r, s) {
    const a = this._getModel(t);
    if (!a)
      return null;
    const u = new RegExp(r, s);
    n.startColumn === n.endColumn && (n = {
      startLineNumber: n.startLineNumber,
      startColumn: n.startColumn,
      endLineNumber: n.endLineNumber,
      endColumn: n.endColumn + 1
    });
    const o = a.getValueInRange(n), c = a.getWordAtPosition({ lineNumber: n.startLineNumber, column: n.startColumn }, u);
    if (!c)
      return null;
    const h = a.getValueInRange(c);
    return jn.INSTANCE.navigateValueSet(n, o, c, h, i);
  }
};
Mn._diffLimit = 1e5, Mn._suggestionsLimit = 1e4;
let oi = Mn;
class It extends oi {
  constructor(t, n) {
    super(), this._host = t, this._foreignModuleFactory = n, this._foreignModule = null;
  }
  async $ping() {
    return "pong";
  }
  $loadForeignModule(t, n, i) {
    const a = {
      host: Tl(i, (u, o) => this._host.$fhr(u, o)),
      getMirrorModels: () => this._getModels()
    };
    return this._foreignModuleFactory ? (this._foreignModule = this._foreignModuleFactory(a, n), Promise.resolve(Rl(this._foreignModule))) : Promise.reject(new Error("Unexpected usage"));
  }
  $fmr(t, n) {
    if (!this._foreignModule || typeof this._foreignModule[t] != "function")
      return Promise.reject(new Error("Missing requestHandler or method: " + t));
    try {
      return Promise.resolve(this._foreignModule[t].apply(this._foreignModule, n));
    } catch (i) {
      return Promise.reject(i);
    }
  }
}
typeof importScripts == "function" && (globalThis.monaco = Al());
let ci = !1;
function ku(e) {
  if (ci)
    return;
  ci = !0;
  const t = new Va((n) => {
    globalThis.postMessage(n);
  }, (n) => new It(ri.getChannel(n), e));
  globalThis.onmessage = (n) => {
    t.onmessage(n.data);
  };
}
globalThis.onmessage = (e) => {
  ci || ku(null);
};
export {
  ku as initialize
};
