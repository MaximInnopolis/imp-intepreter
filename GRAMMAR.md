expr            : KEYWORD:VAR IDENTIFIER EQ expr
                : comparison-expr ((KEYWORD:AND|KEYWORD:OR)comp-expr)*

comparison-expr : NOT comparison-expr
                : arithmetic-expr((EEQ|NEQ|LESS|GREATER|LESS_OR_EQ|GREATER_OR_EQ) arithmetic-expr)*

arithmetic-expr : term ((PLUS|MINUS) term)*

term            : factor ((MUL|DIV) factor)*

factor          : (PLUS|MINUS) factor
                : power
 
pow             : atom (POW factor)*

atom            : INT|FLOAT|IDENTIFIER
                : LPAREN expr RPAREN
                : if-expr
                : for-expr
				: while-expr

if-expr			: KEYWORD:IF expr KEYWORD:THEN expr
				        (KEYWORD:ELIF expr KEYWORD:THEN expr)*
				        (KEYWORD:ELSE expr)?

for-expr		: KEYWORD:FOR IDENTIFIER EQ expr KEYWORD:TO expr 
				        (KEYWORD:STEP expr)? KEYWORD:THEN expr

while-expr	: KEYWORD:WHILE expr KEYWORD:THEN expr
