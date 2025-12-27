from lox.scanner import Scanner
from lox.parser import Parser
from lox.interpreter import Binary, Literal

def parse_expr(source):
    tokens = Scanner(source).scan_tokens()
    parser = Parser(tokens)
    return parser.parse()[0]

def test_binary_expression():
    stmt = parse_expr("1 + 2;")
    expr = stmt.expression

    assert isinstance(expr, Binary)
    assert isinstance(expr.left, Literal)
    assert expr.left.value == 1
    assert expr.operator.lexeme == "+"
    assert expr.right.value == 2

    