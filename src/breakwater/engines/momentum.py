"""Momentum/Trend Following Engine.

Reacts to established trends rather than predicting. If an asset has been
trending for N bars, enters in that direction.

Signals:
  - SMA crossover (50/200 golden/death cross)
  - N-bar breakout (price breaks above/below recent high/low)
  - ADX trend strength filter (only enter when trend is strong)

Works in trending markets. Use regime detector to disable in ranging markets.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MomentumSignal:
    pair: str
    side: str  # "BUY" or "SELL"
    entry_price: float
    stop_price: float
    atr: float
    edge: float  # expected edge per bar (bps)
    confidence: float  # 0-1
    horizon_bars: int
    signal_type: str  # "sma_cross", "breakout", "adx_trend"
    regime_fit: float  # 0-1


def _adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average Directional Index — measures trend strength."""
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.rolling(period).mean()
    return adx


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range."""
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()


def scan_momentum(
    frames: dict[str, pd.DataFrame],
    *,
    sma_fast: int = 50,
    sma_slow: int = 200,
    breakout_lookback: int = 20,
    adx_threshold: float = 25.0,
    adx_period: int = 14,
    min_confidence: float = 0.3,
) -> list[MomentumSignal]:
    """Scan all pairs for momentum/trend signals.

    Args:
        frames: dict of symbol -> DataFrame with columns [open, high, low, close, volume].
        sma_fast: fast SMA period for crossover.
        sma_slow: slow SMA period for crossover.
        breakout_lookback: bars to look back for breakout.
        adx_threshold: minimum ADX to confirm a trend.
        adx_period: ADX calculation period.
        min_confidence: minimum confidence to emit a signal.

    Returns:
        List of MomentumSignal, sorted by confidence descending.
    """
    signals: list[MomentumSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < sma_slow + adx_period:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        # SMA crossover
        sma_f = close.rolling(sma_fast).mean()
        sma_s = close.rolling(sma_slow).mean()
        atr = _atr(high, low, close)
        adx = _adx(high, low, close, adx_period)

        cur_close = close.iloc[-1]
        cur_atr = atr.iloc[-1]
        cur_adx = adx.iloc[-1]
        cur_sma_f = sma_f.iloc[-1]
        cur_sma_s = sma_s.iloc[-1]
        prev_sma_f = sma_f.iloc[-2]
        prev_sma_s = sma_s.iloc[-2]

        if np.isnan(cur_atr) or cur_atr <= 0 or np.isnan(cur_adx):
            continue

        # --- SMA crossover signal ---
        # Golden cross: fast crosses above slow
        if prev_sma_f <= prev_sma_s and cur_sma_f > cur_sma_s:
            trend_strength = min(1.0, cur_adx / 50.0)
            confidence = 0.4 + 0.3 * trend_strength
            # Higher confidence if price is above both SMAs
            if cur_close > cur_sma_f:
                confidence += 0.1
            stop = cur_close - 2.0 * cur_atr
            edge_bps = max(1.0, (cur_close - cur_sma_s) / cur_close * 10000 * 0.1)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol,
                    side="BUY",
                    entry_price=cur_close,
                    stop_price=stop,
                    atr=cur_atr,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=20,
                    signal_type="sma_cross",
                    regime_fit=1.0 if cur_adx > adx_threshold else 0.5,
                ))

        # Death cross: fast crosses below slow
        elif prev_sma_f >= prev_sma_s and cur_sma_f < cur_sma_s:
            trend_strength = min(1.0, cur_adx / 50.0)
            confidence = 0.4 + 0.3 * trend_strength
            if cur_close < cur_sma_f:
                confidence += 0.1
            stop = cur_close + 2.0 * cur_atr
            edge_bps = max(1.0, (cur_sma_s - cur_close) / cur_close * 10000 * 0.1)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol,
                    side="SELL",
                    entry_price=cur_close,
                    stop_price=stop,
                    atr=cur_atr,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=20,
                    signal_type="sma_cross",
                    regime_fit=1.0 if cur_adx > adx_threshold else 0.5,
                ))

        # --- Breakout signal ---
        recent_high = high.iloc[-breakout_lookback:].max()
        recent_low = low.iloc[-breakout_lookback:].min()

        # Bullish breakout: close above recent high with trend confirmation
        if cur_close > recent_high and cur_adx > adx_threshold:
            breakout_pct = (cur_close - recent_high) / recent_high
            confidence = 0.5 + min(0.3, breakout_pct * 100)
            # Extra confidence if fast SMA > slow SMA (trend aligned)
            if cur_sma_f > cur_sma_s:
                confidence += 0.1
            stop = cur_close - 2.0 * cur_atr
            edge_bps = max(1.0, breakout_pct * 10000 * 0.2)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol,
                    side="BUY",
                    entry_price=cur_close,
                    stop_price=stop,
                    atr=cur_atr,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=10,
                    signal_type="breakout",
                    regime_fit=1.0,
                ))

        # Bearish breakout: close below recent low with trend confirmation
        elif cur_close < recent_low and cur_adx > adx_threshold:
            breakout_pct = (recent_low - cur_close) / recent_low
            confidence = 0.5 + min(0.3, breakout_pct * 100)
            if cur_sma_f < cur_sma_s:
                confidence += 0.1
            stop = cur_close + 2.0 * cur_atr
            edge_bps = max(1.0, breakout_pct * 10000 * 0.2)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol,
                    side="SELL",
                    entry_price=cur_close,
                    stop_price=stop,
                    atr=cur_atr,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=10,
                    signal_type="breakout",
                    regime_fit=1.0,
                ))

    return sorted(signals, key=lambda s: -s.confidence)
