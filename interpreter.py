##########
# IMPORTS
##########

from string_with_arrows import *
import lexer
import error

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
            
    def pow_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        
    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None

    def get_comparison_neq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None

    def get_comparison_less(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def get_comparison_greater(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def get_comparison_less_or_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None

    def get_comparison_greater_or_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None

    def and_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None

    def or_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None

    def not_by(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def is_true(self):
        return self.value != 0
        
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
        
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
        self.symbol_table = None


####################
# SYMBOL TABLE
####################

class SymbolTable:
	def __init__(self):
		self.symbols = {}
		self.parent = None

	def get(self, name):
		value = self.symbols.get(name, None)
		if value == None and self.parent:
			return self.parent.get(name)
		return value

	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]


####################
# INTERPRETER
####################

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        result = RuntimeResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if not value:
            return result.failure(error.RuntimeError(node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return result.success(value)
    
    def visit_VarAssignNode(self, node, context):
        result = RuntimeResult()
        var_name = node.var_name_token.value
        value = result.register(self.visit(node.value_node, context))
        if result.error: return result

        context.symbol_table.set(var_name, value)
        return result.success(value)

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
        elif node.operation_token.type == lexer.TT_POW:
            result, error = left.pow_by(right)
        elif node.operation_token.type == lexer.TT_EEQ:
            result, error = left.get_comparison_eq(right)
        elif node.operation_token.type == lexer.TT_NEQ:
            result, error = left.get_comparison_neq(right)
        elif node.operation_token.type == lexer.TT_LESS:
            result, error = left.get_comparison_less(right)
        elif node.operation_token.type == lexer.TT_GREATER:
            result, error = left.get_comparison_greater(right)
        elif node.operation_token.type == lexer.TT_LESS_OR_EQ:
            result, error = left.get_comparison_less_or_eq(right)
        elif node.operation_token.type == lexer.TT_GREATER_OR_EQ:
            result, error = left.get_comparison_greater_or_eq(right)
        elif node.operation_token.matches(lexer.TT_KEYWORD, 'AND'):
            result, error = left.and_by(right)
        elif node.operation_token.matches(lexer.TT_KEYWORD, 'OR'):
            result, error = left.or_by(right)


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
        elif node.operation_token.matches(lexer.TT_KEYWORD, 'NOT'):
            number, error = number.not_by()

        if error: return result.failure(error)
        else:
            return result.success(number.set_pos(node.pos_start, node.pos_end))
    
    def visit_IfNode(self, node, context):
        result = RuntimeResult()

        for condition, expr in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.error: return result

            if condition_value.is_true():
                expr_value = result.register(self.visit(expr, context))
                if result.error: return result
                return result.success(expr_value)

        if node.else_case:
            else_value = result.register(self.visit(node.else_case, context))
            if result.error: return result
            return result.success(else_value)

        return result.success(None)