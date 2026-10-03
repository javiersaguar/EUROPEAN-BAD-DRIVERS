"""German police property-only accidents; keep reporting classifications separate."""

from pathlib import Path

import numpy as np
import pandas as pd

from ebdi.ingestion.download import raw_path
from ebdi.utils.io import write_json


def numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = frame.copy()
    for col in columns:
        # Destatis legend: '-' means nothing present, '.' means unavailable.
        result[col] = pd.to_numeric(result[col].replace({"-": 0, ".": np.nan}), errors="raise")
        observed = result[col].dropna()
        if observed.lt(0).any() or observed.mod(1).ne(0).any():
            raise ValueError("Invalid police accident count")
    return result


def process_material(root: Path) -> dict:
    history = pd.read_excel(
        raw_path(root, "destatis_damage_history"), sheet_name="csv-46241-01", engine="calamine"
    )
    history = history[history.Jahr.between(2010, 2024)].copy()
    history = history.rename(
        columns={
            "Jahr": "year",
            "Unfaelle_insgesamt": "total_crashes",
            "Unfaelle_Personenschaden": "injury_crashes",
            "Unfaelle_Sachschaden": "property_only_crashes",
            "Schwerwiegende_Sachschadensunfaelle_im_engeren_Sinne": "serious_property_crashes",
            "Getoetete": "fatalities",
        }
    )
    if len(history) != 15 or history.year.duplicated().any():
        raise ValueError("Incomplete German national history")
    history = numeric(
        history,
        [
            "total_crashes",
            "injury_crashes",
            "property_only_crashes",
            "serious_property_crashes",
            "fatalities",
        ],
    )
    if not history.total_crashes.eq(history.injury_crashes + history.property_only_crashes).all():
        raise ValueError("Property/injury accidents do not partition national totals")
    history["property_only_share_pct"] = history.property_only_crashes / history.total_crashes * 100
    history = history[
        [
            "year",
            "total_crashes",
            "injury_crashes",
            "property_only_crashes",
            "serious_property_crashes",
            "fatalities",
            "property_only_share_pct",
        ]
    ].sort_values("year")
    frame = pd.read_excel(
        raw_path(root, "destatis_damage_2024"), sheet_name="csv-46241-b01", engine="calamine"
    )
    frame = frame.rename(
        columns={
            "Jahr": "year",
            "Gebiet": "state",
            "Ortslage": "location_source",
            "Unfaelle_insgesamt": "total_crashes",
            "Unfaelle_Personenschaden": "injury_crashes",
            "Schwerwiegende_Sachschadensunfaelle_im_engeren_Sinne": "serious_property_crashes",
            "Sonstiger_Sachschadensunfall_unter_Einfluss_berauschender_Mittel": "intoxicant_property_crashes",
            "uebrige_Sachschadensunfaelle": "other_property_crashes",
        }
    )
    locations = {
        "Innerhalb und außerhalb von Ortschaften": "Total",
        "Innerhalb von Ortschaften": "Urbana",
        "Außerhalb von Ortschaften, ohne Autobahn": "Interurbana sin autopistas",
        "auf Autobahnen": "Autopista",
    }
    frame["location"] = frame.location_source.str.strip().map(locations)
    columns = [
        "total_crashes",
        "injury_crashes",
        "serious_property_crashes",
        "intoxicant_property_crashes",
        "other_property_crashes",
    ]
    frame = numeric(frame, columns)
    expected = pd.MultiIndex.from_product(
        [frame.state.unique(), list(locations.values())], names=["state", "location"]
    )
    missing = set(expected) - set(frame[["state", "location"]].itertuples(index=False, name=None))
    if (
        len(frame) != 67
        or missing != {("Berlin", "Interurbana sin autopistas")}
        or frame.location.isna().any()
        or frame.duplicated(["state", "location"]).any()
        or not frame.year.eq(2024).all()
    ):
        raise ValueError("Expected 17 areas with only Berlin rural location absent in source")
    frame["property_only_crashes"] = frame[columns[2:]].sum(axis=1, min_count=3)
    if not frame.total_crashes.eq(frame.injury_crashes + frame.property_only_crashes).all():
        raise ValueError("German damage classes do not reconcile")
    germany = frame[frame.state.eq("Deutschland")].set_index("location")
    states = frame[frame.state.ne("Deutschland")].groupby("location")[columns].sum(min_count=1)
    if not states.sort_index().equals(germany[columns].sort_index()):
        raise ValueError("State counts do not reconcile with Germany")
    summed = frame[frame.location.ne("Total")].groupby("state")[columns].sum()
    if not summed.sort_index().equals(
        frame[frame.location.eq("Total")].set_index("state")[columns].sort_index()
    ):
        raise ValueError("Road locations do not reconcile")
    frame["property_only_share_pct"] = frame.property_only_crashes / frame.total_crashes * 100
    frame = frame[
        ["year", "state", "location", *columns, "property_only_crashes", "property_only_share_pct"]
    ]
    frame = frame.set_index(["state", "location"]).reindex(expected).reset_index()
    frame["year"] = 2024
    if germany.loc["Total", "property_only_crashes"] != 2_221_996:
        raise ValueError("Audited German 2024 property-only total changed")
    for name, data in [("material_history", history), ("material_states", frame)]:
        data.to_csv(root / f"outputs/tables/{name}.csv", index=False)
        data.to_parquet(root / f"data/processed/{name}.parquet", index=False)
    report = {
        "status": "passed",
        "history_rows": len(history),
        "state_location_rows": len(frame),
        "property_only_2024": 2_221_996,
        "missing_source_keys": [list(key) for key in missing],
        "scope": "German police-recorded road crashes; 16 states, 2024; national history 2010–2024",
        "note": "Share among police-recorded crashes is not personal probability or insurance claim frequency. Unreported minor damage is absent. No Spain extrapolation. Berlin rural location absent in source is preserved as missing. Serious property, intoxicant property and other property-only classes partition property-only accidents.",
        "legend": "Source '-' retained as zero; '.' unavailable; no missing cell is filled with zero",
    }
    write_json(root / "outputs/tables/material_quality.json", report)
    return report
