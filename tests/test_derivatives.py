"""Tests for option payoffs and binomial pricing (Week 6)."""

from __future__ import annotations

import numpy as np
import pytest

from quant_math_roadmap.finance.derivatives import (
    binomial_european_option,
    call_payoff,
    forward_payoff,
    long_straddle_payoff,
    put_call_parity_gap,
    put_payoff,
)


def test_call_payoff_known_values() -> None:
    spot = np.array([80.0, 100.0, 120.0])
    np.testing.assert_allclose(call_payoff(spot, 100.0), [0.0, 0.0, 20.0])


def test_put_payoff_known_values() -> None:
    spot = np.array([80.0, 100.0, 120.0])
    np.testing.assert_allclose(put_payoff(spot, 100.0), [20.0, 0.0, 0.0])


def test_forward_payoff_is_linear() -> None:
    spot = np.array([80.0, 100.0, 120.0])
    np.testing.assert_allclose(forward_payoff(spot, 100.0), [-20.0, 0.0, 20.0])


def test_straddle_is_absolute_distance_from_strike() -> None:
    spot = np.array([70.0, 100.0, 130.0])
    np.testing.assert_allclose(long_straddle_payoff(spot, 100.0), [30.0, 0.0, 30.0])


def test_call_value_increases_with_spot() -> None:
    base = binomial_european_option(100.0, 100.0, 0.03, 0.2, 1.0, n_steps=200)
    higher = binomial_european_option(120.0, 100.0, 0.03, 0.2, 1.0, n_steps=200)
    assert higher > base


def test_call_value_increases_with_volatility() -> None:
    low = binomial_european_option(100.0, 100.0, 0.03, 0.1, 1.0, n_steps=200)
    high = binomial_european_option(100.0, 100.0, 0.03, 0.4, 1.0, n_steps=200)
    assert high > low


def test_call_value_increases_with_maturity() -> None:
    short = binomial_european_option(100.0, 100.0, 0.03, 0.2, 0.25, n_steps=200)
    long = binomial_european_option(100.0, 100.0, 0.03, 0.2, 2.0, n_steps=200)
    assert long > short


def test_deep_in_the_money_call_near_intrinsic() -> None:
    # A deep ITM call is worth at least its discounted intrinsic value.
    rate, maturity = 0.05, 1.0
    price = binomial_european_option(200.0, 100.0, rate, 0.2, maturity, n_steps=300)
    intrinsic = 200.0 - 100.0 * np.exp(-rate * maturity)
    assert price >= intrinsic - 1e-6


def test_option_value_is_non_negative() -> None:
    for strike in (50.0, 100.0, 150.0):
        for kind in ("call", "put"):
            value = binomial_european_option(
                100.0, strike, 0.03, 0.25, 1.0, n_steps=150, option_type=kind
            )
            assert value >= 0.0


def test_binomial_satisfies_put_call_parity() -> None:
    spot, strike, rate, vol, maturity = 100.0, 105.0, 0.04, 0.25, 1.0
    call = binomial_european_option(
        spot, strike, rate, vol, maturity, n_steps=500, option_type="call"
    )
    put = binomial_european_option(
        spot, strike, rate, vol, maturity, n_steps=500, option_type="put"
    )
    gap = put_call_parity_gap(call, put, spot, strike, rate, maturity)
    assert gap == pytest.approx(0.0, abs=1e-2)


def test_binomial_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        binomial_european_option(-100.0, 100.0, 0.03, 0.2, 1.0)
    with pytest.raises(ValueError):
        binomial_european_option(100.0, 100.0, 0.03, -0.2, 1.0)
    with pytest.raises(ValueError, match="option_type"):
        binomial_european_option(100.0, 100.0, 0.03, 0.2, 1.0, option_type="swap")
