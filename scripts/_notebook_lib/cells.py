"""Low-level cell builders shared by every week module.

Splitting these out of the monolithic ``build_notebooks.py`` (see roadmap item
P3-11) lets each per-week module import just the small surface it needs and
keeps merge conflicts contained to one week at a time.
"""

from __future__ import annotations

import nbformat as nbf

# Pinned kernel name. CI registers a kernelspec named ``python3``; do not
# change this without updating .github/workflows/ci.yml as well.
KERNELSPEC = {"display_name": "Python 3", "language": "python", "name": "python3"}
# Intentionally no ``version`` here: Jupyter rewrites it on save and that
# produced noisy diffs against the generator output.
LANGUAGE_INFO = {"name": "python"}


def md(text: str) -> nbf.NotebookNode:
    """Return a markdown cell from a (dedented) string."""
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text: str) -> nbf.NotebookNode:
    """Return a code cell from a (dedented) string."""
    return nbf.v4.new_code_cell(text.strip("\n"))


def ex_code(solution: bool, prompt: str, starter: str, answer: str) -> nbf.NotebookNode:
    """Return an exercise code cell.

    The main notebook gets a runnable ``starter``; the solution notebook gets
    the full ``answer``. Both keep the notebook executable end-to-end.
    """
    body = answer if solution else starter
    return code(prompt.strip("\n") + "\n" + body.strip("\n"))


def build(cells: list[nbf.NotebookNode]) -> nbf.NotebookNode:
    """Assemble cells into a notebook node with a pinned kernelspec.

    Cell IDs are assigned deterministically (``cell-000``, ``cell-001``, …) so
    that regenerating the notebooks produces byte-identical output. Without
    this, nbformat would mint a fresh UUID for each cell on every run, making
    the ``--check`` mode permanently noisy.
    """
    notebook = nbf.v4.new_notebook()
    notebook.cells = cells
    for i, cell in enumerate(cells):
        cell["id"] = f"cell-{i:03d}"
    notebook.metadata = {"kernelspec": KERNELSPEC, "language_info": LANGUAGE_INFO}
    return notebook
