"""Decode JSON-stat without converting absent observations into zeros."""

from typing import Any

import numpy as np
import pandas as pd

EU27 = {
    "BE",
    "BG",
    "CZ",
    "DK",
    "DE",
    "EE",
    "IE",
    "EL",
    "ES",
    "FR",
    "HR",
    "IT",
    "CY",
    "LV",
    "LT",
    "LU",
    "HU",
    "MT",
    "NL",
    "AT",
    "PL",
    "PT",
    "RO",
    "SI",
    "SK",
    "FI",
    "SE",
}


def decode_jsonstat(data: dict[str, Any]) -> pd.DataFrame:
    if data.get("class") != "dataset":
        raise ValueError("Expected a JSON-stat dataset")
    keys, sizes = data["id"], data["size"]
    indexes: dict[str, dict[int, str]] = {}
    for key in keys:
        index = data["dimension"][key]["category"]["index"]
        indexes[key] = (
            {v: k for k, v in index.items()} if isinstance(index, dict) else dict(enumerate(index))
        )
    values = data["value"]
    iterable = values.items() if isinstance(values, dict) else enumerate(values)
    statuses = data.get("status", {})
    rows = []
    for flat, value in iterable:
        if value is None:
            continue
        coords = np.unravel_index(int(flat), sizes)
        row: dict[str, Any] = {k: indexes[k][int(i)] for k, i in zip(keys, coords, strict=True)}
        row["value"] = float(value)
        row["status"] = (
            statuses.get(str(flat), "") if isinstance(statuses, dict) else statuses[int(flat)]
        )
        rows.append(row)
    return pd.DataFrame(rows)
