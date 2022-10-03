from lexer import Lexer
from parser import Parser
from  errors import Exception
from _token import Token
from interpreter import Interpreter
from context import Context

def main(filename: str, text: str) -> Token | Exception:
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    if error: return "", error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return "", ast.error
    
    interperter = Interpreter()
    context = Context("<program>")
    result = interperter.visit(ast.node, context)
    
    return result.value, result.error

def run():
    while True:
        line = input("psharp > ")
        result, error = main("<stdin>", line)
        if error:
            print(error.to_string())
        print(result)