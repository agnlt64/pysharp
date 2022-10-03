class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.next()
            
        if pos_end:
            self.pos_end = pos_end
        
    def __repr__(self) -> str:
        if self.value:
            return f"{self.type}: {self.value}"
        return f"{self.type}"
    
    def matches(self, type, value):
        return self.type == type and self.value == value