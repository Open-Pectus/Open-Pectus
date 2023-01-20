
grammar pcode;


program : WHITESPACE* instruction (NEWLINE WHITESPACE* instruction)* EOF;

instruction
        : block comment?
        | command comment?
        | watch comment?
        | alarm comment?
        | comment
        ;

block   : WHITESPACE* (timeexp WHITESPACE)? BLOCK COLON WHITESPACE* block_name;
block_name : IDENTIFIER; 

// (?P<ws>\s+)?((?P<time>(?P<timed1>\d*)\.(?P<timed2>\d*))\s)?(?P<command>[^:#]+)?(: (?P<argument>[^#\n]+))?((?P<comment>\s?#.*$))?
command : WHITESPACE* (timeexp WHITESPACE)? command_name (COLON WHITESPACE* command_args)?;
command_name: IDENTIFIER;
command_args: .*?  ~(NEWLINE | HASH);

watch   : WATCH ;
alarm   : ALARM ;

timeexp : FLOAT;

comment : HASH comment_text ;
comment_text : .*? ~NEWLINE;

//syntax_error : ANY ~(HASH | NEWLINE)+;

fragment LETTER     : [a-zA-Z] ;
fragment DIGIT      : [0-9] ;

fragment A:('a'|'A');
fragment B:('b'|'B');
fragment C:('c'|'C');
fragment D:('d'|'D');
fragment E:('e'|'E');
fragment F:('f'|'F');
fragment G:('g'|'G');
fragment H:('h'|'H');
fragment I:('i'|'I');
fragment J:('j'|'J');
fragment K:('k'|'K');
fragment L:('l'|'L');
fragment M:('m'|'M');
fragment N:('n'|'N');
fragment O:('o'|'O');
fragment P:('p'|'P');
fragment Q:('q'|'Q');
fragment R:('r'|'R');
fragment S:('s'|'S');
fragment T:('t'|'T');
fragment U:('u'|'U');
fragment V:('v'|'V');
fragment W:('w'|'W');
fragment X:('x'|'X');
fragment Y:('y'|'Y');
fragment Z:('z'|'Z');

BLOCK   : B L O C K ;
WATCH   : W A T C H ;
ALARM   : A L A R M ;

IDENTIFIER: LETTER (LETTER | DIGIT | WHITESPACE)*;  // allow whitespace? For command "Inlet PU01: VA01" what is name and what is args?
FLOAT   : DIGIT+ (PERIOD DIGIT+)?
        | DIGIT+ (COMMA DIGIT+)?
        ;

WHITESPACE: SPACE | TAB ;
PERIOD: '.' ;
COMMA:  ',' ;
SPACE:  ' ' ;
TAB:    '\t' ;
HASH    : '#' ;
COLON   : ':' ;

NEWLINE	: ( '\r' | '\n' | '\r' '\n' ) ;


// see tips in chapter 33 https://tomassetti.me/antlr-mega-tutorial/ 
// maybe channels for comments?
// maybe channels for cmd_args?
ANY : . ;