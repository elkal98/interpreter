from lox.scanner import Scanner
from lox.token_type import TokenType

def scan(source):
    scanner = Scanner(source)
    return scanner.scan_tokens()

def test_single_number():
    tokens = scan("123;")
    assert tokens[0].token_type == TokenType.NUMBER
    assert tokens[-1].token_type == TokenType.EOF

def test_string_literal():
    tokens = scan('"hello"')
    assert tokens[0].token_type == TokenType.STRING
    assert tokens[0].literal == "hello"
