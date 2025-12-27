from lox.scanner import Scanner
from lox.parser import Parser
from lox.interpreter import Interpreter

def interpret(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    interpreter = Interpreter()
    interpreter.interpret(statements)

    return interpreter

def test_var_declaration():
    interpreter = interpret("var a = 10;")

    assert "a" in interpreter.globals.values
    assert interpreter.globals.values["a"] == 10