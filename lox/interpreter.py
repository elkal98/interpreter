from abc import ABC, abstractmethod
from .token_type import * 

class Token:
    def __init__(self, lexeme):
        self.lexeme = lexeme

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class Variable(Expr):
    def __init__(self, name):
        self.name = name
    def accept(self, visitor):
        return visitor.visit_variable_expr(self)

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def accept(self, visitor):
        return visitor.visit_assign_expr(self)

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visit_Binary(self)

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visit_Unary(self)

class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_Grouping(self)

class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class VarStatement(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer
    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

class PrintStatement(Stmt):
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class ExpressionStatement(Stmt):
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class Environment:
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        raise RuntimeError(f"Undefined variable '{name}'.")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.enclosing:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'.")

    def get_at(self, distance, name):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env.values[name]

    def assign_at(self, distance, name, value):
        env = self
        for _ in range(distance):
            env = env.enclosing
        env.values[name] = value

class Interpreter:
    def __init__(self):
        self.globals = Environment() 
        self.environment = self.globals
        self.locals = {}

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def evaluate(self, expr):
        return expr.accept(self)

    def interpret(self, statements):
        for stmt in statements:
            stmt.accept(self)
  
    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.globals.define(stmt.name.lexeme, value)
        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(value)

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_variable_expr(self, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, expr.name.lexeme)
        return self.globals.get(expr.name.lexeme)

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name.lexeme, value)
        else:
            self.globals.assign(expr.name.lexeme, value)
        return value

    def visit_Binary(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        t = expr.operator.token_type

        if t == TokenType.PLUS:
            return left + right
        elif t == TokenType.MINUS:
            return left - right
        elif t == TokenType.STAR:
            return left * right
        elif t == TokenType.SLASH:
            return left / right
        else:
            raise RuntimeError(f"Unknown binary operator {t}")

    def visit_Unary(self, expr):
        right = self.evaluate(expr.right)
        t = expr.operator.token_type

        if t == TokenType.MINUS:
            return -right
        else:
            raise RuntimeError(f"Unknown unary operator {t}")

    def visit_Grouping(self, expr):
        return self.evaluate(expr.expression)
