"""English-language section builders for the i18n notebook track.

These mirror :mod:`scripts._notebook_lib.parts` one-for-one. English notebooks
are emitted into ``notebooks/en/`` (solutions into ``notebooks/en/solutions/``),
which sit one directory deeper than their Chinese counterparts — hence the
different ``docs_prefix_en``.
"""

from __future__ import annotations

import nbformat as nbf

from .cells import code, md
from .parts import QuizItem, quiz_cells


def docs_prefix_en(solution: bool) -> str:
    """Relative prefix to ``docs/`` from ``notebooks/en[/solutions]/``."""
    return "../../../docs/" if solution else "../../docs/"


def quiz_cells_en(solution: bool, *, week: int, items: list[QuizItem]) -> list[nbf.NotebookNode]:
    """English wrapper around :func:`quiz_cells` (same hashes, English UI)."""
    return quiz_cells(solution, week=week, items=items, lang="en")


def style_setup_cell_en() -> nbf.NotebookNode:
    """Plot/rng setup for the English notebooks (no CJK font list needed)."""
    return code(
        "# Teaching style setup (deterministic look, consistent figures)\n"
        "import matplotlib as _mpl\n"
        "_mpl.rcParams['axes.unicode_minus'] = False\n"
        "_mpl.rcParams['figure.figsize'] = (8.5, 4.5)\n"
        "_mpl.rcParams['savefig.dpi'] = 100\n"
        "import numpy as _np\n"
        "_np.random.seed(0)  # belt-and-braces; library functions take explicit seeds"
    )


def header_en(
    *,
    solution: bool,
    week: str,
    title: str,
    objectives: list[str],
    hours: str,
    prereqs: list[str],
    resources: list[tuple[str, str]],
) -> list[nbf.NotebookNode]:
    """Return the standard English opening cells."""
    obj = "\n".join(f"- {o}" for o in objectives)
    pre = "\n".join(f"- {p}" for p in prereqs)
    res = "\n".join(f"- [{name}]({url})" for name, url in resources)
    res_block = res if resources else "- (Setup week — no external resources)"
    _ = solution  # reserved for future per-version header changes
    return [
        md(
            f"# {week} — {title}\n\n"
            "> Part of the open-source teaching project **quant-math-roadmap**.\n"
            "> For **education and research methodology only** — not investment "
            "advice; no result here represents a profitable or investable "
            "strategy."
        ),
        md(
            "## Learning objectives\n\n"
            f"{obj}\n\n"
            "## Estimated study time\n\n"
            f"About {hours}.\n\n"
            "## Prerequisites\n\n"
            f"{pre}\n\n"
            "## External resources\n\n"
            f"{res_block}\n\n"
            "> External resources are linked for reference only; this project "
            "does not reproduce any copyrighted course material."
        ),
        style_setup_cell_en(),
    ]


def footer_references_en(solution: bool) -> nbf.NotebookNode:
    """Return the standard English closing 'references and disclaimer' cell."""
    p = docs_prefix_en(solution)
    return md(
        "## References and attribution\n\n"
        "- Every explanation, example and exercise in this notebook is "
        "**original** to this project.\n"
        f"- Recommended external resources: [`docs/resources.md`]({p}resources.md).\n"
        f"- Concept notes: [`docs/math/`]({p}math/) and "
        f"[`docs/finance/`]({p}finance/).\n\n"
        "### Privacy and disclaimer\n\n"
        "- This notebook contains no real personal information.\n"
        "- This notebook uses only reproducible synthetic data and needs no "
        "network access.\n"
        "- This notebook makes no claim of real-world trading profitability."
    )


def checklist_en(items: list[str]) -> nbf.NotebookNode:
    """Return the English 'what you should be able to do' checklist cell."""
    body = "\n".join(f"- [ ] {i}" for i in items)
    return md("## After this week, you should be able to\n\n" + body)


def mistakes_en(items: list[str]) -> nbf.NotebookNode:
    """Return the English common-mistakes cell."""
    body = "\n".join(f"- **{i}**" for i in items)
    return md("## Common mistakes\n\n" + body)


def exercises_intro_en() -> nbf.NotebookNode:
    """Return the English exercises section heading."""
    return md(
        "## Exercises\n\n"
        "Work through these in order. **Basic exercises** consolidate the "
        "definitions, **applied exercises** are hands-on coding, and the "
        "**reflection question** connects the mathematics to backtesting and "
        "research methodology.\n\n"
        "> The main notebook ships runnable starter code for each coding "
        "exercise. Full reference answers live in the matching `_solution` "
        "notebook under `notebooks/en/solutions/`."
    )
