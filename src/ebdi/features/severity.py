"""Outcome-free predictors for the recorded-crash conditional severity target."""

import numpy as np
import pandas as pd

CATEGORICAL = [
    "COD_PROVINCIA",
    "ZONA_AGRUPADA",
    "TIPO_VIA",
    "TIPO_ACCIDENTE",
    "NUDO",
    "CONDICION_METEO",
    "CONDICION_ILUMINACION",
    "CONDICION_FIRME",
    "DIA_SEMANA",
]
NUMERIC = ["hour_sin", "hour_cos", "month_sin", "month_cos"]


def make_features(accidents: pd.DataFrame) -> pd.DataFrame:
    missing = set([*CATEGORICAL, "HORA", "MES"]) - set(accidents)
    if missing:
        raise ValueError(f"Missing audited predictors: {sorted(missing)}")
    result = accidents[CATEGORICAL].copy()
    for column in CATEGORICAL:
        result[column] = (
            pd.to_numeric(result[column], errors="raise")
            .astype("Int64")
            .astype("string")
            .fillna("unknown")
            .astype(str)
        )
    for source, prefix, period in [("HORA", "hour", 24), ("MES", "month", 12)]:
        phase = accidents[source].astype(float) * 2 * np.pi / period
        result[f"{prefix}_sin"] = np.sin(phase)
        result[f"{prefix}_cos"] = np.cos(phase)
    return result


def severity_target(accidents: pd.DataFrame) -> pd.Series:
    return (accidents["TOTAL_MU30DF"].gt(0) | accidents["TOTAL_HG30DF"].gt(0)).astype(int)


def temporal_split(accidents: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = accidents.loc[accidents.year.eq(2022)].copy()
    validation = accidents.loc[accidents.year.eq(2023)].copy()
    test = accidents.loc[accidents.year.eq(2024)].copy()
    if any(part.empty for part in [train, validation, test]):
        raise ValueError("Need observed 2022 train, 2023 validation and 2024 holdout cohorts")
    return train, validation, test
