# quant-math-roadmap — An 8-Week Quant Finance Math Roadmap

> A **self-study, reproducible, rigorous** 8-week roadmap that takes a learner
> with programming experience from refreshed mathematical foundations to a
> small, correct, leakage-aware quantitative research workflow.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

> The primary teaching language of this repository is **Traditional Chinese**.
> This page is a concise English summary for international visitors; see
> [`README.md`](README.md) for the full guide.

---

## What this is

An 8-week preparation program (plus a Week 0 diagnostic) for **applied
quantitative finance, systematic research, financial-algorithms coursework,
econometrics/time-series coursework, and rigorous backtesting projects**. It
emphasises mathematical understanding, reproducible experiments, correct
evaluation methodology, practical Python, and the prevention of common
backtesting mistakes.

**Intended for:** *a learner with programming experience preparing for
quantitative finance and systematic research coursework* — someone who has
previously studied calculus, linear algebra and probability and now wants to
refresh them and build stronger statistics, regression, financial-mathematics,
portfolio, time-series and backtesting foundations.

## What this is NOT

- **Not investment advice.** This repository is for education and research
  methodology only.
- **Not a claim of any profitable strategy.** No notebook result should be read
  as evidence of trading profitability or practical investability.
- **Not an advanced mathematical-finance textbook.** It deliberately avoids
  high-frequency trading, advanced stochastic calculus, measure-theoretic
  probability, and deep reinforcement-learning trading systems.

## The 8-week roadmap

| Week | Topic |
|------|-------|
| 0 | Setup & readiness diagnostic |
| 1 | Returns, risk & linear algebra |
| 2 | Multivariable calculus & the minimum-variance portfolio |
| 3 | Probability refresh: simulation, LLN & CLT |
| 4 | Statistical inference for strategy returns |
| 5 | Regression & factor models |
| 6 | Financial mathematics & option pricing |
| 7 | Time-series diagnostics |
| 8 | Walk-forward forecasting & backtesting integrity |

## Quick start (uv)

```bash
# Install uv: https://docs.astral.sh/uv/getting-started/installation/
uv venv --python 3.12
uv pip install -e ".[dev]"
uv run python scripts/generate_synthetic_dataset.py   # build sample data
uv run pytest                                          # run tests
uv run python scripts/run_all_notebooks.py             # validate notebooks
uv run jupyter lab                                     # open the notebooks
```

## Repository layout

- `docs/` — roadmap, study guide, resource guide, math/finance concept notes,
  and the open-source/data policy.
- `notebooks/` — the Week 0–8 lessons; `notebooks/solutions/` holds full
  reference answers.
- `src/quant_math_roadmap/` — the reusable, tested Python package the notebooks
  import (`data`, `math`, `finance`, `time_series`, `backtesting`).
- `scripts/` — synthetic-data generation and notebook validation.
- `tests/` — `pytest` suite, including explicit look-ahead, cost,
  annualisation and baseline checks.

## Data policy

All notebooks and tests run **offline on reproducible synthetic data** by
default. No third-party market data is committed; the optional download folder
`data/raw/` is git-ignored. **Users are responsible for complying with the
terms of use of any data provider they choose.** See
[`docs/open_source_and_data_policy.md`](docs/open_source_and_data_policy.md).

## Contributing & license

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Released under the
[MIT License](LICENSE). To cite the project, see [`CITATION.cff`](CITATION.cff).

## Disclaimer

This repository is for **education and research methodology only**. It is
**not investment advice**, and no result it produces is a claim of trading
profitability or practical investability.
