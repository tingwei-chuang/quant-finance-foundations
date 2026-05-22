"""Generate the bundled synthetic price dataset.

Running this script (re)creates ``data/sample/synthetic_prices.csv``. The file
is small, reproducible, and entirely repository-owned — it contains no
third-party market data. Every notebook and test can therefore run offline.

Usage::

    uv run python scripts/generate_synthetic_dataset.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from quant_math_roadmap.data.synthetic import SyntheticConfig, generate_correlated_prices
from quant_math_roadmap.data.validation import validate_price_frame

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "data" / "sample" / "synthetic_prices.csv"

# A fixed, documented configuration so the committed CSV is fully reproducible.
SAMPLE_CONFIG = SyntheticConfig(
    n_assets=5,
    n_periods=756,  # roughly three years of business days
    start="2019-01-01",
    seed=20240101,
    annual_drift=[0.08, 0.05, 0.10, 0.03, 0.06],
    annual_vol=[0.18, 0.14, 0.28, 0.10, 0.22],
    average_correlation=0.35,
    initial_price=100.0,
    market_factor_loading=0.30,
    vol_regime_multiplier=1.6,
    asset_names=["EQUITY_A", "EQUITY_B", "EQUITY_C", "DEFENSIVE_D", "CYCLICAL_E"],
)


def main() -> None:
    """Generate and write the synthetic price dataset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="destination CSV path (default: data/sample/synthetic_prices.csv)",
    )
    args = parser.parse_args()

    prices = generate_correlated_prices(SAMPLE_CONFIG)

    report = validate_price_frame(prices, require_business_days=True)
    report.raise_if_failed()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    prices.round(6).to_csv(args.output)

    print(f"Wrote {prices.shape[0]} rows x {prices.shape[1]} assets to {args.output}")
    print(f"Date range: {prices.index[0].date()} .. {prices.index[-1].date()}")
    print(f"Seed: {SAMPLE_CONFIG.seed} (reproducible)")


if __name__ == "__main__":
    main()
