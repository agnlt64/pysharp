from lexer import Lexer
from parser import Parser
from number import Number
from  errors import Exception
from pys_token import Token
from interpreter import Interpreter, SymbolTable
from context import Context
import sys

global_symbol_table = SymbolTable()
global_symbol_table.set("nothing", Number(0))
global_symbol_table.set("true", Number(1))
global_symbol_table.set("false", Number(0))


def main(filename: str, text: str) -> Token | Exception:
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    if error: return "", error
    
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return "", ast.error
    
    interperter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interperter.visit(ast.node, context)
    
    return result.value, result.error

def run():
    while True:
        line = input("psharp > ")
        if line == "exit":
            sys.exit(0)
        result, error = main("<stdin>", line)
        if error:
            print(error.to_string())
        elif result:
            print(result)