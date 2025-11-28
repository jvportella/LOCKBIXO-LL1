import argparse
import shutil

from .lexer import Lexer
from .tokens import TERMS
from .grammar import G, NONTERMS, START_SYMBOL
from .first_follow import compute_first_follow
from .table import build_ll1_table
from .parser import LL1Parser, ParserError


EXAMPLE_OK = """
int x; int y; boolean b;
write("Lockbixo!\\n");
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

TERMS_NO_EOF = [t for t in TERMS if t != "EOF"]


def is_terminal(sym: str) -> bool:
    return sym == "EOF" or sym in TERMS_NO_EOF


def is_nonterminal(sym: str) -> bool:
    return sym in NONTERMS


def print_tokens(toks):
    print("TOKENS:")
    for t in toks:
        print(f"  Token({t.kind}, '{t.lexeme}', {t.line}:{t.col})")


def print_first_follow(FIRST, FOLLOW):
    print("\nFIRST sets:")
    for A in NONTERMS:
        items = ", ".join(sorted(FIRST[A]))
        print(f"  FIRST({A}) = {{ {items} }}")

    print("\nFOLLOW sets:")
    for A in NONTERMS:
        items = ", ".join(sorted(FOLLOW[A]))
        print(f"  FOLLOW({A}) = {{ {items} }}")


def print_conflicts(conflicts):
    if not conflicts:
        print("\n✅ Sem conflitos: gramática OK para LL(1) (pelos terminais considerados).")
        return
    print("\n❌ *** CONFLITOS ENCONTRADOS (gramática NÃO é LL(1)): ***")
    for (A, a, p1, p2) in conflicts:
        rhs1 = " ".join(p1)
        rhs2 = " ".join(p2)
        print(f"  M[{A}, {a}]: {A} → {rhs1}   vs   {A} → {rhs2}")


def print_table_list(TABLE):
    print("\nTABELA LL(1) (lista):")
    for A in NONTERMS:
        row = TABLE.get(A, {})
        if not row:
            continue
        print(f"\n{A}:")
        for a in sorted(row.keys()):
            rhs = " ".join(row[a])
            print(f"  M[{A}, {a}] = {A} → {rhs}")


def print_table_matrix(TABLE, *, max_cols=6, cell_w=34):
    base_terms = list(TERMS_NO_EOF)

    used_terms = set()
    for A in NONTERMS:
        used_terms.update(TABLE.get(A, {}).keys())

    cols = [t for t in base_terms if t in used_terms]
    if "EOF" in used_terms and "EOF" not in cols:
        cols.append("EOF")

    if not cols:
        print("\nTABELA LL(1) (matriz):\n  (vazia) — nenhuma entrada foi gerada.")
        return

    def short_prod(A, prod):
        rhs = " ".join(prod)
        s = f"{A}→{rhs}"
        if len(s) > cell_w - 1:
            s = s[: cell_w - 2] + "…"
        return s

    print("\nTABELA LL(1) (matriz):")
    for start in range(0, len(cols), max_cols):
        chunk = cols[start : start + max_cols]
        header = " " * 16 + "".join(f"{c:>{cell_w}s}" for c in chunk)
        print("\n" + header)
        print(" " * 16 + "-" * (cell_w * len(chunk)))

        for A in NONTERMS:
            row = TABLE.get(A, {})
            if not row:
                continue
            if not any(c in row for c in chunk):
                continue

            line = f"{A:<16s}"
            for c in chunk:
                line += f"{short_prod(A, row[c]):>{cell_w}s}" if c in row else f"{'':>{cell_w}s}"
            print(line)


def _clip(s: str, w: int) -> str:
    s = str(s)
    if w <= 0:
        return ""
    if len(s) <= w:
        return s.ljust(w)
    if w == 1:
        return "…"
    return s[: w - 1] + "…"


def _fmt_stack(ev: dict, max_items: int = 12) -> str:
    if "stack" in ev and isinstance(ev["stack"], list):
        st = ev["stack"]
    elif "stack_before" in ev and isinstance(ev["stack_before"], list):
        st = list(reversed(ev["stack_before"]))  # geralmente vem fundo→topo
    else:
        st = []

    if len(st) <= max_items:
        return "[" + ", ".join(st) + "]"

    head = st[: max_items - 1]
    return "[" + ", ".join(head) + ", …]"


def print_trace(trace, limit=200):
    term_w = shutil.get_terminal_size((140, 20)).columns

    stack_w = min(64, max(34, term_w // 3))
    x_w = 16
    la_w = 16
    action_w = max(24, term_w - (stack_w + x_w + la_w + 12))

    print("\nPARSE TRACE (pilha topo→fundo / X / lookahead / AÇÃO):")
    for ev in trace[:limit]:
        stack_s = _fmt_stack(ev, max_items=12)
        line = (
            f"{_clip(stack_s, stack_w)}  "
            f"X={_clip(ev.get('X',''), x_w)}  "
            f"LA={_clip(ev.get('lookahead',''), la_w)}  "
            f"AÇÃO={_clip(ev.get('action',''), action_w)}"
        )
        print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", help="arquivo .lbx para analisar")
    ap.add_argument("--err", action="store_true", help="usar exemplo com erro")

    ap.add_argument("--dump-first-follow", action="store_true", help="imprime FIRST e FOLLOW")
    ap.add_argument("--dump-table", action="store_true", help="imprime tabela LL(1) em formato de lista (recomendado)")
    ap.add_argument("--dump-table-matrix", action="store_true", help="imprime tabela LL(1) em formato de matriz (debug)")

    ap.add_argument("--matrix-cols", type=int, default=6, help="colunas por página na matriz")
    ap.add_argument("--matrix-cellw", type=int, default=34, help="largura da célula na matriz")

    ap.add_argument("--trace", action="store_true", help="mostra passo a passo do parser")
    ap.add_argument("--trace-limit", type=int, default=200, help="limite de passos do trace")

    args = ap.parse_args()

    if args.source:
        with open(args.source, "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = EXAMPLE_ERR if args.err else EXAMPLE_OK

    toks = list(Lexer(code).tokens())

    FIRST, FOLLOW, first_of_sequence = compute_first_follow(G, NONTERMS, TERMS_NO_EOF, START_SYMBOL)
    TABLE, conflicts = build_ll1_table(G, NONTERMS, TERMS_NO_EOF, FIRST, FOLLOW, first_of_sequence)

    if args.dump_first_follow:
        print_first_follow(FIRST, FOLLOW)

    if args.dump_table or args.dump_table_matrix:
        print_conflicts(conflicts)

    if args.dump_table:
        print_table_list(TABLE)

    if args.dump_table_matrix:
        print_table_matrix(TABLE, max_cols=args.matrix_cols, cell_w=args.matrix_cellw)

    print_tokens(toks)

    parser = LL1Parser(TABLE, START_SYMBOL, is_terminal, is_nonterminal)

    try:
        accepted, trace = parser.parse(toks)

        if args.trace:
            print_trace(trace, limit=args.trace_limit)

        print("\n✅ Cadeia aceita (parse concluído sem erros)." if accepted else "\n❌ Cadeia NÃO aceita.")
    except ParserError as e:
        print(f"\n❌ Erro sintático: {e}")


if __name__ == "__main__":
    main()
