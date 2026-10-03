"""Reconciled descriptive analysis of claims, police crashes and recorded persons."""

from pathlib import Path

import duckdb
import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import norm

from ebdi.metrics.rates import poisson_interval
from ebdi.utils.io import write_json

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def wilson(successes: pd.Series, trials: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Binomial model intervals for a conditional fraction; not census measurement error."""
    valid = trials.gt(0) & successes.ge(0) & successes.le(trials)
    n = trials.where(valid)
    p = successes / n
    z = norm.ppf(0.975)
    center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    radius = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    lower = ((center - radius).clip(lower=0) * 100).mask(valid & successes.eq(0), 0)
    upper = ((center + radius).clip(upper=1) * 100).mask(valid & successes.eq(trials), 100)
    return lower, upper


def extended_analysis(root: Path) -> dict:
    tables = root / "outputs/tables"
    collision = pd.read_csv(tables / "dgt_collision_types.csv")
    measures = ["crashes", "fatal_crashes", "fatalities", "hospitalized", "non_hospitalized"]
    leaves = collision[collision.category.ne("Total")].groupby(["year", "zone"])[measures].sum()
    published = collision[collision.category.eq("Total")].set_index(["year", "zone"])[measures]
    if not leaves.sort_index().equals(published.sort_index()):
        raise ValueError("Accident categories must partition published totals")
    zones = collision[collision.zone.ne("Total")].groupby(["year", "category"])[measures].sum()
    if not zones.sort_index().equals(
        collision[collision.zone.eq("Total")].set_index(["year", "category"])[measures].sort_index()
    ):
        raise ValueError("Accident zones must partition totals")
    collision["fatal_crash_pct"] = collision.fatal_crashes / collision.crashes * 100
    collision["lower"], collision["upper"] = wilson(collision.fatal_crashes, collision.crashes)
    parents = published.crashes
    collision["crash_share_pct"] = (
        collision.crashes
        / pd.MultiIndex.from_frame(collision[["year", "zone"]]).map(parents.to_dict())
        * 100
    )
    collision["small_sample"] = collision.crashes.lt(100)
    collision["is_total"] = collision.category.eq("Total")
    collision.to_csv(tables / "collision_analysis.csv", index=False)

    vehicles = pd.read_csv(tables / "dgt_vehicle_age.csv")
    components = (
        vehicles[vehicles.category.ne("Total")].groupby(["year", "zone", "age"]).vehicles.sum()
    )
    parent = vehicles[vehicles.category.eq("Total")].set_index(["year", "zone", "age"]).vehicles
    delta = components - parent
    gaps = delta[delta.ne(0)].to_dict()
    expected_gaps = {
        (2024, zone, age): -gap
        for zone, gap in [("Total", 87), ("Vías interurbanas", 24), ("Vías urbanas", 63)]
        for age in ["Se desconoce", "Total"]
    }
    if gaps != expected_gaps:
        raise ValueError(f"Unexpected vehicle-type source gaps: {gaps}")
    ages = vehicles[vehicles.age.ne("Total")].groupby(["year", "zone", "category"]).vehicles.sum()
    parents = vehicles[vehicles.age.eq("Total")].set_index(["year", "zone", "category"]).vehicles
    if not ages.sort_index().equals(parents.sort_index()):
        raise ValueError("Vehicle ages fail published totals")
    vehicles["share_all_pct"] = (
        vehicles.vehicles
        / pd.MultiIndex.from_frame(vehicles[["year", "zone", "category"]]).map(parents.to_dict())
        * 100
    )
    vehicles.to_csv(tables / "vehicle_age_analysis.csv", index=False)

    persons = pd.read_csv(tables / "dgt_demographics.csv")
    population = pd.read_csv(tables / "spain_age_population.csv")
    cells = (
        persons[
            (persons.role == "all_victims")
            & (persons.category == "Total")
            & persons.sex.isin(["M", "F"])
            & persons.age_band.ne("Desconocida")
        ]
        .groupby(["year", "sex", "age_band"], as_index=False)
        .fatalities.sum()
    )
    cells = cells.merge(population, on=["year", "sex", "age_band"], validate="one_to_one")
    cells["fatalities_per_million"] = cells.fatalities / cells.population * 1_000_000
    cells["lower"], cells["upper"] = poisson_interval(cells.fatalities, cells.population, 1_000_000)
    cells.to_csv(tables / "spain_age_sex_rates.csv", index=False)

    claims = pd.read_csv(tables / "ncid_ultimate.csv")
    changes = []
    for category, frame in claims.groupby("category"):
        baseline = frame[frame.year.eq(2019)].iloc[0]
        for _, row in frame.iterrows():
            changes.append(
                {
                    "year": int(row.year),
                    "category": category,
                    **{
                        f"{key}_change_2019_pct": (row[key] / baseline[key] - 1) * 100
                        if baseline[key] > 0
                        else None
                        for key in [
                            "ultimate_claims",
                            "frequency_per_1000_all_policies",
                            "mean_cost_eur",
                            "mean_cost_2024_eur",
                            "cost_per_policy_eur",
                        ]
                    },
                }
            )
    pd.DataFrame(changes).to_csv(tables / "ncid_changes.csv", index=False)
    current = claims[claims.year.eq(2024)].set_index("category").to_dict(orient="index")
    material = pd.read_csv(tables / "material_history.csv")
    latest = material[material.year.eq(2024)].iloc[0]
    rates = pd.read_csv(tables / "spain_sex_rates.csv")
    recent = rates[rates.year.eq(2024)].set_index("sex").to_dict(orient="index")
    report = {
        "status": "passed",
        "claims_2024": {
            "damage_ultimate_estimate": float(current["Daños materiales"]["ultimate_claims"]),
            "damage_frequency_per_1000_portfolio": float(
                current["Daños materiales"]["frequency_per_1000_all_policies"]
            ),
            "damage_mean_cost_eur": float(current["Daños materiales"]["mean_cost_eur"]),
        },
        "germany_2024": {
            "property_only_crashes": int(latest.property_only_crashes),
            "share_recorded_crashes_pct": float(latest.property_only_share_pct),
        },
        "spain_2024": {
            "male_female_crude_rate_ratio": float(
                recent["M"]["crude_per_million"] / recent["F"]["crude_per_million"]
            ),
            "male_female_standardized_rate_ratio": float(
                recent["M"]["age_standardized_per_million"]
                / recent["F"]["age_standardized_per_million"]
            ),
        },
        "checks": [
            "21 accident types partition each year/zone",
            "urban + interurban accident counts reconcile",
            "vehicle ages reconcile; 2024 vehicle-type Total includes 87 counts in an unlabelled workbook column",
            "single-age populations reconcile; fixed common 2024 weights",
            "claim costs decomposed into frequency × mean cost without mixing settlement cohorts",
        ],
        "vehicle_type_source_note": "2024 table 8.3 has an unlabelled numeric column: 24 interurban + 63 urban counts, all unknown age. Published Total exceeds labelled vehicle-type components by 87. Counts retained in Total; no invented type or forced redistribution.",
        "interpretation": "Descriptive associations, no fault attribution, causal effect or personal-risk prediction. Wilson/Poisson intervals are conditional model intervals, not uncertainty about enumerated administrative totals. Ultimate estimates have no count intervals. Age adjustment controls only the five recorded age bands; no distance, driving exposure or socioeconomic controls.",
    }
    write_json(tables / "extended_analysis.json", report)
    # Shareable standalone scientific figures; same data as the frontend.
    plt.rcParams.update(
        {
            "figure.facecolor": "#fffef8",
            "axes.facecolor": "#fffef8",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
        }
    )
    figures = root / "outputs/figures"

    def save(name: str, title: str, ylabel: str, note: str) -> None:
        plt.title(title, loc="left", pad=15)
        plt.ylabel(ylabel)
        plt.grid(axis="y", alpha=0.15)
        plt.gcf().text(0.12, 0.02, note, fontsize=8)
        plt.tight_layout(rect=(0, 0.06, 1, 1))
        plt.savefig(figures / f"{name}.svg")
        plt.close()

    plt.figure(figsize=(10, 5))
    for category, color in [("Daños materiales", "#355e50"), ("Lesiones", "#b87736")]:
        frame = claims[claims.category.eq(category)].sort_values("year")
        plt.plot(frame.year, frame.frequency_per_1000_all_policies, label=category, color=color)
    plt.legend()
    save(
        "ncid_frequency",
        "Irlanda · frecuencia estimada por año de ocurrencia",
        "Reclamaciones / 1.000 pólizas-año de cartera",
        "NCID Report 7 · UltData 2010–2024 · incluye nulos; estimaciones revisables. Javier Saguar.",
    )
    plt.figure(figsize=(10, 5))
    damage = claims[claims.category.eq("Daños materiales")].sort_values("year")
    for key, title in [
        ("mean_cost_eur", "Euros nominales"),
        ("mean_cost_2024_eur", "Euros de 2024"),
    ]:
        plt.plot(damage.year, damage[key], label=title)
    plt.legend()
    save(
        "ncid_costs",
        "Irlanda · coste medio estimado de daños materiales",
        "Euros por reclamación",
        "NCID + Eurostat HICP general de Irlanda; no índice específico de reparación. Javier Saguar.",
    )
    plt.figure(figsize=(10, 5))
    plt.plot(material.year, material.property_only_share_pct, color="#355e50")
    save(
        "germany_property_share",
        "Alemania · accidentes con solo daños materiales",
        "% de accidentes registrados por la policía",
        "Destatis 2010–2024 · daños no denunciados fuera de cobertura; no extrapolar a España. Javier Saguar.",
    )
    plt.figure(figsize=(10, 5))
    for sex, title in [("M", "Hombres"), ("F", "Mujeres")]:
        frame = rates[rates.sex.eq(sex)].sort_values("year")
        plt.plot(frame.year, frame.crude_per_million, label=f"{title} · bruta")
        plt.plot(
            frame.year,
            frame.age_standardized_per_million,
            linestyle="--",
            label=f"{title} · ajustada por edad",
        )
    plt.xticks([2022, 2023, 2024])
    plt.legend()
    save(
        "spain_sex_mortality",
        "España · mortalidad por sexo registrado",
        "Fallecidos / millón de habitantes del sexo",
        "DGT + Eurostat · ajuste común España 2024, cinco edades; no mide culpa ni riesgo por km. Javier Saguar.",
    )
    plt.figure(figsize=(10, 7))
    selected = (
        collision[(collision.year == 2024) & (collision.zone == "Total") & ~collision.is_total]
        .nlargest(10, "crashes")
        .sort_values("crashes")
    )
    plt.barh(selected.category, selected.crashes, color="#355e50")
    save(
        "spain_collision_categories",
        "España · diez tipos con más siniestros registrados en 2024",
        "Siniestros con víctimas",
        "DGT tabla 1.3 · categorías excluyentes; selección por volumen, no por riesgo. Javier Saguar.",
    )
    # Separate grains and bases remain separate, queryable tables.
    names = [
        "ncid_ultimate",
        "ncid_settled",
        "ncid_changes",
        "material_history",
        "material_states",
        "dgt_demographics",
        "collision_analysis",
        "vehicle_age_analysis",
        "spain_sex_rates",
        "spain_age_sex_rates",
        "spain_age_population",
        "europe_sex_users",
    ]
    with duckdb.connect(str(root / "data/processed/ebdi.duckdb")) as connection:
        for name in names:
            frame = pd.read_csv(tables / f"{name}.csv")
            frame.to_parquet(root / f"data/processed/{name}.parquet", index=False)
            connection.register("audited_frame", frame)
            connection.execute(f'CREATE OR REPLACE TABLE "{name}" AS SELECT * FROM audited_frame')
            connection.unregister("audited_frame")
    return report
