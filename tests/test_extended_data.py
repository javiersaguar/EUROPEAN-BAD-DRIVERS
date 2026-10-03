"""Independent conservation, cohort and missing-value checks on published aggregates."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ebdi.ingestion.demographics import age_band
from ebdi.visualization.extended import wilson

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def table(name):
    return pd.read_csv(TABLES / f"{name}.csv")


def test_ncid_complete_cohort_and_cost_frequency_identity():
    frame = table("ncid_ultimate")
    assert len(frame) == 150 and not frame.duplicated(["year", "category"]).any()
    assert frame.groupby("category").year.nunique().eq(15).all()
    np.testing.assert_allclose(
        frame.cost_per_policy_eur,
        frame.frequency_per_1000_all_policies / 1000 * frame.mean_cost_eur,
    )
    for year, group in frame.groupby("year"):
        material = group[group.category.eq("Daños materiales")].iloc[0]
        pieces = group[
            group.claim_type.isin(
                ["Accidental Damage", "Fire and Theft", "Third Party Damage", "Windscreen"]
            )
        ]
        assert pieces.ultimate_claims.sum() == pytest.approx(material.ultimate_claims)
        portfolio = group[group.category.eq("Total")].iloc[0]
        injury = group[group.claim_type.eq("Third Party Injury (Total)")].iloc[0]
        assert portfolio.ultimate_claims == pytest.approx(
            material.ultimate_claims + injury.ultimate_claims
        )
        if year == 2024:
            assert material.ultimate_claims == pytest.approx(193329.185365)
            assert material.frequency_per_1000_all_policies == pytest.approx(85.69093092596462)
    assert not any(c in frame for c in ["lower", "upper"])


def test_ncid_covered_denominator_only_where_published_and_settlement_separate():
    frame = table("ncid_ultimate")
    own = frame.claim_type.eq("Accidental Damage")
    assert frame.loc[~own, "earned_policies_covered"].isna().all()
    assert frame.loc[own, "earned_policies_covered"].lt(frame.loc[own, "earned_policies_all"]).all()
    np.testing.assert_allclose(
        frame.loc[own, "frequency_per_1000_comprehensive"],
        frame.loc[own, "ultimate_claims"] / frame.loc[own, "earned_policies_covered"] * 1000,
    )
    settled = table("ncid_settled")
    assert len(settled) == 50 and set(settled.year) == set(range(2015, 2025))
    assert not any("frequency" in c or "policies" in c for c in settled)
    assert (
        settled.query("year == 2024 and category == 'Daños materiales'").settled_claims.iloc[0]
        == 139433
    )
    quality = json.loads((TABLES / "ncid_quality.json").read_text())
    assert quality["matched_exposure_sheet"] == "UltData (not PremData)"
    assert quality["table14_minus_table11_damage_claims_2024"] == 0
    assert quality["table14_minus_table12_summary_2024"] == 18


def test_deflation_uses_same_year_prices_and_2024_base():
    frame = table("ncid_ultimate")
    base = frame.loc[frame.year.eq(2024), "hicp"].unique()
    assert len(base) == 1
    np.testing.assert_allclose(frame.mean_cost_2024_eur, frame.mean_cost_eur * base[0] / frame.hicp)
    np.testing.assert_allclose(
        frame.loc[frame.year.eq(2024), "mean_cost_eur"],
        frame.loc[frame.year.eq(2024), "mean_cost_2024_eur"],
    )


def test_german_totals_and_missing_berlin_do_not_become_zero():
    frame = table("material_states")
    assert len(frame) == 68
    absent = frame.state.eq("Berlin") & frame.location.eq("Interurbana sin autopistas")
    assert absent.sum() == 1 and frame.loc[absent, "total_crashes"].isna().all()
    observed = frame[~absent]
    np.testing.assert_array_equal(
        observed.total_crashes.to_numpy(),
        observed.injury_crashes
        + observed.serious_property_crashes
        + observed.intoxicant_property_crashes
        + observed.other_property_crashes.to_numpy(),
    )
    states = frame[frame.location.eq("Total") & frame.state.ne("Deutschland")]
    assert states.property_only_crashes.sum() == 2221996
    history = table("material_history")
    assert len(history) == 15
    assert history.total_crashes.eq(history.injury_crashes + history.property_only_crashes).all()


def test_person_totals_match_independent_crash_deaths_and_roles_are_separate():
    frame = table("dgt_demographics")
    assert (
        len(frame) == 3780
        and not frame.duplicated(["year", "zone", "role", "age_band", "sex", "category"]).any()
    )
    assert set(frame.sex) == {"M", "F", "UNK"}
    assert set(frame.role) == {"all_victims", "drivers_victims", "drivers_involved"}
    deaths = (
        frame[(frame.role == "all_victims") & frame.category.eq("Total")]
        .groupby("year")
        .fatalities.sum()
    )
    expected = table("national_totals").set_index("year").fatalities
    pd.testing.assert_series_equal(deaths, expected, check_dtype=False)
    assert frame.loc[frame.role.eq("drivers_involved"), "fatalities"].isna().all()
    assert frame.loc[~frame.role.eq("drivers_involved"), "involved"].isna().all()


def test_original_absent_bicycle_cells_and_source_gaps_are_disclosed():
    frame = table("dgt_demographics")
    bicycle = frame[
        (frame.year == 2024)
        & (frame.role == "all_victims")
        & (frame.zone == "Urbana")
        & (frame.category == "Bicicleta")
    ]
    assert len(bicycle) == 18
    assert (
        bicycle[["fatalities", "hospitalized", "non_hospitalized", "casualties"]].isna().all().all()
    )
    notes = json.loads((TABLES / "demographics_quality.json").read_text())["source_notes"]
    gaps = {n["measure"]: n["published_components_minus_total"] for n in notes if "measure" in n}
    assert gaps == {"fatalities": 5, "hospitalized": 5, "non_hospitalized": 13}
    assert sorted(n["missing_cells"] for n in notes if "missing_cells" in n) == [1, 240]


def test_standardization_has_fixed_common_weights_and_unknown_age_policy():
    pop = table("spain_age_population")
    assert len(pop) == 30 and pop.population.gt(0).all()
    assert pop.groupby(["year", "sex"]).standard_weight_2024.sum().eq(1).all()
    assert pop.groupby("age_band").standard_weight_2024.nunique().eq(1).all()
    cells = table("spain_age_sex_rates")
    standardized = (
        (cells.fatalities / cells.population * cells.standard_weight_2024 * 1_000_000)
        .groupby([cells.year, cells.sex])
        .sum()
    )
    published = table("spain_sex_rates").set_index(["year", "sex"])
    np.testing.assert_allclose(
        standardized.sort_index(), published.age_standardized_per_million.sort_index()
    )
    np.testing.assert_allclose(
        published.crude_per_million, published.fatalities / published.population * 1_000_000
    )
    assert (published.lower <= published.crude_per_million).all() and (
        published.upper >= published.crude_per_million
    ).all()


def test_europe_dense_grain_flags_and_unknown_sex_without_exposure():
    frame = table("europe_sex_users")
    assert len(frame) == 27 * 15 * 4 * 5
    assert not frame.duplicated(["geo", "year", "sex", "pers_cat"]).any()
    unknown = frame.sex.eq("UNK")
    assert frame.loc[unknown, "population"].isna().all()
    assert frame.loc[unknown, "fatalities_per_million"].isna().all()
    assert frame.loc[unknown, "fatalities"].notna().any()
    assert frame.fatalities.isna().any()
    assert {"fatalities_status", "population_status"} <= set(frame)
    matched = frame[frame.included]
    np.testing.assert_allclose(
        matched.fatalities_per_million, matched.fatalities / matched.population * 1_000_000
    )


def test_collision_partitions_and_conditional_intervals():
    frame = table("collision_analysis")
    assert len(frame) == 3 * 3 * 22
    counts = frame[~frame.is_total].groupby(["year", "zone"]).crashes.sum()
    totals = frame[frame.is_total].set_index(["year", "zone"]).crashes
    pd.testing.assert_series_equal(counts.sort_index(), totals.sort_index())
    assert frame.fatal_crashes.le(frame.crashes).all()
    observed = frame[frame.crashes.gt(0)]
    assert (
        observed.lower.le(observed.fatal_crash_pct).all()
        and observed.upper.ge(observed.fatal_crash_pct).all()
    )
    assert frame.loc[frame.crashes.eq(0), ["fatal_crash_pct", "lower", "upper"]].isna().all().all()
    lower, upper = wilson(pd.Series([0, 5]), pd.Series([10, 0]))
    assert lower.iloc[0] == 0 and 0 < upper.iloc[0] < 100
    assert pd.isna(lower.iloc[1]) and pd.isna(upper.iloc[1])


def test_vehicle_age_includes_unknown_in_denominator_and_discloses_unlabelled_type():
    frame = table("vehicle_age_analysis")
    parts = frame[frame.age.ne("Total")].groupby(["year", "zone", "category"]).vehicles.sum()
    parent = frame[frame.age.eq("Total")].set_index(["year", "zone", "category"]).vehicles
    pd.testing.assert_series_equal(parts.sort_index(), parent.sort_index())
    total = frame[(frame.year == 2024) & frame.zone.eq("Total") & frame.category.eq("Total")]
    assert total.loc[total.age.eq("Total"), "vehicles"].iloc[0] == 160345
    assert total.loc[total.age.eq("Se desconoce"), "vehicles"].iloc[0] == 41578
    assert total.loc[total.age.eq("Más de 15 años"), "share_all_pct"].iloc[0] == pytest.approx(
        40835 / 160345 * 100
    )
    assert (
        "87"
        in json.loads((TABLES / "extended_analysis.json").read_text())["vehicle_type_source_note"]
    )


def test_age_mapping_rejects_overlapping_groups():
    assert age_band("De 18 a 20 años") == "18–24"
    assert age_band("Más de 74 años") == "65+"
    with pytest.raises(ValueError, match="crosses"):
        age_band("De 15 a 20 años")
