from typing import Union
import os
from pathlib import Path

from pasquim.parser import Lexer, Parser
from pasquim.primitives import compile_expr, wordsize

# A Scheme expression, which can be an Atom or List
Exp = Union[str, int, float, list]


class Compiler:
    """A Scheme compiler.

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

    def _emit_expr(self, expr: Exp) -> None:
        """Compiles a single passed expression."""

        for i in compile_expr(expr, -wordsize):
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
        self._emit_expr(self.program)

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
