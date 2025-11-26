from typing import List, Tuple
from .tokens import Token
from .grammar import EPS

class ParserError(Exception):
    pass

class LL1Parser:
    def __init__(self, table, start, is_terminal, is_nonterminal):
        self.table = table
        self.start = start
        self.is_terminal = is_terminal
        self.is_nonterminal = is_nonterminal

    def parse(self, tokens: List[Token]) -> Tuple[bool, list]:
        stack = ['EOF', self.start]
        i = 0
        trace = []
        while stack:
            X = stack.pop()
            look = tokens[i]
            trace.append((list(stack), X, look.kind))

            if X == 'EOF':
                if look.kind == 'EOF':
                    return True, trace
                raise ParserError(f"Esperava EOF, veio {look}")

            if self.is_terminal(X):
                if X == look.kind:
                    i += 1
                else:
                    raise ParserError(f"{look.line}:{look.col}: esperava {X}, veio {look.kind} ('{look.lexeme}')")
            elif X == EPS:
                continue
            else:
                entry = self.table.get(X, {}).get(look.kind)
                if not entry:
                    raise ParserError(
                        f"{look.line}:{look.col}: nenhuma produção para (A={X}, a={look.kind}) com lexema '{look.lexeme}'")
                for sym in reversed(entry):
                    if sym != EPS:
                        stack.append(sym)
        return False, trace