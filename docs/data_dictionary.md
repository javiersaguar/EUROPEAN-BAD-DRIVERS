# Data dictionary

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
| `registered_vehicles` | DGT year-end total excluding mopeds, including trailers; audited 2022–2024 |
| `licensed_drivers` | DGT resident driving-permit holders excluding special licences; audited 2022–2024 |
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
| `ID_ACCIDENTE` | int64 | 0 |
| `ANYO` | int64 | 0 |
| `MES` | int64 | 0 |
| `DIA_SEMANA` | int64 | 0 |
| `HORA` | int64 | 0 |
| `COD_PROVINCIA` | int64 | 0 |
| `COD_MUNICIPIO` | int64 | 0 |
| `ISLA` | float64 | 286,699 |
| `ZONA` | int64 | 0 |
| `ZONA_AGRUPADA` | int64 | 0 |
| `CARRETERA` | object | 0 |
| `KM` | float64 | 173,068 |
| `SENTIDO_1F` | int64 | 0 |
| `TITULARIDAD_VIA` | int64 | 0 |
| `TIPO_VIA` | int64 | 0 |
| `TIPO_ACCIDENTE` | float64 | 35 |
| `TOTAL_MU24H` | int64 | 0 |
| `TOTAL_HG24H` | int64 | 0 |
| `TOTAL_HL24H` | int64 | 0 |
| `TOTAL_VICTIMAS_24H` | int64 | 0 |
| `TOTAL_MU30DF` | int64 | 0 |
| `TOTAL_HG30DF` | int64 | 0 |
| `TOTAL_HL30DF` | int64 | 0 |
| `TOTAL_VICTIMAS_30DF` | int64 | 0 |
| `TOTAL_VEHICULOS` | int64 | 0 |
| `TOT_PEAT_MU24H` | int64 | 0 |
| `TOT_BICI_MU24H` | int64 | 0 |
| `TOT_CICLO_MU24H` | int64 | 0 |
| `TOT_MOTO_MU24H` | int64 | 0 |
| `TOT_TUR_MU24H` | int64 | 0 |
| `TOT_FURG_MU24H` | int64 | 0 |
| `TOT_CAM_MENOS3500_MU24H` | int64 | 0 |
| `TOT_CAM_MAS3500_MU24H` | int64 | 0 |
| `TOT_BUS_MU24H` | int64 | 0 |
| `TOT_OTRO_MU24H` | int64 | 0 |
| `TOT_SINESPECIF_MU24H` | int64 | 0 |
| `TOT_PEAT_MU30DF` | int64 | 0 |
| `TOT_BICI_MU30DF` | int64 | 0 |
| `TOT_CICLO_MU30DF` | int64 | 0 |
| `TOT_MOTO_MU30DF` | int64 | 0 |
| `TOT_TUR_MU30DF` | int64 | 0 |
| `TOT_FURG_MU30DF` | int64 | 0 |
| `TOT_CAM_MENOS3500_MU30DF` | int64 | 0 |
| `TOT_CAM_MAS3500_MU30DF` | int64 | 0 |
| `TOT_BUS_MU30DF` | int64 | 0 |
| `TOT_VMP_MU30DF` | int64 | 0 |
| `TOT_OTRO_MU30DF` | int64 | 0 |
| `TOT_SINESPECIF_MU30DF` | int64 | 0 |
| `NUDO` | float64 | 66 |
| `NUDO_INFO` | float64 | 157,926 |
| `CARRETERA_CRUCE` | object | 293,112 |
| `PRIORI_NORMA` | int64 | 0 |
| `PRIORI_AGENTE` | int64 | 0 |
| `PRIORI_SEMAFORO` | int64 | 0 |
| `PRIORI_VERT_STOP` | int64 | 0 |
| `PRIORI_VERT_CEDA` | int64 | 0 |
| `PRIORI_HORIZ_STOP` | int64 | 0 |
| `PRIORI_HORIZ_CEDA` | int64 | 0 |
| `PRIORI_MARCAS` | int64 | 0 |
| `PRIORI_PEA_NO_ELEV` | int64 | 0 |
| `PRIORI_PEA_ELEV` | int64 | 0 |
| `PRIORI_MARCA_CICLOS` | int64 | 0 |
| `PRIORI_CIRCUNSTANCIAL` | int64 | 0 |
| `PRIORI_OTRA` | int64 | 0 |
| `CONDICION_NIVEL_CIRCULA` | int64 | 0 |
| `CONDICION_FIRME` | int64 | 0 |
| `CONDICION_ILUMINACION` | int64 | 0 |
| `CONDICION_METEO` | int64 | 0 |
| `CONDICION_NIEBLA` | float64 | 278,313 |
| `CONDICION_VIENTO` | float64 | 300,306 |
| `VISIB_RESTRINGIDA_POR` | int64 | 0 |
| `ACERA` | int64 | 0 |
| `TRAZADO_PLANTA` | int64 | 0 |

## Publisher category lookups

These labels are transcribed from the DGT code dictionary, credited to DGT. Unknowns stay explicit; a code is not a continuous numeric predictor.

### TIPO_ACCIDENTE

| Code | Publisher label |
|---|---|
| 1 | Frontal |
| 2 | Fronto-lateral |
| 3 | Lateral |
| 4 | Por alcance |
| 5 | Múltiple o en caravana |
| 6 | Colisión contra obstáculo o elemento de la vía |
| 7 | Atropello a personas |
| 8 | Atropello a animales |
| 9 | Vuelco |
| 10 | Caída |
| 11 | Sólo salida de la vía |
| 12 | Salida de la vía por la izquierda con colisión |
| 13 | Salida de la vía por la izquierda con despeñamiento |
| 14 | Salida de la vía por la izquierda con vuelco |
| 15 | Salida de la vía por la izquierda, otro tipo |
| 16 | Salida de la vía por la derecha con colisión |
| 17 | Salida de la vía por la derecha con despeñamiento |
| 18 | Salida de la vía por la derecha con vuelco |
| 19 | Salida de la vía por la derecha otro tipo |
| 20 | Otro tipo de accidente |

### ZONA_AGRUPADA

| Code | Publisher label |
|---|---|
| 1 | VÍAS INTERURBANAS |
| 2 | VÍAS URBANAS |

### TIPO_VIA

| Code | Publisher label |
|---|---|
| 1 | Autopista de peaje |
| 2 | Autopista libre |
| 3 | Autovía |
| 4 | Vía para automóviles |
| 5 | Carretera Convencional de doble calzada |
| 6 | Carretera Convencional de calzada única |
| 7 | Vía de servicio |
| 8 | Ramal de enlace |
| 9 | Calle |
| 10 | Camino vecinal |
| 11 | Recinto delimitado |
| 12 | Vía ciclista |
| 13 | Senda ciclable |
| 14 | Otro |

### DIA_SEMANA

| Code | Publisher label |
|---|---|
| 1 | LUNES |
| 2 | MARTES |
| 3 | MIÉRCOLES |
| 4 | JUEVES |
| 5 | VIERNES |
| 6 | SÁBADO |
| 7 | DOMINGO |

### CONDICION_METEO

| Code | Publisher label |
|---|---|
| 1 | Despejado |
| 2 | Nublado |
| 3 | Lluvia débil |
| 4 | Lluvia fuerte |
| 5 | Granizando |
| 6 | Nevando |
| 7 | Se desconoce |
| 999 | Sin especificar |

### CONDICION_ILUMINACION

| Code | Publisher label |
|---|---|
| 1 | Luz del día natural, solar |
| 2 | Amanecer o atardecer, sin luz artificial |
| 3 | Amanecer o atardecer, con luz artificial |
| 4 | Sin luz natural y con iluminación artificial encen |
| 5 | Sin luz natural y con iluminación artificial no en |
| 6 | Sin luz natural ni artificial |
| 999 | Sin especificar |

### NUDO

| Code | Publisher label |
|---|---|
| 1 | En intersección o nudo |
| 2 | Fuera de intersección o nudo |

## Model artifacts

Model metrics include n, positive n, prevalence, ROC-AUC, average precision (PR-AUC), log loss, Brier score, threshold, precision/recall and TN/FP/FN/TP. Calibration bins contain mean prediction, observed severe fraction and sample count. Permutation importance is increase in holdout log loss, with repetition SD. SHAP CSVs contain mean absolute raw-log-odds attribution grouped by original feature; the JSON records seed, sample and additivity error. See the model card for units, selection and valid use.


## Extended material-damage and demographic contracts (0.3.0)

| Artifact | Grain / nested parents | Meaning and units |
|---|---|---|
| `ncid_ultimate.csv` | Accident year × claim category; Total/damage/injury parents and injury size bands overlap | Actuarial final estimates including nil claims; matched UltData portfolio policy-years, mean cost, all-policy frequency /1,000, HICP-2024 costs. `earned_policies_covered` and comprehensive frequency exist only for own accidental damage. No count intervals |
| `ncid_settled.csv` | Final settlement year × damage type; damage Total is a parent | Observed final liquidations and costs, 2015–2024. No policy exposure or frequency attached. Market coverage % is provided only for 2024 and refers to earned-premium market share |
| `ncid_changes.csv` | Year × category | Descriptive relative changes (%) against the fixed 2019 observation, separate frequency and nominal/constant cost |
| `material_history.csv` | German national year, 2010–2024 | Police-recorded injury vs property-only crashes; share (%) among recorded crashes |
| `material_states.csv` | State × road location, 2024 | 16 states + Germany, four locations; 68 dense keys, one missing Berlin rural key. Serious, intoxicant-other and remaining property classes are disjoint |
| `dgt_demographics.csv` | Year × zone × population role × age band × sex × user category | 3,780 cells; M/F/UNK, six disjoint age bands including unknown. User Total is a parent, never additive to its categories. Roles: all victims, driver victims, involved drivers. Role-inapplicable and source-absent measures are missing |
| `dgt_persons_detail.csv` | Source year/sheet/row × original age × recorded sex × original user type | 30,904 source aggregate rows including age/sex/user Totals; downloadable without loading redundant original totals into the browser. Source blanks and audited gaps retained |
| `europe_sex_users.csv` | EU27 country × year × sex × person role | 8,100 dense keys, 2010–2024; T/M/F/UNK × TOTAL/DRIV/PAS/PED/UNK. Nested Totals; source flags and absent observations retained. Mortality per million population of the same sex/year, Garwood Poisson 95% limits where compatible; unknown sex has no exposure |
| `spain_age_population.csv` | Year × sex × known age band | 30 population cells, fixed pooled Spanish M+F 2024 standard weights; population flags retained. All single ages reconcile with published population totals |
| `spain_age_sex_rates.csv` | Year × sex × known age band | 30 observed mortality rates per million age/sex residents and Poisson limits |
| `spain_sex_rates.csv` | Year × sex, M/F | Six national crude rates and Poisson limits, adjusted point rates per million under common five-age weights; unknown-age death counts disclosed |
| `collision_analysis.csv` | Year × zone × collision category; Total is a parent | 198 cells, 21 disjoint source accident types + parent. Accident counts, fatal accident fraction (%), conditional Wilson 95% model limits, contributions and n<100 flag. Counts are accidents, not people |
| `vehicle_age_analysis.csv` | Year × zone × vehicle type × vehicle age; Totals are parents | Involved motor vehicles and shares (%) including unknown age in denominators. No age-specific fleet/exposure risk estimate |
| `demographics_quality.json`, `material_quality.json`, `ncid_quality.json`, `extended_analysis.json` | Dataset-level audit | Reconciliations, known source gaps, unavailable quantities and interpretation |

See [extended analysis](extended_analysis.md) for scope, exact original discrepancies and formulas. Unknown sex/age and absent cells are distinct. Grouping across any missing component must retain an unavailable aggregate rather than sum only the available cells. Do not combine person populations, nested totals, insurance cohorts or incompatible countries' reporting scopes.
