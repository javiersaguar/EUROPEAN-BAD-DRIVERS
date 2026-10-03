"""Explicit province identifiers and strict name reconciliation."""

import re
import unicodedata
from typing import Any

import pandas as pd

ALIASES = {
    "balearsilles": "illesbalears",
    "palmaslas": "laspalmas",
    "riojala": "larioja",
    "corunaa": "acoruna",
    "sctenerife": "santacruzdetenerife",
    "santacruzdetenerife": "santacruzdetenerife",
    "alava": "arabaalava",
    "alicante": "alicantealacant",
    "castellon": "castelloncastello",
    "valencia": "valenciavalencia",
    "guipuzcoa": "gipuzkoa",
    "vizcaya": "bizkaia",
}


def normalized_name(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    key = re.sub(r"[^a-z]", "", ascii_value)
    return ALIASES.get(key, key)


def province_code(value: Any) -> str:
    if pd.isna(value) or float(value) != int(float(value)) or not 1 <= int(float(value)) <= 52:
        raise ValueError(f"Invalid Spanish province code: {value!r}")
    return f"{int(float(value)):02d}"


def checked_join(left: pd.DataFrame, right: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if right.duplicated(keys).any():
        raise ValueError(f"Duplicate denominator keys: {keys}")
    result = left.merge(right, on=keys, how="left", validate="many_to_one", indicator=True)
    if result["_merge"].ne("both").any():
        bad = result.loc[result["_merge"].ne("both"), keys].head().to_dict("records")
        raise ValueError(f"Unmatched geographic/year keys: {bad}")
    return result.drop(columns="_merge")
