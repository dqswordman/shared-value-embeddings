"""Paired world bootstrap with the R4 max absolute centered statistic."""
import numpy as np


def resample_counts(n, seed, replicates):
    rng = np.random.Generator(np.random.PCG64(seed))
    return np.array([np.bincount(rng.integers(0, n, n), minlength=n)
                     for _ in range(replicates)], dtype=np.float64)


def summarize(vector, samples):
    v = vector[np.isfinite(vector)]
    b = samples[np.isfinite(samples)]
    if not len(v) or not len(b):
        return dict(estimate=None, ordinary_low=None, ordinary_high=None,
                    bootstrap_sd=None, n_worlds=int(len(v)), bootstrap_valid=int(len(b)))
    theta = float(v.mean())
    if np.all(v == v[0]):
        low = high = theta
        sd = 0.
    else:
        low, high = map(float, np.quantile(b, [.025, .975], method="linear"))
        sd = float(b.std(ddof=1)) if len(b) > 1 else None
    return dict(estimate=theta, ordinary_low=low, ordinary_high=high,
                bootstrap_sd=sd, n_worlds=int(len(v)), bootstrap_valid=int(len(b)))


def ordinary(vectors, weights, keep_draws=False):
    results = {}
    draws = {}
    keys = list(vectors)
    for start in range(0, len(keys), 96):
        current = keys[start:start + 96]
        array = np.column_stack([vectors[k] for k in current])
        valid = np.isfinite(array)
        value = np.where(valid, array, 0.)
        numerator = weights @ value
        denominator = weights.shape[1] if valid.all() else weights @ valid.astype(np.float64)
        boot = np.divide(numerator, denominator, out=np.full_like(numerator, np.nan),
                         where=np.asarray(denominator) > 0)
        for column, key in enumerate(current):
            results[key] = summarize(array[:, column], boot[:, column])
            if keep_draws:
                draws[key] = boot[:, column].copy()
    return results, draws


def simultaneous(vectors, seed, replicates, full_weights=None):
    """Select the estimable fixed subfamily by coverage alone."""
    available = {k: np.asarray(v) for k, v in vectors.items() if np.isfinite(v).any()}
    planned_n = len(next(iter(vectors.values())))
    common = (np.isfinite(np.column_stack(list(available.values()))).all(1) if available
              else np.zeros(planned_n, dtype=bool))
    n = int(common.sum())
    if not n:
        return {}, common, None, []
    weights = full_weights if n == planned_n and full_weights is not None else resample_counts(n, seed, replicates)
    results, boot = ordinary({k: v[common] for k, v in available.items()}, weights, keep_draws=True)
    terms = []
    for key, row in results.items():
        if row["bootstrap_sd"]:
            terms.append(np.abs((boot[key] - row["estimate"]) / row["bootstrap_sd"]))
    critical = float(np.quantile(np.max(terms, axis=0), .95, method="linear")) if terms else 0.
    for row in results.values():
        margin = critical * row["bootstrap_sd"]
        row.update(simultaneous_low=row["estimate"] - margin, simultaneous_high=row["estimate"] + margin,
                   simultaneous_critical=critical, zero_sd=row["bootstrap_sd"] == 0.)
    return results, common, critical, list(available)
