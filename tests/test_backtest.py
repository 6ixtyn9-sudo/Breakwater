"""The backtest harness must be right on data whose answer we know before
any verdict from it is believed."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from breakwater import backtest


def _daily(prices: list[float], *, start=datetime(2024, 1, 1, tzinfo=timezone.utc), spread=0.01) -> pd.DataFrame:
    rows = []
    for i, p in enumerate(prices):
        rows.append({
            "time": start + timedelta(days=i),
            "open": p, "high": p * (1 + spread), "low": p * (1 - spread), "close": p, "volume": 1.0,
        })
    return pd.DataFrame(rows)


def test_trend_trail_rides_a_clean_uptrend_and_pays_costs_on_noise():
    up = _daily([100 * (1.01 ** i) for i in range(400)])
    trades = backtest.simulate_trend_trail(up, coin="UP", sma_n=50, atr_k=3.0)
    assert trades, "a 400-day uptrend must produce at least one long"
    assert all(t.side == "LONG" for t in trades)
    assert sum(t.ret for t in trades) > 0.5

    rng = np.random.default_rng(7)
    flat = _daily(list(100 + rng.normal(0, 0.5, 400).cumsum() * 0.01 + 100))
    trades = backtest.simulate_trend_trail(flat, coin="FLAT", sma_n=50, atr_k=3.0)
    # noise with no drift: every trade pays 2 x fee + slip; the sum is not positive
    assert sum(t.ret for t in trades) <= 0.0


def test_trend_trail_stop_fill_takes_slip_bounded_by_the_low():
    prices = [100 * (1.01 ** i) for i in range(120)] + [100 * (1.01 ** 119) * 0.7]  # crash day
    frame = _daily(prices)
    trades = backtest.simulate_trend_trail(frame, coin="X", sma_n=50, atr_k=2.0)
    stop_trades = [t for t in trades if t.reason == "trail"]
    assert stop_trades
    last = stop_trades[-1]
    crash = frame.iloc[-1]
    # the 30% crash gaps through the trailed stop: fill = stop less 15 bps,
    # never better than that, never worse than the bar low, below the prior close
    assert crash["low"] <= last.exit < frame.iloc[-2]["close"]
    assert last.exit_time == crash["time"]


def test_funding_carry_collects_positive_funding_for_shorts():
    daily = _daily([100.0] * 60)  # flat price: directional == funding - fees
    days = pd.date_range(daily["time"].min(), periods=60, freq="D", tz="UTC")
    funding = pd.DataFrame({"time": days, "funding_day": [0.001] * 60})  # 0.1%/day = 36.5% annualised
    episodes = backtest.simulate_funding_carry(daily, funding, coin="F", threshold_annual=0.20)
    assert len(episodes) == 1 and episodes[0].days == 59  # still open at the end, marked at the last close
    # make the funding lapse so the episode closes on its own
    funding.loc[funding.index >= 40, "funding_day"] = 0.0
    episodes = backtest.simulate_funding_carry(daily, funding, coin="F", threshold_annual=0.20)
    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.side == "SHORT"
    assert math.isclose(ep.price, 0.0, abs_tol=1e-12)
    assert ep.funding > 0.03  # ~39 days x 0.1%
    assert math.isclose(ep.hedged, ep.funding - 4 * backtest.FEE_BPS / 1e4)
    assert math.isclose(ep.directional, ep.funding - 2 * backtest.FEE_BPS / 1e4)


def test_verdict_reads_the_median_variant_not_the_best():
    rows = []
    for variant, net in ((1, -0.10), (2, -0.02), (3, 0.50)):
        for coin in ("A", "B"):
            for year in (2024, 2025):
                rows.append({"v": variant, "coin": coin, "year": year, "holdout": year == 2025, "net": net})
    table = pd.DataFrame(rows)
    verdict = backtest._verdict(table, key_cols=["v"])
    assert verdict["verdict"] == "FAIL"
    assert verdict["median_variant"]["variant"] == (2,)
    assert verdict["best_variant"]["variant"] == (3,)


def test_load_daily_splices_binance_before_hyperliquid(tmp_path):
    out = backtest.data_dir(tmp_path)
    bn = _daily([1.0] * 10, start=datetime(2023, 1, 1, tzinfo=timezone.utc))
    hl = _daily([2.0] * 5, start=datetime(2023, 1, 8, tzinfo=timezone.utc))
    bn.to_csv(out / "binance_BTCUSDT_1d.csv", index=False)
    hl.to_csv(out / "hl_BTC_1d.csv", index=False)
    frame = backtest.load_daily(tmp_path, "BTC")
    assert len(frame) == 7 + 5
    assert frame["time"].is_monotonic_increasing
    assert (frame.loc[frame["source"] == "hyperliquid", "close"] == 2.0).all()
