"""Time-aware train/test splitting (Weeks 7 and 8).

Random k-fold splitting is *wrong* for time-series prediction: it lets the
model train on the future to predict the past. Every splitter here respects
the arrow of time — the training set is always strictly earlier than the test
set it is paired with.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
import pandas as pd

IndexLike = pd.Index | np.ndarray


@dataclass(frozen=True)
class Split:
    """A single train/test split expressed as positional index arrays.

    Attributes:
        train_index: Positional indices of the training observations.
        test_index: Positional indices of the test observations.
    """

    train_index: np.ndarray
    test_index: np.ndarray

    def __post_init__(self) -> None:
        if self.train_index.size == 0 or self.test_index.size == 0:
            raise ValueError("both train and test index must be non-empty")
        if self.train_index.max() >= self.test_index.min():
            raise ValueError(
                "look-ahead detected: every training index must precede every test index"
            )


def train_test_split_time(n_samples: int, *, test_size: float = 0.3) -> Split:
    """Split a series into one earlier train block and one later test block.

    Args:
        n_samples: Total number of observations.
        test_size: Fraction of observations assigned to the (later) test block,
            in ``(0, 1)``.

    Returns:
        A :class:`Split` with contiguous, time-ordered train and test indices.
    """
    if n_samples < 2:
        raise ValueError("need at least two samples to split")
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must lie in (0, 1)")
    n_test = max(1, int(round(n_samples * test_size)))
    n_train = n_samples - n_test
    if n_train < 1:
        raise ValueError("test_size leaves no training data")
    train_index = np.arange(n_train)
    test_index = np.arange(n_train, n_samples)
    return Split(train_index=train_index, test_index=test_index)


def expanding_window_splits(
    n_samples: int,
    *,
    initial_train_size: int,
    test_size: int = 1,
    step: int | None = None,
) -> Iterator[Split]:
    """Yield expanding-window (anchored) walk-forward splits.

    The training window always starts at observation ``0`` and grows; each test
    block immediately follows the current training window. This mimics a
    researcher who keeps *all* history and re-fits as new data arrives.

    Args:
        n_samples: Total number of observations.
        initial_train_size: Size of the first training window.
        test_size: Number of observations in each test block.
        step: How far the training window advances between splits. Defaults to
            ``test_size`` (non-overlapping test blocks).

    Yields:
        :class:`Split` objects in chronological order.
    """
    if initial_train_size < 1:
        raise ValueError("initial_train_size must be >= 1")
    if test_size < 1:
        raise ValueError("test_size must be >= 1")
    advance = test_size if step is None else step
    if advance < 1:
        raise ValueError("step must be >= 1")

    train_end = initial_train_size
    while train_end + test_size <= n_samples:
        train_index = np.arange(0, train_end)
        test_index = np.arange(train_end, train_end + test_size)
        yield Split(train_index=train_index, test_index=test_index)
        train_end += advance


def rolling_window_splits(
    n_samples: int,
    *,
    train_size: int,
    test_size: int = 1,
    step: int | None = None,
) -> Iterator[Split]:
    """Yield rolling-window (fixed-length) walk-forward splits.

    The training window has a *constant* length and slides forward, so the
    model always learns from the most recent ``train_size`` observations and
    deliberately forgets the distant past. This is the right choice when the
    data-generating process drifts over time.

    Args:
        n_samples: Total number of observations.
        train_size: Fixed size of every training window.
        test_size: Number of observations in each test block.
        step: How far the window advances between splits. Defaults to
            ``test_size``.

    Yields:
        :class:`Split` objects in chronological order.
    """
    if train_size < 1:
        raise ValueError("train_size must be >= 1")
    if test_size < 1:
        raise ValueError("test_size must be >= 1")
    advance = test_size if step is None else step
    if advance < 1:
        raise ValueError("step must be >= 1")

    train_start = 0
    while train_start + train_size + test_size <= n_samples:
        train_index = np.arange(train_start, train_start + train_size)
        test_index = np.arange(train_start + train_size, train_start + train_size + test_size)
        yield Split(train_index=train_index, test_index=test_index)
        train_start += advance
