from typing import List, Tuple, Dict, Any
from .tokens import Token
from .grammar import EPS

class ParserError(Exception):
    pass

def _fmt_expected_single(sym: str) -> str:
    return "{ " + sym + " }"

def _fmt_expected_row(row: dict) -> str:
    if not row:
        return "{ }"
    terms = sorted(row.keys())
    return "{ " + ", ".join(terms) + " }"

def _stack_topdown(stack_internal: List[str]) -> List[str]:
    return list(reversed(stack_internal))

class LL1Parser:
    def __init__(self, table, start, is_terminal, is_nonterminal):
        self.table = table
        self.start = start
        self.is_terminal = is_terminal
        self.is_nonterminal = is_nonterminal

    def parse(self, tokens: List[Token]) -> Tuple[bool, List[Dict[str, Any]]]:
        stack = ['EOF', self.start]
        i = 0
        trace: List[Dict[str, Any]] = []

        while stack:
            stack_before_internal = list(stack)
            X = stack.pop()
            look = tokens[i]

            def emit(action: str):
                trace.append({
                    "i": i,
                    "stack": _stack_topdown(stack_before_internal),
                    "X": X,
                    "lookahead": look.kind,
                    "look_lexeme": look.lexeme,
                    "action": action,
                })

            if X == 'EOF':
                if look.kind == 'EOF':
                    emit("ACCEPT")
                    return True, trace
                raise ParserError(
                    f"{look.line}:{look.col}: esperado EOF, mas veio {look.kind} '{look.lexeme}'"
                )

            if self.is_terminal(X):
                if X == look.kind:
                    emit(f"MATCH '{look.lexeme}'")
                    i += 1
                else:
                    expected = _fmt_expected_single(X)
                    raise ParserError(
                        f"{look.line}:{look.col}: O parser esperava {expected}, "
                        f"mas veio {look.kind} '{look.lexeme}'"
                    )
                continue

            if X == EPS:
                emit("ε (pula)")
                continue

            row = self.table.get(X, {})
            prod = row.get(look.kind)

            if not prod:
                expected = _fmt_expected_row(row)
                raise ParserError(
                    f"{look.line}:{look.col}: O parser esperava {expected}, "
                    f"mas veio {look.kind} '{look.lexeme}'"
                )

            for sym in reversed(prod):
                if sym != EPS:
                    stack.append(sym)

            emit(f"{X} → {' '.join(prod)}")

        return False, trace
