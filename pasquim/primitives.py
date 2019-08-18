"""
Module containing every implemented primitive operator.

Every operator has a corresponding Python function that
takes the argument `arg` containing the procedure call's
arguments, and returns a list of instructions to emmit
to the assembly program.

A dict called `primitives` maps the name of the operator
in Scheme to the corresponding Python function.
"""
from typing import List

from pasquim.datatypes import immediate_rep


def add1(args: list) -> List[str]:
    """Adds 1 to a number."""
    if len(args) != 1:
        raise ValueError("A single argument should be passed to add1.")

    instructions = [
        f"movl ${immediate_rep(args[0])}, %eax",
        f"addl ${immediate_rep(1)}, %eax"
    ]
    return instructions


def sub1(args: list) -> List[str]:
    """Subtracts 1 to a number."""
    if len(args) != 1:
        raise ValueError("A single argument should be passed to sub1.")

    instructions = [
        f"movl ${immediate_rep(args[0])}, %eax",
        f"subl ${immediate_rep(1)}, %eax"
    ]
    return instructions


def integer_to_char(args: list) -> List[str]:
    NotImplemented


primitives = {
    'add1': add1,
    'sub1': sub1,
    'integer->char': integer_to_char
}
