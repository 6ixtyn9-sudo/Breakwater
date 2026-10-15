"""Residualized discovery/validation must reject market beta and admit alpha.

Two synthetic universes:

* ``beta_universe``  -- every symbol shares one strong common uptrend plus
  noise; the feature carries no cross-sectional information.  Raw-return
  discovery flags LONG states as significant (that is beta).  Residualized
  discovery must not.

* ``alpha_universe`` -- same common uptrend, but symbols whose feature is in
  the top state outperform peers over the next bar, and bottom-state symbols
  underperform.  Residualized discovery must still find the LONG edge in the
  top state and, crucially, must let a SHORT candidate on the bottom state pass
  the direction gate even though the market is rising.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import breakwater.discovery as discovery
import breakwater.validation as validation
from breakwater.discovery import (
    SliceStat,
    attach_market_benchmark,
    discover_slices,
    prepare_pooled,
)
from breakwater.validation import validate_slices


def _frame(symbol: str, close: np.ndarray, signal: np.ndarray, rng) -> pd.DataFrame:
    n = len(close)
    return pd.DataFrame({
        "start": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "symbol": symbol,
        "open": close,
        "high": close * 1.004,
        "low": close * 0.996,
        "close": close,
        "volume": rng.uniform(10, 50, n),
        "sig": signal,
    })


def beta_universe(n_symbols=8, n=900, seed=7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    market = np.full(n, 0.0015) + rng.normal(0, 0.002, n)  # strong common drift
    parts = []
    for i in range(n_symbols):
        idio = rng.normal(0, 0.002, n)
        rets = market + idio
        close = 100.0 * np.cumprod(1.0 + rets)
        signal = rng.normal(0, 1, n)  # pure noise feature
        parts.append(_frame(f"B{i}", close, signal, rng))
    return pd.concat(parts, ignore_index=True)


def alpha_universe(n_symbols=8, n=900, seed=11, alpha=0.004) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    market = np.full(n, 0.0015) + rng.normal(0, 0.002, n)
    signals = rng.normal(0, 1, (n_symbols, n))
    # cross-sectional z-score of the signal at each bar
    z = (signals - signals.mean(axis=0)) / (signals.std(axis=0) + 1e-9)
    parts = []
    for i in range(n_symbols):
        idio = rng.normal(0, 0.002, n)
        rets = np.zeros(n)
        # signal at t predicts relative return over t -> t+1
        rets[1:] = market[1:] + idio[1:] + alpha * z[i, :-1]
        close = 100.0 * np.cumprod(1.0 + rets)
        parts.append(_frame(f"A{i}", close, signals[i], rng))
    return pd.concat(parts, ignore_index=True)


def _passes(slices, side):
    return [s for s in slices if s.bonferroni_pass and s.side == side]


def test_market_benchmark_is_leave_one_out_and_zero_without_peers():
    frame = beta_universe(n_symbols=3, n=300)
    prepared = prepare_pooled(frame, ["sig"], cost_bps=0.0, horizon_bars=1)
    assert {"fwd_ret_market", "fwd_ret_resid", "fwd_trade_net_long_resid", "fwd_trade_net_short_resid"} <= set(prepared.columns)
    one = prepared[prepared["start"] == prepared["start"].iloc[10]]
    raw = one["fwd_ret_raw"].to_numpy()
    for k in range(3):
        peers = np.delete(raw, k).mean()
        assert one["fwd_ret_market"].iloc[k] == pytest.approx(peers)
        assert one["fwd_ret_resid"].iloc[k] == pytest.approx(raw[k] - peers)
    # Residuals sum to ~0 across the cross-section only in the LOO-scaled sense;
    # what matters is the mean residual over the sample is ~0 under pure beta.
    assert abs(prepared["fwd_ret_resid"].mean()) < abs(prepared["fwd_ret_raw"].mean()) / 5

    single = prepare_pooled(frame[frame["symbol"] == "B0"], ["sig"], cost_bps=0.0, horizon_bars=1)
    assert (single["market_peers"] == 0).all()
    assert (single["fwd_ret_market"] == 0.0).all()
    np.testing.assert_allclose(
        single["fwd_trade_net_long_resid"].to_numpy(), single["fwd_trade_net_long"].to_numpy(), equal_nan=True
    )


def test_raw_scoring_flags_beta_but_residualized_does_not(monkeypatch):
    frame = beta_universe()

    monkeypatch.setattr(discovery, "RESIDUALIZE", False)
    raw_slices = discover_slices(frame, kind="SPOT", feature_columns=["sig"], cost_bps=0.0, horizon_bars=1)
    # Raw returns: the common drift makes LONG look significant in every state.
    assert len(_passes(raw_slices, "LONG")) >= 2
    assert not _passes(raw_slices, "SHORT")

    monkeypatch.setattr(discovery, "RESIDUALIZE", True)
    resid_slices = discover_slices(frame, kind="SPOT", feature_columns=["sig"], cost_bps=0.0, horizon_bars=1)
    assert all(s.residualized for s in resid_slices)
    assert not _passes(resid_slices, "LONG")
    assert not _passes(resid_slices, "SHORT")
    # Raw expectation is still reported (positive -- it is a bull market) but
    # alpha evidence is flat.
    longs = [s for s in resid_slices if s.side == "LONG"]
    assert all(s.mean_ret_costadj > 0 for s in longs)
    assert all(abs(s.alpha_t_stat) < 3.0 for s in longs)


def test_residualized_discovery_finds_relative_alpha():
    frame = alpha_universe()
    slices = discover_slices(frame, kind="SPOT", feature_columns=["sig"], cost_bps=0.0, horizon_bars=1)
    by_id = {s.slice_id: s for s in slices}
    top_long = by_id["sig:2:LONG"]
    bottom_long = by_id["sig:0:LONG"]
    bottom_short = by_id["sig:0:SHORT"]
    assert top_long.bonferroni_pass
    assert top_long.mean_resid_costadj > bottom_long.mean_resid_costadj
    # Bottom-state LONG underperforms the universe and must not pass.
    assert bottom_long.mean_resid_costadj < 0
    assert not bottom_long.bonferroni_pass
    # Bottom-state SHORT has real relative alpha; discovery now sees it.
    assert bottom_short.alpha_p_value < 0.01
    assert bottom_short.mean_resid_costadj > 0


def _cand(state, side, bonf=True):
    return SliceStat(
        slice_id=f"sig:{state}:{side}", kind="SPOT", feature="sig", state=state, side=side,
        n=300, mean_ret_costadj=0.001, median_ret_costadj=0.0, hit_rate=0.5,
        t_stat=4.0, p_value=1e-4, bonferroni_pass=bonf, horizon_bars=1,
    )


def test_validation_direction_gate_uses_alpha_not_beta(monkeypatch):
    monkeypatch.setattr(validation, "RESIDUAL_VALIDATION", True)
    frame = alpha_universe()
    prepared = prepare_pooled(frame, ["sig"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [_cand(0, "SHORT"), _cand(0, "LONG"), _cand(2, "LONG")])
    by_id = {r.slice_id: r for r in rows}
    # In a rising market the raw training mean favours LONG everywhere; the
    # residual gate must instead prefer SHORT on the underperforming state.
    assert by_id["sig:0:SHORT"].side_train == "SHORT"
    assert by_id["sig:0:SHORT"].direction_ok
    assert not by_id["sig:0:LONG"].direction_ok
    assert by_id["sig:2:LONG"].direction_ok
    assert by_id["sig:2:LONG"].residual_mode
    assert by_id["sig:2:LONG"].mean_resid_ret > 0
    # Regime-stratified columns are populated.
    v = by_id["sig:2:LONG"]
    assert v.regime_bull_n + v.regime_neutral_n + v.regime_bear_n > 0


def test_validation_beta_universe_long_fails_stability_gates(monkeypatch):
    monkeypatch.setattr(validation, "RESIDUAL_VALIDATION", True)
    frame = beta_universe()
    prepared = prepare_pooled(frame, ["sig"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [_cand(s, "LONG") for s in (0, 1, 2)])
    assert rows
    # Raw mean is positive (bull drift) but none of these should validate as an edge.
    assert all(r.mean_positive for r in rows)
    assert not any(r.validated for r in rows)


def test_validated_schema_roundtrip_with_alpha_fields(tmp_path):
    frame = alpha_universe(n_symbols=4, n=400)
    prepared = prepare_pooled(frame, ["sig"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [_cand(2, "LONG")])
    path = tmp_path / "validated.csv"
    validation.write_validated(path, rows)
    back = validation.read_validated(path)
    assert back[0].residual_mode == rows[0].residual_mode
    assert back[0].mean_resid_ret == pytest.approx(rows[0].mean_resid_ret)
    assert back[0].regime_gate_ok == rows[0].regime_gate_ok
    assert back[0].regime_bear_n == rows[0].regime_bear_n


def test_attach_market_benchmark_noop_without_required_columns():
    df = pd.DataFrame({"x": [1, 2]})
    assert attach_market_benchmark(df) is df
