"""Generate the bundled synthetic price dataset.

Running this script (re)creates ``data/sample/synthetic_prices.csv``. The file
is small, reproducible, and entirely repository-owned — it contains no
third-party market data. Every notebook and test can therefore run offline.

Usage::

    uv run python scripts/generate_synthetic_dataset.py
"""

from __future__ import annotations

import argparse
import sys
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


def _render_csv() -> str:
    """Generate the dataset in memory and render it exactly as written to disk."""
    prices = generate_correlated_prices(SAMPLE_CONFIG)
    validate_price_frame(prices, require_business_days=True).raise_if_failed()
    return prices.round(6).to_csv()


def main() -> int:
    """Generate (or verify) the synthetic price dataset."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="destination CSV path (default: data/sample/synthetic_prices.csv)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="do not write anything; regenerate in memory and exit non-zero "
        "if the committed CSV differs from the generator output. Used by CI "
        "as a reproducibility guarantee for the sample dataset.",
    )
    args = parser.parse_args()

    rendered = _render_csv()

    if args.verify:
        if not args.output.exists():
            print(f"VERIFY FAILED: {args.output} does not exist.", file=sys.stderr)
            return 1
        # Normalise line endings so the check is OS-independent.
        committed = args.output.read_text().replace("\r\n", "\n")
        if committed != rendered.replace("\r\n", "\n"):
            print(
                f"VERIFY FAILED: {args.output} differs from the generator "
                "output. Regenerate it with:\n"
                "    uv run python scripts/generate_synthetic_dataset.py",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {args.output} matches the generator (seed {SAMPLE_CONFIG.seed}).")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)

    n_rows = rendered.count("\n") - 1
    print(f"Wrote {n_rows} rows to {args.output}")
    print(f"Seed: {SAMPLE_CONFIG.seed} (reproducible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
