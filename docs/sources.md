# Source register

Audited 4 October 2026. Exact URLs, hashes, retrieval times and schema metadata are versioned in `configs/sources.yaml`. Runtime provenance is in the local `data/raw/manifest.json`. Source code is MIT; datasets retain their own conditions. The pipeline transforms original data into aggregated analysis and credits publishers; no raw workbooks are redistributed.

Source terms should be checked before reuse. DGT 2024's government catalog lists CC BY 4.0; INE and Eurostat require source attribution; GISCO additionally requires © EuroGeographics map credit. Insurance Europe retains copyright.
## dgt_accidents_2022

[DGT · Recorded road crashes with victims](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Ficheros-microdatos-de-accidentes-con-victimas-2022/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/24h/TABLA_ACCIDENTES_22.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2022] |
| geographic_level | province |
| observation_unit | injury crash |
| key_variables | ['ID_ACCIDENTE', 'ANYO', 'MES', 'DIA_SEMANA', 'HORA', 'COD_PROVINCIA', 'TIPO_ACCIDENTE', 'ZONA_AGRUPADA', 'TOTAL_MU30DF', 'TOTAL_HG30DF'] |
| denominator | none (numerator) |
| known_limitations | Injury crashes only; no driver demographics, individual vehicle age or non-crash controls; crash location differs from exposure residence. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:45.587679+00:00 |
| sample_sha256 | 89f1b926c7df70588d1506ab89c373c1a64c373bb042e01406830759a0ede600 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_dictionary

[DGT · Accident table code dictionary](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Ficheros-microdatos-de-accidentes-con-victimas-2022/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Ficheros_microdatos_de_accidentalidad_con_victimas/Diccionario-Tabla-Accidente.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2024] |
| geographic_level | province |
| observation_unit | code lookup |
| key_variables | ['category code', 'publisher label'] |
| denominator | not applicable |
| known_limitations | Code labels require workbook-specific sheet layouts; optional missing categories remain unknown. |
| update_frequency | irregular |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:42.665749+00:00 |
| sample_sha256 | 1df06643eff95dd7f3211fca7fad2c95f2d926930d12ca97a345c764995d0ae9 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_vehicles_2022

[DGT · Registered vehicle fleet by province](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Parque-de-vehiculos-Tablas-estadisticas-2022/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/parque-de-vehiculos/Parque-de-vehiculos-Tablas-estadisticas-2022.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2022] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['province', 'vehicle-category stocks', 'total stock'] |
| denominator | year-end registered vehicle stock excluding mopeds |
| known_limitations | Year-end registrations, not vehicle-kilometres; selected total excludes mopeds and includes trailers/semitrailers. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:42.482615+00:00 |
| sample_sha256 | 051ae4c25c968bbcdd1d18363616ff83986ff7c93b0773ac5005d40d491e92ec |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_drivers_2022

[DGT · Driving-permit holders by residence province](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Censo-de-conductores-Tablas-estadisticas-2022/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Censo_conductores/Censo-de-conductores_Tablas-estadisticas-2022.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2022] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['residence province', 'sex', 'driving permits', 'special licences'] |
| denominator | year-end resident driving-permit holders excluding special licences |
| known_limitations | Year-end residence stock, not trips; selected column excludes special licences; crash participant demographics cannot be derived from census sex. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:47.554894+00:00 |
| sample_sha256 | 465d8f878a4708571a940c11fb9823bf668b53548c57d88211ce24d464c94725 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_accidents_2023

[DGT · Recorded road crashes with victims](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Ficheros-microdatos-de-accidentes-con-victimas-2023/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/24h/TABLA_ACCIDENTES_23.XLSX)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2023] |
| geographic_level | province |
| observation_unit | injury crash |
| key_variables | ['ID_ACCIDENTE', 'ANYO', 'MES', 'DIA_SEMANA', 'HORA', 'COD_PROVINCIA', 'TIPO_ACCIDENTE', 'ZONA_AGRUPADA', 'TOTAL_MU30DF', 'TOTAL_HG30DF'] |
| denominator | none (numerator) |
| known_limitations | Injury crashes only; no driver demographics, individual vehicle age or non-crash controls; crash location differs from exposure residence. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:45.339797+00:00 |
| sample_sha256 | d46c80382cb1d6655111735decfade72fe85b97abc315a9584e2c291f81f1e8b |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_accidents_2024

[DGT · Recorded road crashes with victims](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Ficheros-de-microdatos-de-accidentes-con-victimas-2024/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Ficheros_microdatos_de_accidentalidad_con_victimas/TABLA_ACCIDENTES_24.XLSX)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2024] |
| geographic_level | province |
| observation_unit | injury crash |
| key_variables | ['ID_ACCIDENTE', 'ANYO', 'MES', 'DIA_SEMANA', 'HORA', 'COD_PROVINCIA', 'TIPO_ACCIDENTE', 'ZONA_AGRUPADA', 'TOTAL_MU30DF', 'TOTAL_HG30DF'] |
| denominator | none (numerator) |
| known_limitations | Injury crashes only; no driver demographics, individual vehicle age or non-crash controls; crash location differs from exposure residence. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:43.428241+00:00 |
| sample_sha256 | 4c39dbdf3c31fcd0c99a0b9e68fdd7fc017c689cda01546d1d34545a3c64b387 |
| reuse | CC BY 4.0 per datos.gob.es catalogue; attribute DGT and identify transformations; MIT applies only to original code |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_vehicles_2024

[DGT · Registered vehicle fleet by province](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Parque-de-vehiculos-Tablas-estadisticas-2024/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Parque-de-vehiculos-Tablas-Estadisticas/Parque-de-vehiculos-Tablas-estadisticas-2024.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2024] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['province', 'vehicle-category stocks', 'total stock'] |
| denominator | year-end registered vehicle stock excluding mopeds |
| known_limitations | Year-end registrations, not vehicle-kilometres; selected total excludes mopeds and includes trailers/semitrailers. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:42.986232+00:00 |
| sample_sha256 | 85b8302a3d73546578500c3a94b32b9b068961d23eda16c39044e7e1e7b107a8 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_drivers_2024

[DGT · Driving-permit holders by residence province](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Censo-de-conductores-Tablas-estadisticas-2024/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Censo-conductores-Tablas-estadisticas/Censo-de-conductores-Tablas-estadisticas-2024.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2024] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['residence province', 'sex', 'driving permits', 'special licences'] |
| denominator | year-end resident driving-permit holders excluding special licences |
| known_limitations | Year-end residence stock, not trips; selected column excludes special licences; crash participant demographics cannot be derived from census sex. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:43.289207+00:00 |
| sample_sha256 | 661de54f6cae97437e05bf4ea1b7ecebb7b4ab304e8155a068fd93fb5a197476 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## ine_population

[INE · Population on 1 January](https://www.ine.es/jaxiT3/Tabla.htm?t=2852) · [exact download/API](https://www.ine.es/jaxiT3/files/t/csv_bd/2852.csv)

| Property | Audited value |
|---|---|
| format | csv |
| years | [1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['geography', 'sex total', 'age total where available', 'year', 'residents', 'publisher flags where available'] |
| denominator | resident population on 1 January |
| known_limitations | Resident stock is a travel exposure proxy; source geography and reference date must match explicitly. This legacy table ends in 2021; disabled for the 2022–2024 panel. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Population is an exposure proxy, not travel distance |
| enabled | False |
| sample_retrieved_at | 2026-10-03T14:05:43.812905+00:00 |
| sample_sha256 | 60396c8312b6eed5870efdd487679c89aa2724697556bcf25b9610abdab04d77 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.ine.es/aviso_legal).

## erso_fatalities

[European Commission / Eurostat · Road fatalities at 30 days](https://road-safety.transport.ec.europa.eu/european-road-safety-observatory/data-and-analysis_en) · [exact download/API](https://road-safety.transport.ec.europa.eu/document/download/a4a2cfe6-2100-4918-9702-188f995d9272_en?filename=fatalities_per_pop_2010-24_public_0.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | country |
| observation_unit | country-year |
| key_variables | ['country', 'year', 'fatalities', 'publisher flags or notes'] |
| denominator | none (numerator) |
| known_limitations | Includes all road users; follow-up and registration differ; retain notes/flags. Not an injury or driving-quality comparison. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | 30-day fatalities; country notes and flags must be retained |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:44.159485+00:00 |
| sample_sha256 | e72092cc2ecdbf835ed8563bab58438701583228cb0774341e6e5070f2db467e |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## insurance_europe_motor

[Insurance Europe · Historical motor insurance statistical workbook](https://www.insuranceeurope.eu/statistics) · [exact download/API](https://www.insuranceeurope.eu/downloads/european-insurance-industry-database-motor-insurance-statistics/Database-Motor.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016] |
| geographic_level | country |
| observation_unit | workbook tables |
| key_variables | ['MTPL claims', 'insured vehicle-years', 'claim frequency', 'country', 'year', 'table notes'] |
| denominator | insured vehicle-years (check each table) |
| known_limitations | Ends in 2016; units/country coverage vary; frequency notes permit fallback denominators. Downloaded for audit only, excluded from current facts. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Historical coverage and reporting vary; do not combine with modern Spanish incidents |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:05:44.084833+00:00 |
| sample_sha256 | 8af8a6600082567fced7bce9d298d398ec82669f018cf0e77dd952ab51ae443b |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.insuranceeurope.eu/about-us/2/how-we-work/disclaimer).

## ine_population_67988

[INE · Population on 1 January](https://www.ine.es/jaxiT3/Tabla.htm?t=67988) · [exact download/API](https://www.ine.es/jaxiT3/files/t/csv_bd/67988.csv)

| Property | Audited value |
|---|---|
| format | csv |
| years | [2021, 2022, 2023, 2024, 2025] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['geography', 'sex total', 'age total where available', 'year', 'residents', 'publisher flags where available'] |
| denominator | resident population on 1 January |
| known_limitations | Resident stock is a travel exposure proxy; source geography and reference date must match explicitly. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Population is an exposure proxy, not travel distance |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:10:57.184770+00:00 |
| sample_sha256 | 1e83b03f07744c99d44edc6146237b50d88ca24b8efe65879a081aa27a03c8e1 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.ine.es/aviso_legal).

## eurostat_fatalities

[European Commission / Eurostat · Road fatalities at 30 days](https://ec.europa.eu/eurostat/cache/metadata/en/tran_sf_road_esms.htm) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tran_sf_roadus?lang=EN&sex=T&age=TOTAL&unit=NR&pers_cat=TOTAL&sinceTimePeriod=2022&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2022, 2023, 2024] |
| geographic_level | country |
| observation_unit | country-year |
| key_variables | ['country', 'year', 'fatalities', 'publisher flags or notes'] |
| denominator | none (numerator) |
| known_limitations | Includes all road users; follow-up and registration differ; retain notes/flags. Not an injury or driving-quality comparison. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | 30-day fatalities; country notes and flags must be retained |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:10:56.876324+00:00 |
| sample_sha256 | 473b64a8351608c08de88cd66cf94db8ea03a3c0d2f1b44363f755540ba991c1 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## eurostat_population

[European Commission / Eurostat · Population on 1 January](https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjan?lang=EN&sex=T&age=TOTAL&unit=NR&sinceTimePeriod=2022&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2022, 2023, 2024] |
| geographic_level | country |
| observation_unit | country-year |
| key_variables | ['geography', 'sex total', 'age total where available', 'year', 'residents', 'publisher flags where available'] |
| denominator | resident population on 1 January |
| known_limitations | Resident stock is a travel exposure proxy; source geography and reference date must match explicitly. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Country population is an exposure proxy |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:10:57.543652+00:00 |
| sample_sha256 | e924bf4b65c94a4c03e8053b8f60702304687ba6df34903d8c8408e37db7ec5a |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## gisco_nuts3

[European Commission / Eurostat · NUTS 2024 level-3 boundaries at 1:20 million](https://gisco-services.ec.europa.eu/distribution/v2/nuts/) · [exact download/API](https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_20M_2024_4326_LEVL_3.geojson)

| Property | Audited value |
|---|---|
| format | geojson |
| years | [2024] |
| geographic_level | NUTS3 |
| observation_unit | polygon |
| key_variables | ['NUTS_ID', 'NUTS_NAME', 'CNTR_CODE', 'geometry'] |
| denominator | not applicable |
| known_limitations | Map only; generalized boundary vintage; island NUTS3 areas aggregated to Spanish provinces; no exposure measure. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Administrative boundary vintage 2024; islands require province aggregation |
| enabled | True |
| sample_retrieved_at | 2026-10-03T14:10:57.101762+00:00 |
| sample_sha256 | 2ce745f8ace09acabacb6944482ba8a57d7df9ba99827a7e78e6ba73094127c4 |
| reuse | GISCO download provisions and map attribution: © EuroGeographics; not relicensed under MIT |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## unespa_motor_2024

[UNESPA · Automobile insurance claims 2024, PDF tables 1, 2, 8 and 9](https://www.unespa.es/notasdeprensa/siniestros-automovil-datos-2024/) · [exact download/API](https://www.unespa.es/main-files/uploads/2026/02/NdP-Siniestros-del-seguro-de-auto-2024-FINAL.pdf)

| Property | Audited value |
|---|---|
| format | pdf |
| years | [2024] |
| geographic_level | national, province and selected municipality |
| observation_unit | coverage or selected municipality-coverage, year 2024 |
| key_variables | ['coverage', 'claims_share_pct', 'payments_share_pct', 'mean_cost_eur', 'municipality', 'relative_difference_pct', 'all_coverage_claims'] |
| denominator | Published national coverage shares and relative municipal differences; insured vehicle-years unavailable |
| known_limitations | Only 20 highest and 20 lowest cities per coverage above 50,000 inhabitants. Relative differences, not absolute probabilities. Material claims need not be injury-free. Provincial totals cover all categories; counts and exposures by municipal coverage unavailable. |
| update_frequency | annual |
| schema_version | PDF published 2026-02-10, 11 pages, audited 2026-10-03 |
| comparability | Separate insurance explorer; never merged with DGT or the composite index |
| enabled | True |
| sample_retrieved_at | 2026-10-03T16:46:40.020620+00:00 |
| sample_sha256 | 20211e0e670fc7397e0455320d27166036c357a331b6bc8fddd8fd95d32aa429 |
| reuse | Publisher terms apply; factual aggregates attributed to UNESPA; no raw PDF redistributed or relicensed under MIT |

[Reuse terms](https://www.unespa.es/aviso-legal/).

## dgt_vehicles_2023

[DGT · Registered vehicle fleet by province](https://datos.gob.es/es/catalogo/e00130502-parque-de-vehiculos-tablas-estadisticas-2023) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Parque-de-vehiculos-Tablas-Estadisticas/Parque-de-vehiculos-Tablas-estadisticas-2023.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2023] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['province', 'vehicle-category stocks', 'total stock'] |
| denominator | year-end registered vehicle stock excluding mopeds |
| known_limitations | Year-end registrations, not vehicle-kilometres; selected total excludes mopeds and includes trailers/semitrailers. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T17:17:04.056779+00:00 |
| sample_sha256 | f46f244b13d4fd14666565e59c0e7c312e22c429f9e805c118a3b5f625d8fb48 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_drivers_2023

[DGT · Driving-permit holders by residence province](https://datos.gob.es/es/catalogo/e00130502-censo-de-conductores-tablas-estadisticas-2023) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Censo_conductores/Censo-de-conductores-Tablas-estadisticas-2023.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2023] |
| geographic_level | province |
| observation_unit | province-year |
| key_variables | ['residence province', 'sex', 'driving permits', 'special licences'] |
| denominator | year-end resident driving-permit holders excluding special licences |
| known_limitations | Year-end residence stock, not trips; selected column excludes special licences; crash participant demographics cannot be derived from census sex. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Counts at crash location; exposure stock at residence; not individual risk |
| enabled | True |
| sample_retrieved_at | 2026-10-03T17:17:04.350327+00:00 |
| sample_sha256 | 520377ec2091e8164f4ef5caeb6f3e2c93fc6e6157664e955273347d6e0857d0 |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## eurostat_fatalities_history

[European Commission / Eurostat · Road fatalities at 30 days · 2010–2024 historical context](https://ec.europa.eu/eurostat/cache/metadata/en/tran_sf_road_esms.htm) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tran_sf_roadus?lang=EN&sex=T&age=TOTAL&unit=NR&pers_cat=TOTAL&sinceTimePeriod=2010&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | country |
| observation_unit | country-year |
| key_variables | ['country', 'year', 'fatalities', 'publisher flags or notes'] |
| denominator | none (numerator) |
| known_limitations | Includes all road users; follow-up and registration differ; retain notes/flags. Not an injury or driving-quality comparison. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | 30-day fatalities; country notes and flags must be retained |
| enabled | True |
| sample_retrieved_at | 2026-10-03T17:17:05.688048+00:00 |
| sample_sha256 | 1e494a4fc8eae2525ff2715071bc4c7fd5034fc6a7c2b29517d9b14e2ddfc35c |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## eurostat_population_history

[European Commission / Eurostat · Population on 1 January · 2010–2024 historical context](https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjan?lang=EN&sex=T&age=TOTAL&unit=NR&sinceTimePeriod=2010&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | country |
| observation_unit | country-year |
| key_variables | ['geography', 'sex total', 'age total where available', 'year', 'residents', 'publisher flags where available'] |
| denominator | resident population on 1 January |
| known_limitations | Resident stock is a travel exposure proxy; source geography and reference date must match explicitly. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Country population is an exposure proxy |
| enabled | True |
| sample_retrieved_at | 2026-10-03T17:17:06.840293+00:00 |
| sample_sha256 | 4865bb658213b0622be6fe798be8eab314bf97df646b6bf0962674942e13220f |
| reuse | Source terms apply; not relicensed under MIT |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## transport_rce_2022

[Ministerio de Transportes y Movilidad Sostenible · Traffic in the State Road Network, 2022; provincial vehicle-kilometres](https://mapatrafico.mitma.es/) · [exact download/API](https://mapatrafico.mitma.es/informes/anejos/Bloque%202.pdf)

| Property | Audited value |
|---|---|
| format | pdf |
| years | [2022] |
| geographic_level | province, State Road Network only |
| observation_unit | province-network-year |
| key_variables | See feasibility audit |
| denominator | million vehicle-kilometres, all vehicles, State Road Network (RCE) |
| known_limitations | VKT rounded to 0.1 million. Missing territories excluded, never zero-filled. Road-owner classifications may differ between registries; association is territorial burden per traffic, not personal risk. |
| update_frequency | annual |
| schema_version | PDF page 3, year 2022, published 27 February 2024; audited 2026-10-03 |
| comparability | Only DGT injury crashes labelled Estatal, year 2022, matched province; no all-road rates |
| enabled | True |
| sample_retrieved_at | 2026-10-03T17:27:29.917519+00:00 |
| sample_sha256 | 3bdb0d71ead2877b6bdd952fee7ee3a6b8491bff99ec3cad5fde52e01bc0dd85 |
| reuse | Publisher terms apply; attributed factual aggregates; raw PDF not redistributed |

[Reuse terms](https://www.transportes.gob.es/informacion-para-el-ciudadano/informacion-administrativa/aviso-legal).

## ncid_motor_2024

[Central Bank of Ireland · Irish private motor insurance: ultimate claims, matched exposure and settlements, report 7](https://www.centralbank.ie/statistics/data-and-analysis/national-claims-information-database/ncid-private-motor-insurance) · [exact download/API](https://www.centralbank.ie/docs/default-source/statistics/data-and-analysis/national-claims-information-database/annex-private-motor-insurance-report-7.xlsx?sfvrsn=9a066f1a_12)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | national / country |
| observation_unit | country-year-quarter / claim type |
| key_variables | ['Background', 'PremData', 'UltData', 'Figure13', 'Figure14_19', 'Figure20', 'Figure23', 'Figure24', 'Table9', 'Table10', 'Table 11', 'Table12_13', 'Table14_15', 'Figure26', 'Figure27', 'Table16', 'Table17', 'Figure28', 'Figure29', 'Misc1', 'Misc2', 'Misc3', 'Misc4', 'Figure30', 'Table22', 'Table23', 'Figure32_33', 'Figure34', 'Table25_26', 'Table27_28', 'Misc5', 'Figure35', 'Figure36', 'Figure37'] |
| denominator | Earned policy-years; matching 94% premium-market cohort in UltData |
| known_limitations | Ultimate claims are insurer estimates incl. nils; settlement years differ from accident years. Coverage-specific exposure is not inferred from unmatched PremData. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.172757+00:00 |
| sample_sha256 | 7636369a3134533fb32cc8db8adbf3e15b3663ea0dba4e472da5decd2a173994 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.centralbank.ie/re-use-of-public-sector-information).

## ncid_methodology

[Central Bank of Ireland · NCID report 7 definitions and market coverage](https://www.centralbank.ie/statistics/data-and-analysis/national-claims-information-database/ncid-private-motor-insurance) · [exact download/API](https://www.centralbank.ie/docs/default-source/statistics/data-and-analysis/national-claims-information-database/private-motor-insurance-report-7-national-claims-information-database.pdf?sfvrsn=33056f1a_7)

| Property | Audited value |
|---|---|
| format | pdf |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | national / country |
| observation_unit | methodology |
| key_variables | [] |
| denominator | not applicable |
| known_limitations | 2024 market shares measured by premiums: ultimate 94%, settlements 88%; national only. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.174757+00:00 |
| sample_sha256 | 95419df24d81abf3ee5e6420171141d783f74a970d742d2ab5ba381744f89767 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.centralbank.ie/re-use-of-public-sector-information).

## eurostat_sex_users

[Eurostat · Road deaths by recorded sex and person category, 2010–2024](https://ec.europa.eu/eurostat/cache/metadata/en/tran_sf_road_esms.htm) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tran_sf_roadus?lang=EN&age=TOTAL&unit=NR&sinceTimePeriod=2010&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | national / country |
| observation_unit | country-year-sex-person category |
| key_variables | ['freq', 'sex', 'age', 'unit', 'pers_cat'] |
| denominator | Sex-specific population; no distance or driver exposure |
| known_limitations | 30-day deaths; category totals overlap with TOTAL; flags and missing cells retained; sex is recorded administrative sex. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.172757+00:00 |
| sample_sha256 | b3d232687db561316f3a22033d222f2d48bd40c132e6d6305fbeb71a57f0e347 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## eurostat_sex_population

[Eurostat · Population by sex on 1 January, 2010–2024](https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjan?lang=EN&age=TOTAL&unit=NR&sinceTimePeriod=2010&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | national / country |
| observation_unit | country-year-sex |
| key_variables | ['freq', 'unit', 'age', 'sex'] |
| denominator | resident population |
| known_limitations | Population is a burden denominator, not kilometres travelled or policy exposure. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.172757+00:00 |
| sample_sha256 | 24a8fdf51b492d61aafca02dee0864eb2f8ef68f3b7fbe9900d6c3fe446b8c81 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## eurostat_ie_hicp

[Eurostat · Ireland annual all-items HICP, 2010–2024](https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_aind/default/table) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_aind?lang=EN&unit=INX_A_AVG&coicop=CP00&geo=IE&sinceTimePeriod=2010&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | national / country |
| observation_unit | country-year |
| key_variables | ['freq', 'unit', 'coicop'] |
| denominator | annual all-items consumer price index |
| known_limitations | Deflates nominal insurance costs to 2024 euros; broad consumer basket, not a dedicated repair-cost index. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.175758+00:00 |
| sample_sha256 | dbf219d0f7169089f05e0a97672a99945beac84f82e500710f81c9b014d03e1d |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## eurostat_es_age_population

[Eurostat · Spanish population by single-year age and sex, 2022–2024](https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table) · [exact download/API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjan?lang=EN&unit=NR&geo=ES&sinceTimePeriod=2022&untilTimePeriod=2024)

| Property | Audited value |
|---|---|
| format | json |
| years | [2022, 2023, 2024] |
| geographic_level | national / country |
| observation_unit | country-year-age-sex |
| key_variables | ['freq', 'unit', 'age', 'sex'] |
| denominator | resident population |
| known_limitations | Fixed pooled Spanish 2024 population supports descriptive direct age standardization; unknown ages/sex remain excluded and disclosed. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:08.200627+00:00 |
| sample_sha256 | 5b7dfb104793c8d7bbb66328f8228375e94b5cbbd0a8d84024496978b0d73986 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://ec.europa.eu/eurostat/about-us/policies/copyright).

## dgt_demographics_2024

[DGT · Injury-crash statistical tables: sex, age, road users, vehicle age and crash types, 2024](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Accidentes-con-victimas-Tablas-estadisticas-2024/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Tablas_estadisticas_Accidentes_30_dias/Accidentes-con-victimas-Tablas-estadisticas-2024.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2024] |
| geographic_level | national / country |
| observation_unit | national-zone-age-sex-road user |
| key_variables | ['Índice', 'TABLA 1.1', 'TABLA 1.1.C.A.', 'TABLA 1.3', 'TABLA 1.6', 'TABLA 2.2.I', 'TABLA 2.2.U', 'TABLA 2.3', 'TABLA 3.1', 'TABLA 3.2', 'TABLA 3.3', 'TABLA 3.4.I', 'TABLA 3.4.U', 'TABLA 3.5', 'TABLA 3.7', 'TABLA 4.1.I', 'TABLA 4.1.U', 'TABLA 4.1.1.I', 'TABLA 4.1.1.U', 'TABLA 4.2.I', 'TABLA 4.2.U', 'TABLA 4.4.I', 'TABLA 4.4.U', 'TABLA 5.1', 'TABLA 5.2', 'TABLA 5.3', 'TABLA 6.1.I', 'TABLA 6.1.U', 'TABLA 7.1', 'TABLA 7.2.I', 'TABLA 7.2.U', 'TABLA 7.3.I', 'TABLA 7.3.U', 'TABLA 7.4.I y U', 'TABLA 8.1.I', 'TABLA 8.1.U', 'TABLA 8.1.1', 'TABLA 8.2.I', 'TABLA 8.2.U', 'TABLA 8.3'] |
| denominator | Victims or involved drivers; not crash counts |
| known_limitations | Sex recorded for persons, not entire crashes; involved drivers are not at-fault drivers; aggregate tables have overlapping totals. Fatality follow-up 30 days. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.175758+00:00 |
| sample_sha256 | 8fccd78aa030e093ed057b8c0e3f55d4e9b545f70c6dd3f53aa0df815f24ff05 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_demographics_2023

[DGT · Injury-crash statistical tables: sex, age, road users, vehicle age and crash types, 2023](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Accidentes-con-victimas-Tablas-estadisticas-2023/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Anuario-Estadistico-de-Accidentes/Accidentes-con-victimas-Tablas-estadisticas-2023.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2023] |
| geographic_level | national / country |
| observation_unit | national-zone-age-sex-road user |
| key_variables | ['Índice', 'TABLA 1.1', 'TABLA 1.1.C.A.', 'TABLA 1.3', 'TABLA 1.6', 'TABLA 2.2.I', 'TABLA 2.2.U', 'TABLA 2.3', 'TABLA 3.1', 'TABLA 3.2', 'TABLA 3.3', 'TABLA 3.4.I', 'TABLA 3.4.U', 'TABLA 3.5', 'TABLA 3.7', 'TABLA 4.1.I', 'TABLA 4.1.U', 'TABLA 4.1.1.I', 'TABLA 4.1.1.U', 'TABLA 4.2.I', 'TABLA 4.2.U', 'TABLA 4.4.I', 'TABLA 4.4.U', 'TABLA 5.1', 'TABLA 5.2', 'TABLA 5.3', 'TABLA 6.1.I', 'TABLA 6.1.U', 'TABLA 7.1', 'TABLA 7.2.I', 'TABLA 7.2.U', 'TABLA 7.3.I', 'TABLA 7.3.U', 'TABLA 7.4.I y U', 'TABLA 8.1.I', 'TABLA 8.1.U', 'TABLA 8.1.1', 'TABLA 8.2.I', 'TABLA 8.2.U', 'TABLA 8.3'] |
| denominator | Victims or involved drivers; not crash counts |
| known_limitations | Sex recorded for persons, not entire crashes; involved drivers are not at-fault drivers; aggregate tables have overlapping totals. Fatality follow-up 30 days. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.176758+00:00 |
| sample_sha256 | 6f0f6257b649ab762f025c922b01aff08df54f83eb601d15919005000797bf73 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## dgt_demographics_2022

[DGT · Injury-crash statistical tables: sex, age, road users, vehicle age and crash types, 2022](https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Accidentes-con-victimas-Tablas-estadisticas-2022/) · [exact download/API](https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Tablas_estadisticas_Accidentes_30_dias/Accidentes_con_victimas_Tablas_estadisticas_2022.xlsx)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2022] |
| geographic_level | national / country |
| observation_unit | national-zone-age-sex-road user |
| key_variables | ['Índice', 'TABLA 1.1', 'TABLA 1.1.C.A.', 'TABLA 1.3', 'TABLA 1.6', 'TABLA 2.2', 'TABLA 2.3', 'TABLA 3.1', 'TABLA 3.2', 'TABLA 3.3', 'TABLA 3.4.I', 'TABLA 3.4.U', 'TABLA 3.5', 'TABLA 3.7', 'TABLA 4.1.I', 'TABLA 4.1.U', 'TABLA 4.1.1.I', 'TABLA 4.1.1.U', 'TABLA 4.2.I', 'TABLA 4.2.U', 'TABLA 4.4.I', 'TABLA 4.4.U', 'TABLA 5.1', 'TABLA 5.2', 'TABLA 5.3', 'TABLA 6.1.I', 'TABLA 6.1.U', 'TABLA 7.1', 'TABLA 7.2.I', 'TABLA 7.2.U', 'TABLA 7.3.I', 'TABLA 7.3.U', 'TABLA 7.4.I y U', 'TABLA 8.1.I', 'TABLA 8.1.U', 'TABLA 8.1.1', 'TABLA 8.2.I', 'TABLA 8.2.U', 'TABLA 8.3'] |
| denominator | Victims or involved drivers; not crash counts |
| known_limitations | Sex recorded for persons, not entire crashes; involved drivers are not at-fault drivers; aggregate tables have overlapping totals. Fatality follow-up 30 days. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:07.922347+00:00 |
| sample_sha256 | dda0da1b866a16ef3df1f2839d45ed694582dd506a5345582752603b6d7dd223 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.dgt.es/contenido/aviso-legal/).

## destatis_damage_history

[Destatis · Police-recorded German road accidents: historical damage categories](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Verkehrsunfaelle/Publikationen/_publikationen-verkehrsunfaelle.html) · [exact download/API](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Verkehrsunfaelle/Publikationen/Downloads-Verkehrsunfaelle/statistischer-bericht-verkehrsunfaelle-zeitreihen-5462403.xlsx?__blob=publicationFile&v=17)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024] |
| geographic_level | national / state |
| observation_unit | country-year |
| key_variables | ['Titel ', 'Informationen_Barrierefreiheit', 'Inhaltsübersicht ', 'GENESIS-Online', 'Impressum ', 'Informationen_zur_Statistik', '46241-b01', '46241-01', '46241-02', '46241-03', '46241-04', '46241-05', '46241-06', '46241-07', '46241-08', '46241-09', '46241-10', '46241-11', '46241-12', '46241-13', '46241-14', '46241-15', '46241-16', '46241-17', '46241-18', '46241-19', '46241-20', '46241-21', '46241-22', '46241-23', '46241-24', '46241-25', '46241-26', '46241-27', '46241-28', '46241-29', '46241-30', '46241-31', 'Erläuterung_zu_CSV-Tabellen', 'csv-46241-b01', 'csv-46241-01', 'csv-46241-02', 'csv-46241-03', 'csv-46241-04', 'csv-46241-05', 'csv-46241-06', 'csv-46241-07', 'csv-46241-08', 'csv-46241-09', 'csv-46241-10', 'csv-46241-11', 'csv-46241-12', 'csv-46241-13', 'csv-46241-14', 'csv-46241-15', 'csv-46241-16', 'csv-46241-17', 'csv-46241-18', 'csv-46241-19', 'csv-46241-20', 'csv-46241-21', 'csv-46241-22', 'csv-46241-23', 'csv-46241-24', 'csv-46241-25', 'csv-46241-26', 'csv-46241-27', 'csv-46241-28', 'csv-46241-29', 'csv-46241-30', 'csv-46241-31'] |
| denominator | all police-recorded crashes |
| known_limitations | National time series revision contains 1991–2025; analysis selects 2010–2024. Minor damage not reported to police is missing; severe-property definition has historical changes. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:08.111628+00:00 |
| sample_sha256 | 4fda91bf992a773ff6cea56f98477e37b547ddddd84f4102260770ebf22e93ae |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.destatis.de/EN/Service/Terms-Conditions/_node.html).

## destatis_damage_2024

[Destatis · German police accidents by damage class, state and location, 2024](https://www.destatis.de/EN/Themes/Society-Environment/Traffic-Accidents/Tables/accidents-registered-police.html) · [exact download/API](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Verkehrsunfaelle/Publikationen/Downloads-Verkehrsunfaelle/statistischer-bericht-verkehrsunfaelle-jahr-2080700247005.xlsx?__blob=publicationFile&v=3)

| Property | Audited value |
|---|---|
| format | xlsx |
| years | [2024] |
| geographic_level | national / state |
| observation_unit | state-location-year / crash |
| key_variables | ['Titel ', 'Informationen_Barrierefreiheit', 'Inhaltsübersicht ', 'GENESIS-Online', 'Impressum ', 'Informationen_zur_Statistik', '46241-b01', '46241-01', '46241-02', '46241-03', '46241-04', '46241-05', '46241-06', '46241-07', '46241-08', '46241-09', '46241-10', '46241-11', '46241-12', '46241-13', '46241-14', '46241-15', '46241-16', '46241-17', '46241-18', '46241-19', '46241-20', '46241-21', 'Erläuterung_zu_CSV-Tabellen', 'csv-46241-b01', 'csv-46241-01', 'csv-46241-02', 'csv-46241-03', 'csv-46241-04', 'csv-46241-05', 'csv-46241-06', 'csv-46241-07', 'csv-46241-08', 'csv-46241-09', 'csv-46241-10', 'csv-46241-11', 'csv-46241-12', 'csv-46241-13', 'csv-46241-14', 'csv-46241-15', 'csv-46241-16', 'csv-46241-17', 'csv-46241-18', 'csv-46241-19', 'csv-46241-20', 'csv-46241-21'] |
| denominator | all police-recorded crashes |
| known_limitations | 16 states; serious property-only, intoxicant property-only and other property-only are distinct classifications. No insured exposure or repair costs. |
| update_frequency | annual |
| schema_version | audited 2026-10-03 |
| comparability | Separate descriptive panels; not merged into the territorial composite or severity training |
| enabled | True |
| sample_retrieved_at | 2026-10-03T21:58:08.122137+00:00 |
| sample_sha256 | 9156b04df619035c89b4b966cc28f851ac42d50f8c84255d22ee8c917cd459b2 |
| reuse | Publisher reuse terms; factual aggregates attributed; original workbooks not redistributed |

[Reuse terms](https://www.destatis.de/EN/Service/Terms-Conditions/_node.html).

## Audited sources excluded from ingestion

[Transport Ministry 2024 infrastructure report](https://publicaciones.transportes.gob.es/downloadcustom/sample/4057): PDF, provincial vehicle-kilometres by road ownership, annual, estimated values. Network coverage does not match all-road crash numerators. No full-network VKT denominator was built.

The infrastructure report remains a research lead, not a source merged into the analytical facts. UNESPA 2024 is ingested separately; see [insurance](insurance.md). See [feasibility](data_feasibility.md) and [limitations](limitations.md).
