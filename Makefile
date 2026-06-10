# Convenience commands for quant-math-roadmap.
#
# These targets are thin wrappers around `uv run ...`. On Windows without
# `make`, run the underlying `uv run` commands directly (see README.md);
# the essential Python workflows never depend on `make`.

.PHONY: help install data test lint format typecheck notebooks check clean audit

help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

install:  ## Create the venv (from uv.lock) and install dev dependencies.
	uv sync --extra dev

data:  ## Generate the synthetic sample dataset.
	uv run python scripts/generate_synthetic_dataset.py

test:  ## Run the test suite with coverage (enforces fail_under from pyproject).
	uv run pytest --cov

lint:  ## Run ruff lint AND format checks (matches CI exactly).
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-format the codebase with ruff.
	uv run ruff format .
	uv run ruff check . --fix

typecheck:  ## Run mypy type checking.
	uv run mypy

notebooks:  ## Validate every notebook by execution (matches CI: pytest --nbmake).
	uv run python -m ipykernel install --user --name python3 >/dev/null 2>&1 || true
	uv run python scripts/run_all_notebooks.py

audit:  ## Scan installed deps for known vulnerabilities.
	uv run --with pip-audit pip-audit --strict

check: lint typecheck test  ## Run lint (with format check), type check and tests.

clean:  ## Remove caches and build artefacts.
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml
	rm -rf build dist src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true
