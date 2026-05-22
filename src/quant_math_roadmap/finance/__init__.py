"""Finance building blocks: returns, metrics, fixed income, derivatives, portfolios."""

from __future__ import annotations

from .derivatives import (
    binomial_european_option,
    call_payoff,
    forward_payoff,
    long_straddle_payoff,
    put_call_parity_gap,
    put_payoff,
)
from .fixed_income import (
    bond_price,
    discount_curve,
    discount_factor,
    present_value,
    yield_to_maturity,
    zero_coupon_bond_price,
)
from .metrics import (
    PERIODS_PER_YEAR,
    annualized_mean,
    annualized_volatility,
    correlation_matrix,
    covariance_matrix,
    max_drawdown,
    periods_per_year,
    sharpe_ratio,
    turnover,
)
from .portfolio import (
    buy_and_hold_weights,
    equal_weights,
    minimum_variance_portfolio,
    portfolio_return,
    portfolio_variance,
    shrinkage_covariance,
)
from .returns import (
    cumulative_returns,
    log_returns,
    log_to_simple,
    simple_returns,
    simple_to_log,
    total_return,
)

__all__ = [
    "PERIODS_PER_YEAR",
    "annualized_mean",
    "annualized_volatility",
    "binomial_european_option",
    "bond_price",
    "buy_and_hold_weights",
    "call_payoff",
    "correlation_matrix",
    "covariance_matrix",
    "cumulative_returns",
    "discount_curve",
    "discount_factor",
    "equal_weights",
    "forward_payoff",
    "log_returns",
    "log_to_simple",
    "long_straddle_payoff",
    "max_drawdown",
    "minimum_variance_portfolio",
    "periods_per_year",
    "portfolio_return",
    "portfolio_variance",
    "present_value",
    "put_call_parity_gap",
    "put_payoff",
    "sharpe_ratio",
    "shrinkage_covariance",
    "simple_returns",
    "simple_to_log",
    "total_return",
    "turnover",
    "yield_to_maturity",
    "zero_coupon_bond_price",
]
