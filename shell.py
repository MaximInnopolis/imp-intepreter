import interpreter
import lexer
import parse

global_symbol_table = interpreter.SymbolTable()
global_symbol_table.set("null", interpreter.Number(0))

def run(file_name, text):
    # Generate tokens
    lex = lexer.Lexer(file_name, text)
    tokens, error = lex.create_tokens()
    if error: return None, error

    # return tokens, error

    # Generate AST
    parser = parse.Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
  
    # return ast.node, ast.error

    # Generate Interpreter
    interp = interpreter.Interpreter()
    context = interpreter.Context('<program>')
    context.symbol_table = global_symbol_table
    result = interp.visit(ast.node, context)

    return result.value, result.error

while True:
    text = input('imp > ')
    result, err = run('<stdin>', text)

    if err: print(err.as_string())
    elif result: print(result)
