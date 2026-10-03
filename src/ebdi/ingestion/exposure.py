"""Matched state-owned road numerator and RCE vehicle-kilometres, 2022 only."""

import re
from pathlib import Path

import pandas as pd
import pdfplumber

from ebdi.cleaning.geography import normalized_name
from ebdi.ingestion.download import raw_path
from ebdi.metrics.rates import poisson_interval, rate
from ebdi.utils.io import write_json


def parse_rce(text: str) -> pd.DataFrame:
    if "AÑO 2022" not in text or "TIPO DE VEHÍCULO: Todos" not in text:
        raise ValueError("RCE year/vehicle contract changed")
    records = []
    for line in text.splitlines():
        match = re.match(r"^(.+?)\s+(\d[\d.]*,\d)\s+(\d[\d.]*,\d)(?:\s|$)", line)
        if match:
            name, length, vkm = match.groups()
            records.append(
                {
                    "source_name": name,
                    "road_length_km": float(length.replace(".", "").replace(",", ".")),
                    "vehicle_km_million": float(vkm.replace(".", "").replace(",", ".")),
                }
            )
    frame = pd.DataFrame(records)
    totals = frame.loc[frame.source_name.eq("Total")]
    provinces = frame.loc[~frame.source_name.eq("Total")].copy()
    if len(totals) != 1 or provinces.source_name.duplicated().any() or len(provinces) < 40:
        raise ValueError("RCE table coverage changed")
    if (
        abs(provinces.vehicle_km_million.sum() - totals.vehicle_km_million.iloc[0])
        > len(provinces) * 0.05
    ):
        raise ValueError("RCE VKT total does not reconcile within published rounding")
    if provinces.vehicle_km_million.le(0).any():
        raise ValueError("Nonpositive RCE exposure")
    return provinces


def process_exposure(root: Path) -> pd.DataFrame:
    with pdfplumber.open(raw_path(root, "transport_rce_2022")) as pdf:
        traffic = parse_rce(pdf.pages[2].extract_text() or "")
    geo = pd.read_parquet(root / "data/processed/dim_geography.parquet")
    keys = {
        normalized_name(n): str(c).zfill(2)
        for c, n in geo[["province_code", "province"]].itertuples(index=False, name=None)
    }
    traffic["source_name"] = traffic.source_name.replace({"RIOJA": "La Rioja", "ORENSE": "Ourense"})
    traffic["province_code"] = traffic.source_name.map(normalized_name).map(keys)
    if traffic.province_code.isna().any():
        raise ValueError(
            f"Unmatched RCE provinces: {traffic.loc[traffic.province_code.isna(), 'source_name'].tolist()}"
        )
    facts = pd.read_parquet(root / "data/processed/fact_accidents.parquet")
    state = facts.loc[facts.year.eq(2022) & facts.TITULARIDAD_VIA.eq(1)]
    numerators = (
        state.groupby("province_code")
        .agg(rce_injury_crashes=("year", "size"), rce_fatalities=("TOTAL_MU30DF", "sum"))
        .reset_index()
    )
    numerators["province_code"] = numerators["province_code"].astype(str).str.zfill(2)
    frame = geo[["province_code", "province"]].copy()
    frame["province_code"] = frame["province_code"].astype(str).str.zfill(2)
    frame = frame.merge(numerators, on="province_code", how="left", validate="one_to_one")
    frame[["rce_injury_crashes", "rce_fatalities"]] = (
        frame[["rce_injury_crashes", "rce_fatalities"]].fillna(0).astype(int)
    )
    frame = frame.merge(traffic, on="province_code", how="left", validate="one_to_one")
    frame["year"] = 2022
    frame["rce_crashes_per_100m_vkm"] = rate(
        frame.rce_injury_crashes, frame.vehicle_km_million, 100
    )
    frame["lower"], frame["upper"] = poisson_interval(
        frame.rce_injury_crashes, frame.vehicle_km_million, 100
    )
    frame["matched_exposure"] = frame.vehicle_km_million.notna()
    frame["scope"] = (
        "RCE traffic / DGT state-owned roads; all vehicles; 2022; administrative network definitions may differ"
    )
    frame.to_csv(root / "outputs/tables/rce_exposure.csv", index=False)
    write_json(
        root / "outputs/tables/rce_quality.json",
        {
            "year": 2022,
            "provinces_with_exposure": int(frame.matched_exposure.sum()),
            "vkm_million_sum": float(frame.vehicle_km_million.sum()),
            "state_injury_crashes": int(frame.rce_injury_crashes.sum()),
            "unmatched_injury_crashes": int(
                frame.loc[~frame.matched_exposure, "rce_injury_crashes"].sum()
            ),
            "scope": "Only state-owned road network; not all-road risk; rounding and administrative classifications retained",
        },
    )
    return frame
