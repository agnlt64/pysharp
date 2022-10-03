from  _token import Token
from  constants import *
from  errors import IllegalCharacterException
from  position import Position

class Lexer:
    def __init__(self, filename: str, text: str):
        self.filename = filename
        self.text = text
        self.position = Position(-1, 0, -1, filename, text)
        self.current_character = None
        self.next()
    
    def next(self):
        self.position.next(self.current_character)
        self.current_character = self.text[self.position.index] if self.position.index < len(self.text) else None
        
    def make_tokens(self) -> Token:
        tokens = []
        
        while self.current_character is not None:
            if self.current_character in " \t":
                self.next()
            elif self.current_character == "+":
                tokens.append(Token(TOKEN_PLUS, pos_start=self.position))
                self.next()
            elif self.current_character == "-":
                tokens.append(Token(TOKEN_MINUS, pos_start=self.position))
                self.next()
            elif self.current_character == "*":
                tokens.append(Token(TOKEN_MULTIPLY, pos_start=self.position))
                self.next()
            elif self.current_character == "/":
                tokens.append(Token(TOKEN_DIVIDE, pos_start=self.position))
                self.next()
            elif self.current_character == "^":
                tokens.append(Token(TOKEN_POWER, pos_start=self.position))
                self.next()
            elif self.current_character == "=":
                tokens.append(Token(TOKEN_EQUALS, pos_start=self.position))
                self.next()
            elif self.current_character == "(":
                tokens.append(Token(TOKEN_LEFT_PARENTHESIS, pos_start=self.position))
                self.next()
            elif self.current_character == ")":
                tokens.append(Token(TOKEN_RIGHT_PARENTHESIS, pos_start=self.position))
                self.next()
            elif self.current_character in DIGITS:
                tokens.append(self.make_number())
            elif self.current_character in LETTERS:
                tokens.append(self.make_identifier())
            else:
                pos_start = self.position.copy()
                char = self.current_character
                self.next()
                return "", IllegalCharacterException(pos_start, self.position, f"'{char}'")
        tokens.append(Token(TOKEN_EOF, pos_start=self.position))
        return tokens, ""

    def make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.position.copy()
        
        while self.current_character is not None and self.current_character in DIGITS + ".":
            if self.current_character == ".":
                if dot_count == 1:
                    break
                dot_count +=  1
                num_str += "."
            else:
                num_str += self.current_character
            self.next()
                
        if dot_count == 0:
            return Token(TOKEN_INT, int(num_str), pos_start, self.position)
        return Token(TOKEN_FLOAT, float(num_str), pos_start, self.position)

    def make_identifier(self):
        id_str = ""
        pos_start = self.position.copy()
        
        while self.current_character is not None and self.current_character in LETTERS_DIGITS + "_":
            id_str += self.current_character
            self.next()
        
        token_type = TOKEN_KEYWORD if id_str in KEYWORDS else TOKEN_IDENTIFIER
        return Token(token_type, id_str, pos_start, self.position)
