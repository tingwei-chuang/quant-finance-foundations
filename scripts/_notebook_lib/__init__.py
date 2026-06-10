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
from .week0_en import week as week0_en
from .week1 import week as week1
from .week1_en import week as week1_en
from .week2 import week as week2
from .week2_en import week as week2_en
from .week3 import week as week3
from .week3_en import week as week3_en
from .week4 import week as week4
from .week4_en import week as week4_en
from .week5 import week as week5
from .week5_en import week as week5_en
from .week6 import week as week6
from .week6_en import week as week6_en
from .week7 import week as week7
from .week7_en import week as week7_en
from .week8 import week as week8
from .week8_en import week as week8_en

_STEMS = [
    "00_setup_and_readiness_diagnostic",
    "01_returns_covariance_and_linear_algebra",
    "02_multivariable_calculus_and_min_variance_portfolio",
    "03_probability_simulation_lln_clt",
    "04_statistical_inference_for_strategy_returns",
    "05_regression_and_factor_models",
    "06_financial_mathematics_and_option_pricing",
    "07_time_series_diagnostics",
    "08_walk_forward_forecasting_and_backtesting_integrity",
]

NOTEBOOKS = dict(
    zip(_STEMS, [week0, week1, week2, week3, week4, week5, week6, week7, week8], strict=True)
)

# The English i18n track: identical structure, prose translated, emitted into
# notebooks/en/ (solutions into notebooks/en/solutions/).
NOTEBOOKS_EN = dict(
    zip(
        _STEMS,
        [week0_en, week1_en, week2_en, week3_en, week4_en, week5_en, week6_en, week7_en, week8_en],
        strict=True,
    )
)

__all__ = [
    "KERNELSPEC",
    "LANGUAGE_INFO",
    "NOTEBOOKS",
    "NOTEBOOKS_EN",
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
