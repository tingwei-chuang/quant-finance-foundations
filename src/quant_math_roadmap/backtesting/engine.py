"""A minimal, leakage-aware single-asset backtest engine (Week 8).

The engine is intentionally small. Its job is pedagogical: to wire together the
*correct* sequence of steps — lag the signal into positions, apply realised
returns, charge costs, then report gross **and** net performance — so that the
notebook can focus on methodology rather than plumbing.

This engine does not model leverage, margin, multiple assets, or intraday
execution. It is a teaching tool, not a production system.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..finance.metrics import max_drawdown, sharpe_ratio
from .costs import apply_transaction_costs, position_turnover
from .leakage_checks import signal_to_positions, strategy_returns


@dataclass(frozen=True)
class BacktestResult:
    """Container for the output of :func:`run_backtest`.

    Attributes:
        positions: Position actually held each period (the lagged signal).
        gross_returns: Strategy returns before transaction costs.
        net_returns: Strategy returns after transaction costs.
        gross_equity: Compounded equity curve from ``gross_returns``.
        net_equity: Compounded equity curve from ``net_returns``.
    """

    positions: pd.Series
    gross_returns: pd.Series
    net_returns: pd.Series
    gross_equity: pd.Series
    net_equity: pd.Series

    def summary(self, *, frequency: str = "daily") -> dict[str, float]:
        """Return headline performance statistics.

        Args:
            frequency: Data frequency, passed through to annualised metrics.

        Returns:
            A dictionary of gross/net total return, net Sharpe ratio, net
            maximum drawdown and average turnover.
        """
        total_gross = float((1.0 + self.gross_returns).prod() - 1.0)
        total_net = float((1.0 + self.net_returns).prod() - 1.0)
        return {
            "total_gross_return": total_gross,
            "total_net_return": total_net,
            "cost_drag": total_gross - total_net,
            "net_sharpe": sharpe_ratio(self.net_returns, frequency=frequency),
            "net_max_drawdown": max_drawdown(self.net_equity),
            "avg_turnover": float(position_turnover(self.positions).mean()),
        }


def run_backtest(
    signal: pd.Series,
    asset_returns: pd.Series,
    *,
    signal_lag: int = 1,
    cost_per_unit_turnover: float = 0.0005,
    initial_capital: float = 1.0,
) -> BacktestResult:
    """Run a leakage-aware single-asset backtest.

    The pipeline, in order:

    1. **Lag** the signal into tradable positions (``signal_lag >= 1``) so no
       position uses contemporaneous information.
    2. **Apply** realised returns to get gross strategy returns.
    3. **Charge** proportional transaction costs based on turnover.
    4. **Compound** gross and net returns into equity curves.

    Args:
        signal: Desired exposure computed from information up to each date.
        asset_returns: Realised per-period returns of the traded asset.
        signal_lag: Periods to delay the signal before trading (``>= 1``).
        cost_per_unit_turnover: Proportional cost per unit of turnover.
        initial_capital: Starting capital for the equity curves.

    Returns:
        A :class:`BacktestResult`.
    """
    if not signal.index.equals(asset_returns.index):
        raise ValueError("signal and asset_returns must share an index")

    positions = signal_to_positions(signal, lag=signal_lag)
    gross = strategy_returns(positions, asset_returns)
    net = apply_transaction_costs(gross, positions, cost_per_unit_turnover=cost_per_unit_turnover)

    gross_equity = initial_capital * (1.0 + gross).cumprod()
    net_equity = initial_capital * (1.0 + net).cumprod()

    return BacktestResult(
        positions=positions,
        gross_returns=gross,
        net_returns=net,
        gross_equity=gross_equity,
        net_equity=net_equity,
    )


@dataclass(frozen=True)
class PortfolioBacktestResult:
    """Container for the output of :func:`run_portfolio_backtest`.

    Attributes:
        positions: Weights actually held each period (the lagged targets).
        gross_returns: Portfolio returns before transaction costs.
        net_returns: Portfolio returns after transaction costs.
        gross_equity: Compounded equity curve from ``gross_returns``.
        net_equity: Compounded equity curve from ``net_returns``.
        turnover: Per-period traded weight ``sum_j |w_t,j - w_{t-1},j|``.
    """

    positions: pd.DataFrame
    gross_returns: pd.Series
    net_returns: pd.Series
    gross_equity: pd.Series
    net_equity: pd.Series
    turnover: pd.Series

    def summary(self, *, frequency: str = "daily") -> dict[str, float]:
        """Return headline performance statistics.

        Args:
            frequency: Data frequency, passed through to annualised metrics.

        Returns:
            A dictionary of gross/net total return, net Sharpe ratio, net
            maximum drawdown and average turnover.
        """
        total_gross = float((1.0 + self.gross_returns).prod() - 1.0)
        total_net = float((1.0 + self.net_returns).prod() - 1.0)
        return {
            "total_gross_return": total_gross,
            "total_net_return": total_net,
            "cost_drag": total_gross - total_net,
            "net_sharpe": sharpe_ratio(self.net_returns, frequency=frequency),
            "net_max_drawdown": max_drawdown(self.net_equity),
            "avg_turnover": float(self.turnover.mean()),
        }


def run_portfolio_backtest(
    target_weights: pd.DataFrame,
    asset_returns: pd.DataFrame,
    *,
    weight_lag: int = 1,
    cost_per_unit_turnover: float = 0.0005,
    initial_capital: float = 1.0,
) -> PortfolioBacktestResult:
    """Run a leakage-aware **multi-asset** backtest from a weight schedule.

    The pipeline mirrors the single-asset :func:`run_backtest`:

    1. **Lag** the target weights by ``weight_lag`` periods — a weight decided
       with information up to ``t`` can only be held from ``t + 1`` onward.
       The first ``weight_lag`` rows are flat (all zeros).
    2. **Apply** realised returns: portfolio return is the weight-weighted sum
       of asset returns each period.
    3. **Charge** proportional costs on the traded weight,
       ``cost * sum_j |w_t,j - w_{t-1},j|``, including the opening trade.
    4. **Compound** gross and net returns into equity curves.

    .. note::
       Turnover is computed on the *target* weights. Within-period weight
       drift (winners growing as a share of the book between rebalances) is
       deliberately ignored, exactly like the single-asset engine ignores
       compounding inside a period. The simplification keeps every number in
       the lesson reproducible by hand.

    Args:
        target_weights: Desired weights, one column per asset, computed from
            information available at each row's date. Rows need not sum to 1
            (e.g. partial cash positions are allowed).
        asset_returns: Realised per-period simple returns, same index and
            columns as ``target_weights``.
        weight_lag: Periods to delay the weights before holding (``>= 1``).
        cost_per_unit_turnover: Proportional cost per unit of traded weight.
        initial_capital: Starting capital for the equity curves.

    Returns:
        A :class:`PortfolioBacktestResult`.
    """
    if weight_lag < 1:
        raise ValueError("weight_lag must be >= 1 to avoid look-ahead")
    if cost_per_unit_turnover < 0:
        raise ValueError("cost_per_unit_turnover must be non-negative")
    if not target_weights.index.equals(asset_returns.index):
        raise ValueError("target_weights and asset_returns must share an index")
    if list(target_weights.columns) != list(asset_returns.columns):
        raise ValueError("target_weights and asset_returns must share columns")

    positions = target_weights.shift(weight_lag).fillna(0.0)
    gross = (positions * asset_returns).sum(axis=1)

    previous = positions.shift(1).fillna(0.0)
    traded = (positions - previous).abs().sum(axis=1)
    net = gross - cost_per_unit_turnover * traded

    gross_equity = initial_capital * (1.0 + gross).cumprod()
    net_equity = initial_capital * (1.0 + net).cumprod()

    return PortfolioBacktestResult(
        positions=positions,
        gross_returns=gross,
        net_returns=net,
        gross_equity=gross_equity,
        net_equity=net_equity,
        turnover=traded,
    )


def buy_and_hold_benchmark(asset_returns: pd.Series, *, initial_capital: float = 1.0) -> pd.Series:
    """Return the single-asset buy-and-hold equity curve.

    For one asset, buy-and-hold simply means staying fully invested: the equity
    curve is the compounded return path. It is the benchmark every single-asset
    strategy must be compared against.

    Args:
        asset_returns: Realised per-period returns.
        initial_capital: Starting capital.

    Returns:
        The buy-and-hold equity curve.
    """
    return initial_capital * (1.0 + asset_returns).cumprod()


def information_coefficient(signal: pd.Series, forward_returns: pd.Series) -> float:
    """Return the correlation between a (lagged) signal and forward returns.

    The information coefficient (IC) is a quick measure of predictive content.
    The caller must pass *forward* returns (the return earned *after* the signal
    date) so the comparison is honest.

    Args:
        signal: The predictive signal.
        forward_returns: Returns realised after each signal observation.

    Returns:
        The Pearson correlation, or ``0.0`` if either series is constant.
    """
    aligned = pd.concat([signal, forward_returns], axis=1, join="inner").dropna()
    if aligned.shape[0] < 3:
        return 0.0
    a = aligned.iloc[:, 0].to_numpy()
    b = aligned.iloc[:, 1].to_numpy()
    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])
