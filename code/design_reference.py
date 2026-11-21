"""R5 all-different matching design: finite mathematics only.

已完成纯数学核对；未运行模型。本文件不读取模型、权重、历史工作区或结果。
The optional command-line summary is a mathematical diagnostic, not an execution
admission gate. It does not certify a model run or scientific result.

State convention: a,b,c,d,e,f are the most-to-least-significant bits. All
reconstruction coefficients act on the 64 native raw-h states of ONE condition,
render, presentation and world, in integer state order 0..63. Algebra is on raw
h; normalize only the reconstructed vector. A coefficient row is not an encoder.

Public interfaces:
  ORIGINS, TARGETS, MASKS, CONDITIONS
  bits(state)
  assignments(condition, state) -> (3,4) integer local city ids
  candidate_designs() -> 1037 deterministic candidate dictionaries
  q_coeff(edges, triples, origin, relative_target) -> (64,) float64
  native_q2_coeff(origin, relative_target) -> (64,) float64

CONDITIONS rows have exactly id/permutations/STAR/CYCLE/E12. Candidate families
are TRI70, PART21, PART23, PAIR21, PAIRPLUS23, FULLPAIR22, STRUCTPAIR19.
PART21 defines all 840 NMSE candidates; its 80-candidate functional shortlist
and all CAL winner selection are the execution/analysis code's responsibility.
"""

from collections import Counter
from itertools import combinations, product
import json

import numpy as np


MASKS = (32, 16, 8, 4, 2, 1)
ORIGINS = tuple(
    int(value, 2)
    for value in (
        "000000", "010101", "001100", "011001",
        "000011", "010110", "001111", "011010",
        "111111", "101010", "110011", "100110",
        "111100", "101001", "110000", "100101",
    )
)
TARGETS = tuple(state for state in range(64) if state.bit_count() >= 4)

ALL_PAIRS = tuple(combinations(range(6), 2))
ALL_TRIPLES = tuple(combinations(range(6), 3))
E12 = tuple(edge for edge in ALL_PAIRS if edge not in ((0, 1), (2, 3), (4, 5)))
T8 = tuple(
    triple for triple in ALL_TRIPLES
    if all(edge in E12 for edge in combinations(triple, 2))
)
STAR_EVEN = ((0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4))
CYCLE_EVEN = tuple(triple for triple in T8 if triple not in STAR_EVEN)

# Every first block contains variable a, so complementary 3+3 partitions occur
# once and in the same canonical order as the R4 finite design.
PARTITIONS = tuple(
    (block, tuple(i for i in range(6) if i not in block))
    for block in combinations(range(6), 3)
    if 0 in block
)

_MATCHINGS = ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2))
_CYCLIC_ORDERS = ((0, 1, 2), (1, 2, 0), (2, 0, 1))


def _condition_rows():
    rows = []
    for cycle, matching_order in enumerate(_CYCLIC_ORDERS):
        for parity in ("E", "O"):
            permutations = [_MATCHINGS[i] for i in matching_order]
            if parity == "O":
                # Swap R's two EDIT PAIR BLOCKS, not the two values within a
                # block and not a state bit. This exchanges STAR/CYCLE indices.
                r = permutations[2]
                permutations[2] = r[2:] + r[:2]
            rows.append({
                "id": f"AD_C{cycle}_{parity}",
                "permutations": tuple(permutations),
                "STAR": STAR_EVEN if parity == "E" else CYCLE_EVEN,
                "CYCLE": CYCLE_EVEN if parity == "E" else STAR_EVEN,
                "E12": E12,
            })
    return tuple(rows)


CONDITIONS = _condition_rows()


def _state(value):
    if not isinstance(value, (int, np.integer)) or not 0 <= int(value) < 64:
        raise ValueError("state must be an integer in 0..63")
    return int(value)


def bits(state):
    """Return a,b,c,d,e,f as six 0/1 int64 values, MSB first."""
    state = _state(state)
    return np.array([int(bool(state & mask)) for mask in MASKS], dtype=np.int64)


def _condition(condition):
    if isinstance(condition, str):
        for row in CONDITIONS:
            if row["id"] == condition:
                return row
        raise ValueError(f"unknown condition id: {condition}")
    return condition


def assignments(condition, state):
    """Return L0..L3, Q0..Q3, R0..R3 local city ids in shape (3,4).

    `condition` can be one CONDITIONS row or its string id. Local city ids are
    0=A, 1=B, 2=C, 3=D; execution code maps them to the world's actual values.
    Presentation and rendering are deliberately outside this function.
    """
    row = _condition(condition)
    result = np.asarray(row["permutations"], dtype=np.int64).copy()
    edit_bits = bits(state)
    for variable, active in enumerate(edit_bits):
        if active:
            relation, pair = divmod(variable, 2)
            left = 2 * pair
            result[relation, left], result[relation, left + 1] = (
                result[relation, left + 1], result[relation, left]
            )
    return result


def candidate_designs():
    """Enumerate all finite candidates deterministically, with actual budgets.

    Stable IDs (all indices are zero-based):
      TRI70_T00..T69
      PART21_P00_A00..PART21_P09_A83
      PART23_P00_O00..PART23_P09_O08
      PAIR21_O00..O14
      PAIRPLUS23_T00..T19
      FULLPAIR22, STRUCTPAIR19

    TRI70_T28 is STAR in E conditions and CYCLE in O conditions; TRI70_T41 is
    the converse. PART21/23 use the same ten canonical PARTITIONS. All pair and
    triple tuples, family loops and IDs have stable lexicographic order; no
    unordered set iteration determines an ID or candidate.
    """
    rows = []
    for index, triples in enumerate(combinations(T8, 4)):
        rows.append({
            "id": f"TRI70_T{index:02d}", "family": "TRI70",
            "edges": E12, "triples": triples, "budget": 23,
        })

    for partition_index, partition in enumerate(PARTITIONS):
        partition_id = f"P{partition_index:02d}"
        intra = tuple(
            edge for edge in ALL_PAIRS
            if any(all(i in block for i in edge) for block in partition)
        )
        cross = tuple(edge for edge in ALL_PAIRS if edge not in intra)
        for extra_index, extra in enumerate(combinations(cross, 6)):
            edges = tuple(edge for edge in ALL_PAIRS if edge in intra or edge in extra)
            rows.append({
                "id": f"PART21_{partition_id}_A{extra_index:02d}",
                "family": "PART21", "partition_id": partition_id,
                "edges": edges, "triples": partition, "budget": 21,
            })

    for partition_index, partition in enumerate(PARTITIONS):
        partition_id = f"P{partition_index:02d}"
        intra = tuple(
            edge for edge in ALL_PAIRS
            if any(all(i in block for i in edge) for block in partition)
        )
        cross = tuple(edge for edge in ALL_PAIRS if edge not in intra)
        for omission_index, omitted in enumerate(cross):
            rows.append({
                "id": f"PART23_{partition_id}_O{omission_index:02d}",
                "family": "PART23", "partition_id": partition_id,
                "edges": tuple(edge for edge in ALL_PAIRS if edge != omitted),
                "triples": partition, "budget": 23,
            })

    for index, omitted in enumerate(ALL_PAIRS):
        rows.append({
            "id": f"PAIR21_O{index:02d}", "family": "PAIR21",
            "edges": tuple(edge for edge in ALL_PAIRS if edge != omitted),
            "triples": (), "budget": 21,
        })

    for index, triple in enumerate(ALL_TRIPLES):
        rows.append({
            "id": f"PAIRPLUS23_T{index:02d}", "family": "PAIRPLUS23",
            "edges": ALL_PAIRS, "triples": (triple,), "budget": 23,
        })

    rows.extend((
        {"id": "FULLPAIR22", "family": "FULLPAIR22", "edges": ALL_PAIRS,
         "triples": (), "budget": 22},
        {"id": "STRUCTPAIR19", "family": "STRUCTPAIR19", "edges": E12,
         "triples": (), "budget": 19},
    ))
    return rows


def _delta_zero(indices):
    result = np.zeros(64, dtype=np.float64)
    for size in range(len(indices) + 1):
        for subset in combinations(indices, size):
            mask = sum(MASKS[i] for i in subset)
            result[mask] += (-1) ** (len(indices) - size)
    return result


_BITS = np.stack([bits(state) for state in range(64)])
_DEGREES = _BITS.sum(axis=1)
_WALSH = (1 - 2 * ((_BITS @ _BITS.T) % 2)).astype(np.float64)
_LOW_WALSH = _WALSH[_DEGREES <= 2]
_NATIVE_Q2 = (_LOW_WALSH.T @ _LOW_WALSH) / 64
_STATE_INDEX = np.arange(64, dtype=np.int64)

_BASE = np.broadcast_to(_delta_zero(()), (64, 64)).copy()
for _variable in range(6):
    _BASE += _BITS[:, _variable, None] * _delta_zero((_variable,))

_PAIR_TERMS = {
    pair: np.prod(_BITS[:, pair], axis=1)[:, None] * _delta_zero(pair)
    for pair in ALL_PAIRS
}
_TRIPLE_TERMS = {}
_ANCHORED_TRIPLE_TERMS = {}
for _triple in ALL_TRIPLES:
    # phi_t = (1 - 2*sum_i b_i + 4*sum_{i<j} b_i*b_j) / 8.
    # All entries are dyadic, allowing exact float64 coefficient comparisons.
    _phi_numerator = 1 - 2 * _BITS[:, _triple].sum(axis=1)
    for _pair in combinations(_triple, 2):
        _phi_numerator += 4 * np.prod(_BITS[:, _pair], axis=1)
    _TRIPLE_TERMS[_triple] = (_phi_numerator / 8)[:, None] * _delta_zero(_triple)
    _ANCHORED_TRIPLE_TERMS[_triple] = (
        np.prod(_BITS[:, _triple], axis=1)[:, None] * _delta_zero(_triple)
    )


def q_coeff(edges, triples, origin, relative_target):
    """64 raw-h coefficients for the frozen projected anchored construction.

    For t={i,j,k}, its joint observation is multiplied by
      phi_t(b)=1/8-sum(b_i)/4+sum(b_i*b_j)/2,
    the Walsh<=2 projection of b_i*b_j*b_k. This is NOT the native 64-state
    Walsh projection. Do not reanchor the resulting vector at b=0.

    `edges` and `triples` may be tuples or JSON lists of sorted variable indices.
    A target-blind evaluation uses relative_target in TARGETS (Hamming>=4).
    The function also accepts other targets to support algebraic diagnostics.
    """
    origin = _state(origin)
    relative_target = _state(relative_target)
    result = _BASE[relative_target].copy()
    for edge in edges:
        result += _PAIR_TERMS[tuple(edge)][relative_target]
    for triple in triples:
        result += _TRIPLE_TERMS[tuple(triple)][relative_target]
    # absolute source s receives relative coefficient indexed by s XOR origin.
    return result[_STATE_INDEX ^ origin]


def native_q2_coeff(origin, relative_target):
    """Uniform native-64 Walsh<=2 projection at state origin XOR target.

    This privileged diagnostic includes the target's own native vector (its
    diagonal coefficient is 22/64). It is neither target-blind nor a functional
    upper bound. The returned array is a copy and can be used independently.
    """
    absolute_target = _state(origin) ^ _state(relative_target)
    return _NATIVE_Q2[absolute_target].copy()


def _all_relative_coefficients(edges, triples, anchored_cubic=False):
    result = _BASE.copy()
    for edge in edges:
        result += _PAIR_TERMS[tuple(edge)]
    terms = _ANCHORED_TRIPLE_TERMS if anchored_cubic else _TRIPLE_TERMS
    for triple in triples:
        result += terms[tuple(triple)]
    return result


def mathematical_summary():
    """Read-only finite-design checks; no model or external asset access."""
    issues = []
    candidates = candidate_designs()
    family_counts = dict(Counter(row["family"] for row in candidates))
    budget_counts = {}
    for row in candidates:
        budget_counts[str(row["budget"])] = budget_counts.get(str(row["budget"]), 0) + 1

    target_indices = np.array(TARGETS, dtype=np.int64)
    max_target_self = 0.0
    max_high_degree = 0.0
    max_projection_difference = 0.0
    max_origin_translation_difference = 0.0
    budgets_match = True
    anchor_closure = True
    for row in candidates:
        edges, triples = row["edges"], row["triples"]
        matrix = _all_relative_coefficients(edges, triples)
        support = np.flatnonzero(np.any(matrix[target_indices] != 0, axis=0))
        declared = np.zeros(64, dtype=bool)
        for subset in ((), *((i,) for i in range(6)), *edges, *triples):
            declared[sum(MASKS[i] for i in subset)] = True
        correct_budget = (
            len(support) == row["budget"]
            and np.array_equal(support, np.flatnonzero(declared))
        )
        budgets_match = bool(budgets_match and correct_budget)
        closed = all(pair in edges for triple in triples for pair in combinations(triple, 2))
        anchor_closure = bool(anchor_closure and closed)
        if not correct_budget or not closed:
            issues.append({"candidate": row["id"], "budget_match": correct_budget,
                           "anchor_closure": closed})
        max_target_self = max(max_target_self, float(np.abs(matrix[target_indices, target_indices]).max()))
        max_high_degree = max(max_high_degree, float(np.abs(_WALSH[_DEGREES > 2] @ matrix).max()))
        anchored = _all_relative_coefficients(edges, triples, anchored_cubic=True)
        max_projection_difference = max(
            max_projection_difference, float(np.abs(_NATIVE_Q2 @ anchored - matrix).max())
        )
        # Directly check the public origin translation at all 16 origins for
        # one fixed non-anchor target; full target self-coefficients were checked
        # above, and XOR is a bijection on source states.
        for origin in ORIGINS:
            observed = q_coeff(edges, triples, origin, TARGETS[0])
            expected = matrix[TARGETS[0], _STATE_INDEX ^ origin]
            max_origin_translation_difference = max(
                max_origin_translation_difference, float(np.abs(observed - expected).max())
            )

    origin_balance = {}
    for order in (1, 2, 3):
        balanced = True
        for variables in combinations(range(6), order):
            counts = Counter(tuple(int(bits(origin)[i]) for i in variables) for origin in ORIGINS)
            balanced = balanced and all(
                counts.get(pattern, 0) == len(ORIGINS) // (2 ** order)
                for pattern in product((0, 1), repeat=order)
            )
        origin_balance[str(order)] = bool(balanced)

    native_assignments = []
    frequency_invariant = True
    for condition in CONDITIONS:
        pairs = tuple(
            tuple(permutation[start:start + 2])
            for permutation in condition["permutations"] for start in (0, 2)
        )
        observed_edges = tuple(
            edge for edge in ALL_PAIRS
            if any(all(value in pairs[i] for i in edge) for value in range(4))
        )
        observed_star = tuple(
            triple for triple in T8
            if any(all(value in pairs[i] for i in triple) for value in range(4))
        )
        observed_cycle = tuple(triple for triple in T8 if triple not in observed_star)
        if (observed_edges != condition["E12"] or observed_star != condition["STAR"]
                or observed_cycle != condition["CYCLE"]):
            issues.append({"condition": condition["id"], "incidence_definition_mismatch": True})
        for state in range(64):
            assignment = assignments(condition, state).reshape(-1)
            native_assignments.append(tuple(map(int, assignment)))
            frequency_invariant = frequency_invariant and bool(
                np.array_equal(np.bincount(assignment, minlength=4), np.full(4, 3))
            )

    identifiers = tuple(row["id"] for row in candidates)
    unique_ids = len(dict.fromkeys(identifiers)) == len(identifiers)
    if not unique_ids:
        issues.append({"candidate_id_duplicates": True})
    if max_target_self or max_high_degree or max_projection_difference or max_origin_translation_difference:
        issues.append({"coefficient_identity_failure": True})
    if not all(origin_balance.values()):
        issues.append({"origin_balance_failure": True})
    unique_native = len(dict.fromkeys(native_assignments))
    if unique_native != 384 or not frequency_invariant:
        issues.append({"native_assignment_definition_failure": True})

    return {
        "scope": "pure finite mathematics; no models, weights, scientific results or execution approval",
        "model_calls": 0,
        "conditions": len(CONDITIONS),
        "states_per_condition": 64,
        "unique_native_assignments": unique_native,
        "all_local_values_appear_three_times": bool(frequency_invariant),
        "origins": len(ORIGINS),
        "relative_targets": len(TARGETS),
        "origin_balance_by_order": origin_balance,
        "candidate_counts": family_counts,
        "candidate_total": len(candidates),
        "unique_candidate_ids": bool(unique_ids),
        "candidate_budget_counts": budget_counts,
        "all_declared_budgets_match_support": budgets_match,
        "all_triple_subpairs_are_available": anchor_closure,
        "max_target_self_coefficient": max_target_self,
        "max_output_Walsh_degree_above_two_coefficient": max_high_degree,
        "max_projected_anchored_identity_difference": max_projection_difference,
        "max_origin_translation_difference": max_origin_translation_difference,
        "native_q2_target_diagonal": float(native_q2_coeff(0, TARGETS[0])[TARGETS[0]]),
        "issues": issues,
    }


if __name__ == "__main__":
    print(json.dumps(mathematical_summary(), ensure_ascii=False, indent=2, allow_nan=False))
