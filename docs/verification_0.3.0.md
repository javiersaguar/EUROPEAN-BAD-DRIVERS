# Verification of release 0.3.0

Local execution on 4 October 2026, Windows / Python 3.12 / Node 24.

| Check | Actual result |
|---|---|
| `uv run ebdi all` | Completed successfully against all 31 cached, hash-verified active official sources; rebuilt core facts, analysis, models, extended ingestions, analysis and public aggregate contract |
| New source/model audits | National DGT deaths reconciled, collision partitions exact, fixed population weights verified, source discrepancies and missing values retained, compatible NCID exposure kept separate from settlements |
| `uv run pytest -q` | 80 passed locally, including raw PDF roundtrip; CI skips that raw-file-dependent check when the source PDF is absent |
| Ruff and mypy | Checks and formatting passed; 28 source modules type checked |
| Executed notebooks | All five completed; the new notebook includes source audits, six substantive explorations and five actual scientific figures |
| Frontend | TypeScript/build, ESLint, Prettier and 8 unit checks passed |
| Browser checks | 45 passed, 1 intentional desktop skip; all thirteen pages passed desktop/mobile axe WCAG A/AA, reflow and console checks; filter restoration, exports, missing-cell preservation, unknown-sex exposure and table alternatives exercised |
| Source monitor | 31 active releases reachable and byte-identical to audited source hashes; no original revision activated |

Browser tests use actual Chromium, including real CSV/PDF/SVG/PNG downloads. The single intentional browser skip is the mobile-only menu test in the desktop project. Manual visual checks cover the new pages at desktop and mobile widths, abbreviated axes, unknown-cell behavior and graph interpretations.

The full analytical formulas and original-data limitations are in [extended analysis](extended_analysis.md). This verification does not establish personal driving risk, responsibility, causality or equivalent reporting coverage across source countries.

Continuous integration and public deployment results are appended after their actual runs complete.
