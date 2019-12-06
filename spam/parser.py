from lark import Lark, InlineTransformer
from pathlib import Path

from .runtime import Symbol


class SpamTransformer(InlineTransformer):
    def start(self, *args): 
        return ["module", *args]  # (begin x1 x2 x3 ...)

    def vento(self, i):
        return int(i)

    def dobrarameta(self, f):
        return float(f)

    def nome(self, x):
        return Symbol(x)

    def mandioca(self, x):
        return str(x)[1:-1].replace(r"\n", "\n").replace(r"\t", "\t").replace(r"\"", "\"")

    def list(self, *args): # *args passa um numero nao contabilizado de argumentos, transformando-os numa lista
        return list(args)   

    def simplecmd(self, expr):
        return ['simplecmd', expr] 


def parse(src: str):
    """
    Compila string de entrada e retorna a S-expression equivalente.
    """
    return parser.parse(src)


def _make_grammar():
    """
    Retorna uma gramática do Lark inicializada.
    """

    path = Path(__file__).parent / 'grammar.lark'
    with open(path) as fd:
        grammar = Lark(fd, parser='lalr', transformer=SpamTransformer())
    return grammar

parser = _make_grammar()