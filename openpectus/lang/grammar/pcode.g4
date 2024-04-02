
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
 
condition       : condition_tag WHITESPACE* compare_op WHITESPACE* condition_value (WHITESPACE* condition_unit)? WHITESPACE*
                | condition_error ;
condition_tag   : identifier ;
compare_op      : COMPARE_OP ;
condition_value : POSITIVE_FLOAT | MINUS POSITIVE_FLOAT ; // TODO support text 
condition_unit  : CONDITION_UNIT; 
condition_error : .*?  ~(NEWLINE | HASH);

increment_rc    : time? INCREMENT_RC ;
restart         : time? RESTART ;
stop            : time? STOP ;
pause           : time? PAUSE ;

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
RESTART : 'Restart' ;
MARK    : 'Mark' ;
BLOCK   : 'Block' ;
END_BLOCK       : 'End block' ;
END_BLOCKS      : 'End blocks' ;
INCREMENT_RC    : 'Increment run counter' ;

// does not play well with identifier - and is also not what we want
// CONDITION_UNIT  : UNIT_CHAR UNIT_CHAR? UNIT_CHAR? UNIT_CHAR? ;
// UNIT_CHAR       : LETTER | '%' | '/' ;


CONDITION_UNIT  : VOLUME_UNIT
                | MASS_UNIT
                | DISTANCE_UNIT
                | DURATION_UNIT
                | OTHER_UNIT
                ;

VOLUME_UNIT     : 'L' | 'mL' ;
MASS_UNIT       : 'kg' | 'g' ;
DISTANCE_UNIT   : 'm' | 'cm' ;
DURATION_UNIT   : 'h' | 'min' | 's';
OTHER_UNIT      : '%' | 'CV' | 'AU' | 'L/h' | 'kg/h' | 'ms/cm' ;

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