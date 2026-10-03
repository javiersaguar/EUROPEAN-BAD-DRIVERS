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

Public delivery checked on 4 October 2026 at 00:56 CEST against functional commit `7aee236520eda1d4eb991cb98c2243e54ef8520b`:

| External check | Observed result |
|---|---|
| [Research checks](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37159806241) | Successful on Windows and Ubuntu: 79 passed, 1 raw-PDF-dependent skip on each; Ruff, mypy and notebook regeneration passed |
| [Observatory checks](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37159806246) | Successful: 8 unit checks, 45 browser checks and 1 intentional skip, dependency audits and container build/runtime checks passed |
| [Pages publication](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37159806224) | Successful; public health and data both report 0.3.0 |
| Public data delivery | 32 tables, 32 registered sources, 33 CSV downloads verified against the published SHA-256 hashes, including the full original demographic detail; JSON served with gzip |
| Public visual review | New material-damage and persons pages verified at desktop and mobile widths; charts, interpretation and source context rendered in the published application |
| [Source and availability monitor](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37159822144) | Public availability passed. Source check correctly raised attention: 30 releases unchanged, UNESPA returned CAPTCHA HTML to the GitHub runner instead of a PDF; all eleven newly integrated releases were unchanged |

The UNESPA CAPTCHA response has SHA-256 `bdd0034bfd836a9017631fbe43fc4e7f7a5989d0bbd9c17aa6c2bc6e135d3530`. Its missing PDF signature caused quarantine and failure of that monitoring job. This is an external retrieval incident, not an activated source revision. The previously audited PDF remains active (`20211e0e670fc7397e0455320d27166036c357a331b6bc8fddd8fd95d32aa429`), and the independent local probe returned its original bytes. No CAPTCHA was bypassed and the monitor was not weakened to hide the incident.

Visual evidence from the public site:

- [Material-damage desktop view](../outputs/figures/material_desktop_0.3.0.png)
- [Material categories, interpretation and source audit](../outputs/figures/material_charts_0.3.0.png)
- [Persons desktop view](../outputs/figures/persons_desktop_0.3.0.png)
- [Persons mobile view](../outputs/figures/persons_mobile_0.3.0.png)

All release commits use Javier Saguar as sole author and committer, with no coauthor trailers.
