from typing import Union


# Scheme primitives
Symbol = str  # A Symbol is implemented as a Python str
Number = Union[int, float]  # A Number is implemented as a Python int or float
Atom = Union[Symbol, Number]  # An Atom is a Symbol or Number
List = list  # A List is implemented as a Python list
Exp = Union[Atom, List]  # An expression is an Atom or List
