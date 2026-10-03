"""Generate reference documentation from the audited registry and actual schema."""

import json
from pathlib import Path

import pandas as pd

from ebdi.ingestion.download import catalog, raw_path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sources = catalog(ROOT)
    sections = [
        "# Source register\n\nAudited 3 October 2026. Exact URLs, hashes, retrieval times and schema metadata are versioned in `configs/sources.yaml`. Runtime provenance is in the local `data/raw/manifest.json`. Source code is MIT; datasets retain their own conditions. The pipeline transforms original data into aggregated analysis and credits publishers; no raw workbooks are redistributed.\n\nSource terms should be checked before reuse. DGT 2024's government catalog lists CC BY 4.0; INE and Eurostat require source attribution; GISCO additionally requires © EuroGeographics map credit. Insurance Europe retains copyright.\n"
    ]
    for source in sources:
        sections.append(
            f"## {source['id']}\n\n[{source['organization']} · {source.get('dataset_title', source['dataset'])}]({source['page_url']}) · [exact download/API]({source['url']})\n\n"
        )
        fields = [
            "format",
            "years",
            "geographic_level",
            "observation_unit",
            "key_variables",
            "denominator",
            "known_limitations",
            "update_frequency",
            "schema_version",
            "comparability",
            "enabled",
            "sample_retrieved_at",
            "sample_sha256",
            "reuse",
        ]
        sections.append(
            "| Property | Audited value |\n|---|---|\n"
            + "\n".join(
                f"| {field} | {str(source.get(field, 'See feasibility audit')).replace('|', '/')} |"
                for field in fields
            )
        )
        sections.append(f"\n\n[Reuse terms]({source['license_url']}).\n\n")
    sections.append(
        "## Audited sources excluded from ingestion\n\n[Transport Ministry 2024 infrastructure report](https://publicaciones.transportes.gob.es/downloadcustom/sample/4057): PDF, provincial vehicle-kilometres by road ownership, annual, estimated values. Network coverage does not match all-road crash numerators. No full-network VKT denominator was built.\n\nThe infrastructure report remains a research lead, not a source merged into the analytical facts. UNESPA 2024 is ingested separately; see [insurance](insurance.md). See [feasibility](data_feasibility.md) and [limitations](limitations.md).\n"
    )
    (ROOT / "docs/sources.md").write_text("".join(sections), encoding="utf-8")
    dictionary = """# Data dictionary

## Analytical grain and keys

| Artifact | Grain / key | Contents |
|---|---|---|
| `fact_accidents.parquet` | `(year, ID_ACCIDENTE)` | Original 73 fields and derived province/year/flags; local only |
| `dim_geography.parquet` | `province_code` | 52 provinces, names and autonomous-community labels |
| `fact_exposure.parquet` | `(province_code, year)` | Population and observed vehicle/permit stocks |
| `spain_metrics.parquet` / published CSV | Province-year | Counts, rates and limits; 156 rows |
| `europe_metrics.parquet` / published CSV | `(geo, year)` | EU-27 fatalities, population, flags and rates; 81 rows |
| `index.parquet` / published CSV | Province-year | Experimental score, rank and eligibility |
| `ebdi.duckdb` | Named tables above, except index | Queryable local analytical database |
| `country_comparability.csv` | Country-year-variable | Inclusion, source, definition, status and limitations |
| `crash_breakdowns.csv` | Year-dimension-code | Counts, shares and severe-outcome fractions; no travel exposure |
| `sensitivity.csv` | Latest-year province | Weight-scenario ranges and conditional event-bootstrap limits |
| `insurance_coverage.csv` | National coverage, 2024 | Shares of claims/payments (%) and mean cost (€); 11 rows |
| `insurance_municipal.csv` | Selected municipality-coverage, 2024 | Relative differences (%), published selection, source order/page/table; 80 rows |
| `insurance_provinces.csv` | Province, 2024 | All-coverage claims and payments (€); 50 rows |
| `insurance_quality.json` | UNESPA release | Source hash, reconciliation gaps and unavailable quantities |

`province_code` is a two-character string (01–52), not a number without leading zeros. `year` is integer. `geo` is the publisher's country code (EL for Greece). Numeric missing values remain null/NaN; exports use empty cells. Source status strings are not replaced with estimates.

## Derived columns

| Column / pattern | Definition |
|---|---|
| `injury_crashes` | Number of recorded crashes with victims |
| `fatalities` | People dead at 30 days, all road users |
| `hospitalized` | Hospitalized injured at 30 days; people, not crashes |
| `urban_crashes` / `urban` | Crash location urban, `ZONA_AGRUPADA = 2` |
| `rear_lateral_crashes` / `rear_lateral` | Collision types 2, 3 or 4; excludes unknown codes |
| `severe_crashes` / `severe` | Crash has ≥1 fatality or hospitalized injured person at 30 days |
| `unknown_collision` | Count/flag of missing collision type |
| `population` | INE residents at 1 January of the same year |
| `registered_vehicles` | DGT year-end total excluding mopeds, including trailers; missing in 2023 |
| `licensed_drivers` | DGT resident driving-permit holders excluding special licences; missing in 2023 |
| `*_per_100k_*` | Numerator divided by named stock ×100,000 |
| `*_lower`, `*_upper` | Conditional Poisson central 95% interval for the named rate |
| `small_sample` | Province has fewer than 30 injury crashes |
| `index_score`, `index_rank` | Weighted normalized metric; 1 = highest score; ties get average rank |
| `index_eligible` | All active components observed and minimum sample satisfied |
| `weight_rank_*` | Rank distribution under 500 explicit weight scenarios |
| `bootstrap_*_lower/upper` | 2.5th/97.5th percentiles, 200-repeat conditional Poisson event bootstrap |
| `share_of_recorded_crashes` | Group crash count / all recorded crashes that year; not accident probability |
| `conditional_severe_fraction` | Severe group crashes / recorded group crashes |
| `fatalities_status`, `population_status` | Unmodified Eurostat flags (e.g. p provisional, e estimated, b break, d differing definition) |
| `fatalities_per_million_population` | European fatalities / residents ×1,000,000 |

## Insurance definitions

`relative_difference_pct` is the published difference relative to the national reference, not an absolute probability. `selection` identifies higher/lower published extremes, and `source_order` is their source row order. Labels are retained as printed. Municipal claim counts and insured vehicle-years are unavailable; they are never imputed. Provincial counts cover all insurance categories. See [insurance](insurance.md) for exact scope and reconciliation differences.

## Original DGT schema

The ordered 73-column contract is in `configs/accident_schema.json`; category codes are validated against the real publisher dictionary. `ANYO`, `MES`, `DIA_SEMANA` and `HORA` supply temporal bins, not an exact date. `TOTAL_*24H` are 24-hour outcomes; `TOTAL_*30DF` are 30-day outcomes. `TOT_*` outcome totals by road-user/vehicle category are not individual vehicle characteristics. All outcome fields are excluded from model predictors. `TOTAL_VEHICULOS` counts involved vehicles; it does not describe their individual type or age.

Full observed columns and types follow. Types describe this processed release, not a universal publisher contract. Optional fields can contain missing values. Age, sex, licence tenure and individual vehicle age are absent rather than imputed.

| Field | Observed type | Missing rows (2022–2024) |
|---|---|---:|
"""
    frame = pd.read_parquet(ROOT / "data/processed/fact_accidents.parquet")
    columns = json.loads((ROOT / "configs/accident_schema.json").read_text())["columns"]
    dictionary += "\n".join(
        f"| `{c}` | {frame[c].dtype} | {int(frame[c].isna().sum()):,} |" for c in columns
    )
    dictionary += "\n\n## Publisher category lookups\n\nThese labels are transcribed from the DGT code dictionary, credited to DGT. Unknowns stay explicit; a code is not a continuous numeric predictor.\n\n"
    workbook = pd.ExcelFile(raw_path(ROOT, "dgt_dictionary"), engine="calamine")
    for sheet in [
        "TIPO_ACCIDENTE",
        "ZONA_AGRUPADA",
        "TIPO_VIA",
        "DIA_SEMANA",
        "CONDICION_METEO",
        "CONDICION_ILUMINACION",
        "NUDO",
    ]:
        codes = pd.read_excel(workbook, sheet_name=sheet, header=1)
        valid = pd.to_numeric(codes.iloc[:, 0], errors="coerce").notna()
        dictionary += (
            f"### {sheet}\n\n| Code | Publisher label |\n|---|---|\n"
            + "\n".join(
                f"| {int(r.iloc[0])} | {str(r.iloc[1]).strip()} |"
                for _, r in codes.loc[valid].iterrows()
            )
            + "\n\n"
        )
    dictionary += "## Model artifacts\n\nModel metrics include n, positive n, prevalence, ROC-AUC, average precision (PR-AUC), log loss, Brier score, threshold, precision/recall and TN/FP/FN/TP. Calibration bins contain mean prediction, observed severe fraction and sample count. Permutation importance is increase in holdout log loss, with repetition SD. SHAP CSVs contain mean absolute raw-log-odds attribution grouped by original feature; the JSON records seed, sample and additivity error. See the model card for units, selection and valid use.\n"
    (ROOT / "docs/data_dictionary.md").write_text(dictionary, encoding="utf-8")
    print("Generated source register and full observed data dictionary")


if __name__ == "__main__":
    main()
