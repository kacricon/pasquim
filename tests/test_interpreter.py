from unittest import TestCase
import math

from pasquim.parser import parse
from pasquim.env import eval


class TestEval(TestCase):
    def test_eval(self):
        program = "(begin (define r 10) (* pi (* r r)))"

        expected = 314.1592653589793
        results = eval(parse(program))

        assert isinstance(results, float)
        assert math.isclose(results, expected)


class TestLambda(TestCase):
    def test_circle_area(self):
        # circle area function
        function = "(define circle-area (lambda (r) (* pi (* r r))))"
        program = "(circle-area 3)"
        expected = 28.274333877

        eval(parse(function))
        results = eval(parse(program))

        assert isinstance(results, float)
        assert math.isclose(results, expected)

    def test_fact(self):
        # fact
        function = "(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))"
        program = "(fact 10)"
        expected = 3628800

        eval(parse(function))
        results = eval(parse(program))

        assert results == expected
