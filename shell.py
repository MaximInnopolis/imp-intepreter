import interpreter
import lexer
import parse

def run(file_name, text):
    # Generate tokens
    lex = lexer.Lexer(file_name, text)
    tokens, error = lex.create_tokens()
    if error: return None, error

    #return tokens, error

    # Generate AST
    parser = parse.Parser(tokens)
    ast = parser.parse()
   
    #return ast.node, ast.error

    # Generate Interpreter
    interp = interpreter.Interpreter()
    context = interpreter.Context('program')
    result = interp.visit(ast.node, context)

    return result.value, result.error

while True:
    text = input('basic > ')
    result, err = run('<stdin>', text)

    if err: print(err.as_string())
    else: print(result)
