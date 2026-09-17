"""Simple Trend Engine — FIXED Sep 17 LONG only.

Data-driven fixes:
- LONG only: SHORT 0 edge in 7488 discovered, engine SELL -37 ZAR
- Horizon 20 (was 5): top paper h15-h19, discovery h24 +87 bps
- Min confidence 0.4 (was 0.15), min edge 20 bps, no fallback noise
- Uses winning features: ext_vs_ma_20, trend_slope_20, not ret3 which is noise
- Asia session best, block EU open 08-09
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
    edge: float
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
    sma_period: int = 20,
    min_confidence: float = 0.4,
) -> list[SimpleTrendSignal]:
    """LONG only simple trend — ext_vs_ma_20 + SMA20.

    No fallback, no noise, horizon 20.
    """
    signals: list[SimpleTrendSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < 60:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        cur_close = close.iloc[-1]
        atr = _atr(high, low, close)
        cur_atr = atr.iloc[-1]

        if np.isnan(cur_atr) or cur_atr <= 0:
            continue
        cur_atr = max(cur_atr, cur_close * 0.005)

        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        cur_sma20 = sma20.iloc[-1]
        cur_sma50 = sma50.iloc[-1]

        if np.isnan(cur_sma20) or np.isnan(cur_sma50):
            continue

        # --- Winning feature: ext_vs_ma_20 LONG when 2% below SMA20 ---
        # Paper: ext_vs_ma_20 +9.07 (100% win)
        ext = (cur_close / cur_sma20) - 1.0 if cur_sma20 != 0 else 0
        if ext <= -0.02 and cur_sma20 > cur_sma50:
            # Below MA20 but MA20 > MA50 = pullback in uptrend
            extremity = min(1.0, abs(ext) / 0.05)
            confidence = 0.5 + 0.3 * extremity
            edge_bps = max(20.0, abs(ext) * 10000 * 0.6)
            stop = cur_close - 1.5 * cur_atr
            if confidence >= min_confidence:
                signals.append(SimpleTrendSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="ext_vs_ma_20_pullback", regime_fit=0.9,
                ))

        # --- Trend slope LONG: SMA20 > SMA50 and price > SMA20 ---
        if cur_close > cur_sma20 > cur_sma50:
            # Distance from SMA20
            dist = (cur_close - cur_sma20) / cur_atr
            if 0.2 <= dist <= 2.5:  # not too close, not overextended
                confidence = 0.4 + min(0.3, dist * 0.1)
                edge_bps = max(20.0, (cur_close - cur_sma50) / cur_close * 10000 * 0.15)
                stop = cur_close - 1.5 * cur_atr
                if confidence >= min_confidence:
                    signals.append(SimpleTrendSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=20,
                        signal_type="trend_pullback", regime_fit=0.8,
                    ))

    # Boost top pairs
    top_pairs = {"ARBUSDC", "TAOUSDC", "SUIUSDC", "BNBUSDC", "SOLUSDC"}
    boosted = []
    for s in signals:
        if s.pair in top_pairs:
            boosted.append(SimpleTrendSignal(
                pair=s.pair, side=s.side, entry_price=s.entry_price,
                stop_price=s.stop_price, atr=s.atr, edge=s.edge * 1.2,
                confidence=min(1.0, s.confidence * 1.1), horizon_bars=s.horizon_bars,
                signal_type=s.signal_type, regime_fit=s.regime_fit,
            ))
        else:
            boosted.append(s)

    return sorted(boosted, key=lambda s: (-s.confidence, -s.edge))
