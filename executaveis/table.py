from typing import Dict, List, Tuple
from .grammar import EPS

def build_ll1_table(G, NONTERMS, TERMS, FIRST, FOLLOW, first_of_sequence):
    TABLE: Dict[str, Dict[str, List[str]]] = {A: {} for A in NONTERMS}
    conflicts: List[Tuple[str,str,List[str],List[str]]] = []
    for A in NONTERMS:
        for prod in G[A]:
            f = first_of_sequence(prod)
            for a in (f - {EPS}):
                if a in TABLE[A]:
                    conflicts.append((A, a, TABLE[A][a], prod))
                TABLE[A][a] = prod
            if EPS in f:
                for b in FOLLOW[A]:
                    if b in TABLE[A]:
                        conflicts.append((A, b, TABLE[A][b], prod))
                    TABLE[A][b] = prod
    return TABLE, conflicts