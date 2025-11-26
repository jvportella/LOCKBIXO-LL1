from typing import Dict, List, Set
from .grammar import EPS

def compute_first_follow(G, NONTERMS: List[str], TERMS: List[str], START_SYMBOL: str):
    FIRST: Dict[str, Set[str]] = {A: set() for A in NONTERMS}
    for t in TERMS:
        FIRST[t] = {t}
    FIRST[EPS] = {EPS}

    def first_of_sequence(alpha: List[str]) -> Set[str]:
        res: Set[str] = set()
        if not alpha:
            res.add(EPS)
            return res
        for X in alpha:
            if X == EPS:
                res.add(EPS)
                break
            if X in FIRST and FIRST[X] == {X}:  # terminal
                res.add(X)
                break
            res.update(s for s in FIRST[X] if s != EPS)
            if EPS not in FIRST[X]:
                break
        else:
            res.add(EPS)
        return res

    changed = True
    while changed:
        changed = False
        for A in NONTERMS:
            for prod in G[A]:
                f = first_of_sequence(prod)
                before = len(FIRST[A])
                FIRST[A].update(f)
                if len(FIRST[A]) != before:
                    changed = True

    FOLLOW: Dict[str, Set[str]] = {A: set() for A in NONTERMS}
    FOLLOW[START_SYMBOL].add('EOF')

    changed = True
    while changed:
        changed = False
        for A in NONTERMS:
            for prod in G[A]:
                trailer = FOLLOW[A].copy()
                for X in reversed(prod):
                    if X in NONTERMS:
                        before = len(FOLLOW[X])
                        FOLLOW[X].update(trailer)
                        if len(FOLLOW[X]) != before:
                            changed = True
                        # Atualiza trailer
                        alpha_first = FIRST[X]
                        if EPS in alpha_first:
                            trailer = trailer.union(alpha_first - {EPS})
                        else:
                            trailer = alpha_first - {EPS}
                    else:
                        # terminal
                        trailer = FIRST[X] - {EPS} if X in FIRST else {X}

    return FIRST, FOLLOW, first_of_sequence