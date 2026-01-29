class Environment:
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing

    def _key(self, name):
        return name.lexeme if hasattr(name, "lexeme") else name

    def define(self, name, value):
        self.values[self._key(name)] = value

    def get(self, name):
        key = self._key(name)
        if key in self.values:
            return self.values[key]
        if self.enclosing:
            return self.enclosing.get(key)
        raise RuntimeError(f"Undefined variable '{key}'.")

    def assign(self, name, value):
        key = self._key(name)
        if key in self.values:
            self.values[key] = value
        elif self.enclosing:
            self.enclosing.assign(key, value)
        else:
            raise RuntimeError(f"Undefined variable '{key}'.")

    def get_at(self, distance, name):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env.values[self._key(name)]

    def assign_at(self, distance, name, value):
        env = self
        for _ in range(distance):
            env = env.enclosing
        env.values[self._key(name)] = value
