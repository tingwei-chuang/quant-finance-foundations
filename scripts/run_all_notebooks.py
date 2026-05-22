"""Execute every course notebook top-to-bottom to validate it.

This is a lightweight, network-free notebook check: each notebook is run with
``nbclient`` and any execution error fails the script. It is the same kind of
validation the CI workflow performs (CI uses ``pytest --nbmake``).

Usage::

    uv run python scripts/run_all_notebooks.py
    uv run python scripts/run_all_notebooks.py --include-solutions
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = REPO_ROOT / "notebooks"


def run_notebook(path: Path, timeout: int) -> tuple[bool, str]:
    """Execute a single notebook and report success.

    Args:
        path: Path to the ``.ipynb`` file.
        timeout: Per-cell execution timeout in seconds.

    Returns:
        A ``(success, message)`` tuple.
    """
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    )
    start = time.perf_counter()
    try:
        client.execute()
    except CellExecutionError as exc:
        return False, f"cell execution error: {exc}"
    except Exception as exc:  # noqa: BLE001 - surface any failure to the caller
        return False, f"unexpected error: {exc}"
    elapsed = time.perf_counter() - start
    return True, f"ok ({elapsed:.1f}s)"


def main() -> int:
    """Run all notebooks and return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-solutions",
        action="store_true",
        help="also execute notebooks under notebooks/solutions/",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="per-cell timeout in seconds (default: 600)",
    )
    args = parser.parse_args()

    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if args.include_solutions:
        notebooks += sorted((NOTEBOOK_DIR / "solutions").glob("*.ipynb"))

    if not notebooks:
        print("No notebooks found.")
        return 1

    failures: list[str] = []
    for path in notebooks:
        rel = path.relative_to(REPO_ROOT)
        print(f"Running {rel} ... ", end="", flush=True)
        success, message = run_notebook(path, args.timeout)
        print(message)
        if not success:
            failures.append(str(rel))

    print()
    if failures:
        print(f"FAILED ({len(failures)}/{len(notebooks)}):")
        for name in failures:
            print(f"  - {name}")
        return 1
    print(f"All {len(notebooks)} notebook(s) executed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
