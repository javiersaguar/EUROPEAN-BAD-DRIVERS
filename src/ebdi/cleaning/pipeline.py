"""Build audited facts and a province/year analytical panel."""

import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from ebdi.cleaning.geography import checked_join, normalized_name, province_code
from ebdi.ingestion.download import raw_path
from ebdi.ingestion.europe import EU27, decode_jsonstat
from ebdi.metrics.rates import add_rates, poisson_interval, rate
from ebdi.utils.io import read_yaml, write_json
from ebdi.validation.quality import validate_accidents


def dictionary(root: Path, sheet: str) -> dict[int, str]:
    df = pd.read_excel(
        raw_path(root, "dgt_dictionary"), sheet_name=sheet, header=1, engine="calamine"
    )
    numeric = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    valid = numeric.notna()
    return dict(
        zip(
            numeric[valid].astype(int),
            df.loc[valid].iloc[:, 1].astype(str).str.strip(),
            strict=True,
        )
    )


def stocks(root: Path, kind: str, year: int, geography: pd.DataFrame) -> pd.DataFrame:
    sheet = "V_4" if kind == "vehicles" else "P_6_1_1_10"
    df = pd.read_excel(
        raw_path(root, f"dgt_{kind}_{year}"), sheet_name=sheet, header=2, engine="calamine"
    )
    total_col = df.columns[9] if kind == "vehicles" else df.columns[3]
    column = "registered_vehicles" if kind == "vehicles" else "licensed_drivers"
    df = df.iloc[:, [0, 9 if kind == "vehicles" else 3]].copy()
    df.columns = ["source_name", column]
    keys = {
        normalized_name(n): c
        for c, n in geography[["province_code", "province"]].itertuples(index=False, name=None)
    }
    df["province_code"] = df["source_name"].astype(str).map(normalized_name).map(keys)
    unmatched = df.loc[
        df["province_code"].isna() & pd.to_numeric(df[column], errors="coerce").notna()
    ]
    if any(normalized_name(str(n)) != "total" for n in unmatched["source_name"]):
        raise ValueError(
            f"{kind}/{year}: unknown geographic labels {unmatched.source_name.tolist()}"
        )
    provinces = df.loc[df["province_code"].notna()].copy()
    if len(provinces) != 52 or provinces["province_code"].duplicated().any():
        raise ValueError(f"{kind}/{year}: expected 52 unique provinces")
    provinces[column] = pd.to_numeric(provinces[column], errors="raise")
    if provinces[column].isna().any() or provinces[column].le(0).any():
        raise ValueError(f"{kind}/{year}: missing/nonpositive exposure")
    total_row = df.loc[df["source_name"].astype(str).map(normalized_name).eq("total"), column]
    if len(total_row) != 1 or int(total_row.iloc[0]) != int(provinces[column].sum()):
        raise ValueError(f"{kind}/{year}: provincial totals do not reconcile in {total_col}")
    provinces["year"] = year
    return provinces[["province_code", "year", column]]


def population(root: Path, years: list[int]) -> pd.DataFrame:
    df = pd.read_csv(
        raw_path(root, "ine_population_67988"), sep="\t", encoding="utf-8-sig", dtype=str
    )
    df = df.loc[df["Provincias"].notna() & df["Sexo"].eq("Total")].copy()
    df["province_code"] = df["Provincias"].str.extract(r"^(\d{2})", expand=False)
    df["year"] = df["Periodo"].astype(int)
    df["population"] = pd.to_numeric(df["Total"].str.replace(".", "", regex=False), errors="raise")
    df["community_code"] = df["Comunidades y Ciudades Autónomas"].str[:2]
    df["community"] = df["Comunidades y Ciudades Autónomas"].str[3:]
    df = df.loc[df.year.isin(years)]
    if df[["province_code", "population"]].isna().any().any() or df.population.le(0).any():
        raise ValueError("Invalid INE province population")
    if len(df) != 52 * len(years) or df.duplicated(["province_code", "year"]).any():
        raise ValueError("INE coverage or duplicate keys changed")
    return df[["province_code", "year", "population", "community_code", "community"]]


def geometry(root: Path, geo: pd.DataFrame) -> None:
    source = json.loads(raw_path(root, "gisco_nuts3").read_text(encoding="utf-8"))
    keys = {
        normalized_name(n): c
        for c, n in geo[["province_code", "province"]].itertuples(index=False, name=None)
    }
    names = dict(geo[["province_code", "province"]].itertuples(index=False, name=None))
    islands = {
        "ES703": "38",
        "ES704": "35",
        "ES705": "35",
        "ES706": "38",
        "ES707": "38",
        "ES708": "35",
        "ES709": "38",
    }
    polygons: dict[str, list[Any]] = {}
    crosswalk = []
    for feature in source["features"]:
        props = feature["properties"]
        if props["CNTR_CODE"] != "ES":
            continue
        nuts = props["NUTS_ID"]
        code = (
            "07"
            if nuts.startswith("ES53")
            else islands.get(nuts, keys.get(normalized_name(props["NUTS_NAME"])))
        )
        if code is None:
            raise ValueError(f"Unmatched GISCO NUTS3: {nuts} {props['NUTS_NAME']}")
        geo_type = feature["geometry"]["type"]
        coords = feature["geometry"]["coordinates"]
        if geo_type not in {"Polygon", "MultiPolygon"}:
            raise ValueError(f"Unexpected GISCO geometry {geo_type}")
        polygons.setdefault(code, []).extend([coords] if geo_type == "Polygon" else coords)
        crosswalk.append({"nuts_id": nuts, "nuts_name": props["NUTS_NAME"], "province_code": code})
    if set(polygons) != set(geo.province_code):
        raise ValueError("GISCO-to-province crosswalk does not cover all 52 provinces")
    features = [
        {
            "type": "Feature",
            "properties": {"province_code": c, "province": names[c]},
            "geometry": {"type": "MultiPolygon", "coordinates": p},
        }
        for c, p in sorted(polygons.items())
    ]
    write_json(
        root / "data/processed/spain_provinces.geojson",
        {"type": "FeatureCollection", "features": features},
    )
    pd.DataFrame(crosswalk).to_csv(root / "outputs/tables/geographic_crosswalk.csv", index=False)


def europe(root: Path) -> pd.DataFrame:
    fatalities = decode_jsonstat(
        json.loads(raw_path(root, "eurostat_fatalities").read_text(encoding="utf-8"))
    )
    residents = decode_jsonstat(
        json.loads(raw_path(root, "eurostat_population").read_text(encoding="utf-8"))
    )
    left = fatalities.loc[fatalities.geo.isin(EU27), ["geo", "time", "value", "status"]].rename(
        columns={"value": "fatalities", "status": "fatalities_status"}
    )
    right = residents[["geo", "time", "value", "status"]].rename(
        columns={"value": "population", "status": "population_status"}
    )
    df = checked_join(left, right, ["geo", "time"])
    if (
        df.duplicated(["geo", "time"]).any()
        or df[["fatalities", "population"]].isna().any().any()
        or df.population.le(0).any()
        or df.fatalities.lt(0).any()
    ):
        raise ValueError("Invalid European observations")
    years = read_yaml(root / "configs/sources.yaml")["years"]
    expected = {(country, str(year)) for country in EU27 for year in years}
    if set(df[["geo", "time"]].itertuples(index=False, name=None)) != expected:
        raise ValueError("European country/year coverage changed; expected EU-27 for audited years")
    labels = json.loads(raw_path(root, "eurostat_fatalities").read_text(encoding="utf-8"))[
        "dimension"
    ]["geo"]["category"]["label"]
    df["country"] = df.geo.map(labels)
    df["year"] = df.time.astype(int)
    df["fatalities_per_million_population"] = rate(df.fatalities, df.population, 1_000_000)
    df["lower"], df["upper"] = poisson_interval(df.fatalities, df.population, 1_000_000)
    df["comparability"] = "30-day fatality burden; population proxy; national reporting notes apply"
    return df.drop(columns="time")


def process(root: Path) -> dict[str, Any]:
    years = read_yaml(root / "configs/sources.yaml")["years"]
    out = root / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    geo = pd.DataFrame(
        [
            {"province_code": province_code(c), "province": n}
            for c, n in dictionary(root, "COD_PROVINCIA").items()
        ]
    )
    pop = population(root, years)
    geo = checked_join(
        geo,
        pop.loc[pop.year.eq(max(years)), ["province_code", "community_code", "community"]],
        ["province_code"],
    )
    schema = json.loads((root / "configs/accident_schema.json").read_text(encoding="utf-8"))[
        "columns"
    ]
    categorical = [
        "TIPO_ACCIDENTE",
        "TIPO_VIA",
        "ZONA_AGRUPADA",
        "ZONA",
        "TITULARIDAD_VIA",
        "CONDICION_METEO",
        "CONDICION_ILUMINACION",
        "CONDICION_FIRME",
        "NUDO",
    ]
    allowed = {c: set(dictionary(root, c)) for c in categorical}
    crashes, reports = [], []
    for year in years:
        print(f"Processing DGT {year}...", flush=True)
        df = pd.read_excel(raw_path(root, f"dgt_accidents_{year}"), engine="calamine")
        reports.append(validate_accidents(df, year, schema, allowed))
        df["province_code"] = df.COD_PROVINCIA.map(province_code)
        df["year"] = df.ANYO.astype(int)
        df["urban"] = df.ZONA_AGRUPADA.eq(2)
        df["rear_lateral"] = df.TIPO_ACCIDENTE.isin([2, 3, 4])
        df["unknown_collision"] = df.TIPO_ACCIDENTE.isna()
        df["severe"] = df.TOTAL_MU30DF.gt(0) | df.TOTAL_HG30DF.gt(0)
        crashes.append(df)
    accidents = pd.concat(crashes, ignore_index=True)
    counts = accidents.groupby(["province_code", "year"], as_index=False).agg(
        injury_crashes=("ID_ACCIDENTE", "size"),
        fatalities=("TOTAL_MU30DF", "sum"),
        hospitalized=("TOTAL_HG30DF", "sum"),
        urban_crashes=("urban", "sum"),
        rear_lateral_crashes=("rear_lateral", "sum"),
        severe_crashes=("severe", "sum"),
        unknown_collision=("unknown_collision", "sum"),
    )
    panel = pop.merge(counts, on=["province_code", "year"], how="left", validate="one_to_one")
    count_cols = [
        "injury_crashes",
        "fatalities",
        "hospitalized",
        "urban_crashes",
        "rear_lateral_crashes",
        "severe_crashes",
        "unknown_collision",
    ]
    panel[count_cols] = panel[count_cols].fillna(0).astype(int)
    panel = checked_join(panel, geo[["province_code", "province"]], ["province_code"])
    for kind in ["vehicles", "drivers"]:
        stock = pd.concat(
            [stocks(root, kind, year, geo) for year in [2022, 2024]], ignore_index=True
        )
        panel = panel.merge(stock, on=["province_code", "year"], how="left", validate="one_to_one")
    panel = add_rates(panel)
    panel = panel.sort_values(["year", "province_code"]).reset_index(drop=True)
    euro = europe(root)
    facts = {
        "fact_accidents": accidents,
        "dim_geography": geo,
        "fact_exposure": panel[
            ["province_code", "year", "population", "registered_vehicles", "licensed_drivers"]
        ],
        "spain_metrics": panel,
        "europe_metrics": euro,
    }
    geometry(root, geo)
    with duckdb.connect(str(out / "ebdi.duckdb")) as connection:
        for name, frame in facts.items():
            frame.to_parquet(out / f"{name}.parquet", index=False)
            connection.register("staging", frame)
            connection.execute(f'CREATE OR REPLACE TABLE "{name}" AS SELECT * FROM staging')
            connection.unregister("staging")
    # Public summary contains aggregated original analysis, never participant identifiers.
    panel.to_csv(root / "outputs/tables/spain_metrics.csv", index=False)
    euro.to_csv(root / "outputs/tables/europe_metrics.csv", index=False)
    comparisons = []
    for record in euro.to_dict("records"):
        for variable in [
            "fatalities",
            "population",
            "injury_crashes",
            "insurance_claims",
            "vehicle_km",
        ]:
            available = variable in {"fatalities", "population"}
            comparisons.append(
                {
                    "geo": record["geo"],
                    "country": record["country"],
                    "year": record["year"],
                    "variable": variable,
                    "included": available,
                    "source": "tran_sf_roadus"
                    if variable == "fatalities"
                    else "demo_pjan"
                    if variable == "population"
                    else "not harmonized in this release",
                    "status_flag": record.get(f"{variable}_status", ""),
                    "definition": "30-day road deaths, all users"
                    if variable == "fatalities"
                    else "resident population, 1 January"
                    if variable == "population"
                    else "no audited comparable modern panel",
                    "comparability": "limited: registration differences; retain publisher flags"
                    if variable == "fatalities"
                    else "exposure proxy, not kilometres travelled"
                    if variable == "population"
                    else "excluded; never filled or combined with modern fatalities",
                }
            )
    pd.DataFrame(comparisons).to_csv(root / "outputs/tables/country_comparability.csv", index=False)
    write_json(
        root / "outputs/tables/source_schema.json",
        {
            "accident_columns": schema,
            "categorical_codes": {k: sorted(v) for k, v in allowed.items()},
        },
    )
    quality = {
        "status": "passed",
        "accidents": reports,
        "join_rows": len(panel),
        "province_count": len(geo),
        "missing_exposures": {
            c: int(panel[c].isna().sum())
            for c in ["population", "registered_vehicles", "licensed_drivers"]
        },
        "europe_rows": len(euro),
        "denominators_are_travel_proxies": True,
    }
    write_json(root / "outputs/tables/data_quality.json", quality)
    (root / "docs/data_quality.md").write_text(
        "# Data quality report\n\nGenerated by `ebdi process` from verified source files.\n\n"
        + "| Year | Rows | Fatalities, 30d | Unknown municipality | Checks |\n|---|---:|---:|---:|---|\n"
        + "\n".join(
            f"| {r['year']} | {r['rows']:,} | {r['fatalities_30d']:,} | {r['unknown_municipality']:,} | passed |"
            for r in reports
        )
        + "\n\n52 provinces × 3 years; no missing population joins. Vehicle and driver stocks are missing for all 52 provinces in 2023 and remain missing.\n\n"
        + "Checks reject duplicate IDs, null critical fields, negative/fractional counts, invalid time bins, unknown provinces, category/schema drift, inconsistent victim/stock totals and source revisions. Optional code missingness is retained. Full details: `outputs/tables/data_quality.json`.\n",
        encoding="utf-8",
    )
    return quality
