import json
from pathlib import Path

import numpy as np
import pandas as pd

from ebdi.ingestion.europe import EU27
from ebdi.metrics.index import composite
from ebdi.utils.io import read_yaml

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def test_national_reconciliation_exposure_coverage_and_rate_formula():
    frame = pd.read_csv(TABLES / "spain_metrics.csv", dtype={"province_code": str})
    assert not frame.duplicated(["province_code", "year"]).any()
    assert frame.groupby("year").size().eq(52).all()
    assert frame.groupby("year").injury_crashes.sum().to_dict() == {
        2022: 97916,
        2023: 101306,
        2024: 101996,
    }
    assert frame.groupby("year").fatalities.sum().to_dict() == {2022: 1746, 2023: 1806, 2024: 1785}
    assert frame.loc[frame.year.eq(2024), "population"].sum() == 48619695
    assert frame.loc[frame.year.eq(2024), "registered_vehicles"].sum() == 36241784
    assert frame.loc[frame.year.eq(2024), "licensed_drivers"].sum() == 28138441
    missing = frame.year.eq(2023)
    assert frame.loc[missing, ["registered_vehicles", "licensed_drivers"]].isna().all().all()
    assert frame.loc[missing, "injury_crashes_per_100k_registered_vehicles"].isna().all()
    np.testing.assert_allclose(
        frame.injury_crashes_per_100k_population, frame.injury_crashes / frame.population * 100000
    )
    assert frame.groupby("year").unknown_collision.sum().to_dict() == {2022: 0, 2023: 0, 2024: 35}


def test_index_reproduces_published_scores_and_uncertainty_has_distinct_fields():
    frame = pd.read_csv(TABLES / "spain_metrics.csv", dtype={"province_code": str})
    weights = read_yaml(ROOT / "configs/index_weights.yaml")
    published = pd.read_csv(TABLES / "index.csv", dtype={"province_code": str})
    actual = pd.concat(
        [
            composite(
                group,
                weights["weights"],
                weights["normalization"],
                weights["minimum_injury_crashes"],
            )
            for _, group in frame.groupby("year")
        ]
    )
    merged = actual.merge(published, on=["year", "province_code"], validate="one_to_one")
    np.testing.assert_allclose(merged.index_score_x, merged.index_score_y)
    np.testing.assert_allclose(merged.index_rank_x, merged.index_rank_y)
    uncertainty = pd.read_csv(TABLES / "sensitivity.csv")
    assert uncertainty.weight_rank_min.le(uncertainty.weight_rank_max).all()
    assert uncertainty.bootstrap_rank_lower.le(uncertainty.bootstrap_rank_upper).all()
    assert len(uncertainty) == 52


def test_europe_has_only_actual_eu27_observations_and_variable_metadata():
    frame = pd.read_csv(TABLES / "europe_metrics.csv")
    assert len(frame) == 81
    assert set(frame.geo) == EU27
    assert not frame.duplicated(["geo", "year"]).any()
    assert frame.groupby("year").size().eq(27).all()
    np.testing.assert_allclose(
        frame.fatalities_per_million_population, frame.fatalities / frame.population * 1000000
    )
    metadata = pd.read_csv(TABLES / "country_comparability.csv").fillna("")
    assert len(metadata) == 405
    assert metadata.loc[metadata.included, "variable"].isin(["fatalities", "population"]).all()
    for variable in ["fatalities", "population"]:
        observed = metadata.loc[metadata.variable.eq(variable)]
        joined = observed.merge(frame, on=["geo", "year"], validate="one_to_one").fillna("")
        assert joined.status_flag.eq(joined[f"{variable}_status"]).all()


def test_all_eda_dimensions_conserve_events_including_unknown_codes():
    groups = pd.read_csv(TABLES / "crash_breakdowns.csv")
    nation = pd.read_csv(TABLES / "national_totals.csv").set_index("year")
    for measure in ["injury_crashes", "fatalities", "hospitalized", "severe_crashes"]:
        totals = groups.groupby(["year", "dimension"])[measure].sum().unstack()
        assert totals.eq(nation[measure], axis=0).all().all()
    assert (
        groups.groupby(["year", "dimension"])
        .share_of_recorded_crashes.sum()
        .sub(1)
        .abs()
        .lt(1e-10)
        .all()
    )


def test_model_report_target_and_final_holdout_are_consistent():
    card = json.loads((TABLES / "model_card.json").read_text())
    metrics = pd.read_csv(TABLES / "model_metrics.csv")
    assert card["personal_accident_risk"] is False
    assert card["test_year"] > max(card["refit_years"])
    assert metrics.selected_on_validation.sum() == 1
    assert metrics.n.eq(101996).all()
    assert metrics.positive_n.eq(10019).all()
    assert (metrics.tn + metrics.fp + metrics.fn + metrics.tp).eq(metrics.n).all()
    assert (metrics.fn + metrics.tp).eq(metrics.positive_n).all()
