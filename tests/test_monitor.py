from datetime import datetime, timezone

import numpy as np
import pandas as pd

from breakwater.monitor import monitor_book


def trending_frame(n=260, drift=0.01, seed=3):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(np.full(n, drift)) + rng.normal(0, 0.05, n)
    frame = pd.DataFrame({
        "start": pd.date_range("2026-07-01", periods=n, freq="h", tz="UTC"),
        "open": close - 0.2,
        "high": close + 0.4,
        "low": close - 0.4,
        "close": close,
        "volume": rng.uniform(10, 50, n),
    })
    frame["symbol"] = "BTCUSDC"
    return frame


def book_row(state, feature="feat_ret_1", side="LONG", status="monitored"):
    return {
        "slice_id": f"{feature}:{state}:{side}",
        "kind": "PERP",
        "feature": feature,
        "state": str(state),
        "side": side,
        "status": status,
        "mean_ret_costadj": "0.001",
    }


def test_monitor_emits_signal_when_latest_state_matches():
    frame = trending_frame(drift=0.02, seed=1)
    rows = [
        book_row(2, feature="feat_ret_20"),
        book_row(0, feature="feat_ret_20"),
    ]
    signals = monitor_book(rows, {"BTCUSDC": frame}, server_time=datetime.now(timezone.utc))
    assert signals
    assert all(signal.pair == "BTCUSDC" for signal in signals)
    assert all(signal.side.value in {"BUY", "SELL"} for signal in signals)


def test_monitor_skips_non_monitored_rows():
    frame = trending_frame()
    rows = [book_row(2, feature="feat_ret_20", status="cooldown")]
    signals = monitor_book(rows, {"BTCUSDC": frame}, server_time=datetime.now(timezone.utc))
    assert signals == []


def test_monitor_needs_enough_history():
    frame = trending_frame(n=20)
    rows = [book_row(2, feature="feat_ret_20")]
    signals = monitor_book(rows, {"BTCUSDC": frame}, server_time=datetime.now(timezone.utc))
    assert signals == []
