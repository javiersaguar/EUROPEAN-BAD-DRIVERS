"""Fail on invalid facts; explicitly report coverage limitations."""

from typing import Any

import pandas as pd

BASELINE_ROWS = {2022: 97916, 2023: 101306, 2024: 101996}
BASELINE_DEATHS = {2022: 1746, 2023: 1806, 2024: 1785}
CRITICAL = [
    "ID_ACCIDENTE",
    "ANYO",
    "MES",
    "DIA_SEMANA",
    "HORA",
    "COD_PROVINCIA",
    "ZONA_AGRUPADA",
    "TOTAL_MU30DF",
    "TOTAL_HG30DF",
    "TOTAL_HL30DF",
    "TOTAL_VICTIMAS_30DF",
]


def validate_accidents(
    df: pd.DataFrame, year: int, expected_columns: list[str], categories: dict[str, set[int]]
) -> dict[str, Any]:
    if list(df.columns) != expected_columns:
        raise ValueError(f"{year}: schema drift; compare with configs/accident_schema.json")
    if df[CRITICAL].isna().any().any():
        raise ValueError(f"{year}: null critical fields")
    if df.duplicated(["ID_ACCIDENTE", "ANYO"]).any():
        raise ValueError(f"{year}: duplicate crash ID/year")
    if not df["ANYO"].eq(year).all():
        raise ValueError(f"{year}: calendar year mapping mismatch")
    ranges = {"MES": (1, 12), "DIA_SEMANA": (1, 7), "HORA": (0, 23), "COD_PROVINCIA": (1, 52)}
    for col, (low, high) in ranges.items():
        if not df[col].between(low, high).all() or not df[col].mod(1).eq(0).all():
            raise ValueError(f"{year}: invalid {col}")
    count_cols = [str(c) for c in df if str(c).startswith(("TOTAL_", "TOT_"))]
    if (
        df[count_cols].isna().any().any()
        or (df[count_cols] < 0).any().any()
        or df[count_cols].mod(1).ne(0).any().any()
    ):
        raise ValueError(f"{year}: missing, negative or fractional victim/vehicle counts")
    if (
        not df[["TOTAL_MU30DF", "TOTAL_HG30DF", "TOTAL_HL30DF"]]
        .sum(axis=1)
        .eq(df["TOTAL_VICTIMAS_30DF"])
        .all()
    ):
        raise ValueError(f"{year}: inconsistent victim totals")
    if not df["TOTAL_VICTIMAS_30DF"].ge(1).all():
        raise ValueError(f"{year}: non-injury row in injury-crash source")
    for col, allowed in categories.items():
        unexpected = set(df[col].dropna().astype(int)) - allowed
        if unexpected:
            raise ValueError(f"{year}: category drift in {col}: {unexpected}")
    if abs(len(df) / BASELINE_ROWS[year] - 1) > 0.2:
        raise ValueError(f"{year}: unexpected row-count change >20%")
    if int(df["TOTAL_MU30DF"].sum()) != BASELINE_DEATHS[year]:
        raise ValueError(f"{year}: deaths changed from audited official release; re-audit revision")
    return {
        "year": year,
        "rows": len(df),
        "fields": len(df.columns),
        "checks": "passed",
        "fatalities_30d": int(df["TOTAL_MU30DF"].sum()),
        "hospitalized_30d": int(df["TOTAL_HG30DF"].sum()),
        "unknown_municipality": int(df["COD_MUNICIPIO"].fillna(0).eq(0).sum()),
        "unknown_collision": int(df["TIPO_ACCIDENTE"].isna().sum()),
        "missing_by_column": {c: int(n) for c, n in df.isna().sum().items() if n},
        "driver_age_check": "not applicable: driver ages are absent; no values manufactured",
        "date_check": "only year/month/weekday/hour available; exact calendar date absent",
    }
