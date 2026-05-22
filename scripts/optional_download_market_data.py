"""OPTIONAL helper for fetching real market data into a local, ignored folder.

This script is **not** required by any notebook or test. The entire course runs
on synthetic data. It exists only for learners who, *after* finishing the
methodology material, want to repeat an exercise on real prices.

Important rules
---------------
* Downloaded data is written to ``data/raw/``, which is git-ignored. **Never
  commit it.**
* You are responsible for complying with the terms of use of whichever data
  provider you choose. Many providers prohibit redistribution.
* This script intentionally ships **without** a hard dependency on any specific
  market-data library. It prints guidance and only attempts a download if you
  explicitly opt in and have an optional library installed.

Usage::

    uv run python scripts/optional_download_market_data.py --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"

GUIDANCE = """\
This optional script does not bundle a data provider.

To fetch real data yourself:

  1. Choose a provider and review its terms of use. Confirm that downloading
     and locally storing the data is permitted for your use case.
  2. Install a client library in your own environment, for example one of the
     community packages that wrap public market-data APIs.
  3. Save the result as a CSV into:

         data/raw/

     This folder is git-ignored. Downloaded data must never be committed to
     the repository.
  4. Load it with `quant_math_roadmap.data.loaders.load_prices_csv`, which
     validates the date index, checks for missing values, and verifies that
     prices are positive.

The course itself never needs this step: every notebook and test runs on the
reproducible synthetic dataset created by
`scripts/generate_synthetic_dataset.py`.
"""


def main() -> int:
    """Print download guidance and ensure the ignored raw-data folder exists."""
    parser = argparse.ArgumentParser(
        description="Optional, user-driven real-data download helper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=GUIDANCE,
    )
    parser.add_argument(
        "--acknowledge-terms",
        action="store_true",
        help="confirm you have reviewed and accept your data provider's terms",
    )
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(GUIDANCE)

    if not args.acknowledge_terms:
        print(
            "No data was downloaded. This script only prints guidance unless you "
            "implement a provider-specific download and pass --acknowledge-terms."
        )
        return 0

    print(
        f"Acknowledged. Place any downloaded CSV files into: {RAW_DIR}\n"
        "Reminder: data/raw/ is git-ignored on purpose. Do not commit market data."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
