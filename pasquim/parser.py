from pasquim.types import Exp, Atom, Symbol


def parse(chars: str) -> Exp:
    """Reads a Scheme expression from a string."""
    return read_from_tokens(tokenize(chars))


def tokenize(chars: str) -> list:
    """Converts a string of characters into a list of tokens."""
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def read_from_tokens(tokens: list) -> Exp:
    """Reads an expression from a sequence of tokens."""
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token: str) -> Atom:
    """Numbers become numbers; every other token is a symbol."""
    try:
        return int(token)  # tries to evaluate token as int first
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)
