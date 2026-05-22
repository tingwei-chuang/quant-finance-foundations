"""Tests for time value of money and bond pricing (Week 6)."""

from __future__ import annotations

import pytest

from quant_math_roadmap.finance.fixed_income import (
    bond_price,
    discount_factor,
    present_value,
    yield_to_maturity,
    zero_coupon_bond_price,
)


def test_discount_factor_zero_rate_is_one() -> None:
    assert discount_factor(0.0, 5.0) == pytest.approx(1.0)


def test_discount_factor_decreases_with_time() -> None:
    df1 = discount_factor(0.05, 1.0)
    df5 = discount_factor(0.05, 5.0)
    assert df5 < df1 < 1.0


def test_discount_factor_known_value() -> None:
    # 5% annual, 2 years, annual compounding: 1 / 1.05**2.
    assert discount_factor(0.05, 2.0) == pytest.approx(1.0 / 1.05**2)


def test_present_value_of_single_cash_flow() -> None:
    pv = present_value([100.0], [3.0], 0.04)
    assert pv == pytest.approx(100.0 * discount_factor(0.04, 3.0))


def test_present_value_zero_rate_is_sum() -> None:
    pv = present_value([10.0, 20.0, 30.0], [1.0, 2.0, 3.0], 0.0)
    assert pv == pytest.approx(60.0)


def test_zero_coupon_bond_equals_discounted_face() -> None:
    price = zero_coupon_bond_price(1000.0, 4.0, 0.03)
    assert price == pytest.approx(1000.0 * discount_factor(0.03, 4.0))
    assert price < 1000.0


def test_bond_priced_at_par_when_coupon_equals_yield() -> None:
    # A bond whose coupon rate equals its yield prices at par (face value).
    price = bond_price(
        face_value=1000.0,
        coupon_rate=0.06,
        years_to_maturity=5.0,
        yield_to_maturity=0.06,
        coupons_per_year=2,
    )
    assert price == pytest.approx(1000.0, rel=1e-9)


def test_bond_premium_and_discount() -> None:
    par = 1000.0
    premium = bond_price(par, 0.08, 5.0, 0.06, coupons_per_year=2)
    discount = bond_price(par, 0.04, 5.0, 0.06, coupons_per_year=2)
    assert premium > par  # high coupon -> premium bond
    assert discount < par  # low coupon -> discount bond


def test_bond_price_decreases_with_yield() -> None:
    low = bond_price(1000.0, 0.05, 10.0, 0.03, coupons_per_year=2)
    high = bond_price(1000.0, 0.05, 10.0, 0.07, coupons_per_year=2)
    assert high < low


def test_yield_to_maturity_inverts_bond_price() -> None:
    true_yield = 0.045
    price = bond_price(1000.0, 0.05, 7.0, true_yield, coupons_per_year=2)
    recovered = yield_to_maturity(price, 1000.0, 0.05, 7.0, coupons_per_year=2)
    assert recovered == pytest.approx(true_yield, abs=1e-6)


def test_bond_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        bond_price(-1.0, 0.05, 5.0, 0.05)
    with pytest.raises(ValueError):
        bond_price(1000.0, 0.05, 0.0, 0.05)
