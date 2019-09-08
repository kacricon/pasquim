from typing import Type

from unittest import TestCase
import pytest
from hypothesis import settings, given, example, assume, strategies as st
from subprocess import run, PIPE

from pasquim.compiler import Compiler


TEMP_FOLDER = "tmp"
INT_RANGE = [-2 ** 29, 2 ** 29 + 1]  # 30-bits
CHAR_RANGE = {
    # ASCII, but only consider letters and underscores
    'min_codepoint': 0, 'max_codepoint': 127,
    'whitelist_categories': ['L', 'Pc']
}

settings.register_profile("test", deadline=None)
settings.load_profile("test")


def _compile_and_check(program: str, output: str) -> None:
    """Compiles program and checks if output matches expectation."""
    compiler = Compiler(TEMP_FOLDER, program)
    compiler.compile_to_binary()

    results = run(TEMP_FOLDER+"/a.out", stdout=PIPE)
    assert results.stdout == (output + "\n").encode('UTF-8')


def _compile_and_compare(program_x: str, program_y: str) -> None:
    """Compiles two programs and checks if outputs match."""
    Compiler(TEMP_FOLDER+'/x/', program_x).compile_to_binary()
    Compiler(TEMP_FOLDER+'/y/', program_y).compile_to_binary()

    results_x = run(TEMP_FOLDER+"/x/a.out", stdout=PIPE)
    results_y = run(TEMP_FOLDER+"/y/a.out", stdout=PIPE)
    assert results_x.stdout == results_y.stdout


def _check_exception(program: str, error: Type[BaseException]) -> None:
    compiler = Compiler(TEMP_FOLDER, program)

    with pytest.raises(error):
        compiler.compile_to_binary()


class TestAtoms(TestCase):
    @given(st.integers(*INT_RANGE))
    @example(x=0)
    def test_integer(self, x):
        _compile_and_check(f"{x}", f"{x}")

    @given(st.characters(**CHAR_RANGE))
    def test_char(self, x):
        _compile_and_check(x, f"#\\{x}")

    def test_bool(self):
        _compile_and_check("#t", "#t")
        _compile_and_check("#f", "#f")


class TestUnaryPrimitives(TestCase):
    @given(st.integers(INT_RANGE[0], INT_RANGE[1]-1))
    @example(x=0)
    def test_add1(self, x):
        _compile_and_check(f"(primcall add1 {x})", f"{x+1}")

    def test_add1_no_args(self):
        _check_exception("(primcall add1)", ValueError)

    def test_add1_excess_args(self):
        _check_exception("(primcall add1 1 2)", ValueError)

    @given(st.integers(INT_RANGE[0]+1, INT_RANGE[1]))
    @example(x=0)
    def test_sub1(self, x):
        _compile_and_check(f"(primcall sub1 {x})", f"{x-1}")

    def test_sub1_no_args(self):
        _check_exception("(primcall sub1)", ValueError)

    def test_sub1_excess_args(self):
        _check_exception("(primcall sub1 1 2)", ValueError)

    @given(st.integers(*INT_RANGE))
    @example(x=0)
    def test_integer_is_integer(self, x):
        _compile_and_check(f"(primcall integer? {x})", "#t")

    @given(st.characters(**CHAR_RANGE))
    def test_char_is_integer(self, x):
        _compile_and_check(f"(primcall integer? {x})", "#f")

    def test_bool_is_integer(self):
        _compile_and_check("(primcall integer? #t)", "#f")
        _compile_and_check("(primcall integer? #f)", "#f")

    def test_is_integer_invalid_args(self):
        _check_exception("(primcall integer?)", ValueError)
        _check_exception("(primcall integer? 1 2)", ValueError)

    @given(st.integers(*INT_RANGE))
    @example(x=0)
    def test_integer_is_zero(self, x):
        _compile_and_check(f"(primcall zero? {x})", "#t" if x == 0 else "#f")

    @given(st.characters(**CHAR_RANGE))
    def test_char_is_zero(self, x):
        _compile_and_check(f"(primcall zero? {x})", "#f")

    def test_bool_is_zero(self):
        _compile_and_check("(primcall zero? #t)", "#f")
        _compile_and_check("(primcall zero? #f)", "#f")

    def test_is_zero_no_args(self):
        _check_exception("(primcall zero?)", ValueError)

    def test_is_zero_excess_args(self):
        _check_exception("(primcall zero? 1 2)", ValueError)

    @given(st.integers(*INT_RANGE))
    @example(x=0)
    def test_integer_is_boolean(self, x):
        _compile_and_check(f"(primcall boolean? {x})", "#f")

    @given(st.characters(**CHAR_RANGE))
    def test_char_is_boolean(self, x):
        _compile_and_check(f"(primcall boolean? {x})", "#f")

    def test_boolean_is_boolean(self):
        _compile_and_check("(primcall boolean? #t)", "#t")
        _compile_and_check("(primcall boolean? #f)", "#t")

    def test_is_boolean_no_args(self):
        _check_exception("(primcall boolean?)", ValueError)

    def test_is_boolean_excess_args(self):
        _check_exception("(primcall boolean? 1 2)", ValueError)

    @given(st.integers(*INT_RANGE))
    @example(x=0)
    def test_integer_is_char(self, x):
        _compile_and_check(f"(primcall char? {x})", "#f")

    @given(st.characters(**CHAR_RANGE))
    def test_char_is_char(self, x):
        _compile_and_check(f"(primcall char? {x})", "#t")

    def test_boolean_is_char(self):
        _compile_and_check("(primcall char? #t)", "#f")
        _compile_and_check("(primcall char? #f)", "#f")

    def test_is_char_no_args(self):
        _check_exception("(primcall char?)", ValueError)

    def test_is_char_excess_args(self):
        _check_exception("(primcall char? 1 2)", ValueError)


class TestBinaryPrimitives(TestCase):
    @given(st.integers(*INT_RANGE))
    def test_sum_identity(self, x):
        _compile_and_check(f"(primcall + {x} 0)", f"{x}")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_sum_commutative(self, x, y):
        int_sum = x + y
        assume(INT_RANGE[0] <= int_sum <= INT_RANGE[1])
        _compile_and_check(f"(primcall + {x} {y})", f"{int_sum}")
        _compile_and_check(f"(primcall + {y} {x})", f"{int_sum}")

    @given(st.integers(*INT_RANGE),
           st.integers(*INT_RANGE),
           st.integers(*INT_RANGE))
    def test_sum_associative(self, x, y, z):
        int_sum = x + y + z
        assume(INT_RANGE[0] <= int_sum <= INT_RANGE[1])
        _compile_and_check(f"(primcall + (primcall + {x} {y}) {z})",
                           f"{int_sum}")
        _compile_and_check(f"(primcall + {x} (primcall + {y} {z}))",
                           f"{int_sum}")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_sub(self, x, y):
        int_sub = x - y
        assume(INT_RANGE[0] <= int_sub <= INT_RANGE[1])
        _compile_and_check(f"(primcall - {x} {y})", f"{int_sub}")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_sub_neg_sum(self, x, y):
        int_sub = x - y
        assume(INT_RANGE[0] <= int_sub <= INT_RANGE[1])
        _compile_and_compare(
            f"(primcall - {x} {y})",
            f"(primcall + {x} {-y})")

    @given(st.integers(*INT_RANGE))
    def test_mul_identity(self, x):
        _compile_and_check(f"(primcall * {x} 1)", f"{x}")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_mul_commutative(self, x, y):
        int_mul = x * y
        assume(INT_RANGE[0] <= int_mul <= INT_RANGE[1])
        _compile_and_check(f"(primcall * {x} {y})", f"{int_mul}")
        _compile_and_check(f"(primcall * {y} {x})", f"{int_mul}")

    @given(
        st.tuples(st.integers(*INT_RANGE),
                  st.integers(*INT_RANGE),
                  st.integers(*INT_RANGE))
        .filter(lambda x: INT_RANGE[0] <= (x[0]*x[1]*x[2]) <= INT_RANGE[1]))
    def test_mul_associative(self, args):
        x, y, z = args
        int_mul = x * y * z
        _compile_and_check(f"(primcall * (primcall * {x} {y}) {z})",
                           f"{int_mul}")
        _compile_and_check(f"(primcall * {x} (primcall * {y} {z}))",
                           f"{int_mul}")

    @given(st.integers(*INT_RANGE))
    def test_equal_true(self, x):
        _compile_and_check(f"(primcall = {x} {x})", "#t")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_equal_false(self, x, y):
        assume(x != y)
        _compile_and_check(f"(primcall = {x} {y})", "#f")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_less_than_true(self, x, y):
        assume(x < y)
        _compile_and_check(f"(primcall < {x} {y})", "#t")

    @given(st.integers(*INT_RANGE), st.integers(*INT_RANGE))
    def test_less_than_false(self, x, y):
        assume(x >= y)
        _compile_and_check(f"(primcall < {x} {y})", "#f")

    @given(st.characters(**CHAR_RANGE))
    def test_equal_char_true(self, x):
        _compile_and_check(f"(primcall char=? {x} {x})", "#t")

    @given(st.characters(**CHAR_RANGE), st.characters(**CHAR_RANGE))
    def test_equal_char_false(self, x, y):
        assume(x != y)
        _compile_and_check(f"(primcall char=? {x} {y})", "#f")
