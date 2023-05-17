```c
expr            : KEYWORD:VAR IDENTIFIER EQ expr
                : comparison-expr ((KEYWORD:AND|KEYWORD:OR)comp-expr)*
```

```c
comparison-expr : NOT comparison-expr
                : arithmetic-expr((EEQ|NEQ|LESS|GREATER|LESS_OR_EQ|GREATER_OR_EQ) arithmetic-expr)*
```

```c
arithmetic-expr : term ((PLUS|MINUS) term)*
```

```c
term            : factor ((MUL|DIV) factor)*
```

```c
factor          : (PLUS|MINUS) factor
                : power
 ```

 ```c
pow             : atom (POW factor)*
```

```c
atom            : INT|FLOAT|IDENTIFIER
                : LPAREN expr RPAREN
                : if_expr
                : for_expr
				: while_expr
```

```c
if_expr			: KEYWORD:IF expr KEYWORD:THEN expr
				        (KEYWORD:ELIF expr KEYWORD:THEN expr)*
				        (KEYWORD:ELSE expr)?
```

```c
for_expr		: KEYWORD:FOR IDENTIFIER EQ expr KEYWORD:TO expr 
				        (KEYWORD:STEP expr)? KEYWORD:THEN expr
```

```c
while_expr	: KEYWORD:WHILE expr KEYWORD:THEN expr
```
