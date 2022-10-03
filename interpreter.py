from distutils.log import error
from number import Number
from errors import RuntimeResult, RuntimeError
from constants import *

class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")
    
    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(
            Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end)
        )
        
    def visit_BinaryOperatorNode(self, node, context):
        res = RuntimeResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        
        if node.operator_token.type == TOKEN_PLUS:
            result, error = left.added_to(right)
        elif node.operator_token.type == TOKEN_MINUS:
            result, error = left.subbed_by(right)
        elif node.operator_token.type == TOKEN_MULTIPLY:
            result, error = left.multed_by(right)
        elif node.operator_token.type == TOKEN_DIVIDE:
            result, error = left.divided_by(right)
        elif node.operator_token.type == TOKEN_POWER:
            result, error = left.powed_by(right)
        
        if error:
            return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))
        
    def visit_UnaryOperatorNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        
        error = None
        
        if node.operator_token.type == TOKEN_MINUS:
            number = number.multed_by(Number(-1))
        
        if error:
            return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_VariableAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RuntimeError(node.pos_start, node.pos_end, f"Trying to access variable {var_name} which is undefined", context))
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VariableAssignmentNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_token.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)


class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]