"""Property-based tests (Hypothesis) for core mathematical invariants.

Each property here is also a teaching statement: put-call parity holds for
*any* sane inputs, return conversions are exact inverses, a simplex projection
always lands on the simplex, and time-ordered splits never leak — not just for
the examples in the unit tests, but across the whole input space Hypothesis
explores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quant_math_roadmap.finance.derivatives import (
    binomial_european_option,
    put_call_parity_gap,
)
from quant_math_roadmap.finance.fixed_income import discount_factor
from quant_math_roadmap.finance.returns import log_to_simple, simple_to_log
from quant_math_roadmap.math.optimization import _project_to_simplex
from quant_math_roadmap.time_series.splits import (
    expanding_window_splits,
    rolling_window_splits,
)

# Finite, well-conditioned floats for financial quantities.
sane_simple_returns = st.lists(
    st.floats(min_value=-0.95, max_value=10.0, allow_nan=False, allow_infinity=False),
    min_size=1,
    max_size=50,
)


@given(sane_simple_returns)
def test_simple_log_conversion_round_trips(values: list[float]) -> None:
    simple = pd.Series(values)
    round_tripped = log_to_simple(simple_to_log(simple))
    np.testing.assert_allclose(round_tripped.to_numpy(), simple.to_numpy(), rtol=1e-12)


@settings(max_examples=30, deadline=None)
@given(
    spot=st.floats(min_value=10.0, max_value=500.0),
    strike=st.floats(min_value=10.0, max_value=500.0),
    rate=st.floats(min_value=0.0, max_value=0.10),
    vol=st.floats(min_value=0.05, max_value=0.6),
    maturity=st.floats(min_value=0.1, max_value=3.0),
)
def test_put_call_parity_holds_for_arbitrary_inputs(
    spot: float, strike: float, rate: float, vol: float, maturity: float
) -> None:
    call = binomial_european_option(
        spot, strike, rate, vol, maturity, n_steps=64, option_type="call"
    )
    put = binomial_european_option(spot, strike, rate, vol, maturity, n_steps=64, option_type="put")
    gap = put_call_parity_gap(call, put, spot, strike, rate, maturity)
    # Parity is exact on a CRR tree; tolerance covers float accumulation only.
    assert abs(gap) < 1e-7 * max(spot, strike)


@given(
    st.lists(
        st.floats(min_value=-100.0, max_value=100.0, allow_nan=False),
        min_size=1,
        max_size=30,
    )
)
def test_simplex_projection_invariants(values: list[float]) -> None:
    w = _project_to_simplex(np.asarray(values, dtype=float))
    assert w.sum() == pytest.approx(1.0, abs=1e-9)
    assert (w >= -1e-12).all()


@given(st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False), min_size=2, max_size=10))
def test_simplex_projection_is_identity_on_the_simplex(values: list[float]) -> None:
    v = np.asarray(values, dtype=float) + 1e-9
    v = v / v.sum()  # already on the simplex
    np.testing.assert_allclose(_project_to_simplex(v), v, atol=1e-8)


@settings(max_examples=100, deadline=None)
@given(
    n=st.integers(min_value=10, max_value=300),
    initial=st.integers(min_value=1, max_value=100),
    test_size=st.integers(min_value=1, max_value=20),
    gap=st.integers(min_value=0, max_value=15),
)
def test_expanding_splits_never_leak(n: int, initial: int, test_size: int, gap: int) -> None:
    for split in expanding_window_splits(
        n, initial_train_size=initial, test_size=test_size, gap=gap
    ):
        assert split.train_index.max() + gap < split.test_index.min()
        assert split.test_index.max() < n
        assert split.train_index[0] == 0


@settings(max_examples=100, deadline=None)
@given(
    n=st.integers(min_value=10, max_value=300),
    train=st.integers(min_value=1, max_value=100),
    test_size=st.integers(min_value=1, max_value=20),
    gap=st.integers(min_value=0, max_value=15),
)
def test_rolling_splits_never_leak(n: int, train: int, test_size: int, gap: int) -> None:
    for split in rolling_window_splits(n, train_size=train, test_size=test_size, gap=gap):
        assert split.train_index.max() + gap < split.test_index.min()
        assert split.test_index.max() < n
        assert len(split.train_index) == train


@settings(max_examples=50, deadline=None)
@given(
    rate=st.floats(min_value=-0.5, max_value=0.5),
    t1=st.floats(min_value=0.0, max_value=30.0),
    t2=st.floats(min_value=0.0, max_value=30.0),
)
def test_discount_factor_monotone_in_time_for_positive_rates(
    rate: float, t1: float, t2: float
) -> None:
    df1 = discount_factor(rate, t1)
    df2 = discount_factor(rate, t2)
    assert df1 > 0 and df2 > 0
    if rate > 0 and t1 < t2:
        assert df1 >= df2  # money further away is worth (weakly) less
    if rate == 0:
        assert df1 == pytest.approx(1.0)
