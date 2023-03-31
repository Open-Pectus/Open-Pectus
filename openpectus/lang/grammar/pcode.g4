
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
        | mark
        ;

block           : time? BLOCK COLON WHITESPACE* block_name; // allow whitespace before colon?
block_name      : IDENTIFIER; 
end_block       : time? END_BLOCK ;
end_blocks      : time? END_BLOCKS ;

command         : time? command_name (COLON WHITESPACE* command_args)?;
command_name    : IDENTIFIER;
command_args    : .*?  ~(NEWLINE | HASH);

watch           : time? WATCH (COLON WHITESPACE* condition)?;
alarm           : time? ALARM (COLON WHITESPACE* condition)?;
 
condition       : condition_tag WHITESPACE* compare_op WHITESPACE* condition_value (WHITESPACE* condition_unit)? WHITESPACE*
//condition       : condition_tag WHITESPACE* compare_op WHITESPACE* condition_value WHITESPACE* condition_unit?
                | condition_error;
condition_tag   : IDENTIFIER;
compare_op      : COMPARE_OP;
//condition_value : FLOAT;
condition_value : POSITIVE_FLOAT | MINUS POSITIVE_FLOAT ;
condition_unit  : CONDITION_UNIT; 

condition_error : .*?  ~(NEWLINE | HASH);

increment_rc    : time? INCREMENT_RC ;
stop            : time? STOP ;
pause           : time? PAUSE ;

mark            : time? MARK COLON WHITESPACE* mark_name?;
mark_name       : IDENTIFIER ;

time    : timeexp WHITESPACE+ ;
timeexp : POSITIVE_FLOAT ;

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
MARK    : M A R K ;
BLOCK   : B L O C K ;
END_BLOCK       : E N D SPACE BLOCK ;
END_BLOCKS      : E N D SPACE B L O C K S ;
INCREMENT_RC    : I N C R E M E N T SPACE R U N SPACE C O U N T E R ;

CONDITION_UNIT  : VOLUME_UNIT
                | MASS_UNIT
                | DISTANCE_UNIT
                | DURATION_UNIT
                | OTHER_UNIT
                ;

VOLUME_UNIT     : L | M L ;
MASS_UNIT       : K G | G ;
DISTANCE_UNIT   : M | C M ;
DURATION_UNIT   : H | M I N | S | S E C;
OTHER_UNIT      : '%' | C V | A U | L '/' H | K G '/' H | M S '/' C M ;
/*
Known units:
L|min|h|CV|s|mL        
CV|L|h|min|s|AU|L\/h|\%|bar|mS\/cm|g
CV|L|h|min|s|AU|L\/h|\%|bar|mS\/cm|g|kg\/h
h|min|s|L|CV|AU|L\/h|\%|bar|mS\/cm|g|kg\/h
duration_unit: h|min|s|L|CV
 */

IDENTIFIER : LETTER ( (LETTER | DIGIT | WHITESPACE | UNDERSCORE)* (LETTER | DIGIT | UNDERSCORE)+ )? ;

POSITIVE_FLOAT   : DIGIT+ (PERIOD DIGIT+)?
                 | DIGIT+ (COMMA DIGIT+)?
                 ;

COMPARE_OP : '=' | '==' | '<=' | '<' | '>=' | '>' | '!=';

WHITESPACE: SPACE | TAB ;
UNDERSCORE: '_' ;
PERIOD  : '.' ;
COMMA   : ',' ;
SPACE   : ' ' ;
TAB     : '\t' ;
HASH    : '#' ;
COLON   : ':' ;
MINUS   : '-' ;

NEWLINE	: ( '\r' | '\n' | '\r' '\n' ) ;


// see tips in chapter 33 https://tomassetti.me/antlr-mega-tutorial/ 
// maybe channels for comments?
// maybe channels for cmd_args?
// maybe channels for conditions?
ANY : . ;