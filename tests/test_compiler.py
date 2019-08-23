from typing import Type

from unittest import TestCase
import pytest
from subprocess import run, PIPE

from pasquim.compiler import Compiler

TEMP_FOLDER = "tmp"


def _compile_and_compare(program: str, output: str) -> None:
    compiler = Compiler(TEMP_FOLDER, program)
    compiler.compile_to_binary()

    results = run(TEMP_FOLDER+"/a.out", stdout=PIPE)
    assert results.stdout == (output + "\n").encode('UTF-8')


def _check_exception(program: str, error: Type[BaseException]) -> None:
    compiler = Compiler(TEMP_FOLDER, program)

    with pytest.raises(error):
        compiler.compile_to_binary()


class TestAtoms(TestCase):
    def test_integer(self):
        _compile_and_compare("42", "42")
        _compile_and_compare("-272", "-272")

    def test_char(self):
        _compile_and_compare("a", "#\\a")
        _compile_and_compare("Z", "#\\Z")

    def test_bool(self):
        _compile_and_compare("#t", "#t")
        _compile_and_compare("#f", "#f")


class TestUnaryPrimitives(TestCase):
    def test_add1_to_zero(self):
        _compile_and_compare("(primcall add1 0)", "1")
        _compile_and_compare("(primcall add1 41)", "42")
        _compile_and_compare("(primcall add1 -43)", "-42")

    def test_add1_invalid_args(self):
        _check_exception("(primcall add1)", ValueError)
        _check_exception("(primcall add1 1 2)", ValueError)

    def test_sub1_to_zero(self):
        _compile_and_compare("(primcall sub1 0)", "-1")
        _compile_and_compare("(primcall sub1 43)", "42")
        _compile_and_compare("(primcall sub1 -41)", "-42")

    def test_sub1_invalid_args(self):
        _check_exception("(primcall sub1)", ValueError)
        _check_exception("(primcall sub1 1 2)", ValueError)

    def test_is_integer(self):
        _compile_and_compare("(primcall integer? 10)", "#t")
        _compile_and_compare("(primcall integer? -42)", "#t")
        _compile_and_compare("(primcall integer? #t)", "#f")
        _compile_and_compare("(primcall integer? a)", "#f")

    def test_is_integer_invalid_args(self):
        _check_exception("(primcall integer?)", ValueError)
        _check_exception("(primcall integer? 1 2)", ValueError)

    def test_is_zero(self):
        _compile_and_compare("(primcall zero? 0)", "#t")
        _compile_and_compare("(primcall zero? -42)", "#f")
        _compile_and_compare("(primcall zero? #t)", "#f")
        _compile_and_compare("(primcall zero? a)", "#f")

    def test_is_zero_invalid_args(self):
        _check_exception("(primcall zero?)", ValueError)
        _check_exception("(primcall zero? 1 2)", ValueError)

    def test_is_boolean(self):
        _compile_and_compare("(primcall boolean? 10)", "#f")
        _compile_and_compare("(primcall boolean? -42)", "#f")
        _compile_and_compare("(primcall boolean? #t)", "#t")
        _compile_and_compare("(primcall boolean? a)", "#f")

    def test_is_boolean_invalid_args(self):
        _check_exception("(primcall boolean?)", ValueError)
        _check_exception("(primcall boolean? 1 2)", ValueError)

    def test_is_char(self):
        _compile_and_compare("(primcall char? 10)", "#f")
        _compile_and_compare("(primcall char? -42)", "#f")
        _compile_and_compare("(primcall char? #t)", "#f")
        _compile_and_compare("(primcall char? a)", "#t")

    def test_is_char_invalid_args(self):
        _check_exception("(primcall char?)", ValueError)
        _check_exception("(primcall char? 1 2)", ValueError)


class TestBinaryPrimitives(TestCase):
    def test_add(self):
        _compile_and_compare("(primcall + 0 10)", "10")
        _compile_and_compare("(primcall + 41 1)", "42")
        _compile_and_compare("(primcall + 42 -84 )", "-42")

    def test_sub(self):
        _compile_and_compare("(primcall - 0 10)", "-10")
        _compile_and_compare("(primcall - 43 1)", "42")
        _compile_and_compare("(primcall - 42 84 )", "-42")

    def test_mul(self):
        _compile_and_compare("(primcall * 0 10)", "0")
        _compile_and_compare("(primcall * 42 1)", "42")
        _compile_and_compare("(primcall * -42 -1 )", "42")
        _compile_and_compare("(primcall * 10 13 )", "130")

    def test_equal(self):
        _compile_and_compare("(primcall = -10 10)", "#f")
        _compile_and_compare("(primcall = 0 10)", "#f")
        _compile_and_compare("(primcall = 42 42)", "#t")

    def test_less_than(self):
        _compile_and_compare("(primcall < -10 10)", "#t")
        _compile_and_compare("(primcall < 10 10)", "#f")
        _compile_and_compare("(primcall < 43 42)", "#f")

    def test_equal_char(self):
        _compile_and_compare("(primcall char=? a a)", "#t")
        _compile_and_compare("(primcall char=? a z)", "#f")
