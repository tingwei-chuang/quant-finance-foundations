"""Validation helpers for price/return data.

Real and synthetic data alike can contain silent defects: gaps in the date
index, non-monotonic timestamps, missing values, or non-positive prices. Each
of these breaks a downstream assumption (returns, log returns, annualisation).
Validating *at the boundary* — right after loading — is far cheaper than
debugging a wrong Sharpe ratio later.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ValidationReport:
    """Outcome of validating a price frame.

    Attributes:
        ok: ``True`` when no problems were found.
        problems: Human-readable descriptions of every problem detected.
    """

    ok: bool = True
    problems: list[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        """Record a problem and mark the report as failed."""
        self.ok = False
        self.problems.append(message)

    def raise_if_failed(self) -> None:
        """Raise :class:`ValueError` if any problem was recorded."""
        if not self.ok:
            joined = "\n  - ".join(self.problems)
            raise ValueError(f"Price data failed validation:\n  - {joined}")


def validate_price_frame(
    prices: pd.DataFrame,
    *,
    require_business_days: bool = False,
) -> ValidationReport:
    """Check a price ``DataFrame`` for common data-quality defects.

    Checks performed:

    * the index is a :class:`~pandas.DatetimeIndex`;
    * timestamps are strictly increasing (monotonic, no duplicates);
    * there are no missing values;
    * all prices are strictly positive;
    * optionally, the index matches a continuous business-day range.

    Args:
        prices: Price panel with a datetime index and one column per asset.
        require_business_days: When ``True``, also verify the index equals a
            gap-free business-day range.

    Returns:
        A :class:`ValidationReport`. Call :meth:`ValidationReport.raise_if_failed`
        to convert problems into an exception.
    """
    report = ValidationReport()

    if not isinstance(prices.index, pd.DatetimeIndex):
        report.add("index is not a DatetimeIndex")
        return report

    if prices.empty:
        report.add("price frame is empty")
        return report

    if not prices.index.is_monotonic_increasing:
        report.add("timestamps are not monotonically increasing")

    if prices.index.has_duplicates:
        report.add("timestamps contain duplicates")

    missing = int(prices.isna().sum().sum())
    if missing > 0:
        report.add(f"found {missing} missing value(s)")

    non_positive = int((prices <= 0).sum().sum())
    if non_positive > 0:
        report.add(f"found {non_positive} non-positive price(s)")

    if require_business_days:
        expected = pd.bdate_range(
            start=prices.index[0], end=prices.index[-1], name=prices.index.name
        )
        if not prices.index.equals(expected):
            report.add("index does not match a continuous business-day range")

    return report
