from typing import List, Tuple
from .tokens import Token
from .grammar import EPS

class ParserError(Exception):
    pass

def _fmt_expected_single(sym: str) -> str:
    # exibe como conjunto de 1 elemento
    return "{ " + sym + " }"

def _fmt_expected_row(row: dict) -> str:
    # row: TABLE[A] -> { terminal: produção }
    if not row:
        return "{ }"
    terms = sorted(row.keys())
    return "{ " + ", ".join(terms) + " }"

class LL1Parser:
    def __init__(self, table, start, is_terminal, is_nonterminal):
        self.table = table      # dict: { NonTerm: { terminal: [RHS...] } }
        self.start = start      # símbolo inicial
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

            # Aceitação explícita
            if X == 'EOF':
                if look.kind == 'EOF':
                    return True, trace
                raise ParserError(
                    f"{look.line}:{look.col}: esperado EOF, mas veio {look.kind} '{look.lexeme}'"
                )

            # Caso 1: X é terminal → precisa casar
            if self.is_terminal(X):
                if X == look.kind:
                    i += 1
                else:
                    expected = _fmt_expected_single(X)
                    raise ParserError(
                        f"{look.line} -{look.col}: O parser esperava {expected}, "
                        f"mas veio {look.kind} '{look.lexeme}'"
                    )

            # Caso 2: ε na pilha → ignora
            elif X == EPS:
                continue

            # Caso 3: X é não-terminal → consultar a tabela M[X, look.kind]
            else:
                row = self.table.get(X, {})
                prod = row.get(look.kind)

                if not prod:
                    expected = _fmt_expected_row(row)
                    raise ParserError(
                        f"O parser esperava {expected}, mas veio {look.kind} '{look.lexeme}'"
                    )

                # Empilha a RHS ao contrário (omitindo ε)
                for sym in reversed(prod):
                    if sym != EPS:
                        stack.append(sym)

        # Se saiu do loop sem consumir EOF, não aceitou
        return False, trace
