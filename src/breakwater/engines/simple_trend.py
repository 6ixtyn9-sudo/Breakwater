"""Simple Trend Engine — high-frequency signals from basic price action.

Designed to always produce signals in any market condition. Uses the most
basic momentum indicators that fire on virtually every bar:

- 3-bar return direction (very short-term momentum)
- Price vs SMA10 (micro-trend)
- Consecutive up/down bars (streak detection)

Low confidence, low edge — but always firing. The meta-ranker decides
if they're worth trading based on regime fit.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SimpleTrendSignal:
    pair: str
    side: str
    entry_price: float
    stop_price: float
    atr: float
    edge: float  # bps
    confidence: float
    horizon_bars: int
    signal_type: str
    regime_fit: float


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()


def scan_simple_trend(
    frames: dict[str, pd.DataFrame],
    *,
    lookback: int = 3,
    sma_period: int = 10,
    min_confidence: float = 0.15,
) -> list[SimpleTrendSignal]:
    """Scan for basic trend signals that fire frequently.

    This is the 'always-on' engine — designed to produce at least some
    signals in every market condition. Low confidence, low edge.
    """
    signals: list[SimpleTrendSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < max(lookback, sma_period) + 14:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        cur_close = close.iloc[-1]
        atr = _atr(high, low, close)
        cur_atr = atr.iloc[-1]

        if np.isnan(cur_atr) or cur_atr <= 0:
            continue
        # ATR floor: prevent tiny ATR from causing max leverage in low-vol periods
        cur_atr = max(cur_atr, cur_close * 0.005)

        sma = close.rolling(sma_period).mean()
        cur_sma = sma.iloc[-1]

        # 3-bar return
        ret = (cur_close - close.iloc[-lookback - 1]) / close.iloc[-lookback - 1]

        # Consecutive direction
        last3 = close.iloc[-3:].values
        consecutive_up = all(last3[i] > last3[i - 1] for i in range(1, len(last3)))
        consecutive_down = all(last3[i] < last3[i - 1] for i in range(1, len(last3)))

        # --- 3-bar momentum ---
        if abs(ret) > 0.003:  # >0.3% move
            side = "BUY" if ret > 0 else "SELL"
            strength = min(1.0, abs(ret) / 0.03)  # normalize to 3% max
            confidence = 0.2 + 0.2 * strength
            edge_bps = max(1.0, abs(ret) * 10000 * 0.15)
            stop = cur_close - 2.0 * cur_atr if side == "BUY" else cur_close + 2.0 * cur_atr
            if confidence >= min_confidence:
                signals.append(SimpleTrendSignal(
                    pair=symbol, side=side, entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=5,
                    signal_type="ret3", regime_fit=0.5,
                ))

        # --- Price vs SMA10 ---
        if not np.isnan(cur_sma) and cur_sma > 0:
            dist = (cur_close - cur_sma) / cur_sma
            if abs(dist) > 0.005:  # >0.5% from SMA
                side = "BUY" if dist > 0 else "SELL"
                strength = min(1.0, abs(dist) / 0.05)
                confidence = 0.2 + 0.15 * strength
                edge_bps = max(1.0, abs(dist) * 10000 * 0.2)
                stop = cur_close - 2.0 * cur_atr if side == "BUY" else cur_close + 2.0 * cur_atr
                if confidence >= min_confidence:
                    signals.append(SimpleTrendSignal(
                        pair=symbol, side=side, entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=5,
                        signal_type="sma10_dist", regime_fit=0.5,
                    ))

        # --- Streak detection ---
        if consecutive_up or consecutive_down:
            side = "BUY" if consecutive_up else "SELL"
            streak_ret = abs((close.iloc[-1] - close.iloc[-3]) / close.iloc[-3])
            confidence = 0.25 + min(0.2, streak_ret * 10)
            edge_bps = max(1.0, streak_ret * 10000 * 0.15)
            stop = cur_close - 2.0 * cur_atr if side == "BUY" else cur_close + 2.0 * cur_atr
            if confidence >= min_confidence:
                signals.append(SimpleTrendSignal(
                    pair=symbol, side=side, entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=5,
                    signal_type="streak", regime_fit=0.5,
                ))

    return sorted(signals, key=lambda s: -s.confidence)
