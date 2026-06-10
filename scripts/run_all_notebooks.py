"""Execute every course notebook top-to-bottom to validate it.

This is a lightweight, network-free notebook check: each notebook is run with
``nbclient`` and any execution error fails the script. The canonical CI
mechanism is ``pytest --nbmake`` (see ``.github/workflows/ci.yml``); this
script exists as a faster local convenience with a friendly per-notebook
progress line and optional parallelism.

Usage::

    uv run python scripts/run_all_notebooks.py
    uv run python scripts/run_all_notebooks.py --include-solutions --jobs 4
    uv run python scripts/run_all_notebooks.py --fail-fast
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = REPO_ROOT / "notebooks"

# Only execute the course notebooks themselves (NN_*.ipynb). A learner's
# scratch notebook dropped into notebooks/ should not silently fail CI.
COURSE_NB_GLOB = "[0-9][0-9]_*.ipynb"


def run_notebook(path: Path, timeout: int) -> tuple[bool, str, float]:
    """Execute a single notebook and report success.

    Args:
        path: Path to the ``.ipynb`` file.
        timeout: Per-cell execution timeout in seconds.

    Returns:
        A ``(success, message, elapsed_seconds)`` tuple.
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
        elapsed = time.perf_counter() - start
        return False, f"cell execution error: {exc}", elapsed
    except Exception as exc:  # noqa: BLE001 - surface any failure to the caller
        elapsed = time.perf_counter() - start
        return False, f"unexpected error: {exc}", elapsed
    elapsed = time.perf_counter() - start
    return True, "ok", elapsed


def _collect(include_solutions: bool) -> list[Path]:
    notebooks = sorted(NOTEBOOK_DIR.glob(COURSE_NB_GLOB))
    if include_solutions:
        notebooks += sorted((NOTEBOOK_DIR / "solutions").glob(COURSE_NB_GLOB))
    return notebooks


def main() -> int:
    """Run all notebooks and return a process exit code."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--include-solutions",
        action="store_true",
        help="also execute notebooks under notebooks/solutions/",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="per-cell timeout in seconds (default: 600, matches CI)",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="number of parallel notebook workers (default: 1)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="stop at the first failure instead of running every notebook",
    )
    args = parser.parse_args()

    notebooks = _collect(args.include_solutions)
    if not notebooks:
        print("No course notebooks found (looking for NN_*.ipynb).")
        return 1

    failures: list[str] = []

    def _report(path: Path, success: bool, message: str, elapsed: float) -> None:
        rel = path.relative_to(REPO_ROOT)
        status = "ok" if success else "FAIL"
        print(f"  {status:>4}  {elapsed:>5.1f}s  {rel}  {'' if success else message}")
        if not success:
            failures.append(str(rel))

    print(f"Running {len(notebooks)} notebook(s) with {args.jobs} worker(s):")
    if args.jobs <= 1:
        for path in notebooks:
            success, message, elapsed = run_notebook(path, args.timeout)
            _report(path, success, message, elapsed)
            if not success and args.fail_fast:
                break
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futures = {ex.submit(run_notebook, p, args.timeout): p for p in notebooks}
            try:
                for fut in as_completed(futures):
                    path = futures[fut]
                    success, message, elapsed = fut.result()
                    _report(path, success, message, elapsed)
                    if not success and args.fail_fast:
                        for other in futures:
                            other.cancel()
                        break
            except KeyboardInterrupt:
                return 130

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
