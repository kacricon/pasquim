from unittest import TestCase

import pasquim.parser as parser


class TestParser(TestCase):
    def setUp(self):
        self.program = "(begin (define r 10) (* pi (* r r)))"

    def test_tokenizer(self):
        output = ['(', 'begin', '(', 'define', 'r', '10', ')',
                  '(', '*', 'pi', '(', '*', 'r', 'r', ')', ')', ')']

        assert parser.tokenize(self.program) == output

    def test_parser(self):
        output = ['begin', ['define', 'r', 10], ['*', 'pi', ['*', 'r', 'r']]]

        assert parser.parse(self.program) == output
