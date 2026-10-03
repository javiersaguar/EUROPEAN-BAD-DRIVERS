# Verification — 0.2.0

Local checks, 3 October 2026:

- Python: 68 tests passed; Ruff lint/format; mypy on 24 source modules; four notebooks executed with real aggregate outputs.
- Frontend: six unit tests, reproducing every published reference and alternative score/rank; URL restoration, missing exposure, normalization ties, ratios of totals and CSV escaping; production TypeScript/Vite build.
- Browser visual checks through the in-app browser: desktop 1440 × 1000 and mobile 390 × 844. All ten page content areas returned zero axe WCAG A/AA violations; mobile content had no page-level horizontal overflow. Menu escape focus restoration verified.
- Source monitor: all 20 active releases unchanged; active manifest/catalogue untouched. Report: `outputs/tables/source_monitor.json`.
- `npm audit`: zero known vulnerabilities. `pip-audit` 2.10.1 against the complete pinned runtime dependency graph, including optional SHAP: zero known vulnerabilities.

The CI checks cover the complete page including navigation, desktop/mobile Chromium flows, real file downloads, request failures and retries, browser history, keyboard map, and a read-only non-root container. Their executed results and public availability check are appended after the first deployment. Automatic accessibility checks are useful evidence, not a certification of complete WCAG or screen-reader conformance.
