from typing import Type
from unittest import TestCase

import pytest
from subprocess import run, PIPE
import shutil

from pasquim.compiler import Compiler

TEMP_FOLDER = "tmp"


class BaseCompilerTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tests = []

    def tearDown(self) -> None:
        shutil.rmtree(TEMP_FOLDER, ignore_errors=True)
        self.tests = []

    def check_programs(self) -> None:
        for program, output in self.tests:
            if isinstance(output, str):
                self._check_output(program, output)
            elif issubclass(output, BaseException):
                self._check_exception(program, output)
            else:
                raise NotImplementedError

    @staticmethod
    def _check_output(program: str, output: str) -> None:
        compiler = Compiler(TEMP_FOLDER, program)
        compiler.compile_to_binary()

        results = run(TEMP_FOLDER+"/a.out", stdout=PIPE)
        assert results.stdout == (output + "\n").encode('UTF-8')

    @staticmethod
    def _check_exception(program: str, error: Type[BaseException]) -> None:
        compiler = Compiler(TEMP_FOLDER, program)

        with pytest.raises(error):
            compiler.compile_to_binary()


class TestAtoms(BaseCompilerTest):
    def test_integer(self):
        self.tests = [
            ("42", "42"),
            ("-272", "-272")
        ]
        self.check_programs()

    def test_char(self):
        self.tests = [
            ("a", "#\\a"),
            ("Z", "#\\Z")
        ]
        self.check_programs()

    def test_bool(self):
        self.tests = [
            ("#t", "#t"),
            ("#f", "#f")
        ]
        self.check_programs()


class TestUnaryPrimitives(BaseCompilerTest):
    def test_add1_to_zero(self):
        self.tests = [
            ("(primcall add1 0)", "1"),
            ("(primcall add1 41)", "42"),
            ("(primcall add1 -43)", "-42")
        ]
        self.check_programs()

    def test_add1_invalid_args(self):
        self.tests = [
            ("(primcall add1)", ValueError),
            ("(primcall add1 1 2)", ValueError)
        ]
        self.check_programs()

    def test_sub1_to_zero(self):
        self.tests = [
            ("(primcall sub1 0)", "-1"),
            ("(primcall sub1 43)", "42"),
            ("(primcall sub1 -41)", "-42")
        ]
        self.check_programs()

    def test_sub1_invalid_args(self):
        self.tests = [
            ("(primcall sub1)", ValueError),
            ("(primcall sub1 1 2)", ValueError)
        ]
        self.check_programs()

    def test_is_integer(self):
        self.tests = [
            ("(primcall integer? 10)", "#t"),
            ("(primcall integer? -42)", "#t"),
            ("(primcall integer? #t)", "#f"),
            ("(primcall integer? a)", "#f")
        ]
        self.check_programs()

    def test_is_integer_invalid_args(self):
        self.tests = [
            ("(primcall integer?)", ValueError),
            ("(primcall integer? 1 2)", ValueError)
        ]
        self.check_programs()

    def test_is_zero(self):
        self.tests = [
            ("(primcall zero? 0)", "#t"),
            ("(primcall zero? -42)", "#f"),
            ("(primcall zero? #t)", "#f"),
            ("(primcall zero? a)", "#f")
        ]
        self.check_programs()

    def test_is_zero_invalid_args(self):
        self.tests = [
            ("(primcall zero?)", ValueError),
            ("(primcall zero? 1 2)", ValueError)
        ]
        self.check_programs()

    def test_is_boolean(self):
        self.tests = [
            ("(primcall boolean? 10)", "#f"),
            ("(primcall boolean? -42)", "#f"),
            ("(primcall boolean? #t)", "#t"),
            ("(primcall boolean? a)", "#f")
        ]
        self.check_programs()

    def test_is_boolean_invalid_args(self):
        self.tests = [
            ("(primcall boolean?)", ValueError),
            ("(primcall boolean? 1 2)", ValueError)
        ]
        self.check_programs()

    def test_is_char(self):
        self.tests = [
            ("(primcall char? 10)", "#f"),
            ("(primcall char? -42)", "#f"),
            ("(primcall char? #t)", "#f"),
            ("(primcall char? a)", "#t")
        ]
        self.check_programs()

    def test_is_char_invalid_args(self):
        self.tests = [
            ("(primcall char?)", ValueError),
            ("(primcall char? 1 2)", ValueError)
        ]
        self.check_programs()


class TestBinaryPrimitives(BaseCompilerTest):
    def test_add(self):
        self.tests = [
            ("(primcall + 0 10)", "10"),
            ("(primcall + 41 1)", "42"),
            ("(primcall + 42 -84 )", "-42")
        ]
        self.check_programs()

    def test_sub(self):
        self.tests = [
            ("(primcall - 0 10)", "-10"),
            ("(primcall - 43 1)", "42"),
            ("(primcall - 42 84 )", "-42")
        ]
        self.check_programs()

    def test_mul(self):
        self.tests = [
            ("(primcall * 0 10)", "0"),
            ("(primcall * 42 1)", "42"),
            ("(primcall * -42 -1 )", "42"),
            ("(primcall * 10 13 )", "130")
        ]
        self.check_programs()

    def test_equal(self):
        self.tests = [
            ("(primcall = -10 10)", "#f"),
            ("(primcall = 0 10)", "#f"),
            ("(primcall = 42 42)", "#t")
        ]
        self.check_programs()

    def test_less_than(self):
        self.tests = [
            ("(primcall < -10 10)", "#t"),
            ("(primcall < 10 10)", "#f"),
            ("(primcall < 43 42)", "#f")
        ]
        self.check_programs()

    def test_equal_char(self):
        self.tests = [
            ("(primcall char=? a a)", "#t"),
            ("(primcall char=? a z)", "#f")
        ]
        self.check_programs()
