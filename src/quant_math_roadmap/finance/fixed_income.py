"""Time value of money and bond pricing (Week 6).

Everything here follows from one idea: a cash flow received later is worth less
than the same cash flow today, because money can earn a return in between. The
*discount factor* turns a future amount into its present value.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt


def discount_factor(rate: float, time: float, *, periods_per_year: int = 1) -> float:
    """Return the discount factor for one cash flow.

    With a per-year rate ``r`` compounded ``m`` times per year, a cash flow
    ``t`` years away is discounted by ``(1 + r/m)^(-m*t)``.

    Args:
        rate: Annual interest rate (e.g. ``0.05`` for 5%).
        time: Time until the cash flow, in years.
        periods_per_year: Compounding frequency ``m``.

    Returns:
        The discount factor in ``(0, 1]`` for non-negative rates and times.
    """
    if periods_per_year < 1:
        raise ValueError("periods_per_year must be >= 1")
    if time < 0:
        raise ValueError("time must be non-negative")
    # Per-period gross factor must stay positive. Negative annual rates are
    # legitimate (and give discount factors > 1), but rates so negative that
    # 1 + r/m <= 0 are nonsensical here and silently produce wrong values
    # (even powers) or complex numbers (odd powers).
    per_period = 1.0 + rate / periods_per_year
    if per_period <= 0.0:
        raise ValueError(
            f"rate {rate!r} with periods_per_year={periods_per_year} gives a "
            "non-positive per-period gross factor; discounting is undefined"
        )
    return float(per_period ** (-periods_per_year * time))


def present_value(
    cash_flows: Sequence[float],
    times: Sequence[float],
    rate: float,
    *,
    periods_per_year: int = 1,
) -> float:
    """Return the present value of a stream of dated cash flows.

    Args:
        cash_flows: Cash-flow amounts.
        times: Time (in years) of each cash flow; must align with ``cash_flows``.
        rate: Annual discount rate.
        periods_per_year: Compounding frequency.

    Returns:
        The sum of discounted cash flows.
    """
    cf = np.asarray(cash_flows, dtype=float)
    ts = np.asarray(times, dtype=float)
    if cf.shape != ts.shape:
        raise ValueError("cash_flows and times must have the same length")
    factors = np.array([discount_factor(rate, t, periods_per_year=periods_per_year) for t in ts])
    return float(np.sum(cf * factors))


def bond_price(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_to_maturity: float,
    *,
    coupons_per_year: int = 2,
) -> float:
    """Price a fixed-coupon bond by discounting its cash flows.

    The bond pays a coupon of ``face_value * coupon_rate / coupons_per_year``
    every period and returns ``face_value`` at maturity. Each cash flow is
    discounted at ``yield_to_maturity``.

    Args:
        face_value: Principal repaid at maturity.
        coupon_rate: Annual coupon rate (``0.0`` gives a zero-coupon bond).
        years_to_maturity: Maturity in years; must be a whole number of coupon
            periods.
        yield_to_maturity: Annual yield used to discount cash flows.
        coupons_per_year: Coupon payment frequency.

    Returns:
        The present value (price) of the bond.
    """
    if face_value <= 0:
        raise ValueError("face_value must be positive")
    if years_to_maturity <= 0:
        raise ValueError("years_to_maturity must be positive")
    if coupons_per_year < 1:
        raise ValueError("coupons_per_year must be >= 1")

    n_periods = years_to_maturity * coupons_per_year
    if not np.isclose(n_periods, round(n_periods)):
        raise ValueError("years_to_maturity must be a whole number of coupon periods")
    n_periods = int(round(n_periods))

    coupon = face_value * coupon_rate / coupons_per_year
    cash_flows = [coupon] * n_periods
    cash_flows[-1] += face_value
    times = [(i + 1) / coupons_per_year for i in range(n_periods)]
    return present_value(cash_flows, times, yield_to_maturity, periods_per_year=coupons_per_year)


def zero_coupon_bond_price(
    face_value: float,
    years_to_maturity: float,
    yield_to_maturity: float,
    *,
    periods_per_year: int = 1,
) -> float:
    """Price a zero-coupon bond (a single cash flow at maturity).

    Args:
        face_value: Amount repaid at maturity.
        years_to_maturity: Maturity in years.
        yield_to_maturity: Annual discount yield.
        periods_per_year: Compounding frequency.

    Returns:
        The discounted present value of the face value.
    """
    return face_value * discount_factor(
        yield_to_maturity, years_to_maturity, periods_per_year=periods_per_year
    )


def _bond_cash_flows(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    coupons_per_year: int,
) -> tuple[list[float], list[float]]:
    """Return the ``(cash_flows, times)`` schedule of a fixed-coupon bond."""
    if face_value <= 0:
        raise ValueError("face_value must be positive")
    if years_to_maturity <= 0:
        raise ValueError("years_to_maturity must be positive")
    if coupons_per_year < 1:
        raise ValueError("coupons_per_year must be >= 1")
    n_periods = years_to_maturity * coupons_per_year
    if not np.isclose(n_periods, round(n_periods)):
        raise ValueError("years_to_maturity must be a whole number of coupon periods")
    n_periods = int(round(n_periods))
    coupon = face_value * coupon_rate / coupons_per_year
    cash_flows = [coupon] * n_periods
    cash_flows[-1] += face_value
    times = [(i + 1) / coupons_per_year for i in range(n_periods)]
    return cash_flows, times


def macaulay_duration(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_to_maturity: float,
    *,
    coupons_per_year: int = 2,
) -> float:
    """Macaulay duration: the PV-weighted average time of a bond's cash flows.

    Duration is the natural "centre of mass" of a bond: a zero-coupon bond's
    Macaulay duration equals its maturity exactly, and coupons pull duration
    below maturity. It is the first step toward measuring interest-rate risk.

    Args:
        face_value: Principal repaid at maturity.
        coupon_rate: Annual coupon rate.
        years_to_maturity: Maturity in years (whole number of coupon periods).
        yield_to_maturity: Annual yield used to discount cash flows.
        coupons_per_year: Coupon payment frequency.

    Returns:
        The Macaulay duration, in years.
    """
    cash_flows, times = _bond_cash_flows(
        face_value, coupon_rate, years_to_maturity, coupons_per_year
    )
    pvs = np.array(
        [
            cf * discount_factor(yield_to_maturity, t, periods_per_year=coupons_per_year)
            for cf, t in zip(cash_flows, times, strict=True)
        ]
    )
    price = float(pvs.sum())
    return float(np.dot(times, pvs) / price)


def modified_duration(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_to_maturity: float,
    *,
    coupons_per_year: int = 2,
) -> float:
    """Modified duration: the bond's percentage price sensitivity to yield.

    ``D_mod = -(1/P) dP/dy = D_Macaulay / (1 + y/m)``. A modified duration of
    7 means a 1-percentage-point rise in yield knocks roughly 7% off the
    price (to first order — convexity captures the curvature beyond that).

    Args:
        face_value: Principal repaid at maturity.
        coupon_rate: Annual coupon rate.
        years_to_maturity: Maturity in years (whole number of coupon periods).
        yield_to_maturity: Annual yield used to discount cash flows.
        coupons_per_year: Coupon payment frequency.

    Returns:
        The modified duration, in years.
    """
    macaulay = macaulay_duration(
        face_value,
        coupon_rate,
        years_to_maturity,
        yield_to_maturity,
        coupons_per_year=coupons_per_year,
    )
    return macaulay / (1.0 + yield_to_maturity / coupons_per_year)


def bond_convexity(
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    yield_to_maturity: float,
    *,
    coupons_per_year: int = 2,
) -> float:
    """Convexity: the second-order price sensitivity ``(1/P) d²P/dy²``.

    Duration alone linearises the price/yield curve; convexity corrects for
    its curvature. The second-order price approximation is::

        ΔP/P ≈ -D_mod · Δy + 0.5 · C · Δy²

    For plain (option-free) bonds convexity is positive: prices fall less for
    a yield rise, and gain more for a yield fall, than duration alone implies.

    Args:
        face_value: Principal repaid at maturity.
        coupon_rate: Annual coupon rate.
        years_to_maturity: Maturity in years (whole number of coupon periods).
        yield_to_maturity: Annual yield used to discount cash flows.
        coupons_per_year: Coupon payment frequency.

    Returns:
        The convexity, in years².
    """
    cash_flows, times = _bond_cash_flows(
        face_value, coupon_rate, years_to_maturity, coupons_per_year
    )
    m = coupons_per_year
    y = yield_to_maturity
    per_period = 1.0 + y / m
    if per_period <= 0.0:
        raise ValueError("yield gives a non-positive per-period gross factor")
    price = 0.0
    second_derivative = 0.0
    for cf, t in zip(cash_flows, times, strict=True):
        df = per_period ** (-m * t)
        price += cf * df
        # d²/dy² of (1+y/m)^(-m t) = t (t + 1/m) (1+y/m)^(-m t - 2)
        second_derivative += cf * t * (t + 1.0 / m) * per_period ** (-m * t - 2.0)
    return float(second_derivative / price)


def yield_to_maturity(
    price: float,
    face_value: float,
    coupon_rate: float,
    years_to_maturity: float,
    *,
    coupons_per_year: int = 2,
    tol: float = 1e-10,
    max_iter: int = 200,
) -> float:
    """Solve for the yield that reprices a bond to an observed market price.

    Uses bisection: bond price is strictly decreasing in yield, so the root is
    unique and bracketed reliably.

    Args:
        price: Observed bond price.
        face_value: Bond principal.
        coupon_rate: Annual coupon rate.
        years_to_maturity: Maturity in years.
        coupons_per_year: Coupon frequency.
        tol: Convergence tolerance on price.
        max_iter: Maximum bisection iterations.

    Returns:
        The annual yield to maturity.
    """
    if price <= 0:
        raise ValueError("price must be positive")

    low, high = -0.99, 10.0

    def price_at(y: float) -> float:
        return bond_price(
            face_value,
            coupon_rate,
            years_to_maturity,
            y,
            coupons_per_year=coupons_per_year,
        )

    if (price_at(low) - price) * (price_at(high) - price) > 0:
        raise ValueError("could not bracket the yield; check the inputs")

    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        diff = price_at(mid) - price
        if abs(diff) < tol:
            return mid
        # price decreases in yield: if model price too high, raise the yield.
        if diff > 0:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


def discount_curve(
    rate: float, times: Sequence[float], *, periods_per_year: int = 1
) -> npt.NDArray[np.float64]:
    """Return discount factors for a sequence of maturities at a flat rate.

    Args:
        rate: Annual interest rate.
        times: Maturities in years.
        periods_per_year: Compounding frequency.

    Returns:
        An array of discount factors aligned with ``times``.
    """
    return np.array([discount_factor(rate, t, periods_per_year=periods_per_year) for t in times])
