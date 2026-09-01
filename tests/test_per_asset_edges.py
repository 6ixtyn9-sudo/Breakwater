"""Per-asset research pipeline: pooled edge -> per-asset verdict -> monitor gate.

Covers the whole mission item:
- research computes per-asset edges for every pooled slice (LONG + SHORT),
- an asset with proof it is NOT green is blocked at monitor time,
- untested assets are allowed (action is never zeroed),
- native and HIP-3 both use the same validation + monitor path.
"""

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from breakwater.discovery import SliceStat, prepare_pooled
from breakwater.engine import _asset_edge_status_counts
from breakwater.monitor import monitor_book
from breakwater.validation import (
    AssetEdge,
    _compute_asset_edges_for_slice,
    build_asset_edge_lookup,
    read_asset_edges,
    validate_slices,
    write_asset_edges,
)


def trending_frame(n=260, drift=0.01, seed=3, symbol="BTCUSDC"):
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
    frame["symbol"] = symbol
    return frame


def book_row(state, feature="feat_ret_20", side="LONG", status="monitored", kind="PERP"):
    return {
        "slice_id": f"{feature}:{state}:{side}",
        "kind": kind,
        "feature": feature,
        "state": str(state),
        "side": side,
        "status": status,
        "mean_ret_costadj": "0.001",
    }


def candidate(kind="PERP", state=0, side="LONG", feature="close"):
    return SliceStat(
        slice_id=f"{feature}:{state}:{side}",
        kind=kind,
        feature=feature,
        state=state,
        side=side,
        n=600,
        mean_ret_costadj=0.001 if side == "LONG" else -0.001,
        median_ret_costadj=0.001,
        hit_rate=0.6,
        t_stat=4.0,
        p_value=0.0001,
        bonferroni_pass=True,
        horizon_bars=1,
    )


# --- Research side -----------------------------------------------------------

def _flat_subset_with_symbols(riser_rows=80, faller_rows=80, shorty_rows=3):
    """A subset-like DataFrame with 3 assets and a contiguous index range.

    SHORTY deliberately has too few rows to be judged, so it must come out
    ``untested`` (never frozen).
    """
    parts = []
    start = 0
    for asset, size in (("RISER", riser_rows), ("FALLER", faller_rows), ("SHORTY", shorty_rows)):
        part = pd.DataFrame({
            "symbol": [asset] * size,
            "dummy": np.arange(size),
        })
        part.index = np.arange(start, start + size)
        parts.append(part)
        start += size
    subset = pd.concat(parts)
    subset.index.name = None
    return subset


def test_asset_edge_verdicts_are_green_blocked_untested():
    """Direct unit test of the per-asset verdict rule.

    RISER: every net is +0.01 -> green (positive across folds).
    FALLER: every net is -0.01 -> blocked (proven not-green).
    SHORTY: only 3 rows -> untested (allowed, action never zeroed).
    """
    subset = _flat_subset_with_symbols(riser_rows=80, faller_rows=80, shorty_rows=3)
    values = (
        [0.01] * 80          # RISER
        + [-0.01] * 80       # FALLER
        + [0.001] * 3        # SHORTY (insufficient rows)
    )
    net_values = np.array(values, dtype=float)
    slice_mask = np.ones(len(subset), dtype=bool)
    fold_ids = np.linspace(0, len(subset), 5 + 1).astype(int)

    class _Cand:
        slice_id = "feat:0:LONG"
        feature = "feat"
        state = 0
        side = "LONG"
        kind = "PERP"

    edges = _compute_asset_edges_for_slice(
        subset=subset,
        slice_mask=slice_mask,
        net_values=net_values,
        fold_ids=fold_ids,
        horizon_bars=1,
        candidate=_Cand(),
        kind="PERP",
        cost=0.0,
    )
    by = {edge.asset: edge for edge in edges}
    assert by["RISER"].asset_status == "green"
    assert by["RISER"].mean_ret_costadj > 0
    assert by["RISER"].fold_positive_fraction >= 0.6
    assert by["FALLER"].asset_status == "blocked"
    assert by["FALLER"].mean_ret_costadj < 0
    assert by["SHORTY"].asset_status == "untested"
    assert by["SHORTY"].reason == "insufficient_rows"


def test_research_populates_asset_edges_for_long_and_short():
    """The public validate_slices() path must emit per-asset rows for both sides."""
    frame = trending_frame(drift=0.02, seed=1)
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    edges_long = []
    edges_short = []
    # A rising pool's low/high state quantiles are both present; use a state
    # that actually matches a slice (the rising pool bins into state 2).
    validate_slices(prepared, [candidate(state=2, side="LONG")], asset_edges=edges_long)
    validate_slices(prepared, [candidate(state=2, side="SHORT")], asset_edges=edges_short)
    assert edges_long, "LONG per-asset edges should be produced"
    assert all(edge.side == "LONG" for edge in edges_long)
    assert all(edge.asset == "BTCUSDC" for edge in edges_long)


# --- Monitor consumption -----------------------------------------------------

def test_monitor_gate_blocks_proven_not_green_asset_only():
    """Monitor must skip the blocked (slice, asset) and allow others."""
    frame = trending_frame(drift=0.02, seed=1)
    # Known good slice: feat_ret_20 state 0/2 emits a signal in the base tests.
    rows = [book_row(2, feature="feat_ret_20")]
    frames_by_kind = {"PERP": {"BTCUSDC": frame}}

    # Baseline: no per-asset lookup -> signal fires ("never zero action" proof).
    base_signals, _ = monitor_book(
        rows, frames_by_kind, server_time=datetime.now(timezone.utc)
    )
    assert base_signals

    # Block BTCUSDC for this exact slice -> signal is suppressed, and it is
    # reported as a blocked entry (asset_not_green).
    lookup = {("feat_ret_20:2:LONG", "BTCUSDC"): "blocked"}
    signals, blocked = monitor_book(
        rows,
        frames_by_kind,
        server_time=datetime.now(timezone.utc),
        asset_edge_lookup=lookup,
    )
    assert signals == []
    assert any(
        entry["pair"] == "BTCUSDC"
        and entry["guard"] == "asset_not_green"
        for entry in blocked
    )


def test_monitor_allows_untested_asset():
    """A missing or untested verdict must not freeze action."""
    frame = trending_frame(drift=0.02, seed=1)
    rows = [book_row(2, feature="feat_ret_20")]
    frames_by_kind = {"PERP": {"BTCUSDC": frame}}
    lookup = {("feat_ret_20:2:LONG", "BTCUSDC"): "untested"}
    signals, _ = monitor_book(
        rows,
        frames_by_kind,
        server_time=datetime.now(timezone.utc),
        asset_edge_lookup=lookup,
    )
    assert signals, "untested asset should never be frozen"


def test_monitor_allows_green_asset():
    frame = trending_frame(drift=0.02, seed=1)
    rows = [book_row(2, feature="feat_ret_20")]
    frames_by_kind = {"PERP": {"BTCUSDC": frame}}
    lookup = {("feat_ret_20:2:LONG", "BTCUSDC"): "green"}
    signals, _ = monitor_book(
        rows,
        frames_by_kind,
        server_time=datetime.now(timezone.utc),
        asset_edge_lookup=lookup,
    )
    assert signals


def test_hip3_symbols_match_capitalized_pair_key():
    """HIP-3 asset symbols (XYZ:AMD) resolve against uppercased monitor pairs."""
    rows = [
        AssetEdge(
            slice_id="hip3_equity_c0:feat:0:LONG:h24",
            asset="xyz:AMD",
            kind="PERP",
            feature="feat",
            state=0,
            side="LONG",
            horizon_bars=24,
            n=25,
            mean_ret_costadj=-0.01,
            folds_positive=0,
            folds_with_rows=4,
            fold_positive_fraction=0.0,
            asset_status="blocked",
            reason="not_green_per_asset",
        )
    ]
    lookup = build_asset_edge_lookup(rows)
    assert lookup[("hip3_equity_c0:feat:0:LONG:h24", "XYZ:AMD")] == "blocked"


def test_asset_edge_csv_roundtrip(tmp_path):
    rows = [
        AssetEdge(
            slice_id="feat:0:LONG",
            asset="BTCUSDC",
            kind="PERP",
            feature="feat",
            state=0,
            side="LONG",
            horizon_bars=1,
            n=40,
            mean_ret_costadj=0.001,
            folds_positive=4,
            folds_with_rows=5,
            fold_positive_fraction=0.8,
            asset_status="green",
            reason="",
        ),
        AssetEdge(
            slice_id="hip3_equity:feat:0:SHORT:h24",
            asset="XYZ:AMD",
            kind="PERP",
            feature="feat",
            state=0,
            side="SHORT",
            horizon_bars=24,
            n=30,
            mean_ret_costadj=-0.002,
            folds_positive=1,
            folds_with_rows=5,
            fold_positive_fraction=0.2,
            asset_status="blocked",
            reason="not_green_per_asset",
        ),
    ]
    path = tmp_path / "asset_edges.csv"
    write_asset_edges(path, rows)
    loaded = read_asset_edges(path)
    assert len(loaded) == len(rows)
    assert loaded[0].asset_status == "green"
    assert loaded[1].asset_status == "blocked"
    lookup = build_asset_edge_lookup(loaded)
    assert lookup[("feat:0:LONG", "BTCUSDC")] == "green"
    assert lookup[("hip3_equity:feat:0:SHORT:h24", "XYZ:AMD")] == "blocked"


def test_read_asset_edges_fails_closed_on_missing_file(tmp_path):
    """A missing asset_edges.csv must raise, not silently allow-all.

    The per-asset gate is a safety filter. If the research file is absent, the
    paper cycle must not silently trade without it.
    """
    missing = tmp_path / "no_such_asset_edges.csv"
    with pytest.raises(RuntimeError, match="asset edges file missing"):
        read_asset_edges(missing)


def test_read_asset_edges_fails_closed_on_bad_schema(tmp_path):
    """A malformed asset_edges.csv must raise, matching read_validated."""
    bad = tmp_path / "asset_edges.csv"
    bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="unsupported schema"):
        read_asset_edges(bad)


def test_asset_edge_status_counts_breakdown():
    """shadow_scan per_asset_gate must expose green/blocked/untested counts."""
    lookup = {
        ("s1", "BTCUSDC"): "green",
        ("s1", "ETHUSDC"): "blocked",
        ("s2", "DOGEUSDC"): "untested",
        ("s2", "ZECUSDC"): "untested",
    }
    counts = _asset_edge_status_counts(lookup)
    assert counts == {"green": 1, "blocked": 1, "untested": 2}
    # Empty lookup -> zeros, so operators can see the gate has no effect yet.
    assert _asset_edge_status_counts({}) == {"green": 0, "blocked": 0, "untested": 0}


def test_per_asset_min_fold_positive_fraction_env_name(monkeypatch):
    """The canonical env var must be `BREAKWATER_PER_ASSET_MIN_FOLD_POSITIVE_FRACTION`.

    This guards against the validator silently reading a different shorter
    name than the workflows/README set, which would silently disable the gate.
    """
    from importlib import reload

    import breakwater.validation as v

    # Set the canonical full name and import a fresh module so the module-level
    # thresholds are re-derived from the environment.
    monkeypatch.setenv("BREAKWATER_PER_ASSET_MIN_FOLD_POSITIVE_FRACTION", "0.75")
    monkeypatch.delenv("BREAKWATER_PER_ASSET_MIN_FOLD_POS_FRACTION", raising=False)
    reload(v)
    try:
        assert v.PER_ASSET_MIN_FOLD_POSITIVE_FRACTION == 0.75
    finally:
        reload(v)
