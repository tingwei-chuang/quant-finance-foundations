"""Internal shared type aliases.

The aliases live in a leaf module so that any submodule can import them
without creating circular dependencies. Public callers should still go through
the concrete pandas/numpy types — these aliases are a convenience for the
internal API.
"""

from __future__ import annotations

import pandas as pd

type PandasData = pd.Series | pd.DataFrame
"""Either a labelled 1-D ``Series`` or a 2-D ``DataFrame`` of numeric values."""
