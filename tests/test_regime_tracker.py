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


def test_gate_blocks_hostile_symbol_but_not_asset_on_macro_aggregate():
    # per-symbol hostile/unproven rule still blocks
    assert regime_gate("BUY", "bear", True, None) == (True, "regime_blocked")
    assert regime_gate("BUY", "bear", True, _shift(confirmed_bear=True)) == (True, "regime_blocked")
    assert regime_gate("SELL", "bull", True, _shift(confirmed_bull=True)) == (True, "regime_blocked")
    # the aggregate confirmed shift does NOT block an individual asset; the
    # per-symbol rule already handled the asset's own regime.
    assert regime_gate("BUY", "bear", False, _shift(confirmed_bear=True)) == (False, "")
    assert regime_gate("SELL", "bull", False, _shift(confirmed_bull=True)) == (False, "")
    assert regime_gate("BUY", "neutral", False, _shift(confirmed_bear=True)) == (False, "")


def test_per_asset_status_does_not_override_hostile_symbol_rule():
    """The per-asset verdict is about asset-level research; it never bypasses
    the per-symbol hostile/unproven rule. Green/untested assets still obey the
    symbol's own regime; a per-asset blocked asset is denied outright."""
    for status in ("green", "untested", ""):
        assert regime_gate("BUY", "bear", True, None, asset_status=status) == (True, "regime_blocked")
        assert regime_gate("SELL", "bull", True, None, asset_status=status) == (True, "regime_blocked")
    # a per-asset blocked asset is denied even if it bypassed the monitor
    assert regime_gate("BUY", "neutral", False, None, asset_status="blocked") == (True, "asset_not_green")
    assert regime_gate("SELL", "neutral", False, None, asset_status="blocked") == (True, "asset_not_green")
    # hostile/unproven=False and a non-blocking symbol regime is allowed even
    # when a confirmed macro shift exists: macro is portfolio context only.
    assert regime_gate(
        "BUY", "neutral", False, _shift(confirmed_bear=True), asset_status="untested"
    ) == (False, "")
    assert regime_gate(
        "BUY", "neutral", False, _shift(confirmed_bear=True), asset_status="green"
    ) == (False, "")


def test_defensive_exit_vs_r_gate():
    # Macro shift only closes a per-asset BLOCKED position; the R-gate still wins
    # for winners regardless of per-asset status.
    long_pos = {"side": "BUY", "asset_status": "blocked"}
    short_pos = {"side": "SELL", "asset_status": "blocked"}
    assert defensive_exit(long_pos, _shift(confirmed_bear=True), r_gate_on=False, asset_status="blocked") is True
    assert defensive_exit(short_pos, _shift(confirmed_bear=True), r_gate_on=False, asset_status="blocked") is False
    assert defensive_exit(short_pos, _shift(confirmed_bull=True), r_gate_on=False, asset_status="blocked") is True
    assert defensive_exit(long_pos, _shift(confirmed_bear=True), r_gate_on=True, asset_status="blocked") is False


def test_defensive_exit_only_closes_per_asset_blocked():
    """A confirmed global macro shift must NOT blanket-close individual assets.
    Only a per-asset blocked position is defensively exited; green and untested
    assets ride their own stop/horizon and the green-lane freeze."""
    shift = _shift(confirmed_bear=True)
    for status in ("green", "untested", "", "unknown"):
        assert defensive_exit({"side": "BUY", "asset_status": status}, shift, r_gate_on=False, asset_status=status) is False
    assert defensive_exit({"side": "BUY", "asset_status": "blocked"}, shift, r_gate_on=False, asset_status="blocked") is True
    # Legacy/unknown positions have no per-asset evidence, so they are not blanket-closed.
    assert defensive_exit({"side": "BUY"}, shift, r_gate_on=False) is False


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
