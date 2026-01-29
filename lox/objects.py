from .environment import * 

class LoxCallable:
    def arity(self):
        raise NotImplementedError
    def call(self, interpreter, arguments):
        raise NotImplementedError

class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def arity(self):
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def __str__(self):
        return self.name

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        env = Environment(self.closure)
        env.define("this", instance)
        return LoxFunction(self.declaration, env, self.is_initializer)

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as r:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return r.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name):
        key = name.lexeme if hasattr(name, "lexeme") else name
        if key in self.fields:
            return self.fields[key]
        method = self.klass.find_method(key)
        if method:
            return method.bind(self)
        raise RuntimeError(name, f"Undefined property '{key}'.")

    def set(self, name, value):
        key = name.lexeme if hasattr(name, "lexeme") else name
        self.fields[key] = value

    def __str__(self):
        return f"{self.klass.name} instance"

class Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value