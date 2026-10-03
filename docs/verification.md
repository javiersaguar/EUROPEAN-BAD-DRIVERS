# Verification of the delivered release

Follow-up: the material-damage insurance explorer was reproduced from UNESPA's hashed PDF, with 11 national coverages, 80 selected municipality-coverage rows and 50 all-coverage provincial rows. The expanded suite passes 61 tests locally, including the PDF-to-published-tables roundtrip, standard public-PDF transport and insurance dashboard filters. Ruff lint/format and mypy pass on 17 source modules. Browser inspection confirms the new Golpes de chapa section and the absence of the Deploy button using Streamlit's minimal toolbar configuration. The earlier six-stage verification below remains the record of the initial release.

Verified locally on Windows, Python 3.12, on 3 October 2026.

| Check | Evidence |
|---|---|
| End-to-end core reproduction | `uv run --extra explain ebdi all` completed with hash-verified cached official files, processing, analysis and all three models |
| Processing after expanded category validation | Passed for 2022–2024; 301,218 original records, 156 province-years, 81 EU country-years |
| Published figures and EDA | Generated PNG and SVG figures, counts/rates, nine observed crash dimensions, sensitivity and stability tables |
| SHAP execution | 400 seeded 2024 crashes; maximum raw-log-odds additivity error 3.55e-15 |
| Notebooks | All four notebooks executed with nbclient in the project environment; assertions passed |
| Tests | 53 tests covering data contracts, formulas, cache integrity, published conservation, modeling and dashboard behavior |
| Static checks | Ruff lint/format and mypy on 16 source modules |
| UI | Streamlit AppTest covers all seven views; browser inspection confirms the overview and province map, including island aggregation |
| Authorship | Javier Saguar is the sole author and committer; no co-author trailers |

The workflow is configured for GitHub-hosted Windows and Linux. Optional Docker configuration and Python 3.13 have not been executed locally. Real publisher revisions may require a new audit; a cached reproduction is not a promise that live endpoints remain byte-identical indefinitely.
