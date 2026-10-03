# Findings from the audited release

Generated with `ebdi analysis`. Sources: DGT injury-crash releases 2022–2024 and INE annual census table 67988.

- 301,218 recorded injury crashes across three years and 52 provinces.
- In 2024: 101,996 injury crashes and 1,785 deaths at 30 days.
- Raw-count vs population-rate rank correlation: **0.455** (Spearman).
- Injury-rate vs fatality-rate rank correlation: **-0.352**.
- Largest injury-crash population rate: **Melilla**;
  largest fatality population rate: **Zamora**. These are observed territorial burdens.
- Default index rank correlation, 2022 vs 2024: **0.904**.
- Maximum rank span across 500 alternative weight draws: **50.0 places**.

These comparisons describe this release, these years and these measured denominators. They do not identify driving ability or causal effects.
Weights and normalization are published in `configs/index_weights.yaml`. Urban and collision-specific metrics overlap with injury crashes;
the correlation figure exposes potential double-counting. Scenario bands measure weight sensitivity, while bootstrap bands measure a separate
hypothetical event-sampling model. Neither covers reporting bias or uncertainty in travel exposure.

See `outputs/tables/` for individual metrics, 24 named method scenarios, random-weight summaries, conditional bootstrap intervals and year stability.
The European chart compares only fatalities using a shared 30-day definition; no cross-country injury/claim composite is supported.
