
grammar pcode;


program : instruction_line  (NEWLINE instruction_line)* EOF
        ;

instruction_line
        : WHITESPACE* instruction WHITESPACE* comment?
        ;

instruction
        : block | end_block | end_blocks
        | watch
        | alarm
        | macro
        | call_macro
        | increment_rc
        | restart
        | stop
        | pause
        | hold
        | wait
        | mark
        | batch
        | command
        | comment
        | blank
        | error
        ;

block           : time? BLOCK ((COLON WHITESPACE* block_name)? | inst_error );
block_name      : identifier_ext ; 
end_block       : time? END_BLOCK ;
end_blocks      : time? END_BLOCKS ;

watch           : time? WATCH ( (COLON WHITESPACE* condition)? | inst_error );
alarm           : time? ALARM ( (COLON WHITESPACE* condition)? | inst_error );
macro           : time? MACRO ((COLON WHITESPACE* macro_name)? | inst_error );
macro_name      : identifier_ext ; 
 
condition       : condition_lhs WHITESPACE* compare_op WHITESPACE* condition_rhs ;
compare_op      : COMPARE_OP ;
condition_lhs   : .*?  ~(NEWLINE | HASH | COMPARE_OP | COLON);
condition_rhs   : .*?  ~(NEWLINE | HASH | COMPARE_OP | COLON);

increment_rc    : time? INCREMENT_RC ;
restart         : time? RESTART ;
stop            : time? STOP ;
pause           : time? PAUSE ( (COLON WHITESPACE* duration)? | inst_error);
hold            : time? HOLD  ( (COLON WHITESPACE* duration)? | inst_error) ;
wait            : time? WAIT  ( (COLON WHITESPACE* duration)? | inst_error) ;
duration        : .*?  ~(NEWLINE | HASH | COLON);

mark            : time? MARK COLON WHITESPACE* mark_name?;
mark_name       : identifier_ext ;

batch            : time? BATCH COLON WHITESPACE* batch_name?;
batch_name       : identifier_ext ;

call_macro      : time? CALL_MACRO COLON WHITESPACE* call_macro_name?;
call_macro_name : identifier_ext ;

time            : timeexp WHITESPACE+ ;
timeexp         : POSITIVE_FLOAT ;

comment         : HASH comment_text ;
comment_text    : .*? ~NEWLINE;

blank           : WHITESPACE* ;

command         : time? command_name (COLON WHITESPACE* command_args)?;
command_name    : identifier ;
command_args    : .*?  ~(NEWLINE | HASH);

identifier      : IDENTIFIER ;
identifier_ext  : IDENTIFIER | .*?  ~(NEWLINE | HASH);

inst_error      : .*?  ~(NEWLINE | HASH );
error           : .*?  ~(NEWLINE | HASH);

fragment LETTER : [a-zA-Z] ;
fragment DIGIT  : [0-9] ;


WATCH           : 'Watch' ;
ALARM           : 'Alarm' ;
MACRO           : 'Macro' ;
STOP            : 'Stop' ;
PAUSE           : 'Pause' ;
HOLD            : 'Hold' ;
WAIT            : 'Wait' ;
RESTART         : 'Restart' ;
MARK            : 'Mark' ;
BATCH           : 'Batch' ;
CALL_MACRO      : 'Call macro' ;
BLOCK           : 'Block' ;
END_BLOCK       : 'End block' ;
END_BLOCKS      : 'End blocks' ;
INCREMENT_RC    : 'Increment run counter' ;

IDENTIFIER      : LETTER ( (LETTER | DIGIT | WHITESPACE | UNDERSCORE)* (LETTER | DIGIT | UNDERSCORE)+ )? ;

POSITIVE_FLOAT  : DIGIT+ (PERIOD DIGIT+)?
                | DIGIT+ (COMMA DIGIT+)?
                ;

COMPARE_OP      : '=' | '==' | '<=' | '<' | '>=' | '>' | '!=' ;

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