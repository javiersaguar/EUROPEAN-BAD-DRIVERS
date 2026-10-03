# Authorized aggregate insurer exposure adapter

No complete modern material-claims/insured-vehicle-year panel has been fabricated. The public UNESPA publication is still the observed insurance source. This adapter provides a validated integration point when a licensed aggregate release is available.

CSV columns must be exactly:

```csv
province_code,year,coverage,claims,insured_vehicle_years
```

Province: official two-digit INE code 01–52. Year: integer, 2000 through the current year. Coverage: `rc_material`, `own_damage` or `glass`. Claims: nonnegative integer. Exposure: positive insured vehicle-years in **the same portfolio, coverage, geography and year** as the numerator. One row per province/year/coverage; duplicates, missing/nonfinite values and participant-level columns are rejected. Partial territory coverage remains partial.

Metadata JSON must contain `publisher`, `source_url` (HTTPS), `published_date` (ISO date), `reuse_authorized` (true), and equal nonempty `numerator_scope` / `denominator_scope`. Record the portfolio and insurance definition there; permission must come from the actual data owner or licence. The declaration is a provenance gate, not a legal assessment of the source licence.

```sh
uv run ebdi claims-import --file <aggregate.csv> --metadata <provenance.json>
uv run ebdi site
```

Outputs: `insurance_exposure.csv` and metadata JSON. Rate = claims / insured vehicle-years × 100, with Poisson intervals. The rate is claim frequency, potentially including multiple claims per vehicle; it is not a binomial probability of a personal crash. Validated releases can be included in the static publication after review. The default release contains no example insurer observations; synthetic data exist only inside adapter tests.
