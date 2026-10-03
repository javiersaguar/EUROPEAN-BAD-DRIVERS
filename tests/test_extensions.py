import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from ebdi.ingestion.claims import validate_claims
from ebdi.ingestion.exposure import parse_rce
from ebdi.ingestion.monitor import probe_source, validate_candidate
from ebdi.metrics.alternatives import ALTERNATIVE
from ebdi.metrics.index import composite
from ebdi.modeling.policy import choose_f2_threshold

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def test_historical_grain_flags_and_new_stock_totals():
    history = pd.read_csv(TABLES / "europe_history.csv")
    assert len(history) == 405
    assert not history.duplicated(["geo", "year"]).any()
    assert history.groupby("geo").size().eq(15).all()
    assert history.included.all()
    assert set(history.year) == set(range(2010, 2025))
    np.testing.assert_allclose(
        history.fatalities_per_million_population,
        history.fatalities / history.population * 1_000_000,
    )


def test_alternative_does_not_double_weight_urban_collision_subsets():
    frame = pd.read_csv(TABLES / "spain_metrics.csv", dtype={"province_code": str})
    published = pd.read_csv(TABLES / "index_alternative.csv", dtype={"province_code": str})
    actual = pd.concat([composite(group, ALTERNATIVE) for _, group in frame.groupby("year")])
    merged = actual.merge(published, on=["year", "province_code"], validate="one_to_one")
    np.testing.assert_allclose(merged.index_score_x, merged.index_score_y)
    np.testing.assert_allclose(merged.index_rank_x, merged.index_rank_y)
    assert not any("urban" in key or "rear" in key for key in ALTERNATIVE)


def test_rce_rates_preserve_unmatched_network_exposure_and_rounding():
    frame = pd.read_csv(TABLES / "rce_exposure.csv", dtype={"province_code": str})
    assert len(frame) == 52 and frame.year.eq(2022).all()
    assert frame.rce_injury_crashes.sum() == 10956
    assert frame.matched_exposure.sum() == 44
    assert frame.loc[~frame.matched_exposure, "rce_crashes_per_100m_vkm"].isna().all()
    assert frame.loc[~frame.matched_exposure, "rce_injury_crashes"].sum() == 35
    observed = frame.loc[frame.matched_exposure]
    np.testing.assert_allclose(
        observed.rce_crashes_per_100m_vkm,
        observed.rce_injury_crashes / observed.vehicle_km_million * 100,
    )
    assert abs(observed.vehicle_km_million.sum() - 134902.5) < 44 * 0.05
    with pytest.raises(ValueError, match="contract"):
        parse_rce("AÑO 2024; TIPO DE VEHÍCULO: Todos")


def test_policy_uses_validation_threshold_and_marks_exploratory_status():
    threshold = choose_f2_threshold(np.array([0, 0, 1, 1]), np.array([0.1, 0.2, 0.3, 0.8]))
    assert threshold == 0.3
    card = json.loads((TABLES / "model_policy.json").read_text())
    policy = pd.read_csv(TABLES / "model_policy.csv")
    assert card["threshold_selection_year"] < card["reported_year"]
    assert not card["confirmatory"] and card["future_holdout_required"]
    assert policy.train_year.eq(2022).all()
    assert policy.threshold_selection_year.eq(2023).all()
    assert policy.loc[policy.policy.eq("validation_F2"), "threshold"].iloc[0] == pytest.approx(
        card["selected_threshold"]
    )
    assert (policy.tp + policy.fp + policy.fn + policy.tn).eq(policy.n).all()


def claims_fixture():
    frame = pd.DataFrame(
        {
            "province_code": ["28"],
            "year": [2024],
            "coverage": ["rc_material"],
            "claims": [10],
            "insured_vehicle_years": [200.0],
        }
    )
    metadata = {
        "publisher": "Synthetic test fixture; never published",
        "reuse_authorized": True,
        "source_url": "https://example.org/test",
        "published_date": "2025-01-01",
        "numerator_scope": "test portfolio",
        "denominator_scope": "test portfolio",
    }
    return frame, metadata


def test_insurer_adapter_calculates_matched_rates_and_rejects_unsafe_grains():
    frame, metadata = claims_fixture()
    assert validate_claims(frame, metadata).claims_per_100_vehicle_years.iloc[0] == 5
    for column, value in [
        ("claims", -1),
        ("claims", 1.5),
        ("insured_vehicle_years", 0),
        ("province_code", "99"),
        ("coverage", "unknown"),
    ]:
        broken = frame.copy()
        broken[column] = value
        with pytest.raises(ValueError):
            validate_claims(broken, metadata)
    with pytest.raises(ValueError):
        validate_claims(frame.assign(policyholder="personal data"), metadata)
    with pytest.raises(ValueError):
        validate_claims(frame, {**metadata, "denominator_scope": "different network"})
    with pytest.raises(ValueError):
        validate_claims(frame, {**metadata, "reuse_authorized": False})
    with pytest.raises(ValueError):
        validate_claims(pd.concat([frame, frame]), metadata)


def test_source_monitor_quarantines_revisions_without_activating_them(tmp_path, monkeypatch):
    payload = b'{"id":["geo"],"size":[1],"dimension":{},"value":{"0":1}}'
    source = {
        "id": "eurostat_test",
        "sample_sha256": "0" * 64,
        "format": "json",
        "filename": "test.json",
        "url": "https://example.org/test",
    }
    response = SimpleNamespace(content=payload, raise_for_status=lambda: None)
    monkeypatch.setattr("ebdi.ingestion.monitor.requests.get", lambda *args, **kwargs: response)
    result = probe_source(tmp_path, source)
    assert result["status"] == "needs_review"
    assert (tmp_path / result["quarantine_path"]).read_bytes() == payload
    assert not (tmp_path / "data/raw/manifest.json").exists()
    assert (
        probe_source(tmp_path, {**source, "sample_sha256": hashlib.sha256(payload).hexdigest()})[
            "status"
        ]
        == "unchanged"
    )
    with pytest.raises(ValueError):
        validate_candidate({"id": "pdf", "format": "pdf"}, b"<html>Access denied</html>")


def test_publication_exports_only_aggregates_with_verifiable_lineage():
    payload = json.loads((ROOT / "web/public/data/observatory.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1 and payload["release"] == "0.2.0"
    for name, rows in payload["tables"].items():
        assert rows
        assert "ID_ACCIDENTE" not in rows[0]
        assert (
            payload["table_hashes"][name]
            == hashlib.sha256((TABLES / f"{name}.csv").read_bytes()).hexdigest()
        )
    assert len(payload["tables"]["spain_metrics"]) == 156
    assert len(payload["tables"]["europe_history"]) == 405
    assert (
        len(
            json.loads((ROOT / "web/public/data/spain.geojson").read_text(encoding="utf-8"))[
                "features"
            ]
        )
        == 52
    )
