
grammar pcode;


program : instruction_line 
          (NEWLINE instruction_line)*
          EOF;

instruction_line
        : WHITESPACE* instruction WHITESPACE* comment?
        ;

instruction
        : block
        | end_block | end_blocks
        | watch
        | alarm
        | increment_rc
        | restart
        | stop
        | pause
        | hold
        | wait
        | mark
        | command
        | comment
        | blank
        | error
        ;


block           : time? BLOCK COLON WHITESPACE* block_name; // allow whitespace before colon?
block_name      : identifier ; 
end_block       : time? END_BLOCK ;
end_blocks      : time? END_BLOCKS ;

watch           : time? WATCH (COLON WHITESPACE* condition)?;
alarm           : time? ALARM (COLON WHITESPACE* condition)?;
 
condition       : condition_lhs WHITESPACE* compare_op WHITESPACE* condition_rhs ;
compare_op      : COMPARE_OP ;
condition_lhs   : .*?  ~(NEWLINE | HASH | COMPARE_OP | COLON);
condition_rhs   : .*?  ~(NEWLINE | HASH | COMPARE_OP | COLON);

increment_rc    : time? INCREMENT_RC ;
restart         : time? RESTART ;
stop            : time? STOP ;
pause           : time? PAUSE (COLON WHITESPACE* duration)? ;
hold            : time? HOLD (COLON WHITESPACE* duration)? ;
wait            : time? WAIT COLON WHITESPACE* duration ;
duration        : .*?  ~(NEWLINE | HASH | COLON);

mark            : time? MARK COLON WHITESPACE* mark_name?;
mark_name       : identifier ;

time    : timeexp WHITESPACE+ ;
timeexp : POSITIVE_FLOAT ;

comment : HASH comment_text ;
comment_text : .*? ~NEWLINE;

blank   : WHITESPACE* ;

command         : time? command_name (COLON WHITESPACE* command_args)?;
command_name    : identifier ;
command_args    : .*?  ~(NEWLINE | HASH);

identifier      : IDENTIFIER ;
error   : .*?  ~(NEWLINE | HASH);


fragment LETTER     : [a-zA-Z] ;
fragment DIGIT      : [0-9] ;


WATCH   : 'Watch' ;
ALARM   : 'Alarm' ;
STOP    : 'Stop' ;
PAUSE   : 'Pause' ;
HOLD    : 'Hold' ;
WAIT    : 'Wait' ;
RESTART : 'Restart' ;
MARK    : 'Mark' ;
BLOCK   : 'Block' ;
END_BLOCK       : 'End block' ;
END_BLOCKS      : 'End blocks' ;
INCREMENT_RC    : 'Increment run counter' ;

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