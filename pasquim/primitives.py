from typing import Any, List


"""
Primitive data types, represented by 32-bit words using tagged pointers.

type      | 31            bit             0
-------------------------------------------------
        integer | iiiiiiiiiiiiiiiiiiiiiiiiiiiii00
        boolean | 0000000000000000000000b00001111
           char | 000000000000000cccccccc00000111
   pair pointer | pppppppppppppppppppppppppppp001
 vector pointer | pppppppppppppppppppppppppppp010
 string pointer | pppppppppppppppppppppppppppp011
 symbol pointer | pppppppppppppppppppppppppppp101
closure pointer | pppppppppppppppppppppppppppp110
"""

wordsize = 4  # number of bytes used for each word

# integer
fixnum_shift = 2
fixnum_mask = 3

# bool
bool_mask = 255
bool_shift = 8
bool_tag = 15

# char
char_mask = 255  # character type mask
char_shift = 8
char_tag = 7

# pointers
ptr_mask = 7
ptr_mask_inv = "#xfffffff8"

pair_tag = 1
vec_tag = 2
str_tag = 3
sym_tag = 5
closure_tag = 6


def immediate_rep(expr: Any):
    """Converts a Python object to its 32-bit word representation."""
    if isinstance(expr, bool):
        return (1 << bool_shift) | bool_tag if expr else bool_tag
    elif isinstance(expr, int):
        return expr << fixnum_shift
    elif isinstance(expr, str) and len(expr) == 1:
        return (ord(expr) << char_shift) | char_tag
    else:
        NotImplemented


def compile_expr(expr: Any, si: int) -> List[str]:
    if is_immediate(expr):
        expr = immediate_rep(expr)
        return [f"movl ${expr}, %eax"]
    elif is_primitive_call(expr):
        expr.pop(0)
        primcall_op = expr.pop(0)
        primcall_args = expr

        return primitive_ops.get(primcall_op)(primcall_args, si)
    else:
        raise ValueError(f"Unrecognized expression {str(expr)}")


def is_immediate(expr: Any) -> bool:
    """Checks if expr is an immediate value.

    Immediate values can be an integer, boolean, character or null.
    """
    return (isinstance(expr, int) or
            (isinstance(expr, str) and len(expr) == 1) or
            expr is None)


def is_primitive_call(expr: Any) -> bool:
    """Checks if expr is a primitive call."""
    return isinstance(expr, list) and len(expr) > 1 and expr[0] == 'primcall'


"""
Primitive operators.

Every operator has a corresponding Python function that
takes the argument `arg` containing the procedure call's
arguments, and returns a list of instructions to emmit
to the assembly program.

A dict called `primitives` maps the name of the operator
in Scheme to the corresponding Python function.
"""


# Unary operators
def _check_unary_args(args: list, op_name: str) -> None:
    if len(args) != 1:
        raise ValueError("A single argument should be passed to {op_name}.")


def add1(args: list, si: int) -> List[str]:
    """Adds 1 to a number."""
    _check_unary_args(args, 'add1')

    return compile_expr(args[0], si) + [
        f"addl ${immediate_rep(1)}, %eax"
    ]


def sub1(args: list, si: int) -> List[str]:
    """Subtracts 1 to a number."""
    _check_unary_args(args, 'sub1')

    return compile_expr(args[0], si) + [
        f"subl ${immediate_rep(1)}, %eax"
    ]


def _is_eax_equal_to(val: Any) -> List[str]:
    return [
        f"cmpl ${val}, %eax",         # check eax against val
        f"movl $0, %eax",             # zero eac, leaving equal flag in place
        f"sete %al",                  # set low bit of eax if they were equal
        f"sall ${bool_shift}, %eax",  # shift the bit up to the bool position
        f"orl ${bool_tag}, %eax"      # add boolean type tag
    ]


def is_integer(args: list, si: int) -> List[str]:
    """Checks if value is an integer."""
    _check_unary_args(args, 'integer?')

    return (
        compile_expr(args[0], si) +
        [f"andl ${fixnum_mask}, %eax"] +
        _is_eax_equal_to(0)
    )


def is_zero(args: list, si: int) -> List[str]:
    """Checks if value is the integer zero."""
    _check_unary_args(args, 'zero?')

    return (
        compile_expr(args[0], si) +
        _is_eax_equal_to(0)
    )


def is_boolean(args: list, si: int) -> List[str]:
    """Checks if value is a boolean."""
    _check_unary_args(args, 'boolean?')

    return (
        compile_expr(args[0], si) +
        [f"andl ${bool_mask}, %eax"] +
        _is_eax_equal_to(bool_tag)
    )


def is_char(args: list, si: int) -> List[str]:
    """Checks if value is a char."""
    _check_unary_args(args, 'char?')

    return (
        compile_expr(args[0], si) +
        [f"andl ${char_mask}, %eax"] +
        _is_eax_equal_to(char_tag)
    )


# binary operators
def add(args: list, si: int) -> List[str]:
    """Adds two numbers and returns results."""

    return (
        compile_expr(args[0], si) +
        [f"movl %eax, {si}(%esp)"] +
        compile_expr(args[1], si - wordsize) +
        [f"addl {si}(%esp), %eax"]
    )


def sub(args: list, si: int) -> List[str]:
    """Subtracts two numbers and returns results."""

    return (
        compile_expr(args[1], si) +
        [f"movl %eax, {si}(%esp)"] +
        compile_expr(args[0], si - wordsize) +
        [f"subl {si}(%esp), %eax"]
    )


def mul(args: list, si: int) -> List[str]:
    """Multiplies two numbers and returns results."""

    return (
        compile_expr(args[0], si) +
        [f"movl %eax, {si}(%esp)"] +
        compile_expr(args[1], si - wordsize) +
        [f"shrl ${fixnum_shift}, %eax",
         f"imull {si}(%esp), %eax"]
    )


def equal(args: list, si: int) -> List[str]:
    """Checks for equality between two numbers."""
    return (
        compile_expr(args[0], si) +
        [f"movl %eax, {si}(%esp)"] +
        compile_expr(args[1], si - wordsize) +
        [f"cmpl %eax, {si}(%esp)",
         f"movl $0, %eax",
         f"sete %al",
         f"sall ${bool_shift}, %eax",
         f"orl ${bool_tag}, %eax"]
    )


def less_than(args: list, si: int) -> List[str]:
    """Checks if a number is less than another."""
    return (
        compile_expr(args[0], si) +
        [f"movl %eax, {si}(%esp)"] +
        compile_expr(args[1], si - wordsize) +
        [f"cmpl %eax, {si}(%esp)",
         f"movl $0, %eax",
         f"setl %al",
         f"sall ${bool_shift}, %eax",
         f"orl ${bool_tag}, %eax"]
    )


def char_equal(args: list, si: int) -> List[str]:
    """Checks for equality between two chars."""
    return (
        compile_expr(args[0], si) +
        [f"shrl ${char_shift}, %eax"] +
        [f"movl %eax, {si}(%esp)"] +
        compile_expr(args[1], si - wordsize) +
        [f"shrl ${char_shift}, %eax"] +
        [f"cmpl %eax, {si}(%esp)",
         f"movl $0, %eax",
         f"sete %al",
         f"sall ${bool_shift}, %eax",
         f"orl ${bool_tag}, %eax"]
    )


primitive_ops = {
    # unary
    'add1': add1,
    'sub1': sub1,
    'integer?': is_integer,
    'zero?': is_zero,
    'boolean?': is_boolean,
    'char?': is_char,
    # binary
    '+': add,
    '-': sub,
    '*': mul,
    '=': equal,
    '<': less_than,
    'char=?': char_equal
}
