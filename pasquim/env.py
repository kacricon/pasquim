from __future__ import annotations

from typing import Union, Iterable
import math
import operator as op

from pasquim.parser import Lexer, Parser

# A Scheme expression, which can be an Atom or List
Exp = Union[str, int, float, list]


class Env(dict):
    """An environment represented by a dict of {'variable': value} pairs.

    This environment may be contained by an outer Env.
    """
    def __init__(self, params: Iterable = (), args: Iterable = (),
                 outer: Union[None, Env] = None) -> None:
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var: str) -> Env:
        """Finds the innermost Env that contains 'var'."""
        return self if var in self else self.outer.find(var)


class Procedure:
    """An user-defined Scheme procedure."""
    def __init__(self, params: Iterable, body: Exp, env: Env):
        self.params, self.body, self.env = params, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, self.env))


def standard_env() -> Env:
    """Creates an environment with some Scheme standard procedures."""
    env = Env()

    # `math` module operators
    env.update(vars(math))  # sin, cos, sqrt, pi, ...

    # other operators
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'abs': abs,
        'append': op.add,
        'apply': lambda proc, args: proc(*args),
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'expt': pow,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, (float, int)),
        'print': print,
        'procedure?': callable,
        'round': round,
        'symbol?': lambda x: isinstance(x, str),
    })

    return env


def eval(x: Exp, env: Env = standard_env()) -> Union[Exp, Procedure, None]:
    """Evaluates an expression in an environment."""
    if isinstance(x, str):             # variable reference
        return env.find(x)[x]
    elif not isinstance(x, list):         # constant
        return x

    op, *args = x
    if op == 'quote':                     # quotation
        return args[0]
    elif op == 'if':                      # conditional
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'define':                  # definition
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':                    # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':                  # procedure
        (params, body) = args
        return Procedure(params, body, env)
    else:                                 # procedure call
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)


def repl(prompt: str = 'pasquim> ') -> None:
    """A prompt-read-eval-print loop."""
    while True:
        val = eval(Parser(Lexer(input(prompt)).tokenize()).parse())
        if val is not None:
            print(schemestr(val))


def schemestr(exp) -> str:
    """Converts a Python object back into a Scheme-readable string."""
    if isinstance(exp, list):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)
