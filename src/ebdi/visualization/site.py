"""Versioned public contract for the static observatory; aggregates only."""

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

from ebdi.ingestion.download import catalog
from ebdi.utils.io import write_json

TABLES = [
    "spain_metrics",
    "national_totals",
    "index",
    "index_alternative",
    "sensitivity",
    "europe_metrics",
    "europe_history",
    "country_comparability",
    "crash_breakdowns",
    "insurance_coverage",
    "insurance_municipal",
    "insurance_provinces",
    "model_metrics",
    "model_validation",
    "model_pr_curve",
    "model_calibration",
    "model_permutation_importance",
    "model_policy",
    "model_validation_thresholds",
    "rce_exposure",
]


def export_site(root: Path) -> dict:
    output = root / "web/public/data"
    output.mkdir(parents=True, exist_ok=True)
    payload: dict = {
        "schema_version": 1,
        "release": "0.2.0",
        "audit_date": "2026-10-03",
        "author": "Javier Saguar",
        "tables": {},
        "table_hashes": {},
        "sources": catalog(root),
    }
    names = TABLES + (
        ["insurance_exposure"] if (root / "outputs/tables/insurance_exposure.csv").exists() else []
    )
    for name in names:
        path = root / "outputs/tables" / f"{name}.csv"
        # The public lineage hashes the committed UTF-8/LF representation.
        # Pandas defaults to CRLF on Windows; Git normalizes these text files.
        # Canonicalize derived CSVs so Linux/Windows hash the same publication.
        canonical = path.read_bytes().replace(b"\r\n", b"\n")
        if canonical != path.read_bytes():
            path.write_bytes(canonical)
        frame = pd.read_csv(path, dtype={"province_code": str})
        # pandas JSON emits true JSON nulls (no non-standard NaN, no zero fill).
        payload["tables"][name] = json.loads(
            frame.to_json(orient="records", force_ascii=False, double_precision=12)
        )
        payload["table_hashes"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        shutil.copyfile(path, output / f"{name}.csv")
    for name in ["data_quality", "insurance_quality", "model_policy", "model_card", "rce_quality"]:
        payload[name] = json.loads(
            (root / "outputs/tables" / f"{name}.json").read_text(encoding="utf-8")
        )
    write_json(output / "observatory.json", payload)
    geometry = root / "data/processed/spain_provinces.geojson"
    if geometry.exists():
        content = json.loads(geometry.read_text(encoding="utf-8"))
        (output / "spain.geojson").write_text(
            json.dumps(content, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    elif not (output / "spain.geojson").exists():
        raise FileNotFoundError("Build the audited GISCO province map with ebdi process")
    figures = root / "web/public/figures"
    figures.mkdir(parents=True, exist_ok=True)
    for name in ["model_shap_summary.png", "weight_sensitivity.svg", "model_importance.svg"]:
        path = root / "outputs/figures" / name
        if path.exists():
            shutil.copyfile(path, figures / name)
    health = {
        "status": "ok",
        "release": payload["release"],
        "schema_version": 1,
        "province_years": len(payload["tables"]["spain_metrics"]),
        "history_rows": len(payload["tables"]["europe_history"]),
        "audit_date": payload["audit_date"],
    }
    write_json(root / "web/public/health.json", health)
    return health
