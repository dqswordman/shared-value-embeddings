"""R5 finite text/query definition. No model loading or model experiments.

This is a specification reference, not the local experiment runner.
The execution implementation may vectorize it without changing its meaning.
"""
from itertools import combinations, product
import math
import numpy as np

RELATIONS = ("L", "Q", "R")
VERBS = ("lives", "works", "studies")
VIEWS = tuple(tuple((j + v) % 4 for j in range(4)) for v in range(4))


def _join(items):
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return items[0] + " and " + items[1]
    return ", ".join(items[:-1]) + ", and " + items[-1]


def render(names, cities, values, renderer, view):
    """values[r][j] is the local city ID at a relation/entity address."""
    order = VIEWS[view]
    if renderer == "ATOMIC":
        return " ".join(
            f"{names[j]} {VERBS[r]} in {cities[values[r][j]]}."
            for r in range(3) for j in order
        )
    if renderer != "PROSE_COMPRESSED":
        raise ValueError(renderer)
    sentences = []
    for j in order:
        groups = {}
        for r in range(3):
            groups.setdefault(int(values[r][j]), []).append(VERBS[r])
        clauses = [
            _join(verbs) + " in " + cities[city]
            for city, verbs in groups.items()
        ]
        if len(clauses) == 2:
            body = clauses[0] + ", and " + clauses[1]
        else:
            body = _join(clauses)
        sentences.append(names[j] + " " + body + ".")
    return " ".join(sentences)


def queries(names, cities, condition, split):
    """216 logical queries per world/condition; no origin or view in text."""
    if split not in ("CAL", "TEST"):
        raise ValueError(split)
    prefix, suffix = (
        ("Find a record where ", ".") if split == "CAL"
        else ("Which record states that ", "?")
    )
    perm = condition["permutations"]
    def domain(r, j):
        return tuple(sorted(perm[r][2 * (j // 2):2 * (j // 2) + 2]))
    def phrase(r, j, city):
        return f"{names[j]} {VERBS[r]} in {cities[city]}"
    out = []
    for r in range(3):
        for j in range(4):
            for city in domain(r, j):
                out.append({
                    "logical_id": f"U_{r}_{j}_{city}",
                    "arity": 1, "stratum": "single",
                    "facts": ((r, j, city),),
                    "text": prefix + phrase(r, j, city) + suffix,
                })
    for r1, r2 in combinations(range(3), 2):
        for j1, j2 in product(range(4), repeat=2):
            for c1, c2 in product(domain(r1, j1), domain(r2, j2)):
                out.append({
                    "logical_id": f"B_{r1}_{j1}_{c1}_{r2}_{j2}_{c2}",
                    "arity": 2,
                    "stratum": "same" if j1 == j2 else "different",
                    "facts": ((r1, j1, c1), (r2, j2, c2)),
                    "text": prefix + phrase(r1, j1, c1) + " and "
                            + phrase(r2, j2, c2) + suffix,
                })
    return out


def qrels(query_rows, state_values):
    """Binary AND relevance for every query and every candidate document."""
    return np.array([
        [all(int(v[r][j]) == city for r, j, city in q["facts"])
         for v in state_values]
        for q in query_rows
    ], dtype=np.int8)


def rank_metrics(scores, labels, absolute_state_ids):
    """One query. FP64 cosine descending, absolute state ID ascending on ties."""
    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels, dtype=np.int8)
    ids = np.asarray(absolute_state_ids, dtype=np.int64)
    if len(s) != 22 or not np.all(np.isfinite(s)):
        raise ValueError("Invalid score vector; do not silently impute.")
    positives = int(y.sum())
    if positives <= 0 or positives >= 22:
        raise ValueError("This frozen task requires nonempty positive/negative sets.")
    order = np.lexsort((ids, -s))
    sy, ss = y[order], s[order]
    discount = 1 / np.log2(np.arange(2, 7, dtype=np.float64))
    idcg = float(discount[:min(5, positives)].sum())
    ndcg = float(sy[:5] @ discount / idcg)
    pos, neg = s[y == 1], s[y == 0]
    auc = float(((pos[:, None] > neg).sum()
                 + 0.5 * (pos[:, None] == neg).sum()) / (len(pos) * len(neg)))
    expected_tie_dcg = 0.0
    any_tie = boundary_tie = mixed_top5_tie = False
    start = 0
    while start < len(s):
        end = start + 1
        while end < len(s) and ss[end] == ss[start]:
            end += 1
        n = end - start
        p = int(sy[start:end].sum())
        if n > 1:
            any_tie = True
            boundary_tie |= start < 5 < end
            mixed_top5_tie |= start < 5 and 0 < p < n
        if start < 5:
            expected_tie_dcg += (p / n) * float(discount[start:min(end, 5)].sum())
        start = end
    return {
        "ndcg5": ndcg, "p1": float(sy[0]), "auc": auc,
        "tie_expected_ndcg5": expected_tie_dcg / idcg,
        "any_exact_tie": bool(any_tie),
        "boundary5_exact_tie": bool(boundary_tie),
        "mixed_top5_exact_tie": bool(mixed_top5_tie),
        "n_relevant": positives,
        "top5_absolute_states": [int(x) for x in ids[order[:5]]],
        "random_ndcg5": (positives / 22) * float(discount.sum()) / idcg,
    }


def balanced_query_mean(metric_values, query_rows):
    a = np.asarray(metric_values, dtype=np.float64)
    same = np.array([q["stratum"] == "same" for q in query_rows])
    different = np.array([q["stratum"] == "different" for q in query_rows])
    single = np.array([q["stratum"] == "single" for q in query_rows])
    return {
        "Q2_balanced": 0.5 * float(a[same].mean()) + 0.5 * float(a[different].mean()),
        "Q2_same": float(a[same].mean()),
        "Q2_different": float(a[different].mean()),
        "Q1": float(a[single].mean()),
    }


def finite_check():
    """Only finite task checks, not an encoder result or an execution certificate."""
    from design_reference import CONDITIONS, ORIGINS, TARGETS, assignments
    counts = []
    names = ["Nora", "Oscar", "Priya", "Rafael"]
    cities = ["Accra", "Athens", "Bergen", "Boston"]
    for c in CONDITIONS:
        qs = queries(names, cities, c, "TEST")
        assert len(qs) == 216
        assert sum(q["stratum"] == "same" for q in qs) == 48
        assert sum(q["stratum"] == "different" for q in qs) == 144
        for o in ORIGINS:
            states = [int(o) ^ int(b) for b in TARGETS]
            ys = qrels(qs, [assignments(c, s) for s in states])
            m = ys.sum(axis=1)
            assert set(m[:24]) == {6, 16}
            assert set(m[24:]) == {1, 5, 11}
            assert list(m[:24]).count(6) == 12
            assert list(m[24:]).count(1) == 48
            assert list(m[24:]).count(5) == 96
            assert list(m[24:]).count(11) == 48
            for label, expected in (
                ("same", {1: 12, 5: 24, 11: 12}),
                ("different", {1: 36, 5: 72, 11: 36}),
            ):
                values = [int(value) for value, query in zip(m, qs)
                          if query["stratum"] == label]
                assert {n: values.count(n) for n in set(values)} == expected
        for r in ("ATOMIC", "PROSE_COMPRESSED"):
            for v in range(4):
                text = [render(names, cities, assignments(c, s), r, v)
                        for s in range(64)]
                assert len(set(text)) == 64
        counts.append(c["id"])
    d5 = sum(1 / math.log2(i + 1) for i in range(1, 6))
    y = np.array([1] * 5 + [0] * 17)
    tied = rank_metrics(np.zeros(22), y, list(range(22)))
    assert abs(tied["tie_expected_ndcg5"] - 5 / 22) < 1e-14
    return {
        "checked_conditions": counts, "origins": len(ORIGINS),
        "queries_per_condition": 216, "models_run": 0,
        "random_Q1": 0.5,
        "random_Q2_balanced": (d5 / 22 + 5 / 22 + 5 / 22 + 11 / 22) / 4,
        "scope": "Finite construction and metric arithmetic only.",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(finite_check(), ensure_ascii=False, indent=2))
