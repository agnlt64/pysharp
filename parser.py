from constants import *
from nodes import NumberNode, BinaryOperatorNode, UnaryOperatorNode
from errors import SyntaxError

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, result):
        if isinstance(result, ParseResult):
            if result.error:
                self.error = result.error
            return result.node
        return result
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.next()

    def parse(self):
        res = self.expr()
        if not res.error and self.current_token.type != TOKEN_EOF:
            return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*' of '/'"))
        return res
        
    def next(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    
    def atom(self):
        res = ParseResult()
        token = self.current_token
        
        if token.type in (TOKEN_INT, TOKEN_FLOAT):
            res.register(self.next())
            return res.success(NumberNode(token))
        elif token.type == TOKEN_IDENTIFIER:
            res.register(self.next())
            return res.success(VariableAccessNode())
        elif token.type == TOKEN_LEFT_PARENTHESIS:
            res.register(self.next())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_token.type == TOKEN_RIGHT_PARENTHESIS:
                res.register(self.next())
                return res.success(expr)
            else:
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "')' expected"))
        return res.failure(SyntaxError(token.pos_start, token.pos_end, "Expected int, float, '+', '-', or '('"))
    
    def power(self):
        return self.binary_operation(self.atom, (TOKEN_POWER, ), self.factor)
            
    def factor(self):
        res = ParseResult()
        token = self.current_token
        
        if token.type in (TOKEN_PLUS, TOKEN_MINUS):
            res.register(self.next())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOperatorNode(token, factor))
        return self.power()
    
    def term(self):
        return self.binary_operation(self.factor, (TOKEN_MULTIPLY, TOKEN_DIVIDE))
    
    def expr(self):
        res = ParseResult()
        if self.current_token.matches(TOKEN_KEYWORD, "let"):
            res.register(self.next())
            if self.current_token != TOKEN_IDENTIFIER:
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Variable name expected"))
            
            var_name = self.current_token
            res.register(self.next())
            
            if self.current_token.type != TOKEN_EQUALS:
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "'=' expected"))
            
            res.register(self.next())
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VariableAssignmentNode(var_name, expr))
                
        return self.binary_operation(self.term, (TOKEN_PLUS, TOKEN_MINUS))
    
    def binary_operation(self, callback_a, operation_tokens, callback_b=None):
        if callback_b == None:
            callback_b = callback_a
        res = ParseResult()
        left = res.register(callback_a())
        if res.error: return res
        
        while self.current_token.type in operation_tokens:
            operator_token = self.current_token
            res.register(self.next())
            right = res.register(callback_b())
            if res.error: return res
            left = BinaryOperatorNode(left, operator_token, right)
        return res.success(left)