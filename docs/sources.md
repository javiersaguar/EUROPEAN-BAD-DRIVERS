# Source register

Audited 3 October 2026. Exact URLs, hashes, retrieval times and schema metadata are versioned in `configs/sources.yaml`. Runtime provenance is in the local `data/raw/manifest.json`. Source code is MIT; datasets retain their own conditions. The pipeline transforms original data into aggregated analysis and credits publishers; no raw workbooks are redistributed.

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

## Audited sources excluded from ingestion

[UNESPA automobile claims announcement 2024](https://www.unespa.es/notasdeprensa/siniestros-automovil-datos-2024/): HTML announcement, annual update, municipal/provincial discussion of claims. Direct automated access returned HTTP 403. No complete claims count × insured vehicle-year table was downloaded; no numerical panel or reuse licence is inferred from a press release.

[Transport Ministry 2024 infrastructure report](https://publicaciones.transportes.gob.es/downloadcustom/sample/4057): PDF, provincial vehicle-kilometres by road ownership, annual, estimated values. Network coverage does not match all-road crash numerators. No full-network VKT denominator was built.

Both are documented research leads, not sources merged into the analytical facts. See [feasibility](data_feasibility.md) and [limitations](limitations.md).
