from string_arrows import string_arrows

class Exception:
    def __init__(self, pos_start, pos_end, error_name: str, details: str):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
        
    def to_string(self) -> str:
        result = f"{self.error_name}: {self.details}\n"
        result += f"File {self.pos_start.filename}, line {self.pos_start.line + 1}"
        result += "\n\n" + string_arrows(self.pos_start.content, self.pos_start, self.pos_end)
        return result
    
class IllegalCharacterException(Exception):
    def __init__(self, pos_start: int, pos_end: int, details: str):
        super().__init__(pos_start, pos_end, "Illegal character", details)

class SyntaxError(Exception):
    def __init__(self, pos_start: int, pos_end: int, details: str):
        super().__init__(pos_start, pos_end, "Syntax error", details)
        
class RuntimeError(Exception):
    def __init__(self, pos_start: int, pos_end: int, details: str, context):
        super().__init__(pos_start, pos_end, "Runtime Error", details)
        self.context = context
        
    def to_string(self):
        result = self.generate_traceback()
        result += f"{self.error_name}: {self.details}\n"
        result += "\n" + string_arrows(self.pos_start.content, self.pos_start, self.pos_end)
        return result
        
    def generate_traceback(self):
        result = ""
        pos = self.pos_start
        ctx = self.context
        
        while ctx:
            result = f"  File {pos.filename}, line {str(pos.line + 1)}, in {ctx.display_name}\n" + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
            
        return "Call stack:\n" + result
        
class RuntimeResult:
    def __init__(self):
        self.value = None
        self.error = None
        
    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self