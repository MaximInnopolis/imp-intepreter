##########
# IMPORTS
##########

from string_with_arrows import *
import lexer
import error
import parse


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
                return None, error.RuntimeError(other.pos_start, other.pos_end, 'Division by zero', self.context)
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

        if node.operation_token.type == lexer.TT_PLUS:
            result, error = left.added_to(right)
        elif node.operation_token.type == lexer.TT_MINUS:
            result, error = left.sub_by(right)
        elif node.operation_token.type == lexer.TT_MUL:
            result, error = left.mul_by(right)
        elif node.operation_token.type == lexer.TT_DIV:
            result, error = left.div_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOperationNode(self, node, context):
        result = RuntimeResult()
        number = result.register(self.visit(node.node, context))
        if result.error: return result

        if node.operation_token.type == lexer.TT_MINUS:
            number, error = number.mul_by(Number(-1))

        if error: return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))
    