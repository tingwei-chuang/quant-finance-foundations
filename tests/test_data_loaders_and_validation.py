"""Tests for data loading and validation (P1-1, P0-5, P0-8 regressions)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quant_math_roadmap.data.loaders import (
    _repo_root,
    load_prices_csv,
    load_sample_prices,
    sample_data_dir,
)
from quant_math_roadmap.data.synthetic import SyntheticConfig
from quant_math_roadmap.data.validation import (
    ValidationReport,
    validate_price_frame,
)


def _good_frame() -> pd.DataFrame:
    idx = pd.bdate_range("2021-01-01", periods=10)
    return pd.DataFrame({"A": np.linspace(100, 110, 10)}, index=idx)


# ---------- validation ----------
def test_clean_frame_passes() -> None:
    assert validate_price_frame(_good_frame()).ok


def test_rejects_non_datetime_index() -> None:
    df = pd.DataFrame({"A": [1.0, 2.0, 3.0]})
    report = validate_price_frame(df)
    assert not report.ok
    assert any("DatetimeIndex" in p for p in report.problems)


def test_rejects_empty_frame() -> None:
    df = pd.DataFrame({"A": []}, index=pd.DatetimeIndex([], name="date"))
    report = validate_price_frame(df)
    assert not report.ok
    assert any("empty" in p for p in report.problems)


def test_rejects_duplicate_timestamps() -> None:
    idx = pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-02"])
    df = pd.DataFrame({"A": [100.0, 101.0, 102.0]}, index=idx)
    report = validate_price_frame(df)
    assert any("duplicates" in p for p in report.problems)


def test_rejects_non_monotonic_index() -> None:
    idx = pd.to_datetime(["2021-01-03", "2021-01-01", "2021-01-02"])
    df = pd.DataFrame({"A": [100.0, 101.0, 102.0]}, index=idx)
    report = validate_price_frame(df)
    assert any("monotonic" in p for p in report.problems)


def test_rejects_missing_values() -> None:
    df = _good_frame()
    df.iloc[2, 0] = np.nan
    report = validate_price_frame(df)
    assert any("missing" in p for p in report.problems)


def test_rejects_non_positive_prices() -> None:
    df = _good_frame()
    df.iloc[1, 0] = -5.0
    report = validate_price_frame(df)
    assert any("non-positive" in p for p in report.problems)


def test_rejects_inf_prices_regression_for_p0_5() -> None:
    # Regression for P0-5: inf used to pass validation silently.
    df = _good_frame()
    df.iloc[3, 0] = np.inf
    report = validate_price_frame(df)
    assert not report.ok
    assert any("non-finite" in p for p in report.problems)


def test_require_business_days_flag() -> None:
    df = _good_frame()
    # Drop an interior business day -> the gap-free check should fail.
    df_with_gap = df.drop(df.index[3])
    report = validate_price_frame(df_with_gap, require_business_days=True)
    assert any("business-day" in p for p in report.problems)
    # Without the flag the frame should pass (only the gap is "wrong").
    assert validate_price_frame(df_with_gap).ok


def test_raise_if_failed_raises() -> None:
    report = ValidationReport()
    report.add("something is wrong")
    with pytest.raises(ValueError, match="failed validation"):
        report.raise_if_failed()


def test_raise_if_failed_is_silent_when_ok() -> None:
    ValidationReport().raise_if_failed()  # must not raise


# ---------- loaders ----------
def test_load_prices_csv_round_trip(tmp_path: Path) -> None:
    df = _good_frame()
    csv = tmp_path / "prices.csv"
    df.to_csv(csv)
    loaded = load_prices_csv(csv)
    # Index ``freq`` does not survive a CSV round-trip; everything else must.
    pd.testing.assert_frame_equal(loaded, df, check_names=False, check_freq=False)


def test_load_prices_csv_validates_by_default(tmp_path: Path) -> None:
    df = _good_frame()
    df.iloc[0, 0] = -1.0
    csv = tmp_path / "bad.csv"
    df.to_csv(csv)
    with pytest.raises(ValueError, match="non-positive"):
        load_prices_csv(csv)
    # validate=False should skip the check.
    load_prices_csv(csv, validate=False)


def test_load_sample_prices_works_from_source_checkout() -> None:
    df = load_sample_prices()
    assert df.shape[0] > 0
    assert df.shape[1] >= 1
    # Sample is built with a fixed seed; columns are deterministic.
    assert set(df.columns) == {
        "EQUITY_A",
        "EQUITY_B",
        "EQUITY_C",
        "DEFENSIVE_D",
        "CYCLICAL_E",
    }


def test_load_sample_prices_missing_file_message(tmp_path: Path, monkeypatch) -> None:
    # Force sample_data_dir to point at an empty directory.
    monkeypatch.setattr("quant_math_roadmap.data.loaders.sample_data_dir", lambda: tmp_path)
    with pytest.raises(FileNotFoundError, match="generate_synthetic_dataset"):
        load_sample_prices()


def test_loaders_handle_non_source_install_regression_for_p0_8(monkeypatch) -> None:
    # Regression for P0-8: when the package is not installed from a source
    # checkout, sample_data_dir() returns None and load_sample_prices() gives
    # a clear error instead of pointing at a nonsensical site-packages path.
    monkeypatch.setattr("quant_math_roadmap.data.loaders._repo_root", lambda: None)
    assert sample_data_dir() is None
    with pytest.raises(FileNotFoundError, match="source checkout"):
        load_sample_prices()


def test_repo_root_resolves_in_editable_install() -> None:
    root = _repo_root()
    # In CI / dev we run from a source checkout, so root must exist and have
    # the expected layout.
    assert root is not None
    assert (root / "src" / "quant_math_roadmap").is_dir()


# ---------- SyntheticConfig validation (regression for the late asset_names check) ----------
def test_synthetic_config_rejects_mismatched_asset_names() -> None:
    with pytest.raises(ValueError, match="asset_names"):
        SyntheticConfig(n_assets=3, asset_names=["A", "B"])


def test_synthetic_config_accepts_matching_asset_names() -> None:
    cfg = SyntheticConfig(n_assets=2, asset_names=["X", "Y"])
    assert cfg.asset_names == ["X", "Y"]
