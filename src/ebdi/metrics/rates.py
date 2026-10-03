"""Explicit denominators; count uncertainty conditional on a fixed exposure proxy."""

import numpy as np
import pandas as pd
from scipy.stats import chi2

INCIDENTS = {
    "injury_crashes": "Siniestros con víctimas",
    "fatalities": "Fallecidos a 30 días",
    "urban_crashes": "Siniestros urbanos con víctimas",
    "rear_lateral_crashes": "Alcance, lateral y frontolateral con víctimas",
    "severe_crashes": "Siniestros con fallecidos u hospitalizados",
}
DENOMINATORS = {
    "population": "Habitantes (1 de enero)",
    "registered_vehicles": "Vehículos registrados (fin de año)",
    "licensed_drivers": "Titulares de permisos (residencia, fin de año)",
}


def rate(count: pd.Series, exposure: pd.Series, scale: float = 100_000) -> pd.Series:
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("Scale must be finite and positive")
    if count.lt(0).any() or exposure.lt(0).any():
        raise ValueError("Counts and denominators cannot be negative")
    valid = (
        count.notna()
        & exposure.notna()
        & exposure.gt(0)
        & np.isfinite(count)
        & np.isfinite(exposure)
    )
    return (scale * count / exposure).where(valid)


def poisson_interval(
    count: pd.Series, exposure: pd.Series, scale: float = 100_000, confidence: float = 0.95
) -> tuple[pd.Series, pd.Series]:
    if not 0 < confidence < 1 or count.dropna().mod(1).ne(0).any():
        raise ValueError("Require 0<confidence<1 and integer counts")
    rate(count, exposure, scale)  # shared domain checks
    alpha = 1 - confidence
    low_counts = pd.Series(
        np.where(count.eq(0), 0, chi2.ppf(alpha / 2, 2 * count) / 2), index=count.index
    )
    high_counts = pd.Series(chi2.ppf(1 - alpha / 2, 2 * (count + 1)) / 2, index=count.index)
    return rate(low_counts, exposure, scale), rate(high_counts, exposure, scale)


def add_rates(panel: pd.DataFrame) -> pd.DataFrame:
    result = panel.copy()
    for count in INCIDENTS:
        for exposure in DENOMINATORS:
            metric = f"{count}_per_100k_{exposure}"
            result[metric] = rate(result[count], result[exposure])
            result[f"{metric}_lower"], result[f"{metric}_upper"] = poisson_interval(
                result[count], result[exposure]
            )
    result["small_sample"] = result["injury_crashes"].lt(30)
    return result
