# Convenience commands for quant-math-roadmap.
#
# These targets are thin wrappers around `uv run ...`. On Windows without
# `make`, run the underlying `uv run` commands directly (see README.md);
# the essential Python workflows never depend on `make`.

.PHONY: help install data test lint format typecheck notebooks check clean

help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install:  ## Create the venv and install the package with dev extras.
	uv venv --python 3.12
	uv pip install -e ".[dev]"

data:  ## Generate the synthetic sample dataset.
	uv run python scripts/generate_synthetic_dataset.py

test:  ## Run the test suite with coverage.
	uv run pytest --cov

lint:  ## Run ruff lint checks.
	uv run ruff check .

format:  ## Auto-format the codebase with ruff.
	uv run ruff format .
	uv run ruff check . --fix

typecheck:  ## Run mypy type checking.
	uv run mypy

notebooks:  ## Execute every notebook to validate it runs top-to-bottom.
	uv run python scripts/run_all_notebooks.py --include-solutions

check: lint typecheck test  ## Run lint, type check and tests.

clean:  ## Remove caches and build artefacts.
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml
	rm -rf build dist src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true
