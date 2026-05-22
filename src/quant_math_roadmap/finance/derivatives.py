"""Option payoffs and binomial-tree pricing (Week 6).

The roadmap deliberately stops at the *binomial* model. It needs only
arithmetic and the no-arbitrage idea, yet it already delivers the key insight:
an option price is a discounted, risk-neutral expectation of its payoff.
Black-Scholes and stochastic calculus are intentionally out of scope.

None of these prices should be read as predictions of real market prices.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


def call_payoff(spot: npt.ArrayLike, strike: float) -> FloatArray:
    """Return the payoff of a European call at expiry: ``max(S - K, 0)``.

    Args:
        spot: Underlying price(s) at expiry.
        strike: Strike price ``K``.

    Returns:
        The call payoff, elementwise.
    """
    s = np.asarray(spot, dtype=float)
    return np.maximum(s - strike, 0.0)


def put_payoff(spot: npt.ArrayLike, strike: float) -> FloatArray:
    """Return the payoff of a European put at expiry: ``max(K - S, 0)``.

    Args:
        spot: Underlying price(s) at expiry.
        strike: Strike price ``K``.

    Returns:
        The put payoff, elementwise.
    """
    s = np.asarray(spot, dtype=float)
    return np.maximum(strike - s, 0.0)


def forward_payoff(spot: npt.ArrayLike, forward_price: float) -> FloatArray:
    """Return the payoff of a long forward/futures position: ``S - F``.

    A forward is linear in the underlying: there is no optionality, so the
    payoff can be negative.

    Args:
        spot: Underlying price(s) at expiry.
        forward_price: The agreed forward price ``F``.

    Returns:
        The long-forward payoff, elementwise.
    """
    s = np.asarray(spot, dtype=float)
    return s - forward_price


def long_straddle_payoff(spot: npt.ArrayLike, strike: float) -> FloatArray:
    """Return the payoff of a long straddle (one call + one put at ``strike``).

    A straddle profits from large moves in either direction; it is the simplest
    combination used in the Week 6 payoff-diagram exercises.

    Args:
        spot: Underlying price(s) at expiry.
        strike: Shared strike price.

    Returns:
        The combined payoff ``|S - K|``.
    """
    return call_payoff(spot, strike) + put_payoff(spot, strike)


def binomial_european_option(
    spot: float,
    strike: float,
    rate: float,
    volatility: float,
    maturity: float,
    *,
    n_steps: int = 100,
    option_type: str = "call",
) -> float:
    """Price a European option with the Cox-Ross-Rubinstein binomial tree.

    The underlying moves up by ``u = exp(sigma * sqrt(dt))`` or down by
    ``d = 1/u`` each step. The *risk-neutral* up-probability ``p`` makes the
    discounted expected price a martingale; the option value is the discounted
    risk-neutral expectation of its terminal payoff.

    As ``n_steps`` grows the price converges to the Black-Scholes value, but
    the binomial route needs no stochastic calculus.

    Args:
        spot: Current underlying price ``S0`` (positive).
        strike: Strike price ``K`` (positive).
        rate: Continuously-compounded annual risk-free rate.
        volatility: Annual volatility proxy ``sigma`` (positive).
        maturity: Time to expiry in years (positive).
        n_steps: Number of tree steps; more steps means finer convergence.
        option_type: ``"call"`` or ``"put"``.

    Returns:
        The present value of the option.
    """
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    if maturity <= 0:
        raise ValueError("maturity must be positive")
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1")
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")

    dt = maturity / n_steps
    up = np.exp(volatility * np.sqrt(dt))
    down = 1.0 / up
    discount = np.exp(-rate * dt)
    p_up = (np.exp(rate * dt) - down) / (up - down)
    if not 0.0 <= p_up <= 1.0:
        raise ValueError(
            "risk-neutral probability outside [0, 1]; reduce the step size "
            "or check rate/volatility inputs"
        )

    # Terminal underlying prices: j up-moves out of n_steps.
    j = np.arange(n_steps + 1)
    terminal_spot = spot * (up**j) * (down ** (n_steps - j))
    if option_type == "call":
        values = call_payoff(terminal_spot, strike)
    else:
        values = put_payoff(terminal_spot, strike)

    # Roll the tree back to the root.
    for _ in range(n_steps):
        values = discount * (p_up * values[1:] + (1.0 - p_up) * values[:-1])
    return float(values[0])


def put_call_parity_gap(
    call_price: float,
    put_price: float,
    spot: float,
    strike: float,
    rate: float,
    maturity: float,
) -> float:
    """Return the residual of European put-call parity.

    Parity states ``C - P = S - K * exp(-r * T)``. For arbitrage-free,
    consistently priced European options the returned gap should be ~0; the
    Week 6 notebook uses it as a sanity check on the binomial pricer.

    Args:
        call_price: European call price.
        put_price: European put price.
        spot: Current underlying price.
        strike: Shared strike.
        rate: Continuously-compounded risk-free rate.
        maturity: Time to expiry in years.

    Returns:
        ``(C - P) - (S - K * exp(-r * T))``.
    """
    discounted_strike = strike * np.exp(-rate * maturity)
    return float((call_price - put_price) - (spot - discounted_strike))
