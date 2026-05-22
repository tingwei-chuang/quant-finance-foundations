"""Tests for transaction costs and baseline strategies (Week 8)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.backtesting.baselines import (
    baseline_turnover_comparison,
    buy_and_hold_equity,
    equal_weight_rebalanced_equity,
)
from quant_math_roadmap.backtesting.costs import (
    annualized_turnover,
    apply_transaction_costs,
    cost_summary,
    position_turnover,
)
from quant_math_roadmap.backtesting.engine import run_backtest


@pytest.fixture
def asset_returns() -> pd.Series:
    idx = pd.bdate_range("2021-01-01", periods=300)
    rng = np.random.default_rng(0)
    return pd.Series(rng.normal(0.0003, 0.01, 300), index=idx, name="ret")


def test_position_turnover_known_values() -> None:
    positions = pd.Series([0.0, 1.0, 1.0, -1.0, 0.0])
    # |0-0|, |1-0|, |1-1|, |-1-1|, |0-(-1)|
    expected = pd.Series([0.0, 1.0, 0.0, 2.0, 1.0])
    pd.testing.assert_series_equal(position_turnover(positions), expected)


def test_constant_position_has_only_opening_turnover() -> None:
    positions = pd.Series([1.0] * 10)
    turnover = position_turnover(positions)
    assert turnover.iloc[0] == 1.0  # opening trade from flat
    assert (turnover.iloc[1:] == 0.0).all()  # no further trading


def test_transaction_costs_reduce_returns() -> None:
    idx = pd.bdate_range("2021-01-01", periods=5)
    gross = pd.Series([0.01] * 5, index=idx)
    positions = pd.Series([1.0, -1.0, 1.0, -1.0, 1.0], index=idx)  # heavy trading
    net = apply_transaction_costs(gross, positions, cost_per_unit_turnover=0.001)
    assert (net <= gross).all()
    assert (net < gross).iloc[1:].all()  # every trading period pays a cost


def test_zero_cost_leaves_returns_unchanged() -> None:
    idx = pd.bdate_range("2021-01-01", periods=5)
    gross = pd.Series([0.01, -0.02, 0.0, 0.03, -0.01], index=idx)
    positions = pd.Series([1.0, -1.0, 1.0, 1.0, -1.0], index=idx)
    net = apply_transaction_costs(gross, positions, cost_per_unit_turnover=0.0)
    pd.testing.assert_series_equal(net, gross)


def test_transaction_cost_exact_amount() -> None:
    idx = pd.bdate_range("2021-01-01", periods=3)
    gross = pd.Series([0.0, 0.0, 0.0], index=idx)
    positions = pd.Series([0.0, 1.0, 1.0], index=idx)
    # Turnover is [0, 1, 0]; at 10 bps the cost on period 2 is exactly 0.001.
    net = apply_transaction_costs(gross, positions, cost_per_unit_turnover=0.001)
    np.testing.assert_allclose(net.to_numpy(), [0.0, -0.001, 0.0])


def test_cost_summary_drag_is_non_negative(asset_returns: pd.Series) -> None:
    positions = pd.Series(
        np.sign(np.random.default_rng(1).standard_normal(len(asset_returns))),
        index=asset_returns.index,
    )
    gross = positions * asset_returns
    net = apply_transaction_costs(gross, positions, cost_per_unit_turnover=0.0005)
    summary = cost_summary(gross, net)
    assert summary["cost_drag"] >= 0.0


def test_buy_and_hold_does_not_rebalance() -> None:
    # Asset A rises, asset B falls: a true buy-and-hold lets the winner run.
    idx = pd.bdate_range("2021-01-01", periods=4)
    returns = pd.DataFrame(
        {"A": [0.10, 0.10, 0.10, 0.10], "B": [-0.05, -0.05, -0.05, -0.05]},
        index=idx,
    )
    equity = buy_and_hold_equity(returns, initial_capital=1.0)
    # Manual check: 0.5 in each asset, each compounding independently.
    a_val = 0.5 * (1.10**4)
    b_val = 0.5 * (0.95**4)
    assert equity.iloc[-1] == pytest.approx(a_val + b_val)


def test_buy_and_hold_turns_over_far_less_than_rebalancing() -> None:
    idx = pd.bdate_range("2021-01-01", periods=120)
    rng = np.random.default_rng(2)
    returns = pd.DataFrame(
        rng.normal(0.0, 0.015, (120, 4)), index=idx, columns=list("ABCD")
    )
    comparison = baseline_turnover_comparison(returns)
    assert (
        comparison["buy_and_hold_turnover"]
        < comparison["equal_weight_rebalanced_turnover"]
    )


def test_rebalanced_baseline_runs(asset_returns: pd.Series) -> None:
    returns = pd.DataFrame({"A": asset_returns, "B": asset_returns * 0.5})
    equity = equal_weight_rebalanced_equity(returns)
    assert len(equity) == len(returns)
    assert (equity > 0).all()


def test_annualized_turnover_scales() -> None:
    positions = pd.Series([1.0, -1.0] * 50)  # flips every period
    annual = annualized_turnover(positions, periods_per_year=252)
    assert annual > 0


def test_run_backtest_reports_gross_and_net(asset_returns: pd.Series) -> None:
    signal = pd.Series(
        np.sign(np.random.default_rng(3).standard_normal(len(asset_returns))),
        index=asset_returns.index,
    )
    result = run_backtest(signal, asset_returns, cost_per_unit_turnover=0.001)
    summary = result.summary()
    # Costs can only reduce performance.
    assert summary["total_net_return"] <= summary["total_gross_return"]
    assert summary["cost_drag"] >= 0.0
