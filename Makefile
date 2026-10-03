.PHONY: install download process test lint analysis model explain notebooks dashboard all
.NOTPARALLEL: all

install:
	uv sync --locked --extra explain
download:
	uv run ebdi download
process:
	uv run ebdi process
	uv run python scripts/build_reference.py
test:
	uv run pytest -q
lint:
	uv run ruff check src dashboard tests scripts
	uv run ruff format --check src dashboard tests scripts
	uv run mypy
analysis:
	uv run ebdi analysis
model:
	uv run ebdi model
explain:
	uv run --extra explain ebdi explain
notebooks:
	uv run python scripts/build_notebooks.py
dashboard:
	uv run ebdi dashboard
all: download process analysis model explain notebooks test lint
