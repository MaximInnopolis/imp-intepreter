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
    

class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.var_name_token.pos_end


class VarAssignNode:
	def __init__(self, var_name_token, value_node):
		self.var_name_token = var_name_token
		self.value_node = value_node

		self.pos_start = self.var_name_token.pos_start
		self.pos_end = self.value_node.pos_end
    

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
    

class IfNode:
	def __init__(self, cases, else_case):
		self.cases = cases
		self.else_case = else_case

		self.pos_start = self.cases[0][0].pos_start
		self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

####################
# PARSE RESULT
####################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, result):
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
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

    def advance(self, ):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.cur_token = self.tokens[self.token_index]
        return self.cur_token
    
    def parse(self):
        result = self.expr()

        if not result.error and self.cur_token.type != lexer.TT_EOF:
            return result.failure(error.InvalidSynaxError(self.cur_token.pos_start, self.cur_token.pos_end, 
                                                          "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"))

        return result
    
    def if_expr(self):
        result = ParseResult()
        cases = []
        else_case = None

        if not self.cur_token.matches(lexer.TT_KEYWORD, 'IF'):
            return result.failure(error.InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end, f"Expected 'IF'"))

        result.register_advancement()
        self.advance()

        condition = result.register(self.expr())
        if result.error: return result

        if not self.cur_token.matches(lexer.TT_KEYWORD, 'THEN'):
            return result.failure(error.InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end, f"Expected 'THEN'"))

        result.register_advancement()
        self.advance()
        expr = result.register(self.expr())
        if result.error: return result
        cases.append((condition, expr))

        while self.cur_token.matches(lexer.TT_KEYWORD, 'ELIF'):
            result.register_advancement()
            self.advance()
            condition = result.register(self.expr())
            if result.error: return result

            if not self.cur_token.matches(lexer.TT_KEYWORD, 'THEN'):
                return result.failure(error.InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end,f"Expected 'THEN'"))

            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error: return result
            cases.append((condition, expr))

        if self.cur_token.matches(lexer.TT_KEYWORD, 'ELSE'):
            result.register_advancement()
            self.advance()

            else_case = result.register(self.expr())
            if result.error: return result

        return result.success(IfNode(cases, else_case))
    
    def atom(self):
        result = ParseResult()
        token = self.cur_token

        if token.type in (lexer.TT_INT, lexer.TT_FLOAT):
            result.register_advancement()
            self.advance()
            return result.success(NumberNode(token))
        
        elif token.type in lexer.TT_IDENTIFIER:
            result.register_advancement()
            self.advance()
            return result.success(VarAccessNode(token))
        
        elif token.type in lexer.TT_LPAREN:
            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error: return result
            if self.cur_token.type == lexer.TT_RPAREN:
                result.register_advancement()
                self.advance()
                return result.success(expr)
            else:
                return result.failure(error.InvalidSynaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected ')'"))
            
        elif token.matches(lexer.TT_KEYWORD, 'IF'):
            if_expr = result.register(self.if_expr())
            if result.error: return result
            return result.success(if_expr)

        return result.failure(error.InvalidSynaxError(
            token.pos_start, token.pos_end, "Expected int, float, identifier, '+', '-', or '('"))
    
    def power(self):
        return self.binary_operation(self.atom, (lexer.TT_POW, ), self.factor)

    
    def factor(self):
        result = ParseResult()
        token = self.cur_token

        if token.type in (lexer.TT_PLUS, lexer.TT_MINUS):
            result.register_advancement()
            self.advance()
            factor =  result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOperationNode(token, factor)) 
        
        return self.power()
    
    def term(self):
        return self.binary_operation(self.factor, (lexer.TT_MUL, lexer.TT_DIV))
    
    def arith_expr(self):
            return self.binary_operation(self.term, (lexer.TT_PLUS, lexer.TT_MINUS))

    def comp_expr(self):
        result = ParseResult()

        if self.cur_token.matches(lexer.TT_KEYWORD, 'NOT'):
            op_token = self.cur_token
            result.register_advancement()
            self.advance()

            node = result.register(self.comp_expr())
            if result.error: return result
            return result.success(UnaryOperationNode(op_token, node))
        
        node = result.register(self.binary_operation(self.arith_expr, (
            lexer.TT_EEQ, lexer.TT_NEQ, lexer.TT_LESS, lexer.TT_GREATER, lexer.TT_LESS_OR_EQ, lexer.TT_GREATER_OR_EQ)))
        
        if result.error:
            return result.failure(error.InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end, 
                                                           "Expected int, float, identifier, '+', '-', '(' or 'NOT'"))

        return result.success(node)


    def expr(self):
        result = ParseResult()

        if self.cur_token.matches(lexer.TT_KEYWORD, 'VAR'):
            result.register_advancement()
            self.advance()

            if self.cur_token.type != lexer.TT_IDENTIFIER:
                return result.failure(lexer.InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected identifier"))
            
            var_name = self.cur_token
            result.register_advancement()
            self.advance()

            if self.cur_token.type != lexer.TT_EQ:
                return result.failure(lexer.InvalidSyntaxError(self.cur_token.pos_start, self.cur_token.pos_end, "Expected '='"))
            
            result.register_advancement()
            self.advance()
            expr = result.register(self.expr())
            if result.error: return result
            return result.success(VarAssignNode(var_name, expr))
            
        node = result.register(self.binary_operation(self.comp_expr, ((lexer.TT_KEYWORD, 'AND'), (lexer.TT_KEYWORD, 'OR'))))

        if result.error: return result.failure(error.InvalidSyntaxError(
                self.cur_token.pos_start, self.cur_token.pos_end, "Expected 'Var', 'Identifier', int, float, '+', '-' or '('"))
        return result.success(node)

    def binary_operation(self, func_a, operations, func_b=None):
        if func_b == None:
            func_b = func_a

        result = ParseResult()
        left = result.register(func_a())
        if result.error: return result

        while self.cur_token.type in operations or (self.cur_token.type, self.cur_token.value) in operations:
            operation_token = self.cur_token
            result.register_advancement()
            self.advance()
            right = result.register(func_b())
            if result.error: return result
            left = BinaryOperationNode(left, operation_token, right)

        return result.success(left)