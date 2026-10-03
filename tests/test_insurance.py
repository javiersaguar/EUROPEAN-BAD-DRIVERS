import json
from pathlib import Path

import pandas as pd
import pytest

from ebdi.ingestion.download import raw_path
from ebdi.ingestion.insurance import AUDITED_SHA256, extract_insurance, municipal_rows

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def test_published_material_damage_values_and_selection_contract():
    frame = pd.read_csv(TABLES / "insurance_municipal.csv")
    assert len(frame) == 80
    assert frame.year.unique().tolist() == [2024]
    assert frame.groupby(["coverage", "selection"]).size().tolist() == [20] * 4
    assert not frame.duplicated(["coverage", "municipality"]).any()
    material = frame.loc[frame.coverage.eq("rc_material")].set_index("municipality")
    assert material.loc["Melilla", "relative_difference_pct"] == 40.99
    assert material.loc["Orihuela", "relative_difference_pct"] == -26.93
    assert material.loc["Marbella", "relative_difference_pct"] == 25.34
    assert material.loc["Málaga", "relative_difference_pct"] == 25.34  # Preserve ties.
    assert material.loc["Arona", "province_source"] == "S. C. de Tenerife"  # Wrapped cell.
    bodily = frame.loc[frame.coverage.eq("rc_corporal")].set_index("municipality")
    assert bodily.loc["El Puerto de Santa María", "province_source"] == "Cádiz"  # Wrapped label.
    assert bodily.loc["Chiclana de la Fron.", "relative_difference_pct"] == 154.68
    assert frame.loc[frame.selection.eq("higher"), "relative_difference_pct"].gt(0).all()
    assert frame.loc[frame.selection.eq("lower"), "relative_difference_pct"].lt(0).all()
    assert not {"claims", "insured_vehicle_years", "absolute_probability"}.intersection(
        frame.columns
    )


def test_national_units_and_preserved_provincial_reconciliation_gap():
    frame = pd.read_csv(TABLES / "insurance_coverage.csv").set_index("coverage")
    assert len(frame) == 11
    assert frame.loc["Resp. civil material", "claims_share_pct"] == 15.85
    assert frame.loc["Resp. civil material", "mean_cost_eur"] == 1363
    assert frame.loc["Daños propios del vehículo", "claims_share_pct"] == 21.39
    assert frame.claims_share_pct.sum() == pytest.approx(100, abs=0.05)
    quality = json.loads((TABLES / "insurance_quality.json").read_text(encoding="utf-8"))
    provinces = pd.read_csv(TABLES / "insurance_provinces.csv")
    assert len(provinces) == provinces.province_source.nunique() == 50
    assert not provinces.province_source.isin(["Ceuta", "Melilla"]).any()
    assert quality["national_all_coverage_claims"] == 11_071_215
    assert provinces.all_coverage_claims.sum() == 11_053_508
    assert quality["provincial_claims_difference_from_national"] == -17_707
    assert quality["provincial_payments_difference_from_national"] == -24_573_178
    assert quality["sha256"] == AUDITED_SHA256
    for name in [
        "municipal_claim_counts_available",
        "insured_vehicle_years_available",
        "absolute_municipal_probability_available",
        "complete_municipal_panel",
        "injury_free_event_count_available",
    ]:
        assert quality[name] is False


def test_changed_pdf_requires_new_audit(tmp_path):
    path = tmp_path / "changed.pdf"
    path.write_bytes(b"%PDF-1.7 different publisher revision")
    with pytest.raises(ValueError, match="revision changed"):
        extract_insurance(path)


def test_missing_municipal_rows_are_rejected():
    class EmptyPage:
        def extract_words(self):
            return []

    with pytest.raises(ValueError, match="Expected 20"):
        municipal_rows(EmptyPage(), "rc_material", "higher", (62, 160, 230, 298))


def test_local_hashed_pdf_reproduces_published_tables():
    try:
        path = raw_path(ROOT, "unespa_motor_2024")
    except FileNotFoundError:
        pytest.skip("Local audited PDF absent; published result checks run without network")
    coverage, municipal, provinces, quality = extract_insurance(path)
    for name, actual in [
        ("insurance_coverage", coverage),
        ("insurance_municipal", municipal),
        ("insurance_provinces", provinces),
    ]:
        pd.testing.assert_frame_equal(actual, pd.read_csv(TABLES / f"{name}.csv"))
    assert quality == json.loads((TABLES / "insurance_quality.json").read_text(encoding="utf-8"))
