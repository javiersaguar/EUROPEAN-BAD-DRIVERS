"""NCID report 7: preserve accident/settlement bases and matched market cohorts."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ebdi.ingestion.download import raw_path
from ebdi.ingestion.europe import decode_jsonstat
from ebdi.utils.io import write_json

CLAIMS = {
    "Accidental Damage": "Daños propios por accidente",
    "Fire and Theft": "Incendio y robo",
    "Third Party Damage": "Daños materiales a terceros",
    "Windscreen": "Lunas",
    "Third Party Injury (Total)": "Lesiones a terceros",
    "Third Party Injury (<=250k)": "Lesiones hasta 250.000 €",
    "Third Party Injury (>250k)": "Lesiones superiores a 250.000 €",
}
DAMAGE = list(CLAIMS)[:4]


def extract_ncid(path: Path, hicp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    frame = pd.read_excel(path, sheet_name="UltData", header=None, engine="calamine")
    left = frame.iloc[3:, :5].copy()
    left.columns = ["year", "quarter", "measure", "claim_type", "value"]
    left = left.dropna(how="all")
    right = frame.iloc[3:, 6:11].copy()
    right.columns = ["year", "quarter", "measure", "cover", "value"]
    right = right.dropna(how="all")
    expected = {y * 100 + q for y in range(2010, 2025) for q in [3, 6, 9, 12]}
    for data, dimensions, size in [
        (left, ["measure", "claim_type"], 14),
        (right, ["measure", "cover"], 4),
    ]:
        if (
            data.duplicated(["quarter", *dimensions]).any()
            or data.groupby(dimensions).ngroups != size
        ):
            raise ValueError("NCID grain or categories changed")
        if any(set(g.quarter.astype(int)) != expected for _, g in data.groupby(dimensions)):
            raise ValueError("Incomplete NCID quarters; do not silently sum partial years")
        data["value"] = pd.to_numeric(data.value, errors="raise")
        if not np.isfinite(data.value).all() or data.value.lt(0).any():
            raise ValueError("Invalid NCID observations")
        if not data.year.astype(int).eq(data.quarter.astype(int) // 100).all():
            raise ValueError("NCID accident-year/quarter mismatch")
    annual = (
        left.groupby(["year", "claim_type", "measure"]).value.sum().unstack("measure").reset_index()
    )
    annual = annual.rename(
        columns={
            "Ultimate Costs": "ultimate_cost_eur",
            "Ultimate Numbers (incl. nils)": "ultimate_claims",
        }
    )
    exposure = (
        right.loc[right.measure.eq("Earned Policy Count")]
        .groupby(["year", "cover"])
        .value.sum()
        .unstack("cover")
    )
    annual["earned_policies_all"] = annual.year.map(exposure.sum(axis=1))
    annual["earned_policies_covered"] = np.where(
        annual.claim_type.eq("Accidental Damage"), annual.year.map(exposure.Comprehensive), np.nan
    )
    # Other policy types include third-party fire/theft; use portfolio exposure,
    # rather than inventing their unreported cover-specific policy-year counts.
    annual["frequency_per_1000_all_policies"] = (
        annual.ultimate_claims / annual.earned_policies_all * 1000
    )
    annual["frequency_per_1000_comprehensive"] = (
        annual.ultimate_claims / annual.earned_policies_covered * 1000
    ).where(annual.claim_type.eq("Accidental Damage"))
    annual["mean_cost_eur"] = annual.ultimate_cost_eur / annual.ultimate_claims
    annual["cost_per_policy_eur"] = annual.ultimate_cost_eur / annual.earned_policies_all
    annual["category"] = annual.claim_type.map(CLAIMS)
    if annual.category.isna().any():
        raise ValueError("Unknown NCID claim type")
    injury = annual[annual.claim_type.str.startswith("Third Party Injury")].pivot(
        index="year", columns="claim_type", values=["ultimate_claims", "ultimate_cost_eur"]
    )
    band_differences = {
        value: (
            injury[value]["Third Party Injury (<=250k)"]
            + injury[value]["Third Party Injury (>250k)"]
            - injury[value]["Third Party Injury (Total)"]
        ).to_dict()
        for value in ["ultimate_claims", "ultimate_cost_eur"]
    }
    groups = []
    for name, types in [
        ("Daños materiales", DAMAGE),
        ("Lesiones", ["Third Party Injury (Total)"]),
        ("Total", DAMAGE + ["Third Party Injury (Total)"]),
    ]:
        g = (
            annual.loc[annual.claim_type.isin(types)]
            .groupby("year", as_index=False)[["ultimate_claims", "ultimate_cost_eur"]]
            .sum()
        )
        g["claim_type"], g["category"] = name, name
        g["earned_policies_all"] = g.year.map(exposure.sum(axis=1))
        g["frequency_per_1000_all_policies"] = g.ultimate_claims / g.earned_policies_all * 1000
        g["mean_cost_eur"] = g.ultimate_cost_eur / g.ultimate_claims
        g["cost_per_policy_eur"] = g.ultimate_cost_eur / g.earned_policies_all
        groups.append(g)
    annual = pd.concat([annual, *groups], ignore_index=True)
    prices = hicp.assign(year=hicp.time.astype(int)).set_index("year").value
    if set(prices.index) != set(range(2010, 2025)) or prices.le(0).any():
        raise ValueError("Missing or invalid deflator")
    annual["hicp"] = annual.year.map(prices)
    annual["mean_cost_2024_eur"] = annual.mean_cost_eur * prices.loc[2024] / annual.hicp
    annual["ultimate_cost_2024_eur"] = annual.ultimate_cost_eur * prices.loc[2024] / annual.hicp
    annual["basis"] = "accident_year_ultimate_estimate_including_nils"
    annual.loc[
        annual.claim_type.isin(["Third Party Injury (<=250k)", "Third Party Injury (>250k)"]),
        "basis",
    ] = "size_band_ultimate_estimate_not_additive"
    annual["market_coverage_pct"] = np.where(annual.year.eq(2024), 94, np.nan)
    annual["source_sheet"] = "UltData"
    annual["year"] = annual.year.astype(int)
    settled = pd.read_excel(path, sheet_name="Table14_15", header=None, engine="calamine")
    rows = []
    for _, row in settled.iloc[4:14].iterrows():
        for j, name in enumerate(DAMAGE + ["Daños materiales"], start=1):
            rows.append(
                {
                    "year": int(row[0]),
                    "claim_type": name,
                    "category": CLAIMS.get(name, name),
                    "settled_claims": int(row[j]),
                    "settled_cost_eur": float(row[j + 5]),
                    "basis": "settlement_year",
                    "market_coverage_pct": 88 if int(row[0]) == 2024 else np.nan,
                    "source_sheet": "Table14_15",
                }
            )
    settlements = pd.DataFrame(rows)
    settlements["mean_cost_eur"] = settlements.settled_cost_eur / settlements.settled_claims
    settlements["mean_cost_2024_eur"] = (
        settlements.mean_cost_eur * prices.loc[2024] / settlements.year.map(prices)
    )
    pieces = (
        settlements.loc[settlements.claim_type.isin(DAMAGE)].groupby("year")["settled_claims"].sum()
    )
    if not pieces.eq(
        settlements.loc[settlements.claim_type.eq("Daños materiales")]
        .set_index("year")
        .settled_claims
    ).all():
        raise ValueError("Settled damage types do not reconcile")
    aggregate = pd.read_excel(path, sheet_name="Table 11", header=2, engine="calamine").iloc[:10]
    discrepancy = int(
        settlements.query("year == 2024 and claim_type == 'Daños materiales'").settled_claims.iloc[
            0
        ]
        - aggregate.iloc[-1, 1]
    )
    summary = pd.read_excel(path, sheet_name="Table12_13", header=None, engine="calamine")
    summary_discrepancy = int(
        settlements.query("year == 2024 and claim_type == 'Daños materiales'").settled_claims.iloc[
            0
        ]
        - summary.iloc[5, 10]
    )
    quality = {
        "status": "passed_with_source_note",
        "accident_year_rows": len(annual),
        "settlement_rows": len(settlements),
        "matched_exposure_sheet": "UltData (not PremData)",
        "table14_minus_table11_damage_claims_2024": discrepancy,
        "injury_size_band_minus_total": band_differences,
        "note": "Table11 and Table14 totals reconcile; Table12 summary differs by 18. Source counts retained, no exposure attached to settled counts, no Poisson intervals for estimates.",
        "deflator": "Ireland annual all-items HICP, costs in 2024 euros; not dedicated repair inflation",
        "coverage_note": "94% and 88% refer to 2024 earned-premium market coverage, not population sampling probabilities",
    }
    quality["table14_minus_table12_summary_2024"] = summary_discrepancy
    quality["note"] = (
        "Annex Table12 summary and Table14 settled-damage counts differ by 18 in 2024; counts are preserved. Estimated injury size bands do not exactly partition the published total; they are never summed into the portfolio. No exposure is attached to settlement-year counts; ultimate estimates receive no Poisson intervals."
    )
    return annual, settlements, quality


def process_ncid(root: Path) -> dict:
    hicp = decode_jsonstat(
        json.loads(raw_path(root, "eurostat_ie_hicp").read_text(encoding="utf-8"))
    )
    annual, settled, quality = extract_ncid(raw_path(root, "ncid_motor_2024"), hicp)
    for name, data in [("ncid_ultimate", annual), ("ncid_settled", settled)]:
        data.to_csv(root / f"outputs/tables/{name}.csv", index=False)
        data.to_parquet(root / f"data/processed/{name}.parquet", index=False)
    write_json(root / "outputs/tables/ncid_quality.json", quality)
    return quality
