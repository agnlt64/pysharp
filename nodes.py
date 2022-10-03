class UnaryOperatorNode:
    def __init__(self, operator_token, node):
        self.operator_token = operator_token
        self.node = node
        self.pos_start = self.operator_token.pos_start
        self.pos_end = node.pos_end
        
    def __repr__(self) -> str:
        return f"{self.operator_token}, {self.node}"
    
class NumberNode:
    def __init__(self, token):
        self.token = token
        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end
        
    def __repr__(self) -> str:
        return f"{self.token}"
    
class BinaryOperatorNode:
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
        
    def __repr__(self) -> str:
        return f"({self.left_node}, {self.operator_token}, {self.right_node})"