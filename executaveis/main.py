import argparse
from .lexer import Lexer
from .tokens import TERMS
from .grammar import G, NONTERMS, START_SYMBOL
from .first_follow import compute_first_follow
from .table import build_ll1_table
from .parser import LL1Parser, ParserError

EXAMPLE_OK = """
int x; int y; boolean b;
write("Lockbixo!\n");
x = 10;
y = x + 2 * (x - 3);
b = (x >= y) && true || false;
if (b) { x = x + 1; } else { x = x - 1; }
while (x > 0) { x = x - 1; }
void main() { return; }
"""

EXAMPLE_ERR = """
int x;
if (x >) x = 1; // erro: expressão incompleta
"""

def is_terminal(sym: str) -> bool:
    return sym in TERMS

def is_nonterminal(sym: str) -> bool:
    return sym in NONTERMS

def print_tokens(toks):
    print("TOKENS:")
    for t in toks:
        print(f"  Token({t.kind}, '{t.lexeme}', {t.line}:{t.col})")

def print_first_follow(FIRST, FOLLOW):
    print("\nFIRST sets:")
    for A in NONTERMS:
        items = ', '.join(sorted(FIRST[A]))
        print(f"  FIRST({A}) = {{ {items} }}")
    print("\nFOLLOW sets:")
    for A in NONTERMS:
        items = ', '.join(sorted(FOLLOW[A]))
        print(f"  FOLLOW({A}) = {{ {items} }}")

def print_table(TABLE, conflicts):
    print("\nLL(1) TABLE (M[A,a]):")
    for A in NONTERMS:
        row = TABLE[A]
        if not row:
            continue
        print(f"\n  {A}:")
        for a, prod in sorted(row.items()):
            rhs = ' '.join(prod)
            print(f"    a={a} -> {A} → {rhs}")
    if conflicts:
        print("\n*** CONFLITOS ENCONTRADOS (não LL(1)): ***")
        for (A,a,p1,p2) in conflicts:
            print(f"  ({A}, {a}): {p1}  vs  {p2}")
    else:
        print("\nSem conflitos: gramática está LL(1) para os terminais considerados.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', nargs='?', help='arquivo .lbx para analisar')
    ap.add_argument('--err', action='store_true', help='usar exemplo com erro')
    ap.add_argument('--dump-first-follow', action='store_true')
    ap.add_argument('--dump-table', action='store_true')
    args = ap.parse_args()

    # Entrada
    if args.source:
        with open(args.source, 'r', encoding='utf-8') as f:
            code = f.read()
    else:
        code = EXAMPLE_ERR if args.err else EXAMPLE_OK

    toks = list(Lexer(code).tokens())

    FIRST, FOLLOW, first_of_sequence = compute_first_follow(G, NONTERMS, TERMS, START_SYMBOL)
    TABLE, conflicts = build_ll1_table(G, NONTERMS, TERMS, FIRST, FOLLOW, first_of_sequence)

    parser = LL1Parser(TABLE, START_SYMBOL, is_terminal, is_nonterminal)

    print_tokens(toks)
    if args.dump_first_follow:
        print_first_follow(FIRST, FOLLOW)
    if args.dump_table:
        print_table(TABLE, conflicts)

    print("\nPARSE TRACE (pilha topo→fundo / X / lookahead):")
    try:
        accepted, trace = parser.parse(toks)
        for st, X, la in trace[:160]:
            st_fmt = '[' + ', '.join(reversed(st)) + ']'
            print(f"  {st_fmt:40s}  X={X:14s}  lookahead={la}")
        if accepted:
            print("\n✅ Cadeia aceita (parse concluído sem erros).")
        else:
            print("\n❌ Cadeia NÃO aceita.")
    except ParserError as e:
        print(f"\n❌ Erro sintático: {e}")

if __name__ == '__main__':
    main()