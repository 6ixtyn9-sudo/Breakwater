"""Momentum/Trend Following Engine.

Reacts to established trends rather than predicting. If an asset has been
trending for N bars, enters in that direction.

Signals:
  - SMA crossover (50/200 golden/death cross)
  - N-bar breakout (price breaks above/below recent high/low)
  - Trend alignment (price on correct side of SMA, ADX confirms direction)
"""
from __future__ import annotations

from dataclasses import dataclass

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
    signal_type: str  # "sma_cross", "breakout", "trend_align"
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
    sma_fast: int = 20,
    sma_slow: int = 50,
    breakout_lookback: int = 20,
    adx_threshold: float = 18.0,
    adx_period: int = 14,
    min_confidence: float = 0.2,
) -> list[MomentumSignal]:
    """Scan all pairs for momentum/trend signals.

    Lowered thresholds for real market conditions:
    - SMA: 20/50 (faster crossovers, more signals)
    - ADX: 18 (crypto trends show earlier at lower ADX)
    - Added trend_align signal (price on correct side of SMA + ADX confirmation)
    """
    signals: list[MomentumSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < sma_slow + adx_period:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

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
        # ATR floor: prevent tiny ATR from causing max leverage in low-vol periods
        cur_atr = max(cur_atr, cur_close * 0.005)

        # --- SMA crossover signal ---
        if prev_sma_f <= prev_sma_s and cur_sma_f > cur_sma_s:
            trend_strength = min(1.0, cur_adx / 40.0)
            confidence = 0.35 + 0.3 * trend_strength
            if cur_close > cur_sma_f:
                confidence += 0.1
            stop = cur_close - 1.5 * cur_atr
            edge_bps = max(1.0, (cur_close - cur_sma_s) / cur_close * 10000 * 0.1)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="sma_cross",
                    regime_fit=1.0 if cur_adx > adx_threshold else 0.5,
                ))

        elif prev_sma_f >= prev_sma_s and cur_sma_f < cur_sma_s:
            trend_strength = min(1.0, cur_adx / 40.0)
            confidence = 0.35 + 0.3 * trend_strength
            if cur_close < cur_sma_f:
                confidence += 0.1
            stop = cur_close + 1.5 * cur_atr
            edge_bps = max(1.0, (cur_sma_s - cur_close) / cur_close * 10000 * 0.1)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol, side="SELL", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="sma_cross",
                    regime_fit=1.0 if cur_adx > adx_threshold else 0.5,
                ))

        # --- Breakout signal ---
        recent_high = high.iloc[-breakout_lookback-1:-1].max()
        recent_low = low.iloc[-breakout_lookback-1:-1].min()

        if cur_close >= recent_high and cur_adx > adx_threshold:
            breakout_pct = (cur_close - recent_high) / recent_high
            confidence = 0.35 + min(0.3, breakout_pct * 50)
            if cur_sma_f > cur_sma_s:
                confidence += 0.1
            stop = cur_close - 1.5 * cur_atr
            edge_bps = max(1.0, breakout_pct * 10000 * 0.2)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=10,
                    signal_type="breakout", regime_fit=1.0,
                ))

        elif cur_close <= recent_low and cur_adx > adx_threshold:
            breakout_pct = (recent_low - cur_close) / recent_low
            confidence = 0.35 + min(0.3, breakout_pct * 50)
            if cur_sma_f < cur_sma_s:
                confidence += 0.1
            stop = cur_close + 1.5 * cur_atr
            edge_bps = max(1.0, breakout_pct * 10000 * 0.2)
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol, side="SELL", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=10,
                    signal_type="breakout", regime_fit=1.0,
                ))

        # --- Trend alignment signal (most permissive) ---
        # Price on the correct side of SMA20 + SMA50 aligned + ADX confirms direction
        if cur_adx > adx_threshold:
            # Bullish alignment: price > SMA20 > SMA50
            if cur_close > cur_sma_f > cur_sma_s:
                dist_from_sma = (cur_close - cur_sma_f) / cur_atr
                confidence = 0.25 + min(0.3, dist_from_sma * 0.05)
                edge_bps = max(1.0, (cur_close - cur_sma_s) / cur_close * 10000 * 0.05)
                stop = cur_close - 1.5 * cur_atr
                if confidence >= min_confidence:
                    signals.append(MomentumSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=15,
                        signal_type="trend_align", regime_fit=0.8,
                    ))

            # Bearish alignment: price < SMA20 < SMA50
            elif cur_close < cur_sma_f < cur_sma_s:
                dist_from_sma = (cur_sma_f - cur_close) / cur_atr
                confidence = 0.25 + min(0.3, dist_from_sma * 0.05)
                edge_bps = max(1.0, (cur_sma_s - cur_close) / cur_close * 10000 * 0.05)
                stop = cur_close + 1.5 * cur_atr
                if confidence >= min_confidence:
                    signals.append(MomentumSignal(
                        pair=symbol, side="SELL", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=15,
                        signal_type="trend_align", regime_fit=0.8,
                    ))

    return sorted(signals, key=lambda s: -s.confidence)
