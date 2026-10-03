"""Observed crash distributions; conditional severity never implies accident risk."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ebdi.cleaning.pipeline import dictionary


def breakdowns(root: Path, accidents: pd.DataFrame) -> pd.DataFrame:
    dimensions = [
        "MES",
        "HORA",
        "DIA_SEMANA",
        "TIPO_ACCIDENTE",
        "TIPO_VIA",
        "ZONA_AGRUPADA",
        "CONDICION_METEO",
        "CONDICION_ILUMINACION",
        "NUDO",
    ]
    parts = []
    for dimension in dimensions:
        grouped = (
            accidents.groupby(["year", dimension], dropna=False)
            .agg(
                injury_crashes=("ID_ACCIDENTE", "size"),
                fatalities=("TOTAL_MU30DF", "sum"),
                hospitalized=("TOTAL_HG30DF", "sum"),
                severe_crashes=("severe", "sum"),
            )
            .reset_index()
        )
        grouped["code"] = grouped[dimension].astype("Int64").astype("string").fillna("unknown")
        labels = {} if dimension in {"MES", "HORA"} else dictionary(root, dimension)
        grouped["label"] = grouped[dimension].map(labels).fillna(grouped["code"])
        grouped["dimension"] = dimension
        grouped["share_of_recorded_crashes"] = grouped.injury_crashes / grouped.groupby(
            "year"
        ).injury_crashes.transform("sum")
        grouped["conditional_severe_fraction"] = grouped.severe_crashes / grouped.injury_crashes
        grouped["small_sample"] = grouped.injury_crashes.lt(30)
        parts.append(grouped.drop(columns=dimension))
    result = pd.concat(parts, ignore_index=True)
    result.to_csv(root / "outputs/tables/crash_breakdowns.csv", index=False)
    return result


def figures(root: Path, breakdown: pd.DataFrame, latest_year: int) -> None:
    from ebdi.visualization.reports import save_figure

    months = breakdown.loc[breakdown.dimension.eq("MES")].copy()
    months["month"] = months.code.astype(int)
    fig, ax = plt.subplots(figsize=(10, 5))
    for year, group in months.groupby("year"):
        group = group.sort_values("month")
        ax.plot(group.month, group.injury_crashes, "o-", label=str(year))
    ax.set(
        title="When were injury crashes recorded?",
        xlabel="Month",
        ylabel="Recorded crashes · counts, no travel exposure",
        xticks=range(1, 13),
    )
    ax.legend(frameon=False)
    save_figure(fig, root / "outputs/figures/monthly_crashes")
    collision = breakdown.loc[
        breakdown.dimension.eq("TIPO_ACCIDENTE") & breakdown.year.eq(latest_year)
    ].sort_values("injury_crashes")
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(collision.label, collision.injury_crashes, color="#163b4c")
    ax.set(
        title=f"What kinds of injury crashes were recorded? · {latest_year}",
        xlabel="Recorded crashes · injury-only source; not insurance claims",
    )
    save_figure(fig, root / "outputs/figures/collision_distribution")
