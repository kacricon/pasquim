from unittest import TestCase
from subprocess import run, PIPE

from pasquim.compiler import Compiler


class TestAtoms(TestCase):
    def setUp(self):
        self.path = "tests/tmp"

    def _compile_and_compare(self, program: str, output: bytes):
        compiler = Compiler(self.path, program)
        compiler.compile_to_binary()

        results = run(self.path+"/a.out", stdout=PIPE)
        assert results.stdout == output

    def test_positive_integer(self):
        program = "42"
        output = b'42\n'

        self._compile_and_compare(program, output)

    def test_negative_integer(self):
        program = "-272"
        output = b'-272\n'

        self._compile_and_compare(program, output)

    def test_bool_true(self):
        program = "#t"
        output = b'#t\n'

        self._compile_and_compare(program, output)

    def test_bool_false(self):
        program = "#f"
        output = b'#f\n'

        self._compile_and_compare(program, output)
