"""Transparent complete-case composite and finite-cohort sensitivity."""

import numpy as np
import pandas as pd

METHODS = ["percentile", "zscore", "robust_zscore", "minmax"]


def normalize(values: pd.Series, method: str) -> pd.Series:
    if method not in METHODS:
        raise ValueError(f"Unknown normalization {method}")
    if not np.isfinite(values.dropna()).all():
        raise ValueError("Normalization requires finite observed values")
    valid = values.dropna().astype(float)
    result = pd.Series(np.nan, index=values.index, dtype=float)
    if len(valid) == 0:
        return result
    if valid.nunique() == 1:
        result.loc[valid.index] = 50.0 if method in {"percentile", "minmax"} else 0.0
        return result
    if method == "percentile":
        transformed = (valid.rank(method="average") - 1) / (len(valid) - 1) * 100
    elif method == "minmax":
        transformed = (valid - valid.min()) / (valid.max() - valid.min()) * 100
    elif method == "zscore":
        transformed = (valid - valid.mean()) / valid.std(ddof=0)
    else:
        mad = (valid - valid.median()).abs().median()
        scale = 1.4826 * mad if mad > 0 else valid.std(ddof=0)
        transformed = (valid - valid.median()) / scale
    result.loc[valid.index] = transformed
    return result


def validate_weights(weights: dict[str, float]) -> dict[str, float]:
    if not weights or any(not np.isfinite(w) or w < 0 for w in weights.values()):
        raise ValueError("Require finite nonnegative weights")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("At least one positive weight is required")
    return {k: w / total for k, w in weights.items() if w > 0}


def composite(
    frame: pd.DataFrame, weights: dict[str, float], method: str = "percentile", minimum: int = 30
) -> pd.DataFrame:
    active = validate_weights(weights)
    if minimum < 0:
        raise ValueError("Minimum sample cannot be negative")
    missing = set(active) - set(frame.columns)
    if missing:
        raise ValueError(f"Unknown index components: {sorted(missing)}")
    result = frame.copy()
    eligible = frame[list(active)].notna().all(axis=1) & frame["injury_crashes"].ge(minimum)
    result["index_score"] = np.nan
    result["index_rank"] = np.nan
    result["index_eligible"] = eligible
    if eligible.any():
        scores = pd.Series(0.0, index=frame.index[eligible])
        for key, weight in active.items():
            component = normalize(frame.loc[eligible, key], method)
            result[f"normalized_{key}"] = component
            scores += weight * component
        result.loc[eligible, "index_score"] = scores
        result.loc[eligible, "index_rank"] = scores.rank(ascending=False, method="average")
    return result


def sensitivity(
    frame: pd.DataFrame,
    weights: dict[str, float],
    method: str = "percentile",
    scenarios: int = 500,
    seed: int = 42,
    minimum: int = 30,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    keys = list(validate_weights(weights))
    base = composite(frame, weights, method, minimum)
    cohort = base.loc[base.index_eligible].copy()
    if cohort.empty or scenarios < 1:
        raise ValueError("Need an eligible cohort and at least one scenario")
    normalized = np.column_stack([normalize(cohort[k], method) for k in keys])
    rng = np.random.default_rng(seed)
    alternative_weights = rng.dirichlet(np.ones(len(keys)), size=scenarios)
    scores = normalized @ alternative_weights.T
    ranks = (
        pd.DataFrame(scores, index=cohort.index).rank(ascending=False, method="average").to_numpy()
    )
    summary = cohort[["province_code", "province", "index_score", "index_rank"]].copy()
    summary["weight_rank_min"] = ranks.min(axis=1)
    summary["weight_rank_max"] = ranks.max(axis=1)
    summary["weight_rank_p05"] = np.quantile(ranks, 0.05, axis=1)
    summary["weight_rank_p95"] = np.quantile(ranks, 0.95, axis=1)
    summary["weight_rank_std"] = ranks.std(axis=1)
    details = []
    named = {"default": weights, "equal": dict.fromkeys(keys, 1.0)}
    named.update({key: {key: 1.0} for key in keys})
    for name, setting in named.items():
        for normalization in METHODS:
            trial = composite(cohort, setting, normalization, minimum)
            part = trial[["province_code", "province", "index_score", "index_rank"]].copy()
            part["scenario"] = name
            part["normalization"] = normalization
            details.append(part)
    return summary, pd.concat(details, ignore_index=True)


def bootstrap_index(
    accidents: pd.DataFrame,
    panel: pd.DataFrame,
    weights: dict[str, float],
    method: str = "percentile",
    repetitions: int = 200,
    seed: int = 42,
    minimum: int = 30,
) -> pd.DataFrame:
    """Poisson event bootstrap preserves within-crash overlap between components.

    This is sampling-model uncertainty conditional on fixed stock denominators.
    It cannot quantify underreporting, systematic bias or arbitrary methodological choices.
    """
    if repetitions < 2:
        raise ValueError("Need at least two bootstrap repetitions")
    active = validate_weights(weights)
    permitted = {
        f"{k}_per_100k_population"
        for k in ["injury_crashes", "urban_crashes", "rear_lateral_crashes", "fatalities"]
    }
    if set(active) - permitted:
        raise ValueError("Event bootstrap currently supports audited population components only")
    cells = (
        accidents.groupby(["province_code", "urban", "rear_lateral", "TOTAL_MU30DF"], dropna=False)
        .size()
        .reset_index(name="n")
    )
    provinces = panel.province_code.tolist()
    codes = {c: i for i, c in enumerate(provinces)}
    rng = np.random.default_rng(seed)
    draws = rng.poisson(cells.n.to_numpy()[:, None], size=(len(cells), repetitions))
    result = {
        k: np.zeros((len(panel), repetitions))
        for k in ["injury_crashes", "urban_crashes", "rear_lateral_crashes", "fatalities"]
    }
    for cell, sampled in zip(cells.to_dict("records"), draws, strict=True):
        i = codes[cell["province_code"]]
        for metric, multiplier in [
            ("injury_crashes", 1),
            ("urban_crashes", cell["urban"]),
            ("rear_lateral_crashes", cell["rear_lateral"]),
            ("fatalities", cell["TOTAL_MU30DF"]),
        ]:
            result[metric][i] += sampled * multiplier
    rank_draws, score_draws = [], []
    for b in range(repetitions):
        sample = panel.copy()
        for metric, samples in result.items():
            sample[f"{metric}_per_100k_population"] = (
                samples[:, b] / panel.population.to_numpy() * 100_000
            )
        trial = composite(sample, weights, method, minimum)
        rank_draws.append(trial.index_rank.to_numpy())
        score_draws.append(trial.index_score.to_numpy())
    summary = panel[["province_code", "province"]].copy()
    for name, draws_list in [("bootstrap_rank", rank_draws), ("bootstrap_score", score_draws)]:
        matrix = np.asarray(draws_list)
        summary[f"{name}_lower"] = np.nanquantile(matrix, 0.025, axis=0)
        summary[f"{name}_upper"] = np.nanquantile(matrix, 0.975, axis=0)
    return summary
