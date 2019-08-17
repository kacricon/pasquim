"""
Data types as 32-bit words, using tagged pointers.

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
    """Converts a Python object to a 32-bit word representation."""
    if isinstance(x, bool):
        return (1 << bool_shift) | bool_tag if x else bool_tag
    elif isinstance(x, int):
        return x << fixnum_shift
    elif isinstance(x, str) and len(x) == 1:
        return (ord(x) << char_shift) | char_tag
    else:
        NotImplemented