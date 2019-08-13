import os
from pathlib import Path


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
        self.program = program
        self.asm_program = ""

    @staticmethod
    def _prep_output(path: str) -> Path:
        """Prepares output path for the compiled program."""
        output_path = Path(path)
        output_path.mkdir(parents=True, exist_ok=True)

        return output_path

    def emit(self, line: str) -> None:
        """Adds a line to the assembly program."""
        self.asm_program += line + "\n"

    def compile_expr(self, expr):
        """Compiles a single passed expression."""
        self.emit(f"movl ${expr}, %eax")

    def compile_program(self) -> None:
        self.asm_program = ""  # reset

        self.emit(".text")
        self.emit(".p2align 4,,15")
        self.emit(".globl scheme_entry")
        self.emit("scheme_entry:")

        # handle incoming call from C
        self.emit("push %esi")
        self.emit("push %edi")
        self.emit("push %edx")

        # our code goes here
        self.compile_expr(self.program)

        # restore state for return to C
        self.emit("pop %edx")
        self.emit("pop %edi")
        self.emit("pop %esi")
        self.emit("ret")

    def compile_to_binary(self) -> None:
        self.compile_program()

        compiled_path = self.path.joinpath("compiled.s")
        with open(compiled_path, 'w') as f:
            f.write(self.asm_program)

        os.system(f"gcc -fomit-frame-pointer -m32 "
                  f"{str(compiled_path)} pasquim/src/rts.c "
                  f"-o {str(self.path.joinpath('a.out'))}")
