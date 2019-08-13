from unittest import TestCase
import os

from pasquim.compiler import Compiler


class TestEval(TestCase):
    def test_eval(self):
        path = "tests/tmp"
        program = "42"

        compiler = Compiler(path, program)
        compiler.compile_to_binary()

        assert os.popen(path+"/a.out").read() == "42\n"
