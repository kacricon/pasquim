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


def immediate_rep(x):
    """Converts a Python object to its 32-bit word representation."""
    if isinstance(x, bool):
        return (1 << bool_shift) | bool_tag if x else bool_tag
    elif isinstance(x, int):
        return x << fixnum_shift
    elif isinstance(x, str) and len(x) == 1:
        return (ord(x) << char_shift) | char_tag
    else:
        NotImplemented


def compile_expr(expr: Any) -> List[str]:
    if is_immediate(expr):
        expr = immediate_rep(expr)
        return [f"movl ${expr}, %eax"]
    elif is_primitive_call(expr):
        expr.pop(0)
        primcall_op = expr.pop(0)
        primcall_args = expr

        return primitives.get(primcall_op)(primcall_args)
    else:
        raise ValueError(f"Unrecognized expression {str(expr)}")


def is_immediate(x: Any) -> bool:
    """Checks if x is an immediate value.

    Immediate values can be an integer, boolean, character or null.
    """
    return isinstance(x, int) or\
        (isinstance(x, str) and len(x) == 1) or\
        x is None


def is_primitive_call(x: Any) -> bool:
    """Checks if x is a primitive call.

    Args:
        x ([type]): [description]
    """
    return isinstance(x, list) and len(x) > 1 and x[0] == 'primcall'


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


def add1(args: list) -> List[str]:
    """Adds 1 to a number."""
    _check_unary_args(args, 'add1')

    return [
        f"movl ${immediate_rep(args[0])}, %eax",
        f"addl ${immediate_rep(1)}, %eax"
    ]


def sub1(args: list) -> List[str]:
    """Subtracts 1 to a number."""
    _check_unary_args(args, 'sub1')

    return [
        f"movl ${immediate_rep(args[0])}, %eax",
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


def is_integer(args: list) -> List[str]:
    """Checks if value is an integer."""
    _check_unary_args(args, 'integer?')

    return (
        compile_expr(args[0]) +
        [f"andl ${fixnum_mask}, %eax"] +
        _is_eax_equal_to(0)
    )


def is_zero(args: list) -> List[str]:
    """Checks if value is the integer zero."""
    _check_unary_args(args, 'zero?')

    return (
        compile_expr(args[0]) +
        _is_eax_equal_to(0)
    )


def is_boolean(args: list) -> List[str]:
    """Checks if value is a boolean."""
    _check_unary_args(args, 'boolean?')

    return (
        compile_expr(args[0]) +
        [f"andl ${bool_mask}, %eax"] +
        _is_eax_equal_to(bool_tag)
    )


def is_char(args: list) -> List[str]:
    """Checks if value is a char."""
    _check_unary_args(args, 'char?')

    return (
        compile_expr(args[0]) +
        [f"andl ${char_mask}, %eax"] +
        _is_eax_equal_to(char_tag)
    )


primitives = {
    'add1': add1,
    'sub1': sub1,
    'integer?': is_integer,
    'zero?': is_zero,
    'boolean?': is_boolean,
    'char?': is_char
}
