# Material-damage insurance explorer

The dashboard's **Golpes de chapa** section uses real UNESPA observations for **2024**, published on 10 February 2026. The initial feasibility audit inspected the announcement but missed its linked PDF. This extension corrects that assessment: usable factual tables exist, although a complete claims/exposure panel still does not.

[Official UNESPA PDF](https://www.unespa.es/main-files/uploads/2026/02/NdP-Siniestros-del-seguro-de-auto-2024-FINAL.pdf), tables 1, 2, 8 and 9. UNESPA credits MicroESA and FIVA. The registry records the precise URL, retrieval time and SHA-256. The publisher's PDF is downloaded locally, never redistributed under the project's MIT licence.

| Published artifact | Grain | What it measures |
|---|---|---|
| `insurance_coverage.csv` | 11 national coverages, 2024 | Share of claims and payments (%); average cost per claim (€) |
| `insurance_municipal.csv` | 80 selected municipality-coverage observations, 2024 | 20 higher and 20 lower published relative differences per coverage: 40 material, 40 bodily |
| `insurance_provinces.csv` | 50 provinces, 2024 | Claim counts and payments across **all** coverages |
| `insurance_quality.json` | Report release | Source hash, published totals, coverage checks, reconciliation differences and unavailable quantities |

RC material represents liability claims for material damage and is the publisher's category for minor accidents / “golpes de chapa”. It is distinct from bodily liability, own-vehicle damage and glass coverages. One accident may generate both material and bodily claims. The report does not supply a count restricted to collisions with **no injuries**, uninsured events, unreported collisions or unique accidents across coverages.

Municipal rankings cover cities above 50,000 inhabitants. Only the published extremes are present; an absent city has an unknown value, not zero. Labels and abbreviations are preserved as printed. `source_order` is the row order within a publisher's selected table, not a computed national rank. `relative_difference_pct` is the published difference relative to the national reference. For example, Melilla's +40.99% for RC material is **not** a 40.99% absolute accident probability. No municipal claim counts or insured vehicle-years are supplied, so the project cannot reproduce the underlying frequencies or construct uncertainty intervals or individual risk estimates.

National RC material accounts for 15.85% of claims and has a mean cost of €1,363. The total of 11,071,215 claims covers **all categories**, including roadside assistance; it is not a property-damage-only crash total. National shares are rounded; multiplying them by the total would not yield exact coverage counts, so none are fabricated.

The provincial table omits Ceuta and Melilla. Its published sum is 11,053,508 claims, 17,707 below the national total; payments are €24,573,178 below the national figure. Differences are retained and disclosed without assigning them to missing territories or inferring their cause. No provincial minor-accident frequency ranking is derived from these all-coverage totals.

## Reproduction and validation

```sh
uv run ebdi download
uv run ebdi insurance
```

`ebdi all` and `make all` include this stage. Standard urllib can retrieve the public PDF; the custom requests research client receives HTTP 403 from this publisher. No cookies or credentials are used. Downloaded payloads must start with the PDF signature and match the audited SHA-256. Extraction requires this exact revision; future PDFs require a new layout/definition audit even after download refresh.

Default PDF table detection loses alternating shaded rows. The extraction therefore uses percentage anchors and audited column coordinates, retaining wrapped labels. It validates all 11 national coverages, shares summing to 100 within rounding, 50 unique provinces, and all four 20-row municipal selections. The source pages were rendered and checked visually. Published-result tests verify reference observations, wrapped labels, coverage selection and absence of invented exposure/probability fields. Dashboard tests verify navigation from Panorama and both municipal selections.

These insurance observations remain separate from DGT injury-crash counts, exposure rates, the composite index, European mortality comparisons and conditional-severity models. They extend the project's coverage without changing any of those published results.
