
grammar pcode;


program : INDENT* program_line (NEWLINE INDENT* program_line)* EOF;

program_line : block
        | command
        ;
// program_line : block (HASH comment)?
//         | command (HASH comment)?
//         ;
//        | comment
//        | syntax_error (HASH comment)?;
//        | watch | alarm;


block : INDENT* WHITESPACE* (timeexp WHITESPACE)? BLOCK COLON WHITESPACE* block_name;
block_name : IDENTIFIER; 


// (?P<ws>\s+)?((?P<time>(?P<timed1>\d*)\.(?P<timed2>\d*))\s)?(?P<command>[^:#]+)?(: (?P<argument>[^#\n]+))?((?P<comment>\s?#.*$))?
command : INDENT* WHITESPACE* (timeexp WHITESPACE)? cmd_name (COLON WHITESPACE* cmd_args)?;
cmd_name : IDENTIFIER;
//cmd_args : ANY+ ~(HASH | NEWLINE)+;
cmd_args : .*?  ~(NEWLINE | HASH);
timeexp : FLOAT;

comment : .*? ~NEWLINE;

//syntax_error : ANY ~(HASH | NEWLINE)+;

fragment LETTER     : [a-zA-Z] ;
fragment DIGIT      : [0-9] ;

fragment B: 'b'|'B' ;
fragment L: 'l'|'L' ;
fragment O: 'o'|'O' ;
fragment C: 'c'|'C' ;
fragment K: 'k'|'K' ;


HASH    : '#' ;
COLON   : ':' ;

//NAME    : LETTER+ ;
BLOCK   : B L O C K ;

IDENTIFIER: LETTER (LETTER | DIGIT)*;
FLOAT: DIGIT+ ('.' DIGIT+)? ;

WHITESPACE: ' ' ; //cannot skip because we need it in cmd_args
COMMA: ',' ;

NEWLINE	: ( '\r' | '\n' | '\r' '\n' ) ;
INDENT : '\t'; //TODO we should probabaly also support spaces - which complicates matters because it affects WHITESPACE


//TEXT: IDENTIFIER | '=' | ',' | '.' | WHITESPACE | ANY ;
//TEXT: (LETTER | DIGIT | '-' | '.' | '_' | ',' | ':' | '=' )+ ;

// see tips in chapter 33 https://tomassetti.me/antlr-mega-tutorial/ 
// maybe channels for comments?
// maybe channels for cmd_args?
ANY : . ;