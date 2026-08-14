import numpy as np
import pandas as pd

from breakwater.features import (
    FEATURE_COLUMNS,
    compute_price_features,
    forward_returns,
)


def frame(n=120, seed=7):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 0.5, n))
    return pd.DataFrame({
        "start": pd.date_range("2026-07-01", periods=n, freq="h", tz="UTC"),
        "open": close - 0.2,
        "high": close + 0.4,
        "low": close - 0.4,
        "close": close,
        "volume": rng.uniform(10, 50, n),
    })


def test_all_feature_columns_are_computed():
    featured = compute_price_features(frame())
    for column in FEATURE_COLUMNS:
        assert column in featured.columns
    tail = featured.tail(30)
    assert np.isfinite(tail[FEATURE_COLUMNS].to_numpy()).all()


def test_forward_returns_shift_by_horizon():
    featured = frame(40)
    fwd = forward_returns(featured, horizon=3)
    assert len(fwd) == len(featured)
    assert np.isnan(fwd.iloc[-3:]).all()
    assert fwd.iloc[0] == pytest_approx(featured["close"].iloc[3] / featured["close"].iloc[0] - 1)


def pytest_approx(value):
    import pytest

    return pytest.approx(value, rel=1e-9)
