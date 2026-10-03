# Methodology

The research question is how observed territorial rankings change when the outcome, exposure proxy and index definition change. This release describes recorded injury-crash burden. It does not identify driving ability, resident drivers' accident risk or causal effects. Audit date: 3 October 2026.

## Observation and geography

DGT accident workbooks contain one recorded **crash with victims**, with 24-hour and 30-day victim totals. The primary key is `(year, ID_ACCIDENTE)`. Province is the location of the crash, including Ceuta and Melilla. The province-year panel contains 52 × 3 rows for 2022–2024. Counts are grouped at crash location, then joined to same-year exposure stocks by validated two-digit province code. Population supplies autonomous-community labels. Numeric province codes and a strict accent-normalized alias mapping avoid fuzzy joins. Duplicated or unmatched keys fail processing.

GISCO NUTS 2024, level 3, EPSG:4326 at 1:20 million supplies the local map. Balearic and Canary island geometries are aggregated to their provinces using a published crosswalk. This is visualization geography, not a source of exposures. Municipality code 0 is unknown, so municipality risk rankings are outside this release.

## Numerators and denominators

| Metric | Numerator |
|---|---|
| Injury crashes | Number of DGT crash records |
| Fatalities | Sum of `TOTAL_MU30DF`: people dying within 30 days, all road users |
| Urban crashes | Records with `ZONA_AGRUPADA = 2` |
| Rear/lateral crashes | `TIPO_ACCIDENTE` in 2, 3, 4: frontolateral, lateral and rear-end |
| Severe crashes | At least one 30-day fatality or hospitalized injured person |

Each numerator has rates per 100,000 population, registered vehicles and driving-permit holders when that denominator exists. A rate is `numerator / denominator × 100,000`. Europe uses fatalities per **million** residents. A death count and a crash count have different observation units.

Population is the INE annual census, table 67988, at **1 January of the same year**. DGT vehicle stocks are at year end, sheet `V_4`, total column: they exclude mopeds and include trailers/semitrailers. Driver stocks use sheet `P_6_1_1_10`, driving-permit column, excluding special licences. Stocks are assigned to registration/residence, while crashes are assigned to location. These are territorial burden denominators and imperfect travel exposure proxies. A separate 2022 RCE panel matches state-owned-road counts to provincial vehicle-kilometres, retaining administrative network caveats and missing territories. There is no complete all-road VKT or insured-vehicle-year denominator. Audited vehicle and driver stocks exist for 2022–2024. Five truncated 2023 fleet labels have exact, source-scoped aliases, with 52-row and national-total reconciliation. No interpolation is applied.

Unknown collision codes remain explicit unknowns (35 records in 2024). They count toward all injury crashes but are not assigned to rear/lateral crashes. Missing exposure is never treated as zero. Negative counts fail, and missing/nonpositive exposures produce missing rates. Observed zeros remain zeros. A absent crash group in a fully validated national file is a structural zero; an absent source observation is missing.

## Statistical intervals

Metric intervals use exact central Poisson 95% limits from chi-square quantiles, conditional on a fixed denominator. Zero events have a positive upper bound. They express a hypothetical repeat-event counting model, not uncertainty in a literal census total. Independence, a constant underlying rate and a correct denominator are modeling assumptions. Fatalities in the same crash may be correlated; the Poisson approximation can understate uncertainty. Intervals omit reporting bias, denominator uncertainty, visitor/commuter flows and unmeasured travel exposure.

The minimum index sample is 30 recorded injury crashes. `small_sample` flags smaller provincial samples. It does not guarantee stable fatality rates; counts and intervals remain visible. Municipal shrinkage is not implemented because reliable municipality exposure/join coverage is absent.

## Composite experiment

Default components, all per 100,000 residents, are injury crashes (0.40), urban crashes (0.25), rear/lateral crashes (0.20) and fatalities (0.15). Weights are explicit in `configs/index_weights.yaml` and can change interactively. The default score is the weighted sum of within-year percentile scores. **Rank 1 means highest experimental score**, not worst drivers. Percentile normalization is `(average ascending rank − 1)/(n − 1) × 100`; tied values receive average ranks. Constant components are neutral (50 on bounded scales, zero on standardized scales).

Alternatives are population-standard-deviation z-scores, robust z-scores `(x − median)/(1.4826 × MAD)` (standard-deviation fallback when MAD is zero), and min–max scaling. Only percentile and min–max are bounded 0–100. Weights are normalized to sum to one; negatives, nonfinite values and all-zero weights fail. A zero-weight component is ignored. A province needs all active components and the minimum sample. Missing components are never implicitly reweighted. Normalization uses the eligible cohort, so changing eligibility can change scores.

Injury, urban and collision-specific components overlap. The component correlation figure exposes double-counting; the selected weights are analyst preferences, not estimated scientific importance. Scores are normalized separately each year, so score changes cannot measure absolute improvement. Use the underlying rates for temporal change and Spearman correlation for rank stability.

## Sensitivity and bootstrap

Published sensitivity uses 500 Dirichlet(1,1,1,1) weight draws, seed 42, on the same eligible latest-year cohort. Min/max and 5th/95th rank quantiles are **scenario summaries**, not confidence intervals. There are also 24 named scenarios: default, equal weights and four single-component choices across four normalizations.

The separate 200-repeat Poisson event bootstrap groups crashes by province, urban flag, rear/lateral flag and fatality count, and resamples cell event counts. This preserves within-crash component overlap and multi-fatality counts. It holds population and baseline eligibility fixed, recomputes normalized scores/ranks, and reports 2.5th/97.5th percentiles. This is conditional model-based event-sampling uncertainty, not uncertainty about weights or reporting. Systematic bias is outside both analyses.

## European comparability

The European extension joins Eurostat `tran_sf_roadus` (all ages, sexes and road users; number of 30-day deaths) and `demo_pjan` (all residents, 1 January), for EU-27 in 2022–2024. All source status flags survive processing and appear in the dashboard. A country/year/variable table records inclusion, definition, flags and limitations. A shared death definition permits descriptive mortality comparison; it does not erase registration, follow-up, population or mobility differences. Injury crashes, modern insurance claims and vehicle-kilometres are excluded from the European composite because no comparable panel was validated here. Spain's fatality totals reconcile to the audited ERSO workbook. The separate UNESPA 2024 insurance explorer displays published national coverage shares/costs and selected municipal relative differences, preserving missing counts/exposures; it is outside these mortality and composite calculations. See [insurance definitions](insurance.md).

## Modeling

The valid target is severe outcome **conditional on a recorded injury crash**. Non-severe recorded crashes form its negative class; no non-crash controls exist. Model selection uses 2022 training and 2023 validation log loss, then refits on 2022–2023 and evaluates 2024. All candidates and a fixed 0.5 threshold are specified before test inspection. Feature selection excludes victim totals, outcomes and IDs. Some collision/circumstance attributes are only known after the event, so this is a descriptive model. See the [model card](model_card.md) for metrics, calibration, SHAP and limitations. No personal risk calculator is supported.
