from constants import *
from nodes import NumberNode, BinaryOperatorNode, UnaryOperatorNode, VariableAssignmentNode, VariableAccessNode, IfNode
from errors import SyntaxError

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count  = 0

    def register_next(self):
        self.advance_count += 1

    def register(self, result):
        self.advance_count += result.advance_count  # bug here but idk why, fix later lol
        if result.error: self.error = result.error
        return result.node        
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        if not self.error or self.advance_count == 0:
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
            return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*' or '/'"))
        return res
        
    def next(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TOKEN_KEYWORD, "if"):
            return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "'if' expected"))

        res.register_next()
        self.next()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_token.matches(TOKEN_KEYWORD, "then"):
            return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "'then' expected"))

        res.register_next()
        self.next()

        expr = res.register(self.expr())
        if res.error: return res
        cases.append((condition, expr))

        while self.current_token.matches(TOKEN_KEYWORD, "elif"):
            res.register_next()
            self.next()

            condition = res.register(self.expr())
            if res.error: return res

            if not self.current_token.matches(TOKEN_KEYWORD, "then"):
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "'then expected"))
            
            res.register_next()
            self.next()

            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr))

            if self.current_token.matches(TOKEN_KEYWORD, "else"):
                res.register_next()
                self.next()

                else_case = res.register(self.expr())
                if res.error: return res

            return res.success(IfNode(cases, else_case))

    def atom(self):
        res = ParseResult()
        token = self.current_token
        
        if token.type in (TOKEN_INT, TOKEN_FLOAT):
            res.register_next()
            self.next()
            return res.success(NumberNode(token))
        elif token.type == TOKEN_IDENTIFIER:
            res.register_next()
            self.next()
            return res.success(VariableAccessNode(token))
        elif token.type == TOKEN_LEFT_PARENTHESIS:
            res.register_next()
            self.next()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_token.type == TOKEN_RIGHT_PARENTHESIS:
                res.register_next()
                self.next()
                return res.success(expr)
            else:
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "')' expected"))
        elif token.matches(TOKEN_KEYWORD, "if"):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        return res.failure(SyntaxError(token.pos_start, token.pos_end, "Expected int, float, variable name, '+', '-', or '('"))
    
    def power(self):
        return self.binary_operation(self.atom, (TOKEN_POWER, ), self.factor)
            
    def factor(self):
        res = ParseResult()
        token = self.current_token
        
        if token.type in (TOKEN_PLUS, TOKEN_MINUS):
            res.register_next()
            self.next()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOperatorNode(token, factor))
        return self.power()
    
    def term(self):
        return self.binary_operation(self.factor, (TOKEN_MULTIPLY, TOKEN_DIVIDE))

    def arith_expr(self):
        return self.binary_operation(self.term, (TOKEN_PLUS, TOKEN_MINUS))

    def comp_expr(self):
        res = ParseResult()
        if self.current_token.matches(TOKEN_KEYWORD, "not"):
            operation_token = self.current_token
            self.next()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOperatorNode(operator_token, node))
        
        node = res.register(self.binary_operation(self.arith_expr, (TOKEN_EQUALS_EQUALS, TOKEN_NOT_EQUALS, TOKEN_LESS_THAN, TOKEN_GREATER_THAN, TOKEN_LESS_EQUALS, TOKEN_GREATER_EQUALS)))

        if res.error:
            return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected int, float, vriable name, '+', '-', '(', or 'not'"))
        
        return res.success(node)
    
    def expr(self):
        res = ParseResult()
        if self.current_token.matches(TOKEN_KEYWORD, "let"):
            res.register_next()
            self.next()
            if self.current_token.type != TOKEN_IDENTIFIER:
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Variable name expected"))
            
            var_name = self.current_token
            res.register_next()
            self.next()
            
            if self.current_token.type != TOKEN_EQUALS:
                return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "'=' expected"))
            
            res.register_next()
            self.next()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VariableAssignmentNode(var_name, expr))
                
        node = res.register(self.binary_operation(self.comp_expr, ((TOKEN_KEYWORD, "and"), (TOKEN_KEYWORD, "or"))))

        if res.error:
            return res.failure(SyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'let', int, float, variable name, '+', '-', or '('"))

        return res.success(node)
    
    def binary_operation(self, callback_a, operation_tokens, callback_b=None):
        if callback_b == None:
            callback_b = callback_a
        res = ParseResult()
        left = res.register(callback_a())
        if res.error: return res
        
        while self.current_token.type in operation_tokens or (self.current_token.type, self.current_token.value) in operation_tokens:
            operator_token = self.current_token
            res.register_next()
            self.next()
            right = res.register(callback_b())
            if res.error: return res
            left = BinaryOperatorNode(left, operator_token, right)
        return res.success(left)