"""Validate every course notebook by executing it top-to-bottom.

This script is a thin, friendly wrapper around the **same** ``pytest --nbmake``
invocation that CI uses, so local runs and CI cannot drift apart. (Previously
this script and CI used two different mechanisms — see the engineering
roadmap, item P2-7.)

Usage::

    uv run python scripts/run_all_notebooks.py
    uv run python scripts/run_all_notebooks.py --include-solutions
    uv run python scripts/run_all_notebooks.py --jobs auto --fail-fast
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = REPO_ROOT / "notebooks"


def main() -> int:
    """Run nbmake on the course notebooks and return its exit code."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--include-solutions",
        action="store_true",
        help="also execute notebooks under notebooks/solutions/ (default: no, "
        "since pytest collects them recursively from notebooks/ anyway -- this "
        "flag is kept for backward compatibility)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="per-cell timeout in seconds (default: 600, matches CI)",
    )
    parser.add_argument(
        "--jobs",
        default="0",
        help="pytest-xdist worker count (e.g. 4 or 'auto'); 0 = serial",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop at the first failing notebook (pytest --maxfail=1)",
    )
    parser.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        help="extra arguments are passed through to pytest after --",
    )
    args = parser.parse_args()

    if shutil.which("uv") is None and not (REPO_ROOT / ".venv").exists():
        print("warning: no .venv detected; try `uv sync --extra dev` first.")

    # Pytest recursion already picks up notebooks/solutions/ -- listing both
    # would only matter if the directories were not nested.
    target = NOTEBOOK_DIR if not args.include_solutions else NOTEBOOK_DIR
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--nbmake",
        str(target),
        f"--nbmake-timeout={args.timeout}",
        "-q",
    ]
    if args.fail_fast:
        cmd.append("--maxfail=1")
    if args.jobs != "0":
        # Requires pytest-xdist; pip-install it locally if you want parallelism.
        cmd += ["-n", args.jobs]
    if args.extra:
        # Drop a leading "--" if argparse left one in.
        extras = args.extra[1:] if args.extra and args.extra[0] == "--" else args.extra
        cmd += extras

    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=REPO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
