from unittest import TestCase

from pasquim.parser import Lexer, Parser


class TestParserCircle(TestCase):
    def setUp(self):
        self.program = "(begin (define r 10) (* pi (* r r)))"

    def test_tokenizer(self):
        output = ['(', 'begin', '(', 'define', 'r', '10', ')',
                  '(', '*', 'pi', '(', '*', 'r', 'r', ')', ')', ')']

        assert Lexer(self.program).tokenize() == output

    def test_parser(self):
        output = ['begin', ['define', 'r', 10], ['*', 'pi', ['*', 'r', 'r']]]

        assert Parser(Lexer(self.program).tokenize()).parse() == output


class TestParserBool(TestCase):
    def setUp(self):
        self.program = "(logior #t #f)"

    def test_tokenizer(self):
        output = ['(',  'logior', '#t', '#f', ')']

        assert Lexer(self.program).tokenize() == output

    def test_parser(self):
        output = ['logior', True, False]

        assert Parser(Lexer(self.program).tokenize()).parse() == output
