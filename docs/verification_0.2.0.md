# Verification — 0.2.0

Local checks, 3 October 2026:

- Python: 68 tests passed; Ruff lint/format; mypy on 24 source modules; four notebooks executed with real aggregate outputs.
- Frontend: six unit tests, reproducing every published reference and alternative score/rank; URL restoration, missing exposure, normalization ties, ratios of totals and CSV escaping; production TypeScript/Vite build.
- Browser visual checks through the in-app browser: desktop 1440 × 1000 and mobile 390 × 844. All ten page content areas returned zero axe WCAG A/AA violations; mobile content had no page-level horizontal overflow. Menu escape focus restoration verified.
- Source monitor: all 20 active releases unchanged; active manifest/catalogue untouched. Report: `outputs/tables/source_monitor.json`.
- `npm audit`: zero known vulnerabilities. `pip-audit` 2.10.1 against the complete pinned runtime dependency graph, including optional SHAP: zero known vulnerabilities.

Automatic accessibility checks are useful evidence, not a certification of complete WCAG or screen-reader conformance.

## Executed publication checks

The published application code and aggregate payload at `06e2fbd24d8bcb11921f8b69776f2815c1c2d9a4` passed these GitHub Actions runs on 3 October 2026:

- [Research checks](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37144488652): Python 3.12 on Linux and Windows, 67 passed / one skipped per platform, Ruff, formatting, mypy and four notebook executions. The skip is the raw-PDF roundtrip; the audited PDF is absent in CI. All 68 passed locally with the original PDF.
- [Observatory checks](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37144488653): six unit tests, lint/format/typecheck/build, zero known npm/Python dependency vulnerabilities, and 31 Chromium browser tests passed. One desktop instance of a mobile-only menu test is intentionally skipped. Both desktop/mobile runs covered all ten pages, whole-page axe checks, reflow, URL restoration, keyboard map, all four actual download formats, zero weights and request retry.
- The same observatory run built the digest-pinned production image and verified UID 101, read-only filesystem with temporary writable mounts, health contract and security headers. Docker was tested in CI; it is not installed in the local Windows environment.
- [Publish observatory](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37144488648): browser checks passed against the production subpath before deployment. GitHub Pages published the HTTPS application successfully.
- [Source and availability monitoring](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS/actions/runs/37144862596): first manual execution succeeded for both jobs. All 20 active source releases remained unchanged; the active manifest/catalogue was not rewritten. Source and availability reports were retained as workflow artifacts. Weekly scheduling is enabled.

The public URL is [the observatory](https://javiersaguar.github.io/EUROPEAN-BAD-DRIVERS/). `scripts/check_site.py` independently returned `availability: ok`, release `0.2.0`, matching health/data versions and 156 provincial rows at `2026-10-03T18:36:22Z`. The snapshot is recorded in `outputs/tables/site_monitor.json`. Availability checks do not assert upstream freshness.

Manual public-browser checks confirmed correct subpath assets, mobile menu navigation and keyboard selection. Additional 320-pixel checks found no page-level horizontal overflow on Panorama, Territorios, Ficha provincial, Comparar and Fuentes; remaining pages were covered at 390 pixels by CI and the earlier visual audit. Desktop and mobile evidence is saved in `outputs/figures/observatory_desktop.png` and `observatory_mobile.png`.

## Remaining external dependency

Improvement 3 has a working import contract and public material-damage coverage/selected-city explorer, but a complete territorial claims/insured-vehicle-year dataset remains unavailable. No fictitious rates were introduced. The [twenty-item delivery matrix](release_0.2.0.md) records this scope explicitly.
