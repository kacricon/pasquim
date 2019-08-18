from typing import Type

from unittest import TestCase
import pytest
from subprocess import run, PIPE

from pasquim.compiler import Compiler

TEMP_FOLDER = "tests/tmp"


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


class TestPrimitives(TestCase):
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
