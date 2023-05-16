##########
# IMPORTS
##########

import error
import lexer


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
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.operation_token}, {self.node})'
    

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

        if not result.error and self.cur_token.type != lexer.TT_EOF:
            return result.failure(error.InvalidSynaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected '+', '-', '*', or '/'"))

        return result
    
    def atom(self):
        result = ParseResult()
        token = self.cur_token

        if token.type in (lexer.TT_INT, lexer.TT_FLOAT):
            result.register(self.advance())
            return result.success(NumberNode(token))
        
        elif token.type in lexer.TT_LPAREN:
            result.register(self.advance())
            expr = result.register(self.expr())
            if result.error: return result
            if self.cur_token.type == lexer.TT_RPAREN:
                result.register(self.advance())
                return result.success(expr)
            else:
                return result.failure(error.InvalidSynaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected ')'"))

        return result.failure(error.InvalidSynaxError(token.pos_start, token.pos_end, "Expected int, float, '+', '-', or '('"))
    
    def power(self):
        return self.binary_operation(self.atom, (lexer.TT_POW, ), self.factor)

    
    def factor(self):
        result = ParseResult()
        token = self.cur_token

        if token.type in (lexer.TT_PLUS, lexer.TT_MINUS):
            result.register(self.advance())
            factor =  result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOperationNode(token, factor)) 
        
        return self.power()
    
    def term(self):
        return self.binary_operation(self.factor, (lexer.TT_MUL, lexer.TT_DIV))

    def expr(self):
        return self.binary_operation(self.term, (lexer.TT_PLUS, lexer.TT_MINUS))

    def binary_operation(self, func_a, operations, func_b=None):
        if func_b == None:
            func_b = func_a

        result = ParseResult()
        left = result.register(func_a())
        if result.error: return result

        while self.cur_token.type in operations:
            operation_token = self.cur_token
            result.register(self.advance())
            right = result.register(func_b())
            if result.error: return result
            left = BinaryOperationNode(left, operation_token, right)

        return result.success(left)