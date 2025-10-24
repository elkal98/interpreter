import sys
from scanner import Scanner
from parser import Parser
from interpreter import Interpreter

class Lox:
    def __init__(self):
        self.args = sys.argv
        self.interpreter = Interpreter()

    def main(self):
        if len(self.args) > 2:
            print("Usage: python3 lox.py [script]")
        elif len(self.args) == 2:
            self.run_file(self.args[1])
        else:
            self.run_prompt()

    def run_file(self, path):
        file = open(path)
        self.run(file.read())

    def run_prompt(self):
        while True:
            prompt = input("py-lox> ")
            self.run(prompt)
    
    def run(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()
        self.interpreter.interpret(statements)

if __name__ == "__main__":
    Lox().main()