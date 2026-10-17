"""Market-neutral spread evidence must find planted cross-sectional alpha and
reject beta, crashes and thin legs -- and never raise into the research run."""

from __future__ import annotations

import csv

import numpy as np
import pandas as pd
from test_alpha_vs_beta import alpha_universe, beta_universe, crash_universe

from breakwater.discovery import prepare_pooled
from breakwater.spread_research import (
    MIN_LEG_SYMBOLS,
    SPREAD_HEADERS,
    read_spreads,
    spread_stats,
    write_spreads,
)


def _by_id(rows):
    return {row.spread_id: row for row in rows}


def test_planted_alpha_qualifies_only_in_the_right_pairing():
    prepared = prepare_pooled(alpha_universe(n_symbols=12), ["sig"], cost_bps=9.0, horizon_bars=6)
    rows = _by_id(spread_stats(prepared, kind="PERP", feature_columns=["sig"], horizon_bars=6))
    good, bad = rows["sig:L2S0:h6"], rows["sig:L0S2:h6"]
    assert good.qualifies and good.fail_reasons == ""
    assert good.mean_ret_costadj > 0 and good.fold_pattern == "11111"
    assert good.n_nonoverlap * 6 <= good.n_bars + 6
    assert not bad.qualifies and "mean<=0" in bad.fail_reasons
    # Rows are sorted qualifying-first, then by non-overlap t.
    ordered = spread_stats(prepared, kind="PERP", feature_columns=["sig"], horizon_bars=6)
    assert ordered[0].spread_id == "sig:L2S0:h6"


def test_pure_beta_universe_does_not_qualify_and_pays_both_legs():
    prepared = prepare_pooled(beta_universe(n_symbols=12), ["sig"], cost_bps=9.0, horizon_bars=1)
    rows = spread_stats(prepared, kind="PERP", feature_columns=["sig"], horizon_bars=1)
    assert rows and not any(row.qualifies for row in rows)
    for row in rows:
        # Null spread at h1 should sit near minus one leg of costs (9 bps),
        # i.e. the 9 bps round trip paid on each half of the gross notional.
        assert -0.0020 < row.mean_ret_costadj < 0.0
        assert abs(row.market_corr) < 0.2


def test_crash_asymmetry_is_caught_by_the_neutrality_check():
    prepared = prepare_pooled(crash_universe(n_symbols=12), ["sig"], cost_bps=9.0, horizon_bars=6)
    rows = spread_stats(prepared, kind="PERP", feature_columns=["sig"], horizon_bars=6)
    assert rows and not any(row.qualifies for row in rows)
    # Stops truncate the long leg while the short leg runs: the spread can be
    # positive in a crash, but that is market exposure, not alpha.
    assert any("market_corr" in row.fail_reasons for row in rows)


def test_thin_legs_are_skipped_and_empty_inputs_are_safe():
    prepared = prepare_pooled(alpha_universe(n_symbols=4), ["sig"], cost_bps=9.0, horizon_bars=1)
    rows = spread_stats(prepared, kind="PERP", feature_columns=["sig"], horizon_bars=1)
    # 4 symbols split across 3 terciles can rarely put >=3 names on each leg.
    for row in rows:
        assert row.avg_n_long >= MIN_LEG_SYMBOLS and row.avg_n_short >= MIN_LEG_SYMBOLS
    assert spread_stats(pd.DataFrame(), kind="PERP", feature_columns=["sig"], horizon_bars=1) == []
    assert spread_stats(prepared.drop(columns=["fwd_trade_net_short"]), kind="PERP", feature_columns=["sig"], horizon_bars=1) == []
    assert spread_stats(prepared, kind="PERP", feature_columns=["missing"], horizon_bars=1) == []


def test_spread_is_half_long_plus_half_short_per_bar():
    rng = np.random.default_rng(3)
    starts = pd.date_range("2026-01-01", periods=40, freq="h", tz="UTC")
    parts = []
    for i in range(6):
        parts.append(pd.DataFrame({
            "start": starts,
            "symbol": f"S{i}",
            "state_f": 2 if i < 3 else 0,
            "fwd_trade_net_long": rng.normal(0.001, 0.0005, 40),
            "fwd_trade_net_short": rng.normal(0.0005, 0.0005, 40),
            "fwd_ret_raw": rng.normal(0, 0.001, 40),
        }))
    prepared = pd.concat(parts, ignore_index=True)
    row = _by_id(spread_stats(prepared, kind="PERP", feature_columns=["f"], horizon_bars=1))["f:L2S0:h1"]
    long_mean = prepared[prepared.state_f == 2].fwd_trade_net_long.mean()
    short_mean = prepared[prepared.state_f == 0].fwd_trade_net_short.mean()
    assert row.n_bars == 40
    assert abs(row.long_leg_mean - long_mean) < 1e-12
    assert abs(row.short_leg_mean - short_mean) < 1e-12
    assert abs(row.mean_ret_costadj - 0.5 * (long_mean + short_mean)) < 1e-12
    assert row.avg_n_long == 3.0 and row.avg_n_short == 3.0


def test_write_and_read_round_trip_with_header_only_when_empty(tmp_path):
    path = tmp_path / "research" / "spread_slices_h6_PERP.csv"
    write_spreads(path, [])
    with path.open(newline="") as handle:
        assert next(csv.reader(handle)) == SPREAD_HEADERS
    assert read_spreads(path) == []

    prepared = prepare_pooled(alpha_universe(n_symbols=12), ["sig"], cost_bps=9.0, horizon_bars=6)
    rows = spread_stats(prepared, kind="PERP", feature_columns=["sig"], horizon_bars=6)
    write_spreads(path, rows)
    loaded = read_spreads(path)
    assert [r["spread_id"] for r in loaded] == [r.spread_id for r in rows]
    assert loaded[0]["qualifies"] == "True"
    assert read_spreads(tmp_path / "missing.csv") == []
