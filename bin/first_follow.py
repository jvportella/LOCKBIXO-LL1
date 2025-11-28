from typing import Dict, List, Set, Callable
from .grammar import EPS

def compute_first_follow(G, NONTERMS: List[str], TERMS: List[str], START_SYMBOL: str):
    terms = [t for t in TERMS if t != 'EOF']

    FIRST: Dict[str, Set[str]] = {A: set() for A in NONTERMS}
    for t in terms:
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
                return res

            if X in terms:
                res.add(X)
                return res

            if X == 'EOF':
                return res

            res.update(FIRST[X] - {EPS})

            if EPS not in FIRST[X]:
                return res

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
                trailer = set(FOLLOW[A])
                for X in reversed(prod):
                    if X in NONTERMS:
                        before = len(FOLLOW[X])
                        FOLLOW[X].update(trailer)
                        if len(FOLLOW[X]) != before:
                            changed = True

                        if EPS in FIRST[X]:
                            trailer = trailer.union(FIRST[X] - {EPS})
                        else:
                            trailer = FIRST[X] - {EPS}

                    elif X in terms:
                        trailer = {X}

                    elif X == EPS:
                        continue

                    elif X == 'EOF':
                        trailer = {'EOF'}

                    else:
                        trailer = {X}

    return FIRST, FOLLOW, first_of_sequence
