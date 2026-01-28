from .token_type import *
from .objects import * 

class Token:
    def __init__(self, lexeme):
        self.lexeme = lexeme

class Interpreter:
    def __init__(self):
        self.globals = Environment() 
        self.environment = self.globals
        self.locals = {}

    def interpret(self, statements):
        for stmt in statements:
            self.execute(stmt)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous
    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        t = expr.operator.token_type
        if t == TokenType.MINUS:
            return -right
        elif t == TokenType.BANG:
            return not self.is_truthy(right)
        raise RuntimeError(f"Unknown unary operator {t}")

    def visit_binary_expr(self, expr):
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
        elif t == TokenType.GREATER:
            return left > right
        elif t == TokenType.GREATER_EQUAL:
            return left >= right
        elif t == TokenType.LESS:
            return left < right
        elif t == TokenType.LESS_EQUAL:
            return left <= right
        elif t == TokenType.EQUAL_EQUAL:
            return left == right
        elif t == TokenType.BANG_EQUAL:
            return left != right
        raise RuntimeError(f"Unknown binary operator {t}")

    def visit_variable_expr(self, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, expr.name)
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.environment.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise RuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        return callee.call(self, arguments)

    def visit_get_expr(self, expr):
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise RuntimeError(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr):
        obj = self.evaluate(expr.object)
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    def visit_this_expr(self, expr):
        if expr in self.locals:
            distance = self.locals[expr]
            return self.environment.get_at(distance, expr.keyword)
        return self.environment.get(expr.keyword)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name, value)
        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name, function)
        return None

    def visit_class_stmt(self, stmt):
        superclass = None
        if stmt.superclass:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")
        self.environment.define(stmt.name, None)
        if stmt.superclass:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        klass = LoxClass(stmt.name.lexeme, superclass if isinstance(superclass, LoxClass) else None, methods)
        if stmt.superclass:
            self.environment = self.environment.enclosing
        self.environment.assign(stmt.name, klass)
        return None
    
    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def stringify(self, obj):
        if obj is None:
            return "nil"
        if isinstance(obj, float) and obj.is_integer():
            return str(int(obj))
        return str(obj)
