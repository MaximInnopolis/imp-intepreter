##########
# IMPORTS
##########

from string_with_arrows import *


##########
# CONSTANTS
##########

DIGITS = '0123456789'


####################
# ERROR
####################

class Error:
    def __init__(self, pos_start, pos_end, error_name, info):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.info = info

    def as_string(self):
        result = f'{self.error_name}: {self.info}\n'
        result += f'File {self.pos_start.file_name}, line {self.pos_start.line_num + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, info):
        super().__init__(pos_start, pos_end, 'Illegal Character', info)

class InvalidSynaxError(Error):
    def __init__(self, pos_start, pos_end, info=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', info)

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, info, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', info)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.info}\n'
        result += '\n\n' + string_with_arrows(self.pos_start.file_text, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' File {pos.file_name}, line {str(pos.line_num)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent call last):\n' + result


####################
# POSITION
####################

class Position:
    def __init__(self, index, line_num, col_num, file_name, file_text):
        self.index = index
        self.line_num = line_num
        self.col_num = col_num
        self.file_name = file_name
        self.file_text = file_text

    def advance(self, cur_char=None):
        self.index += 1
        self.col_num += 1

        if cur_char == '\n':
            self.line_num += 1
            self.col_num = 0

        return self
    
    def copy(self):
        return Position(self.index, self.line_num, self.col_num, self.file_name, self.file_text)


####################
# TOKENS
####################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value 

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()


    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


####################
# LEXER
####################

class Lexer:
    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.cur_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.cur_char)
        self.cur_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def create_tokens(self):
        tokens = []

        while self.cur_char != None:
            if self.cur_char in ' \t' :
                self.advance()
            elif self.cur_char in DIGITS:
                tokens.append(self.create_number())
            elif self.cur_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.cur_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.cur_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()

            else:
                pos_start = self.pos.copy()
                char = self.cur_char
                self.advance()
                return [], IllegalCharError(pos_start,  self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def create_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.cur_char != None and self.cur_char in DIGITS + '.':
            if self.cur_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.cur_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
        

####################
# NODES
####################

class NumberNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'
    

class BinaryOperationNode:
    def __init__(self, left_node, operation_token, right_node):
        self.left_node = left_node
        self.operation_token = operation_token
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.operation_token}, {self.right_node})'
    

class UnaryOperationNode:
    def __init__(self, operation_token, node):
        self.operation_token = operation_token
        self.node = node

        self.pos_start = self.operation_token.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.operation_token}, {self.node})'
    

####################
# RUNTIME RESULT
####################

class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, result):
        if result.error: self.error = result.error
        return result.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self


####################
# PARSE RESULT
####################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, result):
        if isinstance(result, ParseResult):
            if result.error: self.error = result.error
            return result.node
        
        return result

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


####################
# PARSER
####################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.cur_token = self.tokens[self.token_index]
        return self.cur_token
    
    def parse(self):
        result = self.expr()

        if not result.error and self.cur_token.type != TT_EOF:
            return result.failure(InvalidSynaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected '+', '-', '*', or '/'"))

        return result
    
    def factor(self):
        result = ParseResult()
        token = self.cur_token

        if token.type in (TT_PLUS, TT_MINUS):
            result.register(self.advance())
            factor =  result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOperationNode(token, factor))

        elif token.type in (TT_INT, TT_FLOAT):
            result.register(self.advance())
            return result.success(NumberNode(token))
        
        elif token.type in TT_LPAREN:
            result.register(self.advance())
            expr = result.register(self.expr())
            if result.error: return result
            if self.cur_token.type == TT_RPAREN:
                result.register(self.advance())
                return result.success(expr)
            else:
                return result.failure(InvalidSynaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected ')'"))
        
        return result.failure(InvalidSynaxError(token.pos_start, token.pos_end, "Expected int or float"))

    def term(self):
        return self.binary_operation(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

    def binary_operation(self, func, operations):
        result = ParseResult()
        left = result.register(func())
        if result.error: return result

        while self.cur_token.type in operations:
            operation_token = self.cur_token
            result.register(self.advance())
            right = result.register(func())
            if result.error: return result
            left = BinaryOperationNode(left, operation_token, right)

        return result.success(left)


####################
# VALUES
####################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context=None):
        self.context = context
        return self


    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        
    def sub_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def mul_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def div_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(other.pos_start, other.pos_end, 'Division by zero', self.context)
            else:
                return Number(self.value / other.value).set_context(self.context), None
        
    def __repr__(self):
        return str(self.value)
        

####################
# CONTEXT
####################

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos


####################
# INTERPRETER
####################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit method {type(node).__name__} defined')
    
    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOperationNode(self, node, context):
        res = RuntimeResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        if node.operation_token.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.operation_token.type == TT_MINUS:
            result, error = left.sub_by(right)
        elif node.operation_token.type == TT_MUL:
            result, error = left.mul_by(right)
        elif node.operation_token.type == TT_DIV:
            result, error = left.div_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOperationNode(self, node, context):
        result = RuntimeResult()
        number = result.register(self.visit(node.node, context))
        if result.error: return result

        if node.operation_token.type == TT_MINUS:
            number, error = number.mul_by(Number(-1))

        if error: return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))
    

####################
# RUN
####################

def run(file_name, text):
    # Generate tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.create_tokens()
    if error: return None, error
    #return tokens, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
   
    #return ast.node, ast.error

    # Generate Interpreter
    interpreter = Interpreter()
    context = Context('program')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error

