"""Build (or check) the Week 0-8 notebooks and their solution counterparts.

This is the entry point. All of the actual cell content and per-week
builders live in :mod:`scripts._notebook_lib`. The split exists so that:

* a week can be edited (and merged) independently of the others;
* ``--only WEEK`` can target just one notebook;
* embedded notebook code lives next to the prose that explains it.

Two locales are generated from the same structure:

* Traditional Chinese (the primary track) into ``notebooks/`` and
  ``notebooks/solutions/``;
* English into ``notebooks/en/`` and ``notebooks/en/solutions/``.

Run with ``uv run python scripts/build_notebooks.py``. The generated
``.ipynb`` files are the artefacts learners actually open and edit.

Every generated notebook:

* runs top-to-bottom offline using synthetic data only;
* uses deterministic seeds;
* imports reusable logic from the ``quant_math_roadmap`` package;
* contains the pedagogical structure required by the roadmap.
"""

from __future__ import annotations

import argparse
import io
import sys
from collections.abc import Callable
from pathlib import Path

import nbformat as nbf

# Make ``_notebook_lib`` importable when this file is invoked directly
# (``python scripts/build_notebooks.py``); when imported as a module the
# package layout already works.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _notebook_lib import NOTEBOOKS, NOTEBOOKS_EN, build, md  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
NB_DIR = REPO_ROOT / "notebooks"

WeekBuilder = Callable[[bool], list[nbf.NotebookNode]]

SOLUTION_BANNERS = {
    "zh": (
        "> 這是對應主 notebook 的**完整參考解答版**。建議先自己完成主"
        "notebook 的練習，再對照本檔。所有解說與解答皆為本專案原創。"
    ),
    "en": (
        "> This is the **full reference-solution edition** of the matching "
        "main notebook. Try the exercises yourself first, then compare. All "
        "explanations and answers are original to this project."
    ),
}

SOLUTION_TITLES = {"zh": "（參考解答）", "en": "(Reference solutions) "}

# (locale, dispatch table, main output dir, solutions output dir)
TRACKS: list[tuple[str, dict[str, WeekBuilder], Path, Path]] = [
    ("zh", NOTEBOOKS, NB_DIR, NB_DIR / "solutions"),
    ("en", NOTEBOOKS_EN, NB_DIR / "en", NB_DIR / "en" / "solutions"),
]


def _render_pair(
    stem: str, builder: WeekBuilder, locale: str
) -> tuple[nbf.NotebookNode, nbf.NotebookNode]:
    """Build the (main, solution) notebook node pair for one week."""
    main_nb = build(builder(False))
    sol_cells = [
        md(f"# {SOLUTION_TITLES[locale]}{stem}\n\n{SOLUTION_BANNERS[locale]}"),
        *builder(True),
    ]
    sol_nb = build(sol_cells)
    return main_nb, sol_nb


def _normalise(nb: nbf.NotebookNode) -> str:
    """Serialise a notebook to a stable JSON string for byte-level diffs."""
    buf = io.StringIO()
    nbf.write(nb, buf)
    return buf.getvalue()


def main() -> int:
    """Generate (or check) all main and solution notebooks in both locales."""
    parser = argparse.ArgumentParser(
        description="Build (or check) the Week 0-8 notebooks and their solutions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--only",
        metavar="WEEK",
        help="rebuild only the notebook(s) whose stem starts with WEEK "
        "(e.g. --only 03 rebuilds the Week 3 pair in both locales).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write any files; instead regenerate every notebook in "
        "memory and report a non-zero exit code if the committed file differs. "
        "Used by CI to catch drift between the generator and the committed "
        "notebooks.",
    )
    args = parser.parse_args()

    selected: list[tuple[str, WeekBuilder, str, Path, Path]] = [
        (stem, builder, locale, main_dir, sol_dir)
        for locale, table, main_dir, sol_dir in TRACKS
        for stem, builder in table.items()
        if args.only is None or stem.startswith(args.only)
    ]
    if not selected:
        print(f"--only={args.only!r} matched no notebook stem.", file=sys.stderr)
        return 2

    if args.check:
        drifted: list[str] = []
        for stem, builder, locale, main_dir, sol_dir in selected:
            main_nb, sol_nb = _render_pair(stem, builder, locale)
            main_path = main_dir / f"{stem}.ipynb"
            sol_path = sol_dir / f"{stem}_solution.ipynb"
            for path, fresh in ((main_path, main_nb), (sol_path, sol_nb)):
                if not path.exists():
                    drifted.append(f"{path.relative_to(REPO_ROOT)}: missing")
                    continue
                if path.read_text() != _normalise(fresh):
                    drifted.append(f"{path.relative_to(REPO_ROOT)}: differs from generator")
        if drifted:
            print("Notebook drift detected:", file=sys.stderr)
            for d in drifted:
                print(f"  - {d}", file=sys.stderr)
            print(
                "\nRun  uv run python scripts/build_notebooks.py  to regenerate.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {len(selected)} notebook pair(s) match the generator.")
        return 0

    for stem, builder, locale, main_dir, sol_dir in selected:
        main_dir.mkdir(parents=True, exist_ok=True)
        sol_dir.mkdir(parents=True, exist_ok=True)
        main_nb, sol_nb = _render_pair(stem, builder, locale)
        nbf.write(main_nb, main_dir / f"{stem}.ipynb")
        nbf.write(sol_nb, sol_dir / f"{stem}_solution.ipynb")
        print(f"generated [{locale}] {stem}.ipynb  (+ solution)")
    print(f"\nDone: {len(selected)} notebook pair(s) across {len(TRACKS)} locale(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
