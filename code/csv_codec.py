"""Lossless decimal CSV representation of redundant FP64 endpoints.

Small corrections are signed steps in the nonnegative binary64 ordering.
Blank cells remain blank. A leading ! escapes an original literal.
"""
import csv
import math
import struct


DOUBLE = struct.Struct(">d")
UINT = struct.Struct(">Q")
UNIT_TABLES = ("unit_results.csv", "cal_selected_world_results.csv")
PAIR_TABLES = ("world_origin_pairs.csv", "world_view_pairs.csv")
COUNTS = {"R22": 1408, "balanced_P1": 18432, "balanced_AUC": 7962071040}


def bits(x):
    return UINT.unpack(DOUBLE.pack(x))[0]


def value(b):
    return DOUBLE.unpack(UINT.pack(b))[0]


def nmse_scaled(row):
    if row["NMSE"] and row["D"]:
        return float(row["NMSE"]) * float(row["D"])


def different(row, prefix=""):
    balanced = row[prefix + "Q2_balanced"]
    same = row[prefix + "Q2_same"]
    if balanced and same:
        return 2 * float(balanced) - float(same)


def balanced(row):
    if row["Q2_balanced"]:
        return float(row["Q2_balanced"])


UNIT_BASES = {"raw_MSE": nmse_scaled, "Q2_different": different, "tie_expected_Q2": balanced}
PAIR_BASES = {
    "STAR23__Q2_different": lambda row: different(row, "STAR23__"),
    "CYCLE23__Q2_different": lambda row: different(row, "CYCLE23__"),
}


def schema(name):
    """Map original field names to (CSV field, formula or count denominator)."""
    if name in UNIT_TABLES:
        return {
            **{field: (field + "_steps", formula) for field, formula in UNIT_BASES.items()},
            **{field: (f"{field}_count_{den}", den) for field, den in COUNTS.items()},
        }
    if name in PAIR_TABLES:
        return {field: (field + "_steps", formula) for field, formula in PAIR_BASES.items()}
    return {}


def step_count(text, actual, base):
    if base is None or not math.isfinite(base) or base < 0 or actual < 0 or repr(actual) != text:
        return None
    steps = bits(actual) - bits(base)
    return steps if -32 <= steps <= 32 else None


def encode_cell(text, rule, row):
    if not text:
        return ""
    actual = float(text)
    if not math.isfinite(actual):
        return "!" + text
    if isinstance(rule, int):
        count = round(actual * rule)
        steps = step_count(text, actual, count / rule)
        if steps is not None:
            return f"{count}:{steps}" if steps else str(count)
    else:
        steps = step_count(text, actual, rule(row))
        if steps is not None:
            return str(steps)
    return "!" + text


def decode_cell(text, rule, row):
    if not text:
        return ""
    if text.startswith("!"):
        return text[1:]
    if isinstance(rule, int):
        numerator, separator, correction = text.partition(":")
        base = int(numerator) / rule
        steps = int(correction) if separator else 0
    else:
        base = rule(row)
        steps = int(text)
    if base is None or not math.isfinite(base) or base < 0 or not -32 <= steps <= 32:
        raise ValueError(f"Invalid exact scalar code: {text!r}, reference {base!r}")
    return repr(value(bits(base) + steps))


def decode_row(row, fields, wanted=None):
    for original, (encoded, rule) in fields.items():
        if encoded in row and (wanted is None or original in wanted):
            row[original] = decode_cell(row.pop(encoded), rule, row)
    return row


def decoded_rows(path, wanted=None):
    fields = schema(path.name)
    with path.open(encoding="utf8", newline="") as stream:
        for row in csv.DictReader(stream):
            yield decode_row(row, fields, wanted) if fields else row


def plain_columns(path):
    original = {encoded: field for field, (encoded, _) in schema(path.name).items()}
    with path.open(encoding="utf8", newline="") as stream:
        return [original.get(name, name) for name in next(csv.reader(stream))]
