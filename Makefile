.PHONY: install download process insurance test lint analysis model explain notebooks dashboard history exposure alternative policy site web monitor all
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
insurance:
	uv run ebdi insurance
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
history:
	uv run ebdi history
exposure:
	uv run ebdi exposure
alternative:
	uv run ebdi alternative
policy:
	uv run ebdi policy
site:
	uv run ebdi site
web:
	cd web && npm ci --ignore-scripts && npm run dev -- --port 8501
monitor:
	uv run ebdi monitor
all: download process insurance analysis model explain history exposure alternative policy site notebooks test lint
