# Reproduction and maintenance

The primary public interface is the React observatory, with ten pages and versioned aggregate data. Run it immediately with Node 24 and the committed npm lockfile:

```sh
cd web
npm ci --ignore-scripts
npm run dev -- --port 8501
```

Open `http://127.0.0.1:8501/`. Production builds use `npm run build`; `npm run preview -- --port 8501` is a local preview. The public HTTPS deployment uses GitHub Pages; see [deployment](deployment.md). Published data, geometry and fonts are bundled, so exploring the product requires no publisher downloads or account. Source links lead to the original releases.

For the reproducible research pipeline, use Python 3.12 or 3.13 and [uv](https://docs.astral.sh/uv/). Python 3.12 is tested in CI. Run commands from the repository root; `--root PATH` also accepts an explicit project root. PowerShell, Linux and macOS use the same CLI.

```sh
uv sync --locked
uv run ebdi dashboard
```

`ebdi dashboard` retains the legacy eight-section Streamlit research interface. Its local choropleth requires downloaded GISCO geometry and `ebdi process`. The React map already includes derived geometry.

```sh
uv run ebdi download
uv run ebdi process
uv run ebdi insurance
uv run ebdi analysis
uv run ebdi model
uv run --extra explain ebdi explain
uv run ebdi history
uv run ebdi exposure
uv run ebdi alternative
uv run ebdi policy
uv run ebdi demographics
uv run ebdi material
uv run ebdi ncid
uv run ebdi extended-analysis
uv run ebdi site
uv run --extra explain python scripts/build_notebooks.py
uv run --extra explain pytest -q
uv run --extra explain ruff check src dashboard tests scripts
uv run --extra explain ruff format --check src dashboard tests scripts
uv run --extra explain mypy
```

`uv run ebdi all` runs download, process, insurance, analysis, model, history, exposure, alternative, policy, demographics, material, ncid, extended-analysis and site. `make all` also generates SHAP, executes the five notebooks and runs checks. For complete model illustrations, run `explain` before `site`, as shown above. Individual Makefile targets support the same stages. Full reproduction downloads three national crash workbooks plus official stocks, population, European fatalities/history, the UNESPA and RCE PDFs and cartography; training and bootstrap take several minutes and require more memory than the aggregate frontend. Network access is needed for installation/source downloads. Raw files, Parquet, DuckDB and fitted models stay local; aggregate tables and original figures are versioned. `ebdi site` derives the browser payload and normalizes exported CSV line endings before hashing, so Windows/Linux publications agree.

Optional authorized insurance aggregates use the strict [claims import contract](claims_import.md). No artificial insured exposure is included. For source checks, run `uv run ebdi monitor`; it quarantines revisions without changing the active catalogue or manifest.

## Immutable cache and source updates

Fresh downloads go to `data/raw/revisions/<sha256>/<filename>`. The raw manifest records URL, retrieval timestamp, HTTP status, bytes and hash. Interrupted runs resume per file. Normal runs verify cached files and require the catalog's audited publisher hashes. Audit-time raw files may be stored flat; the manifest verifies them identically. Modified cached bytes fail integrity checks.

Live publisher endpoints can revise old years, JSON metadata or boundary files. A hash mismatch is intentional: review the revision and schema instead of silently changing published results. `uv run ebdi download --refresh` saves a separate revision, without overwriting previous raw bytes. It activates the new manifest revision; update the audited catalog/schema/expected totals only after review, then regenerate and compare results. Refresh does not make an incompatible revision analytically valid. For exact historical reproduction, the original audited source bytes must remain available in the local cache or from the publisher; this repository does not redistribute huge raw datasets.

## Notebook execution

`scripts/build_notebooks.py` builds valid Jupyter notebooks and executes them using nbclient and the current environment's Python kernel. Outputs contain real analysis of the published aggregate files, with assertions; the pipeline/model artifacts are reproduced by their CLI stages, rather than embedding their implementation in notebooks. Notebooks do not need raw files to explore published results. They can be opened and rerun from the notebooks directory or root.

## Tests and CI

Python tests cover rates, missing denominators, schema/category/year validation, join cardinality, geography, normalization, leakage, history, network scope, insurance import, immutable monitoring and publication hashes. Integration tests check national totals, EU coverage, sensitivity, breakdown conservation and insurance selection limits. Streamlit AppTest retains legacy checks. CI runs Python checks plus notebook execution, Ruff and mypy on Windows/Linux with Python 3.12, without downloading raw data or retraining on every push. The raw-PDF roundtrip test is skipped when the audited PDF is absent; published insurance checks still run. A separate developer reproduction verifies the full pipeline against real files.

React checks run from `web`: `npm run lint`, `npm run format:check`, `npm test`, `npm run build`, and `npm run test:e2e`. Browser tests require `npx playwright install --with-deps chromium`; CI installs it automatically. Tests cover all thirteen pages, desktop/mobile navigation, axe, keyboard map, filter history, failures/retries and actual CSV/PDF/SVG/PNG downloads. CI also audits npm/Python dependencies and checks the production container. Executed results are in [verification](verification_0.3.0.md).

## Optional container

```sh
docker build -t ebdi .
docker run --rm --read-only --tmpfs /tmp --tmpfs /var/cache/nginx -p 8080:8080 ebdi
```

The pinned multi-stage container serves the React observatory at `http://localhost:8080/` as unprivileged UID 101, with bundled geometry and a health endpoint. It downloads no raw data at startup. Its read-only operation, headers and aggregate health contract pass GitHub Actions. Docker is unavailable on the local Windows environment, so the local checks use Node/uv. `Dockerfile.research` retains the optional Streamlit research container.
