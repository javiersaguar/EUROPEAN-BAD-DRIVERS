"""Audited person-level aggregate tables; never assign a sex to a crash."""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from ebdi.ingestion.download import raw_path
from ebdi.ingestion.europe import EU27, decode_jsonstat
from ebdi.metrics.rates import poisson_interval, rate
from ebdi.utils.io import write_json

SEX = {"Hombre": "M", "Mujer": "F", "Se desconoce": "UNK", "Total": "T"}
AGE_BANDS = ["0–17", "18–24", "25–44", "45–64", "65+", "Desconocida"]


def age_band(label: str) -> str:
    if label == "Se desconoce":
        return "Desconocida"
    digits = [int(x) for x in re.findall(r"\d+", label)]
    if not digits:
        raise ValueError(f"Unknown age label: {label}")
    low = digits[0]
    high = digits[-1] if not label.startswith("Más") else 150
    for lower, upper, band in [
        (0, 17, "0–17"),
        (18, 24, "18–24"),
        (25, 44, "25–44"),
        (45, 64, "45–64"),
        (65, 150, "65+"),
    ]:
        if lower <= low <= high <= upper:
            return band
    raise ValueError(f"Age category crosses analysis bands: {label}")


def user_category(label: str) -> str:
    label = " ".join(label.split())
    if label in ["Total", "Peatón", "Bicicleta", "VMP", "Ciclomotor", "Motocicleta"]:
        return label
    if label.startswith("Turismo"):
        return "Turismo"
    if label == "Furgoneta":
        return label
    if label.startswith(("Camión", "Tractocamión", "Vehículo articulado")):
        return "Vehículo pesado"
    if label.startswith("Autobús"):
        return "Autobús"
    if label == "Se desconoce":
        return "Desconocido"
    if label.startswith(("Maquinaria", "Cuadriciclo", "Tren/metro/tranvía", "Otro vehículo")):
        return "Otros"
    raise ValueError(f"Unmapped road-user type: {label}")


def extract_person_table(
    path: Path, year: int, sheet: str, role: str, zone: str, known_gaps: list[dict] | None = None
) -> pd.DataFrame:
    table = pd.read_excel(path, sheet_name=sheet, header=None, engine="calamine")
    if str(year) not in " ".join(table.iloc[:2, 0].dropna().astype(str)):
        raise ValueError("DGT table year changed")
    involved = role == "drivers_involved"
    header_row = 3 if year == 2022 and involved else 2
    start, step = (header_row + 1, 1) if involved else (4, 3)
    headings = table.iloc[header_row]
    rows = []
    age = ""
    for i in range(start, len(table)):
        if pd.notna(table.iloc[i, 0]):
            age = str(table.iloc[i, 0]).strip()
        sex_label = str(table.iloc[i, 1]).strip()
        if sex_label not in SEX:
            raise ValueError(f"Unrecognized recorded sex: {sex_label} in {year}/{sheet}, row {i}")
        for j in range(2, table.shape[1], step):
            user = " ".join(str(headings.iloc[j]).split())
            values = pd.to_numeric(table.iloc[i, j : j + step], errors="raise")
            missing = values.isna()
            allowed_missing = year == 2024 and (
                (sheet == "TABLA 4.1.U" and user == "Bicicleta" and missing.all())
                or (sheet == "TABLA 4.2.I" and i == 58 and user == "Motocicleta" and missing.all())
            )
            if (
                (missing.any() and not allowed_missing)
                or not np.isfinite(values.dropna()).all()
                or values.dropna().lt(0).any()
                or values.dropna().mod(1).ne(0).any()
            ):
                raise ValueError("DGT person cells must be observed nonnegative integers")
            row = {
                "year": year,
                "zone": zone,
                "role": role,
                "age_source": age,
                "sex": SEX[sex_label],
                "user_source": user,
                "source_sheet": sheet,
                "source_row": i + 1,
            }
            if involved:
                row["involved"] = values.iloc[0]
            else:
                row.update(
                    dict(
                        zip(["fatalities", "hospitalized", "non_hospitalized"], values, strict=True)
                    )
                )
            rows.append(row)
    detail = pd.DataFrame(rows)
    source_notes = []
    missing_cells = (
        detail[["involved"] if involved else ["fatalities", "hospitalized", "non_hospitalized"]]
        .isna()
        .sum()
        .sum()
    )
    if missing_cells:
        source_notes.append(
            {
                "year": year,
                "sheet": sheet,
                "missing_cells": int(missing_cells),
                "note": "Original blank cells retained as missing. 2024 urban all-victim bicycle cells are absent; one interurban age 70–74 total motorcyclist-involvement cell is absent. No reconstruction from other tables.",
            }
        )
    known = known_gaps or []
    measures = ["involved"] if involved else ["fatalities", "hospitalized", "non_hospitalized"]

    def complete_sum(x):
        return x.sum() if x.notna().all() else np.nan

    for measure in measures:
        sex_parts = (
            detail[detail.sex.ne("T")]
            .groupby(["age_source", "user_source"])[measure]
            .agg(complete_sum)
        )
        totals = detail[detail.sex.eq("T")].set_index(["age_source", "user_source"])[measure]
        age_parts = (
            detail[detail.age_source.ne("Total")]
            .groupby(["sex", "user_source"])[measure]
            .agg(complete_sum)
        )
        age_totals = detail[detail.age_source.eq("Total")].set_index(["sex", "user_source"])[
            measure
        ]
        for axis, parts, published in [("sex", sex_parts, totals), ("age", age_parts, age_totals)]:
            paired = pd.concat(
                [parts.rename("parts"), published.rename("published")], axis=1
            ).dropna()
            if not paired.parts.eq(paired.published).all():
                raise ValueError(f"{axis} partitions fail in {year}/{sheet}/{measure}")
        user_parts = (
            detail[detail.user_source.ne("Total")]
            .groupby(["sex", "age_source"])[measure]
            .agg(complete_sum)
        )
        user_totals = detail[detail.user_source.eq("Total")].set_index(["sex", "age_source"])[
            measure
        ]
        delta = (user_parts - user_totals).dropna()
        differences = delta[delta.ne(0)].to_dict()
        expected = {
            (SEX[x["sex"]], x["age"]): x["gap"]
            for x in known
            if x["year"] == year and x["sheet"] == sheet and x["measure"] == measure
        }
        if differences != expected:
            raise ValueError(
                f"Unexpected road-user gaps in {year}/{sheet}/{measure}: {differences}"
            )
        if differences:
            source_notes.append(
                {
                    "year": year,
                    "sheet": sheet,
                    "measure": measure,
                    "published_components_minus_total": int(differences.get(("T", "Total"), 0)),
                    "note": "Original 2024 interurban driver-victim components exceed the published Total. Both retained; exact cell differences audited in configs/dgt_known_gaps.json. Do not normalize vehicle components to the Total.",
                }
            )
    detail.attrs["source_notes"] = source_notes
    return detail


def process_persons(root: Path) -> dict:
    details, collisions, vehicle_ages = [], [], []
    known_gaps = json.loads((root / "configs/dgt_known_gaps.json").read_text(encoding="utf-8"))
    for year in [2022, 2023, 2024]:
        path = raw_path(root, f"dgt_demographics_{year}")
        for zone, suffix in [("Interurbana", "I"), ("Urbana", "U")]:
            for prefix, role in [
                ("4.1", "all_victims"),
                ("4.1.1", "drivers_victims"),
                ("4.2", "drivers_involved"),
            ]:
                details.append(
                    extract_person_table(
                        path, year, f"TABLA {prefix}.{suffix}", role, zone, known_gaps
                    )
                )
        collision = pd.read_excel(path, sheet_name="TABLA 1.3", header=None, engine="calamine")
        for i in range(4, len(collision)):
            for zone, col in [("Interurbana", 1), ("Urbana", 6), ("Total", 11)]:
                values = pd.to_numeric(collision.iloc[i, col : col + 5], errors="raise")
                collisions.append(
                    {
                        "year": year,
                        "zone": zone,
                        "category": str(collision.iloc[i, 0]).strip(),
                        **dict(
                            zip(
                                [
                                    "crashes",
                                    "fatal_crashes",
                                    "fatalities",
                                    "hospitalized",
                                    "non_hospitalized",
                                ],
                                values.astype(int),
                                strict=True,
                            )
                        ),
                        "source_sheet": "TABLA 1.3",
                    }
                )
        vehicle = pd.read_excel(path, sheet_name="TABLA 8.3", header=None, engine="calamine")
        zone = ""
        for i in range(3, len(vehicle)):
            if pd.notna(vehicle.iloc[i, 0]):
                zone = str(vehicle.iloc[i, 0]).strip()
            for j in range(2, 12):  # column 12 is an unlabelled workbook artifact
                value = pd.to_numeric(vehicle.iloc[i, j], errors="raise")
                if pd.isna(value) or value < 0 or value % 1:
                    raise ValueError("Invalid vehicle age count")
                vehicle_ages.append(
                    {
                        "year": year,
                        "zone": zone,
                        "age": str(vehicle.iloc[i, 1]).strip(),
                        "category": " ".join(str(vehicle.iloc[2, j]).split()),
                        "vehicles": int(value),
                        "source_sheet": "TABLA 8.3",
                    }
                )
    source_notes = [note for frame in details for note in frame.attrs.get("source_notes", [])]
    detail = pd.concat(details, ignore_index=True)
    detail.to_parquet(root / "data/processed/dgt_persons_detail.parquet", index=False)
    detail.to_csv(root / "outputs/tables/dgt_persons_detail.csv", index=False)
    chosen = detail.loc[detail.sex.ne("T") & detail.age_source.ne("Total")].copy()
    chosen["age_band"] = chosen.age_source.map(age_band)
    chosen["category"] = chosen.user_source.map(user_category)
    measures = ["fatalities", "hospitalized", "non_hospitalized", "involved"]
    persons = chosen.groupby(
        ["year", "zone", "role", "age_band", "sex", "category"], as_index=False
    )[measures].sum(min_count=1)
    persons["casualties"] = persons[["fatalities", "hospitalized", "non_hospitalized"]].sum(
        axis=1, min_count=3
    )
    collision = pd.DataFrame(collisions)
    # The 21 published accident types form a partition; Total is their parent.
    published = collision[collision.category.eq("Total") & collision.zone.eq("Total")].set_index(
        "year"
    )
    national = pd.read_csv(root / "outputs/tables/national_totals.csv").set_index("year")
    for measure, original in [("crashes", "injury_crashes"), ("fatalities", "fatalities")]:
        if not published[measure].eq(national[original]).all():
            raise ValueError("Annual DGT statistics do not match crash microdata")
    sex_totals = (
        detail[
            (detail.role == "all_victims")
            & detail.age_source.eq("Total")
            & detail.user_source.eq("Total")
            & detail.sex.eq("T")
        ]
        .groupby("year")
        .fatalities.sum()
    )
    if not sex_totals.eq(national.fatalities).all():
        raise ValueError("Person deaths do not reconcile with national crash deaths")
    for name, frame in [
        ("dgt_demographics", persons),
        ("dgt_collision_types", collision),
        ("dgt_vehicle_age", pd.DataFrame(vehicle_ages)),
    ]:
        frame.to_csv(root / f"outputs/tables/{name}.csv", index=False)
        frame.to_parquet(root / f"data/processed/{name}.parquet", index=False)
    quality = {
        "status": "passed_with_source_note",
        "source_notes": source_notes,
        "rows": len(persons),
        "detail_rows": len(detail),
        "years": [2022, 2023, 2024],
        "sex_categories": list(SEX.values()),
        "age_and_sex_and_user_partitions": "Complete sex/age partitions exact. Explicit original gaps and missing cells retained; checks involving missing cells are unavailable.",
        "geography": "Spain national by urban/interurban zone; no person-sex province data",
        "roles": ["all_victims", "drivers_victims", "drivers_involved"],
        "note": "Involved drivers are not responsible drivers; a crash can involve multiple sexes. Sex categories are administrative, not gender identity. No non-crash or travel-exposure controls.",
    }
    write_json(root / "outputs/tables/demographics_quality.json", quality)
    return quality


def process_europe_sex(root: Path) -> dict:
    source = json.loads(raw_path(root, "eurostat_sex_users").read_text(encoding="utf-8"))
    deaths = decode_jsonstat(source)
    population = decode_jsonstat(
        json.loads(raw_path(root, "eurostat_sex_population").read_text(encoding="utf-8"))
    )
    dimensions = [
        sorted(EU27),
        [str(y) for y in range(2010, 2025)],
        ["T", "M", "F", "UNK"],
        ["TOTAL", "DRIV", "PAS", "PED", "UNK"],
    ]
    keys = ["geo", "time", "sex", "pers_cat"]
    panel = (
        pd.MultiIndex.from_product(dimensions, names=keys)
        .to_frame(index=False)
        .merge(deaths[keys + ["value", "status"]], how="left", on=keys, validate="one_to_one")
        .rename(columns={"value": "fatalities", "status": "fatalities_status"})
    )
    panel = panel.merge(
        population[["geo", "time", "sex", "value", "status"]].rename(
            columns={"value": "population", "status": "population_status"}
        ),
        how="left",
        on=["geo", "time", "sex"],
        validate="many_to_one",
    )
    panel["year"] = panel.time.astype(int)
    panel["country"] = panel.geo.map(source["dimension"]["geo"]["category"]["label"])
    panel["fatalities_per_million"] = rate(panel.fatalities, panel.population, 1_000_000)
    panel["lower"], panel["upper"] = poisson_interval(panel.fatalities, panel.population, 1_000_000)
    panel["included"] = panel.fatalities.notna() & panel.population.notna()
    panel.drop(columns="time").to_csv(root / "outputs/tables/europe_sex_users.csv", index=False)
    return {
        "rows": len(panel),
        "observed_death_cells": int(panel.fatalities.notna().sum()),
        "included_rate_cells": int(panel.included.sum()),
        "note": "Population of the recorded sex; crude mortality burden, not individual driving risk. Unknown sex has no population denominator. National metadata and revision flags retained; categories are nested in TOTAL.",
    }


def standardize_spain(root: Path) -> pd.DataFrame:
    population = decode_jsonstat(
        json.loads(raw_path(root, "eurostat_es_age_population").read_text(encoding="utf-8"))
    )
    published_totals = (
        population[population.sex.isin(["M", "F"]) & population.age.eq("TOTAL")]
        .set_index(["time", "sex"])
        .value
    )
    unknown = population[population.sex.isin(["M", "F"]) & population.age.eq("UNK")]
    if unknown.value.ne(0).any():
        raise ValueError("Unknown population age prevents exhaustive standardization")
    population = population[
        population.sex.isin(["M", "F"]) & ~population.age.isin(["TOTAL", "UNK"])
    ].copy()
    if (
        not population.groupby(["time", "sex"])
        .value.sum()
        .sort_index()
        .equals(published_totals.sort_index())
    ):
        raise ValueError("Single-age populations do not match their published totals")
    population["age_num"] = population.age.map(
        lambda a: (
            0
            if a == "Y_LT1"
            else 100
            if a == "Y_OPEN"
            else int(a[1:])
            if re.fullmatch(r"Y\d+", a)
            else np.nan
        )
    )
    if population.age_num.isna().any():
        raise ValueError(
            f"Unmapped population ages: {population[population.age_num.isna()].age.unique()}"
        )
    population["age_band"] = population.age_num.map(lambda a: age_band(str(int(a))))
    population["year"] = population.time.astype(int)
    counts = (
        population.groupby(["year", "sex", "age_band"])["value"]
        .sum()
        .rename("population")
        .reset_index()
    )
    statuses = (
        population.assign(status=population.status.fillna(""))
        .groupby(["year", "sex", "age_band"])["status"]
        .agg(lambda x: "|".join(sorted(set(x) - {""})))
        .rename("population_status")
        .reset_index()
    )
    counts = counts.merge(statuses, on=["year", "sex", "age_band"], validate="one_to_one")
    weights = counts[counts.year.eq(2024)].groupby("age_band").population.sum()
    weights = weights / weights.sum()
    persons = pd.read_csv(root / "outputs/tables/dgt_demographics.csv")
    subset = persons[
        (persons.role == "all_victims")
        & (persons.category == "Total")
        & persons.sex.isin(["M", "F"])
    ]
    sums = subset.groupby(["year", "sex", "age_band"], as_index=False).fatalities.sum()
    matched = sums.merge(counts, how="left", on=["year", "sex", "age_band"], validate="one_to_one")
    results = []
    for (year, sex), frame in matched.groupby(["year", "sex"]):
        known = frame[frame.age_band.ne("Desconocida")]
        if len(known) != 5 or known.population.isna().any() or known.population.le(0).any():
            raise ValueError("Incomplete sex/age standardization cells")
        count, exposure = frame.fatalities.sum(), known.population.sum()
        low, high = poisson_interval(pd.Series([count]), pd.Series([exposure]), 1_000_000)
        results.append(
            {
                "year": int(year),
                "sex": sex,
                "fatalities": count,
                "population": exposure,
                "crude_per_million": count / exposure * 1_000_000,
                "lower": low.iloc[0],
                "upper": high.iloc[0],
                "age_standardized_per_million": (
                    known.fatalities / known.population * known.age_band.map(weights)
                ).sum()
                * 1_000_000,
                "unknown_age_deaths": frame[frame.age_band.eq("Desconocida")].fatalities.sum(),
                "standard": "Fixed Spain M+F 2024 population, five exhaustive age bands; standardized point estimate excludes unknown age. Crude rates include unknown age of known sex.",
            }
        )
    result = pd.DataFrame(results)
    result.to_csv(root / "outputs/tables/spain_sex_rates.csv", index=False)
    counts["standard_weight_2024"] = counts.age_band.map(weights)
    counts.to_csv(root / "outputs/tables/spain_age_population.csv", index=False)
    return result


def process_demographics(root: Path) -> dict:
    report = process_persons(root)
    report["europe"] = process_europe_sex(root)
    report["standardized_rows"] = len(standardize_spain(root))
    write_json(root / "outputs/tables/demographics_quality.json", report)
    return report
