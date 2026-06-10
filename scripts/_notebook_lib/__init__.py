"""Internal package backing scripts/build_notebooks.py.

The original generator was a single 2000-line file. Splitting it into a
package gives one file per logical concern (cells, shared parts, each week)
so that:

* a week can be edited or merged independently of the others;
* ``--only WEEK`` can import only the week it needs;
* embedded code cells stay close to the prose they explain.
"""

from __future__ import annotations

from .cells import KERNELSPEC, LANGUAGE_INFO, build, code, ex_code, md
from .parts import (
    checklist,
    docs_prefix,
    exercises_intro,
    footer_references,
    header,
    mistakes,
    style_setup_cell,
)
from .week0 import week as week0
from .week1 import week as week1
from .week2 import week as week2
from .week3 import week as week3
from .week4 import week as week4
from .week5 import week as week5
from .week6 import week as week6
from .week7 import week as week7
from .week8 import week as week8

NOTEBOOKS = {
    "00_setup_and_readiness_diagnostic": week0,
    "01_returns_covariance_and_linear_algebra": week1,
    "02_multivariable_calculus_and_min_variance_portfolio": week2,
    "03_probability_simulation_lln_clt": week3,
    "04_statistical_inference_for_strategy_returns": week4,
    "05_regression_and_factor_models": week5,
    "06_financial_mathematics_and_option_pricing": week6,
    "07_time_series_diagnostics": week7,
    "08_walk_forward_forecasting_and_backtesting_integrity": week8,
}

__all__ = [
    "KERNELSPEC",
    "LANGUAGE_INFO",
    "NOTEBOOKS",
    "build",
    "checklist",
    "code",
    "docs_prefix",
    "ex_code",
    "exercises_intro",
    "footer_references",
    "header",
    "md",
    "mistakes",
    "style_setup_cell",
    "week0",
    "week1",
    "week2",
    "week3",
    "week4",
    "week5",
    "week6",
    "week7",
    "week8",
]
