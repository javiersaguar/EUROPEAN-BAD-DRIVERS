"""Strict aggregate-only adapter for authorized insurer claims/exposure releases."""

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import pandas as pd

from ebdi.metrics.rates import poisson_interval, rate
from ebdi.utils.io import write_json

COLUMNS = {"province_code", "year", "coverage", "claims", "insured_vehicle_years"}
COVERAGES = {"rc_material", "own_damage", "glass"}


def validate_claims(frame: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    if set(frame.columns) != COLUMNS:
        raise ValueError(
            "Require only aggregate province/year/coverage/claims/insured_vehicle_years fields"
        )
    if not metadata.get("reuse_authorized") or not metadata.get("publisher"):
        raise ValueError("Publisher and explicit authorized reuse declaration required")
    if urlparse(metadata.get("source_url", "")).scheme != "https":
        raise ValueError("Require an HTTPS source citation")
    date.fromisoformat(metadata["published_date"])
    if metadata.get("numerator_scope") != metadata.get("denominator_scope") or not metadata.get(
        "numerator_scope"
    ):
        raise ValueError("Claims and insured-vehicle-year scopes must match")
    result = frame.copy()
    result["province_code"] = result.province_code.astype(str).str.zfill(2)
    if (
        not result.province_code.str.fullmatch(r"\d{2}").all()
        or not result.province_code.astype(int).between(1, 52).all()
    ):
        raise ValueError("Unknown province code")
    for key in ["year", "claims", "insured_vehicle_years"]:
        result[key] = pd.to_numeric(result[key], errors="raise")
        if not np.isfinite(result[key]).all():
            raise ValueError(f"Nonfinite {key}")
    if not result.year.between(2000, date.today().year).all() or result.year.mod(1).ne(0).any():
        raise ValueError("Invalid observation year")
    if (
        result.claims.lt(0).any()
        or result.claims.mod(1).ne(0).any()
        or result.insured_vehicle_years.le(0).any()
    ):
        raise ValueError("Require nonnegative integer claims and positive vehicle-year exposure")
    if (
        result.empty
        or not result.coverage.isin(COVERAGES).all()
        or result.duplicated(["province_code", "year", "coverage"]).any()
    ):
        raise ValueError("Empty, unknown coverage or duplicate claims grain")
    result["claims_per_100_vehicle_years"] = rate(result.claims, result.insured_vehicle_years, 100)
    result["lower"], result["upper"] = poisson_interval(
        result.claims, result.insured_vehicle_years, 100
    )
    result["source_url"] = metadata["source_url"]
    result["publisher"] = metadata["publisher"]
    result["scope"] = metadata["numerator_scope"]
    return result


def import_claims(root: Path, file: Path, metadata_file: Path) -> pd.DataFrame:
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    frame = validate_claims(pd.read_csv(file, dtype={"province_code": str}), metadata)
    frame.to_csv(root / "outputs/tables/insurance_exposure.csv", index=False)
    write_json(root / "outputs/tables/insurance_exposure_metadata.json", metadata)
    return frame
