from .token_file import Token
from .token_type import TokenType

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        self.skip_whitespace()
        self.start = self.current
    
        if self.is_at_end():
            return

        char = self.advance()

        if char == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif char == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ';':
            self.add_token(TokenType.SEMICOLON)
        elif char == '=':
            self.add_token(TokenType.EQUAL)
        elif char == '==':
            self.add_token(TokenType.EQUAL_EQUAL)
        elif char == '+':
            self.add_token(TokenType.PLUS)
        elif char == '*':
            self.add_token(TokenType.STAR)
        elif char == '/':
            self.add_token(TokenType.SLASH)
        elif char == '-':
            self.add_token(TokenType.MINUS)
        elif char == '!':
            self.add_token(TokenType.BANG)
        elif char == '!=':
            self.add_token(TokenType.BANG_EQUAL)
        elif char == '>':
            self.add_token(TokenType.GREATER)
        elif char == '<':
            self.add_token(TokenType.LESS)
        elif char == '>=':
            self.add_token(TokenType.GREATER_EQUAL)
        elif char == '<=':
            self.add_token(TokenType.LESS_EQUAL)
        elif char == '.':
            self.add_token(TokenType.DOT)
        elif char == ',':
            self.add_token(TokenType.COMMA)
        elif char == '"':
            self.string()
        elif char.isdigit():
            self.number()
        elif char.isalpha() or char == '_':
            self.identifier()
        else:
            print(f"Unexpected character {char} at line {self.line}")

    def skip_whitespace(self):
        while True:
            c = self.peek()
            if c.isspace():
                if c == '\n':
                    self.line += 1
                self.advance()
            elif c == '/' and self.peek_next() == '/':
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                return

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]

        keywords = {"print": TokenType.PRINT, "var": TokenType.VAR}

        token_type = keywords.get(text, TokenType.IDENTIFIER)

        self.add_token(token_type)

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            print(f"Unterminated string at line {self.line}")
            return

        self.advance() 
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)

    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_at_end(self):
        return self.current >= len(self.source)