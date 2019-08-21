from typing import Any
import os
from pathlib import Path

from pasquim.parser import Lexer, Parser
from pasquim.primitives import immediate_rep, primitives


class Compiler:
    """A Scheme compiler written in pure python.

    Translates a Scheme program into Assembly, then generates an executable
    binary.

    Args:
        path (str): Path where compiled program will be saved.
        program (str): Scheme program to be compiled.
    """
    def __init__(self, path: str, program: str) -> None:
        self.path = self._prep_output(path)
        parser = Parser(Lexer(program).tokenize())
        self.program = parser.parse()

        self.asm_program = ""

    @staticmethod
    def _prep_output(path: str) -> Path:
        """Prepares output path for the compiled program."""
        output_path = Path(path)
        output_path.mkdir(parents=True, exist_ok=True)

        return output_path

    def _emit(self, line: str) -> None:
        """Adds a line to the assembly program."""
        self.asm_program += line + "\n"

    def _compile_expr(self, expr) -> None:
        """Compiles a single passed expression."""
        if is_immediate(expr):
            expr = immediate_rep(expr)
            self._emit(f"movl ${expr}, %eax")
        elif is_primitive_call(expr):
            expr.pop(0)
            primcall_op = expr.pop(0)
            primcall_args = expr

            call = primitives.get(primcall_op)
            for i in call(primcall_args):
                self._emit(i)

    def compile_program(self) -> None:
        """Compiles Scheme program to Assembly."""
        self.asm_program = ""  # reset

        self._emit(".text")
        self._emit(".p2align 4,,15")
        self._emit(".globl scheme_entry")
        self._emit("scheme_entry:")

        # handle incoming call from C
        self._emit("push %esi")
        self._emit("push %edi")
        self._emit("push %edx")

        # program's code
        self._compile_expr(self.program)

        # restore state for return to C
        self._emit("pop %edx")
        self._emit("pop %edi")
        self._emit("pop %esi")
        self._emit("ret")

    def compile_to_binary(self) -> None:
        self.compile_program()

        compiled_path = self.path.joinpath("compiled.s")
        with open(compiled_path, 'w') as f:
            f.write(self.asm_program)

        os.system(f"gcc -fomit-frame-pointer -m32 "
                  f"{str(compiled_path)} pasquim/src/rts.c "
                  f"-o {str(self.path.joinpath('a.out'))}")


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


# def primitive_op(x: list) -> str:
#     """Returns the primitive operation from a passed primcall"""
#     return x[1]
