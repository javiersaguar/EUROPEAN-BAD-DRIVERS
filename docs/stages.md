# Delivery stages

1. **Feasibility:** real downloads, schema inspection, source registry and methodological decisions.
2. **Spain pipeline:** validation, province/year harmonization, explicit population/vehicle/driver rates,
   Parquet, DuckDB and quality reports.
3. **Index experiments:** individual measures, configurable weights, multiple normalizations,
   uncertainty and sensitivity/stability reports.
4. **Dashboard and Europe:** interactive Spain exploration, laboratory, trends and a comparable
   European fatality-only extension. Historical insurance is retained for the feasibility audit only.
   A follow-up adds audited UNESPA 2024 material-damage tables as a separate insurance explorer; see [insurance](insurance.md).
5. **Conditional-severity ML:** temporal evaluation against a dummy baseline, logistic regression
   and histogram gradient boosting; calibration and association explanations. No personal-risk calculator.
6. **Publication:** executed notebooks, original figures, reproduction commands, automated checks and docs.

Each stage has a separate commit. Javier Saguar is the sole commit author; no co-author trailers are used.
Data-dependent features are delivered only where the audited sources support them. Sources which fail
access or comparability checks are documented explicitly instead of replaced with fabricated observations.
