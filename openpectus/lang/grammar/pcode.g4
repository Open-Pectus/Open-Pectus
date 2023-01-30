
grammar pcode;


program : WHITESPACE* instruction (NEWLINE WHITESPACE* instruction)* EOF;

instruction
        : builtin_command comment?
        | command comment?
        | comment
        | blank
        | error comment?
        ;

builtin_command
        : block
        | end_block | end_blocks
        | watch
        | alarm
        | increment_rc
        | stop
        | pause
        ;

block           : time? BLOCK COLON WHITESPACE* block_name; // allow whitespace before colon?
block_name      : IDENTIFIER; 
end_block       : time? END_BLOCK ;
end_blocks      : time? END_BLOCKS ;

// (?P<ws>\s+)?((?P<time>(?P<timed1>\d*)\.(?P<timed2>\d*))\s)?(?P<command>[^:#]+)?(: (?P<argument>[^#\n]+))?((?P<comment>\s?#.*$))?
command         : time? command_name (COLON WHITESPACE* command_args)?;
command_name    : IDENTIFIER;
command_args    : .*?  ~(NEWLINE | HASH);

watch           : time? WATCH (COLON WHITESPACE* condition)?;
alarm           : time? ALARM (COLON WHITESPACE* condition)?;
condition       : .*?  ~(NEWLINE | HASH);

increment_rc    : time? INCREMENT_RC ;
stop            : time? STOP ;
pause           : time? PAUSE ;

time    : timeexp WHITESPACE+ ;
timeexp : FLOAT ;

comment : HASH comment_text ;
comment_text : .*? ~NEWLINE;

blank   : WHITESPACE* ;

error   : .*?  ~(NEWLINE | HASH);


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

WATCH   : W A T C H ;
ALARM   : A L A R M ;
STOP    : S T O P  ;
PAUSE   : P A U S E ;
BLOCK   : B L O C K ;
END_BLOCK       : E N D SPACE BLOCK ;
END_BLOCKS      : E N D SPACE B L O C K S ;
INCREMENT_RC    : I N C R E M E N T SPACE R U N SPACE C O U N T E R ;

IDENTIFIER: LETTER (LETTER | DIGIT | WHITESPACE)*;
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