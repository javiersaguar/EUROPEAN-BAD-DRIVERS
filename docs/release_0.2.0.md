# Observatory 0.2.0 — delivery and evidence

The public product is **Observatorio europeo de siniestralidad vial**. The repository retains EBDI as the historical research name. Original code and commits are authored solely by Javier Saguar. HS-Maisa informed the quiet console layout and warm sage palette; its source, assets and commit authors were not copied.

## Twenty requested improvements

| # | Improvement | Implementation and scope |
|---:|---|---|
| 1 | Neutral brand | Neutral Spanish observatory name across the React product; measures describe territorial outcomes. |
| 2 | Source and coverage before charts | Source chips, exact year, scope, denominator and definition; links to original releases. |
| 3 | Material-damage claims and insured exposure | UNESPA material/corporal municipal explorer, national coverages and all-coverage provincial counts; strict `claims-import` adapter added. **Complete claims/insured-vehicle-year observations remain an external data dependency.** No artificial observations are published. |
| 4 | Real 2023 fleet and permits | Official workbooks, hashes, exact aliases for five truncated fleet cells, 52 unique provinces, national reconciliation: 36,075,238 vehicles; 27,910,056 permits. |
| 5 | Longer history | 405 observations: current EU-27 cohort, mortality and population, 2010–2024, retained source flags. Spain injury-crash series remains 2022–2024. |
| 6 | Matched kilometres | Separate 2022 state-owned-road / RCE panel: 44 observed exposures, 134,902.6 million vehicle-km summed (published total 134,902.5, rounding retained); 10,956 state-road crashes, 35 without matched exposure. No all-road index substitution. |
| 7 | Index without extra subset weights | Alternative 50% injury-crash rate / 50% death rate; reference index retained and clearly labelled. Deaths and injury crashes are still related. |
| 8 | Ranking stability | 2024 reference positions show weight sensitivity separately from Poisson event-bootstrap intervals in province profiles and laboratory. Custom scenarios do not inherit unrelated intervals. |
| 9 | Threshold analysis | Precision–recall/calibration charts; F2 threshold chosen using 2023 and a 2022-fitted model. Original model preserved. New 2024 report explicitly exploratory; future unseen year required for confirmation. |
| 10 | Clear homepage | Three headline measures, geographic exploration, six highest rates, three interpretation cards, national trend. |
| 11 | Province profiles | All 52 provinces, measure/denominator filters, counts, rates, intervals, national comparison, history and index context. |
| 12 | Territory comparisons | Up to three selected provinces, common denominators, three-year trajectories and interval table. |
| 13 | Shareable filters | All filters serialized and validated in query parameters; browser history and reload restoration; clipboard share action. |
| 14 | Mobile and accessibility | Responsive sidebar, inert background and focus management, escape dismissal, keyboard map, visible focus, text/table alternatives, reduced motion; automated WCAG AA checks in CI. Automatic checks do not replace a complete assistive-technology audit. |
| 15 | Design and language | Own warm sage tokens, locally bundled variable DM Sans, consistent Spanish number and unit formats, deliberate empty/error states. Research metadata retains its original English wording. |
| 16 | Export | Filtered CSV/PDF and chart SVG/PNG; scope, source URLs, filters and verification date; CSV formula escaping. Downloads happen locally. |
| 17 | Maintainability | Separate page modules, reusable charts/map/table/source/export components, analytical helpers and typed aggregate contract. Python research pipeline remains independent. |
| 18 | Source monitoring | Weekly scheduled checks and manual CLI; immutable quarantined changes, structural checks, retained hashes and explicit semantic-review gate. Active manifest/catalogue never rewritten by monitoring. |
| 19 | Production verification | Python/Ruff/mypy/notebooks, frontend typecheck/lint/unit contracts, desktop/mobile browser flows, axe, actual downloads, npm and Python dependency audits; read-only non-root container smoke in CI. |
| 20 | Stable publication and operations | HTTPS GitHub Pages workflow and stable project URL, versioned aggregate payload/health, release history, error recovery and scheduled availability/version consistency checks. Custom domain requires an owned domain; none is purchased. |

## Important analytical boundaries

- Public insurance extremes are a selected 40-city panel per coverage, not a full municipality sample or individual accident probability. RC material claims may coexist with bodily injuries.
- RCE and DGT state ownership are matching administrative concepts with potential inventory differences; source rounding and eight absent exposure provinces are retained. The 2024 transport source could not be retrieved through its HTTPS endpoint; the successfully verified report explicitly describes 2022.
- Original ML test results are refitted on 2022–2023; threshold study reports use a different model fitted only on 2022 to keep score distributions consistent between validation and evaluation.
- Source monitoring detects changed releases and unavailable endpoints; availability monitoring checks a running site and release coherence. Neither is a guarantee that upstream data are current.

## Checks

Local Python checks: 68 tests; Ruff; mypy on 24 modules; four executed notebooks. Frontend: six analytical/state/export unit tests, TypeScript production build and ESLint. CI passed on Linux and Windows; 31 browser tests passed, including actual exports and whole-page axe checks, and the read-only non-root container passed its smoke checks. The first source/availability monitoring run succeeded for all 20 active sources. Public HTTPS availability and executed workflow links are recorded in [verification](verification_0.2.0.md).
