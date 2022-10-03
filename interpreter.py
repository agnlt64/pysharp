from distutils.log import error
from number import Number
from errors import RuntimeResult
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