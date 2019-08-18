from typing import List, Union
import re

# A Scheme expression, which can be an Atom or List
Exp = Union[str, int, float, list]


class Lexer:
    """Converts a Scheme program string into a list of tokens.

    Args:
        program (str): The string containing the Scheme program.

    Returns:
        list: List of tokens.
    """
    def __init__(self, program: str) -> None:
        self.program = program

    def tokenize(self) -> List[str]:
        return self.program.replace('(', ' ( ').replace(')', ' ) ').split()


class Parser:
    """Parses list of tokens into an abstract syntax tree.

    Args:
        tokens (List[str]): List of takens to be parsed.

    Returns:
        Resulting AST.
    """
    def __init__(self, tokens: List[str]):
        self.tokens = tokens

    def parse(self) -> Exp:
        """Reads a Scheme expression from a string."""
        return self.read_from_tokens(self.tokens)

    def read_from_tokens(self, tokens: List[str]) -> Exp:
        """Reads an expression from a sequence of tokens."""
        if len(tokens) == 0:
            raise SyntaxError('unexpected EOF')
        token = tokens.pop(0)
        if token == '(':
            L = []
            while tokens[0] != ')':
                L.append(self.read_from_tokens(tokens))
            tokens.pop(0)  # pop off ')'
            return L
        elif token == ')':
            raise SyntaxError('unexpected )')
        else:
            return self.atom(token)

    def atom(self, token: str) -> Union[int, bool, str]:
        """Numbers become numbers; every other token is a symbol."""
        atom_types = [
            ("-?[0-9]+", int),
            ("#t|#f", lambda x: True if x == "#t" else False)
        ]

        for regexp, func in atom_types:
            if re.match("\\A" + regexp, token):
                return func(token)
        return str(token)
