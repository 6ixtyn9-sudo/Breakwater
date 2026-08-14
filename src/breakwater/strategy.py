"""VALR-native lower-frequency trend and volatility expansion detector."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from decimal import Decimal

import numpy as np
import pandas as pd

from breakwater.decimal_utils import D
from breakwater.market import completed_candles
from breakwater.models import Candle, PairType, Side, Signal


def _frame(candles: list[Candle]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "start": candle.start,
            "open": float(candle.open),
            "high": float(candle.high),
            "low": float(candle.low),
            "close": float(candle.close),
            "volume": float(candle.volume),
        }
        for candle in candles
    ]).sort_values("start").reset_index(drop=True)


def detect_big_wave(
    candles: list[Candle],
    *,
    pair: str,
    pair_type: PairType,
    server_time: datetime,
    allowed_side: Side | None = None,
    source_candidate_id: str | None = None,
) -> Signal | None:
    """Detect a confirmed one-hour trend breakout on completed VALR candles."""
    complete = completed_candles(candles, server_time)
    if len(complete) < 80:
        return None
    df = _frame(complete)
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    df["ema20"] = close.ewm(span=20, adjust=False).mean()
    df["ema50"] = close.ewm(span=50, adjust=False).mean()
    prev_close = close.shift(1)
    true_range = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    df["atr14"] = true_range.rolling(14).mean()
    df["prior_high20"] = high.shift(1).rolling(20).max()
    df["prior_low20"] = low.shift(1).rolling(20).min()
    df["volume_median20"] = volume.shift(1).rolling(20).median()
    df["return20"] = close.pct_change(20)

    row = df.iloc[-1]
    required = [
        row["ema20"], row["ema50"], row["atr14"], row["prior_high20"],
        row["prior_low20"], row["volume_median20"], row["return20"],
    ]
    if any(pd.isna(value) or not np.isfinite(float(value)) for value in required):
        return None
    atr = D(row["atr14"], field="atr")
    entry = D(row["close"], field="close")
    if atr <= 0 or entry <= 0:
        return None

    volume_confirmed = row["volume"] >= max(row["volume_median20"], 0)
    long_setup = (
        row["close"] > row["prior_high20"]
        and row["ema20"] > row["ema50"]
        and row["return20"] > 0
        and volume_confirmed
    )
    short_setup = (
        row["close"] < row["prior_low20"]
        and row["ema20"] < row["ema50"]
        and row["return20"] < 0
        and volume_confirmed
    )
    if allowed_side is Side.BUY:
        short_setup = False
    elif allowed_side is Side.SELL:
        long_setup = False
    if pair_type is PairType.SPOT:
        short_setup = False
    if long_setup == short_setup:
        return None

    side = Side.BUY if long_setup else Side.SELL
    stop = entry - Decimal(2) * atr if side is Side.BUY else entry + Decimal(2) * atr
    if stop <= 0:
        return None
    trend_strength = abs(D(row["ema20"] - row["ema50"])) / atr
    breakout_distance = (
        abs(entry - D(row["prior_high20"])) if side is Side.BUY
        else abs(entry - D(row["prior_low20"]))
    )
    score = min(Decimal("10"), trend_strength + breakout_distance / atr)
    candle = complete[-1]
    digest = hashlib.sha256(
        f"{pair}|{side}|{candle.start.isoformat()}".encode()
    ).hexdigest()[:16]
    return Signal(
        signal_id=digest,
        pair=pair.upper(),
        pair_type=pair_type,
        side=side,
        observed_at=server_time.astimezone(timezone.utc),
        candle_start=candle.start,
        entry_price=entry,
        stop_price=stop,
        atr=atr,
        score=score,
        source_candidate_id=source_candidate_id,
    )
