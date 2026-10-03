# Data feasibility audit

Audited on **3 October 2026**, before implementing transformations. The audit downloaded real
files from official publishers, inspected workbook sheets and columns, and counted full records.
Exact download URLs, observed SHA-256 hashes, coverage and reuse references are in
[`configs/sources.yaml`](../configs/sources.yaml). Runtime downloads retain separate retrieval manifests.

## Available

| Source | Observed file / observation unit | Coverage inspected | Join / variables |
|---|---|---|---|
| DGT injury crashes | XLSX; one recorded injury crash | 2022–2024; 73 fields each | `ANYO`, `COD_PROVINCIA`, `ID_ACCIDENTE`; month, weekday, hour, collision, road, weather, lighting, 24h and 30d victim counts |
| DGT vehicle stock | XLSX, sheet `V_4`; province/year | 2022 and 2024 | Province names, total registered stock; includes trailers, excludes mopeds in this table |
| DGT driver census | XLSX, sheet `P_6_1_1_10`; residence province/year | 2022 and 2024 | Residence, sex, licence-holder counts; use the residence table, not province of first issuance |
| INE annual census, table 67988 | Tab-separated CSV; geography/sex/year | 2021–2025 | Numeric province prefixes and same calendar year; population at 1 January |
| EC ERSO historical workbook | XLSX; country/year | Fatality counts 2010–2024; rates have longer coverage | Fatalities and publisher-computed population rates; country-specific notes |
| Eurostat `tran_sf_roadus` | JSON-stat API; country/year after filters | 2022–2024 | Total sex, age, road-user category; 30-day deaths; sparse observations and status flags |
| Eurostat `demo_pjan` | JSON-stat API; country/year | 2022–2024 | Total age and sex; 1 January population; preserve status flags |
| GISCO | NUTS 2024 GeoJSON, EPSG:4326 | 2024 boundary vintage | Spanish NUTS3 polygons; island regions must be aggregated to provinces |

**Observed DGT totals:**

| Year | Injury crashes | Fatalities, 30 days | Hospitalized injured, 30 days |
|---|---:|---:|---:|
| 2022 | 97,916 | 1,746 | 8,502 |
| 2023 | 101,306 | 1,806 | 9,265 |
| 2024 | 101,996 | 1,785 | 9,561 |

The fatality totals agree with the inspected ERSO release. This is a reconciliation check,
not proof that every variable or reporting process is complete.

## Available with limitations

- Collision type is missing in 35 records in 2024. These remain unknown: collision-specific
  numerators count recorded matching types only; missing types are reported separately.
- Municipality codes exist, but 11,513 / 12,201 / 12,232 records respectively have code zero.
  Province is the defensible initial analysis level. An unknown municipality must not become a real municipality.
- Month, weekday and hour exist; a complete calendar day/date does not. Do not fabricate exact dates.
- `TOTAL_VEHICULOS` counts involved vehicles. `TOT_*_MU30DF` classifies fatalities by road-user/vehicle category;
  these are **not vehicle-level observations or involved vehicle-type counts**.
- Resident population, resident licence holders and registered stock are real measured denominators,
  but proxies for travel exposure. Crashes occur at the crash location, not necessarily drivers' residence.
  Tourists, commuters, pedestrians and vehicle occupancy complicate interpretation.
- Default coverage is a fully observed three-year crash/population panel. Vehicle and driver denominators
  are available for 2022 and 2024 only in the audited workbook releases. The initial implementation
  leaves 2023 values missing; it never interpolates them.
- Insurance Europe's downloadable `Database-Motor.xlsx` contains historical country tables through 2016,
  including MTPL insured vehicle-years and notified claims. Calculated frequency tables explicitly permit
  alternative denominators. Zeros, missing countries, nil-claim definitions and older years prevent
  combining this release with current Spanish injury crashes or constructing a modern European claims ranking.
  Historical count/exposure pairs can be explored separately, with flags and source table names.
- UNESPA's 2024 [automobile report announcement](https://www.unespa.es/notasdeprensa/siniestros-automovil-datos-2024/)
  describes claim categories and territorial differences. Direct automated access returned HTTP 403
  during the audit. A press release is not an exhaustive machine-readable territory/exposure panel.
- Spanish Transport Ministry's [2024 infrastructure report](https://publicaciones.transportes.gob.es/downloadcustom/sample/4057)
  has provincial vehicle-km by road ownership, including estimates. It excludes full urban travel exposure.
  All-road injury crashes cannot be divided by state-network kilometres; a matched network definition is required.

## Unavailable in the inspected public DGT crash files

| Requested attribute | Evidence / conclusion |
|---|---|
| Driver age and sex | Absent from all 73-column accident tables; census sex does not supply crash driver sex |
| Licence tenure | Absent |
| Individual vehicle type and age | Absent; fatality-category totals cannot substitute for these features |
| Driver-level negatives / control cohort | Absent; every row is already an injury crash |
| Property-damage-only crashes | Outside the accident-with-victims file's scope |
| Personal annual accident probability | Cannot be identified from these data |

## Needs alternative source

Current provincial insured vehicle-years with claim counts by coverage, full-network travel kilometres,
participant/vehicle microdata with documented access conditions, and a non-crash cohort for involvement risk.
The DGT [municipal annual driver census listing](https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/censo-conductores-prov-sexo-muni.html)
also offers fixed-width TXT files beginning in 2023; these require a separate layout and population-definition
reconciliation before replacing the workbook series. No emails or data-access requests have been sent.

## Recommended MVP and architecture

Use the province × year panel for 2022–2024: DGT injury crashes plus INE table 67988,
supplemented with observed driver/vehicle stocks in 2022 and 2024. Start with individual rates,
then experiment with transparent weighted indices and normalization changes. Retain missingness explicitly.
Use immutable local raw files with hashes, schema checks, Parquet fact/dimension tables,
a DuckDB analytical view, reproducible report/figure generation and Streamlit.

The European extension should compare **30-day fatality burden per population** for a common country/year
set, retaining Eurostat flags and excluding aggregate pseudo-countries. No European composite of incompatible
injury-reporting or insurance systems is supported by this audit.

## Is individual-level accident-risk ML defensible?

**No.** The inspected data contain neither people who did not crash nor driver-year travel exposure.
A different valid experiment predicts whether a **recorded injury crash** contains at least one fatality
or hospitalized injured person. Train on 2022, use 2023 for model selection, and reserve 2024 for evaluation.
Exclude all victim totals, fatality category totals and other outcome-derived features. Results describe
conditional recorded-crash severity, not individual involvement probability or causal effects.

## Reuse

MIT applies to original code only. The [government catalogue entry](https://datos.gob.es/es/catalogo/e00130502-ficheros-de-microdatos-de-accidentes-con-victimas-20241)
identifies CC BY 4.0 for the 2024 DGT crash dataset; credit DGT and identify transformations.
Other source releases have their own terms. INE requires attribution and responsibility for derived calculations;
Insurance Europe retains copyright. GISCO has separate download provisions and map attribution.
Raw source workbooks, the historical insurance tables and geometry are downloaded locally and are not committed.
