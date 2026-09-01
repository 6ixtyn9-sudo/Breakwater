"""Tests for the intraday regime-shift tracker."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from breakwater.regime_tracker import (
    RegimeShift,
    defensive_exit,
    regime_gate,
    update_regime_state,
)


def _frame(price: float, n: int = 260) -> pd.DataFrame:
    idx = pd.date_range("2026-01-01", periods=n, freq="1h", tz="UTC")
    # A monotonically falling series reads as bear: SMA(50) < SMA(200) and
    # last close < SMA(50). A flat series reads as neutral, which masks the
    # bear flip we are testing below.
    positions = pd.Series(range(n), index=idx, dtype="float64")
    close = price * (1.0 - (positions / max(1, n - 1)) * 0.5)
    return pd.DataFrame({"open": close, "high": close, "low": close, "close": close,
                         "volume": pd.Series(1.0, index=idx), "start": idx})


def _snapshot(frames_by_kind, label: str):
    # Minimal snapshot object (dict) shaped as compute_regime_snapshot emits.
    from breakwater.regime_tracker import compute_regime_snapshot

    return compute_regime_snapshot(frames_by_kind)


def _shift(confirmed_bear=False, confirmed_bull=False):
    return RegimeShift(
        label="bear" if confirmed_bear else "neutral",
        bear_breadth=0.6 if confirmed_bear else 0.2,
        bull_breadth=0.1,
        neutral_breadth=0.3,
        confirmed_bear=confirmed_bear,
        confirmed_bull=confirmed_bull,
        flip=confirmed_bear or confirmed_bull,
        flipped_from="bull" if confirmed_bear else "neutral",
        consecutive_bear=2 if confirmed_bear else 0,
        consecutive_bull=0,
        as_of="2026-08-30T12:00:00Z",
    )


def test_gate_blocks_long_only_when_confirmed_bear():
    # existing per-symbol bear rule (hostile_unproven=True) still blocks
    assert regime_gate("BUY", "bear", True, None) == (True, "regime_blocked")
    # hostile_unproven=False would previously be allowed in bear; confirmed shift now blocks it
    assert regime_gate("BUY", "bear", False, _shift(confirmed_bear=True))[0] is True
    shipped = regime_gate("BUY", "bear", False, _shift(confirmed_bear=True))
    assert shipped[1] == "regime_shift_blocked"
    # no confirmed shift, hostile_unproven=False => allowed
    assert regime_gate("BUY", "bear", False, _shift(confirmed_bear=False)) == (False, "")
    # short in a confirmed bull is blocked
    assert regime_gate("SELL", "bull", False, _shift(confirmed_bull=True))[0] is True


def test_defensive_exit_vs_r_gate():
    long_pos = {"side": "BUY"}
    short_pos = {"side": "SELL"}
    assert defensive_exit(long_pos, _shift(confirmed_bear=True), r_gate_on=False) is True
    assert defensive_exit(short_pos, _shift(confirmed_bear=True), r_gate_on=False) is False
    # winner that banked R is not force-closed
    assert defensive_exit(long_pos, _shift(confirmed_bear=True), r_gate_on=True) is False


def test_update_regime_state_confirms_after_two_cycles(tmp_path):
    path = tmp_path / "regime_state.json"
    now = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
    frames = {"PERP": {"BTCUSDC": _frame(80.0)}}
    # first cycle: bear but not yet confirmed
    state1 = update_regime_state(path, _snapshot(frames, "bear"), now=now)
    assert state1.confirmed_bear is False
    # second cycle: confirm
    now2 = datetime(2026, 8, 30, 12, 1, tzinfo=timezone.utc)
    state2 = update_regime_state(path, _snapshot(frames, "bear"), now=now2)
    assert state2.confirmed_bear is True
    assert state2.flip is True
    payload = json.loads(path.read_text())
    assert payload["schema"] == "breakwater.regime_shift.v1"
