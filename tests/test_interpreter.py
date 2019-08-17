from unittest import TestCase
import math

from pasquim.parser import Lexer, Parser
from pasquim.env import eval


class TestInterpreter(TestCase):
    def parse(self, program: str):
        return Parser(Lexer(program).tokenize()).parse()

    def test_eval(self):
        program = "(begin (define r 10) (* pi (* r r)))"

        expected = 314.1592653589793
        results = eval(self.parse(program))

        assert isinstance(results, float)
        assert math.isclose(results, expected)

    def test_circle_area(self):
        # circle area function
        function = "(define circle-area (lambda (r) (* pi (* r r))))"
        program = "(circle-area 3)"
        expected = 28.274333877

        eval(self.parse(function))
        results = eval(self.parse(program))

        assert isinstance(results, float)
        assert math.isclose(results, expected)

    def test_fact(self):
        # fact
        function = "(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))"
        program = "(fact 10)"
        expected = 3628800

        eval(self.parse(function))
        results = eval(self.parse(program))

        assert results == expected
