"""Generate the frozen R5 input worlds only; no models or experimental outcomes.

The shipped inputs/WORLDS_R5.csv is authoritative for execution. This script
documents its deterministic construction and can reproduce it from lexicon.json.
"""
import csv
from itertools import combinations
from pathlib import Path
import json
import numpy as np


FIELDS = ["split", "world_id", "orbit_index", "canonical_lexical_key",
          "name0", "name1", "name2", "name3", "city0", "city1", "city2", "city3"]


def make_worlds(lexicons):
    rows = []
    specs = (("CAL", 256, 2026110901, 2026110903),
             ("TEST", 2048, 2026110902, 2026110904))
    for split, count, sample_seed, role_seed in specs:
        lex = lexicons[split]
        names = list(combinations(lex["names"], 4))
        cities = list(combinations(lex["cities"], 4))
        rng = np.random.Generator(np.random.PCG64(sample_seed))
        roles = np.random.Generator(np.random.PCG64(role_seed))
        indices = sorted(map(int, rng.choice(len(names) * len(cities),
                                             size=count, replace=False)))
        for number, orbit in enumerate(indices):
            ns, cs = names[orbit // len(cities)], cities[orbit % len(cities)]
            assigned_names = [ns[int(i)] for i in roles.permutation(4)]
            assigned_cities = [cs[int(i)] for i in roles.permutation(4)]
            row = {
                "split": split, "world_id": f"{split}{number:04d}",
                "orbit_index": orbit,
                "canonical_lexical_key": "|".join(ns) + "::" + "|".join(cs),
            }
            row.update({f"name{i}": value for i, value in enumerate(assigned_names)})
            row.update({f"city{i}": value for i, value in enumerate(assigned_cities)})
            rows.append(row)
    return rows


def write_worlds(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def execution_order(rows):
    """Independent frozen schedule; keep statistical world indexing unchanged."""
    ids = sorted(row["world_id"] for row in rows if row["split"] == "TEST")
    rng = np.random.Generator(np.random.PCG64(2026110906))
    return [ids[int(i)] for i in rng.permutation(len(ids))]


def write_execution_order(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["execution_position", "world_id"],
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows({"execution_position": i, "world_id": value}
                         for i, value in enumerate(execution_order(rows)))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    lexicons = json.loads((root / "config/lexicon.json").read_text(encoding="utf-8"))
    rows = make_worlds(lexicons)
    target = root / "inputs/WORLDS_R5.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    write_worlds(target, rows)
    write_execution_order(root / "inputs/TEST_EXECUTION_ORDER.csv", rows)
    print(json.dumps({"input_worlds": len(rows), "path": str(target),
                      "model_calls": 0}, ensure_ascii=False))
