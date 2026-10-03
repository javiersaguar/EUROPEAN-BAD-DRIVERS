"""Separate 2010–2024 mortality context; never fabricates historic injury counts."""

import json
from pathlib import Path

import pandas as pd

from ebdi.ingestion.download import raw_path
from ebdi.ingestion.europe import EU27, decode_jsonstat
from ebdi.metrics.rates import poisson_interval, rate


def process_history(root: Path) -> pd.DataFrame:
    source = json.loads(raw_path(root, "eurostat_fatalities_history").read_text(encoding="utf-8"))
    deaths = decode_jsonstat(source)
    population = decode_jsonstat(
        json.loads(raw_path(root, "eurostat_population_history").read_text(encoding="utf-8"))
    )
    keys = pd.MultiIndex.from_product(
        [sorted(EU27), [str(y) for y in range(2010, 2025)]], names=["geo", "time"]
    ).to_frame(index=False)
    frame = keys.merge(
        deaths[["geo", "time", "value", "status"]].rename(
            columns={"value": "fatalities", "status": "fatalities_status"}
        ),
        on=["geo", "time"],
        how="left",
        validate="one_to_one",
    )
    frame = frame.merge(
        population[["geo", "time", "value", "status"]].rename(
            columns={"value": "population", "status": "population_status"}
        ),
        on=["geo", "time"],
        how="left",
        validate="one_to_one",
    )
    if frame.fatalities.dropna().lt(0).any() or frame.population.dropna().le(0).any():
        raise ValueError("Invalid historic death/population observations")
    frame["year"] = frame.time.astype(int)
    frame["country"] = frame.geo.map(source["dimension"]["geo"]["category"]["label"])
    frame["fatalities_per_million_population"] = rate(frame.fatalities, frame.population, 1_000_000)
    frame["lower"], frame["upper"] = poisson_interval(frame.fatalities, frame.population, 1_000_000)
    frame["included"] = frame.fatalities.notna() & frame.population.notna()
    frame["definition"] = (
        "30-day road deaths; current EU-27 cohort retrospectively; population on 1 January; flags retained"
    )
    frame.drop(columns="time").to_csv(root / "outputs/tables/europe_history.csv", index=False)
    return frame
