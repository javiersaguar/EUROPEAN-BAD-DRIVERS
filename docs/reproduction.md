# Reproduction and maintenance

Use Python 3.12 or 3.13 and [uv](https://docs.astral.sh/uv/). Python 3.12 is tested. Run commands from the repository root; `--root PATH` also accepts an explicit project root. PowerShell, Linux and macOS use the same CLI.

```sh
uv sync --locked
uv run ebdi dashboard
```

The published aggregate CSVs allow the dashboard to run immediately. The local choropleth requires downloaded GISCO geometry and `ebdi process`. No account, API token or secret is required.

```sh
uv run ebdi download
uv run ebdi process
uv run ebdi insurance
uv run ebdi analysis
uv run ebdi model
uv run --extra explain ebdi explain
uv run --extra explain python scripts/build_notebooks.py
uv run --extra explain pytest -q
uv run --extra explain ruff check src dashboard tests scripts
uv run --extra explain ruff format --check src dashboard tests scripts
uv run --extra explain mypy
```

`uv run ebdi all` runs download, process, insurance, analysis and model. `make all` also generates SHAP and executes the four notebooks. Individual Makefile targets support the same stages. Full reproduction downloads three national crash workbooks plus official stocks, population, European fatalities, UNESPA's PDF and cartography; training and bootstrap take several minutes and require more memory than the aggregate dashboard. Network access is needed only for installation/source downloads. Raw files, Parquet, DuckDB and fitted models stay local; aggregate tables and original figures are versioned.

## Immutable cache and source updates

Fresh downloads go to `data/raw/revisions/<sha256>/<filename>`. The raw manifest records URL, retrieval timestamp, HTTP status, bytes and hash. Interrupted runs resume per file. Normal runs verify cached files and require the catalog's audited publisher hashes. Audit-time raw files may be stored flat; the manifest verifies them identically. Modified cached bytes fail integrity checks.

Live publisher endpoints can revise old years, JSON metadata or boundary files. A hash mismatch is intentional: review the revision and schema instead of silently changing published results. `uv run ebdi download --refresh` saves a separate revision, without overwriting previous raw bytes. It activates the new manifest revision; update the audited catalog/schema/expected totals only after review, then regenerate and compare results. Refresh does not make an incompatible revision analytically valid. For exact historical reproduction, the original audited source bytes must remain available in the local cache or from the publisher; this repository does not redistribute huge raw datasets.

## Notebook execution

`scripts/build_notebooks.py` builds valid Jupyter notebooks and executes them using nbclient and the current environment's Python kernel. Outputs contain real analysis of the published aggregate files, with assertions; the pipeline/model artifacts are reproduced by their CLI stages, rather than embedding their implementation in notebooks. Notebooks do not need raw files to explore published results. They can be opened and rerun from the notebooks directory or root.

## Tests and CI

Unit tests cover rates, zero/missing denominators, schema/category/year validation, join cardinality, geography, weights, normalization and outcome leakage. Integration tests check the published national totals, EU coverage, sensitivity, crash breakdown conservation and insurance coverage/selection limits. Streamlit AppTest exercises all eight sections, insurance filters, missing-stock years and zero-weight validation. CI runs these checks plus notebook execution, Ruff and mypy on Windows and Linux, without downloading raw data or retraining on every push. The local hashed-PDF roundtrip test is skipped when the raw PDF is absent; published insurance checks still run. A separate developer reproduction verifies the full pipeline with the real audited files.

## Optional container

```sh
docker build -t ebdi .
docker run --rm -p 8501:8501 ebdi
```

The container serves the published aggregate dashboard. Mount or reproduce processed geometry to enable the map. It does not download raw data at startup. Container building is supplied as an optional configuration; the local verified environment is uv on Windows.
