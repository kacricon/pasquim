from unittest import TestCase
from hypothesis import settings, given, strategies as st

from pasquim import primitives
from pasquim.primitives import immediate_rep


INT_RANGE = [-2 ** 29, 2 ** 29 + 1]  # 30-bits
CHAR_RANGE = {
    # ASCII, but only consider letters and underscores
    'min_codepoint': 0, 'max_codepoint': 127,
    'whitelist_categories': ['L', 'Pc']
}

settings.register_profile("test", deadline=None)
settings.load_profile("test")


class TestRepresentation(TestCase):
    """Checks the 32-bit represetation for each data type"""

    @given(st.integers(*INT_RANGE))
    def test_integer(self, x):
        bin_rep = x << primitives.fixnum_shift
        assert immediate_rep(x) == bin_rep

    @given(st.characters(**CHAR_RANGE))
    def test_char(self, x):
        bin_rep = (ord(x) << primitives.char_shift) | primitives.char_tag
        assert immediate_rep(x) == bin_rep

    def test_char_manual_cases(self):
        assert immediate_rep('a') == int('110000100000111', 2)
        assert immediate_rep('z') == int('111101000000111', 2)

    def test_bool(self):
        assert immediate_rep(True) == int('100001111', 2)
        assert immediate_rep(False) == int('1111', 2)
