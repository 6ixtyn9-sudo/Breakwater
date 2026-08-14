import numpy as np
import pandas as pd

from breakwater.discovery import (
    MIN_SLICE_ROWS,
    bin_states,
    discover_slices,
    prepare_pooled,
)
from breakwater.features import FEATURE_COLUMNS


def pooled_frame(n_symbols=3, n=140, seed=11):
    rng = np.random.default_rng(seed)
    parts = []
    for symbol_index in range(n_symbols):
        close = 50 + symbol_index * 10 + np.cumsum(rng.normal(0, 0.5, n))
        parts.append(pd.DataFrame({
            "start": pd.date_range("2026-07-01", periods=n, freq="h", tz="UTC"),
            "symbol": f"PAIR{symbol_index}",
            "open": close - 0.2,
            "high": close + 0.4,
            "low": close - 0.4,
            "close": close,
            "volume": rng.uniform(10, 50, n),
        }))
    return pd.concat(parts, ignore_index=True)


def test_bin_states_emits_three_states_after_warmup():
    frame = pooled_frame(n_symbols=1)
    binned = bin_states(frame, ["feat_ret_1"] if "feat_ret_1" in frame else ["close"])
    states = binned["state_close"].dropna()
    assert set(states.unique()).issubset({0, 1, 2})


def test_prepare_pooled_keeps_symbol_boundaries():
    frame = pooled_frame(n_symbols=2, n=300)
    prepared = prepare_pooled(frame, ["close"], cost_bps=20.0, horizon_bars=1)
    assert "fwd_ret" in prepared.columns
    assert prepared["symbol"].nunique() == 2


def test_discover_slices_on_empty_frame_returns_empty():
    assert discover_slices(
        pd.DataFrame(), kind="SPOT", feature_columns=FEATURE_COLUMNS, cost_bps=20.0
    ) == []


def test_discover_slices_assigns_bonferroni_flags():
    frame = pooled_frame(n_symbols=4, n=300, seed=3)
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    slices = discover_slices(
        prepared, kind="SPOT", feature_columns=["close"], cost_bps=0.0
    )
    assert slices
    for stat in slices:
        assert stat.n >= MIN_SLICE_ROWS
        assert stat.side in {"LONG", "SHORT"}
        assert isinstance(stat.bonferroni_pass, bool)
