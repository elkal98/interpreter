from token_type import TokenType
from interpreter import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except RuntimeError:
            self.synchronize()
            return None
        
    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStatement(name, initializer)

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStatement(expr)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStatement(expr)

    def expression(self):
        return self.term()

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self):
        if self.match(TokenType.NUMBER):
            return Literal(self.previous().literal)
        if self.match(TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise RuntimeError(f"Expected expression, got {self.peek()}.")


    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        raise RuntimeError(message)

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            if self.peek().token_type in (TokenType.VAR, TokenType.PRINT):
                return
            self.advance()