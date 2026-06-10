"""Leakage-aware backtesting: baselines, costs, engine, leakage checks."""

from __future__ import annotations

from .baselines import (
    baseline_turnover_comparison,
    buy_and_hold_equity,
    equal_weight_rebalanced_equity,
)
from .costs import (
    annualized_turnover,
    apply_transaction_costs,
    cost_summary,
    position_turnover,
)
from .engine import (
    BacktestResult,
    PortfolioBacktestResult,
    buy_and_hold_benchmark,
    information_coefficient,
    run_backtest,
    run_portfolio_backtest,
)
from .leakage_checks import (
    assert_no_lookahead,
    leaked_strategy_returns,
    signal_to_positions,
    strategy_returns,
)
from .sweeps import (
    lookback_parameter_sweep,
    trailing_momentum_signal,
)

__all__ = [
    "PortfolioBacktestResult",
    "lookback_parameter_sweep",
    "run_portfolio_backtest",
    "trailing_momentum_signal",
    "BacktestResult",
    "annualized_turnover",
    "apply_transaction_costs",
    "assert_no_lookahead",
    "baseline_turnover_comparison",
    "buy_and_hold_benchmark",
    "buy_and_hold_equity",
    "cost_summary",
    "equal_weight_rebalanced_equity",
    "information_coefficient",
    "leaked_strategy_returns",
    "position_turnover",
    "run_backtest",
    "signal_to_positions",
    "strategy_returns",
]
