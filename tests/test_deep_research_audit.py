from dataclasses import dataclass

import numpy as np
import pandas as pd

from breakwater.deep_research_audit import (
    _attach_plateaus,
    _block_bootstrap_p,
    _both_directions,
    _net_returns_from_prepared,
    _weights,
)
from breakwater.discovery import _trade_net_cols
from breakwater.validation import _compute_stop_aware_net_returns


def test_deep_audit_forces_both_directions():
    @dataclass(frozen=True)
    class Candidate:
        side: str
        feature: str = "feat"
        state: int = 1

    expanded = _both_directions([Candidate(side="LONG")])
    assert [candidate.side for candidate in expanded] == ["LONG", "SHORT"]


def test_deep_audit_does_not_evaluate_a_family_twice():
    # discovery._slice_stats emits LONG and SHORT rows itself; the audit must
    # not re-expand each of them (that doubled every artifact to 2026-11-09).
    @dataclass(frozen=True)
    class Candidate:
        side: str
        feature: str
        state: int

    expanded = _both_directions(
        [
            Candidate("LONG", "feat_a", 1),
            Candidate("SHORT", "feat_a", 1),
            Candidate("SHORT", "feat_a", 2),
            Candidate("LONG", "feat_b", 0),
        ]
    )
    keys = [(c.feature, c.state, c.side) for c in expanded]
    assert len(keys) == len(set(keys)) == 6
    assert sorted({k[:2] for k in keys}) == [("feat_a", 1), ("feat_a", 2), ("feat_b", 0)]


def test_fetch_group_attaches_positioning_for_native_coins(monkeypatch):
    from decimal import Decimal

    import breakwater.deep_research_audit as dra
    from breakwater.deep_research_audit import AuditGroup, _fetch_group
    from breakwater.models import Candle
    from breakwater.positioning_features import PositioningContext

    starts = pd.date_range("2026-01-01", periods=3200, freq="h", tz="UTC")
    close = np.linspace(100, 120, 3200)
    candles = [
        Candle(
            pair="BTCUSDC",
            period_seconds=3600,
            start=ts.to_pydatetime(),
            open=Decimal(str(c)),
            high=Decimal(str(c + 1)),
            low=Decimal(str(c - 1)),
            close=Decimal(str(c)),
            volume=Decimal("10"),
        )
        for ts, c in zip(starts, close)
    ]
    monkeypatch.setattr(dra, "fetch_perp_candles", lambda coin, interval="1h", count=5000: candles)

    funding = pd.DataFrame(
        {"coin": "BTC", "start": starts, "pos_funding": 0.0001, "pos_premium": 0.0002}
    )
    monkeypatch.setattr(
        "breakwater.positioning_features.funding_history_frame",
        lambda coin, *, start, end, session=None: funding,
    )
    ctx = PositioningContext(None, enabled=True, fetch_funding=True, lookback_hours=3200)
    group = AuditGroup("native", "native_crypto_c0", ("BTC",), 26.0)

    pooled, errors = _fetch_group(group, candle_count=3200, sleep_seconds=0, positioning=ctx)

    assert errors == {}
    assert ctx.attached == ["BTCUSDC"]
    assert pooled["pos_funding"].notna().all()
    assert pooled["feat_funding_rate"].notna().sum() > 0

    # HIP-3 groups are never attached (prefixed coins are not native perps).
    hip3 = AuditGroup("hip3", "xyz_equity_c0", ("xyz:SOXL",), 30.0)
    pooled_hip3, _ = _fetch_group(hip3, candle_count=3200, sleep_seconds=0, positioning=ctx)
    assert ctx.attached == ["BTCUSDC"]
    assert pooled_hip3["feat_funding_rate"].isna().all()


def test_frozen_recency_weights_halve_each_thousand_hours():
    ages = np.array([0, 999, 1000, 1999, 2000, 3000, 4000, 4999])
    assert list(_weights(ages)) == [1.0, 1.0, 0.5, 0.5, 0.25, 0.125, 0.0625, 0.0625]


def test_block_bootstrap_is_deterministic_and_respects_time_blocks():
    frame = pd.DataFrame(
        {
            "start": pd.date_range("2026-01-01", periods=480, freq="h", tz="UTC"),
            "net": [0.01] * 480,
            "weight": [1.0] * 480,
        }
    )
    first = _block_bootstrap_p(frame, seed_text="candidate", replicates=100)
    second = _block_bootstrap_p(frame, seed_text="candidate", replicates=100)
    assert first == second
    assert first < 0.05


def test_cached_horizon_returns_match_validation_math():
    parts = []
    for symbol, offset in (("BTC", 0.0), ("ETH", 10.0)):
        close = np.linspace(100 + offset, 130 + offset, 120)
        raw = pd.DataFrame(
            {
                "symbol": symbol,
                "start": pd.date_range("2026-01-01", periods=120, freq="h", tz="UTC"),
                "close": close,
                "high": close + 2,
                "low": close - 2,
            }
        )
        parts.append(
            _trade_net_cols(
                raw,
                horizon_bars=24,
                stop_atr_mult=2.0,
                cost=0.0026,
            )
        )
    prepared = pd.concat(parts, ignore_index=True)
    expected_long, expected_short = _compute_stop_aware_net_returns(
        prepared,
        horizon_bars=24,
        stop_atr_mult=3.1,
        cost=0.0026,
    )
    actual_long, actual_short = _net_returns_from_prepared(
        prepared,
        stop_atr_mult=3.1,
        cost=0.0026,
    )
    np.testing.assert_allclose(actual_long, expected_long, equal_nan=True)
    np.testing.assert_allclose(actual_short, expected_short, equal_nan=True)


def test_only_contiguous_three_horizon_plateaus_pass():
    rows = []
    for horizon in range(1, 8):
        rows.append(
            {
                "lane": "native",
                "group": "crypto",
                "feature": "feat",
                "state": 1,
                "side": "LONG",
                "horizon_bars": horizon,
                "preliminary_pass": horizon in {1, 2, 4, 5, 6, 7},
                "plateau_start": "",
                "plateau_end": "",
                "plateau_width": 0,
                "audit_pass": False,
            }
        )
    _attach_plateaus(rows)
    assert not rows[0]["audit_pass"]
    assert not rows[1]["audit_pass"]
    for index in (3, 4, 5, 6):
        assert rows[index]["audit_pass"]
        assert rows[index]["plateau_start"] == 4
        assert rows[index]["plateau_end"] == 7
        assert rows[index]["plateau_width"] == 4
