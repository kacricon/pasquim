from unittest import TestCase

from pasquim.primitives import immediate_rep


class TestRepresentation(TestCase):
    """Checks the 32-bit represetation for each data type"""
    def test_integer(self):
        assert immediate_rep(125) == int('111110100', 2)

    def test_char(self):
        assert immediate_rep('a') == int('110000100000111', 2)
        assert immediate_rep('z') == int('111101000000111', 2)

    def test_bool(self):
        assert immediate_rep(True) == int('100001111', 2)
        assert immediate_rep(False) == int('1111', 2)
