# Release 0.3.0

4 October 2026 · Javier Saguar.

The observatory now analyzes material-damage records and person demographics throughout the reproducible pipeline and public frontend. Eleven additional official releases bring the register to 32 sources, 31 active. The new analysis uses NCID private motor claims in Ireland, German police property-only crashes, Spanish DGT statistical yearbooks, Eurostat sex/person-role mortality and population, and Irish HICP.

Three new public views contain 21 charts: **Daños materiales · Europa**, **Personas y sexo**, and **Tipos de accidente**. Every chart includes interpretation, scope, primary sources, a table alternative and CSV/PDF/SVG/PNG export. State, claim cohort/category, sex, age, population role, road zone, outcome, user role and year filters persist in the URL. The overview and Spanish insurance page link directly to the extensions. The frontend has thirteen views in total.

## Delivery stages

1. **Official-source audit and ingestion.** Immutable hashed originals, validated source layouts, category mapping, conservation checks and explicit original exceptions. Raw workbooks remain local. CSV and Parquet products preserve source missing values.
2. **Descriptive analysis.** Matched insured exposure, occurrence/settlement separation, HICP-adjusted costs, changes against 2019, German damage classes, Spanish crude/age-adjusted mortality, EU sex/user rates, collision-specific severity and vehicle-age distributions. Five standalone SVG figures and a fifth executed notebook accompany the results.
3. **Public frontend and verification.** New discoverable views, graph readings, table alternatives, explicit original-data notes, compact aggregate transport, responsive charts and tested filter/export behavior. Source and availability monitoring includes the new releases.

## Original-data issues surfaced

The release preserves the NCID 2024 summary discrepancy of 18 liquidations, nonadditive estimated injury bands, missing DGT urban bicycle cells, DGT driver-victim component/total differences, one absent driver-involvement total, the unlabelled 87-count vehicle-type column and the absent Berlin rural location. It does not repair original statistics by guessing. Exact checks, policies and results are documented in [extended analysis](extended_analysis.md), [source register](sources.md), [dictionary](data_dictionary.md) and the dataset quality reports.

## Analytical boundaries

Insured claims, police crashes and people are separate units. Property-only German data and insured Irish data are not extrapolated to Spain or blended into a common ranking. Sex describes recorded persons, not the sex of a crash or a responsible driver. Age adjustment controls only five known age bands. There is still no complete Spanish provincial bodywork claim/exposure panel or sex-by-material-claim dataset in the selected public sources.

The existing conditional-severity experiment is reproduced with its existing inputs and temporal protocol; the aggregate demographic tables do not supply new individual training examples. No causal, fault or personal-risk claim is made. See [verification](verification_0.3.0.md) for actual execution results and deployed checks.

All delivery commits use Javier Saguar as sole author and committer, with no co-author trailer.
