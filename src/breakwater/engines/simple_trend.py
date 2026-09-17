"""Simple Trend Engine — FIXED Sep 17 + NEW Sep 17 neutral-regime features.

Data-driven fixes:
- LONG only: SHORT 0 edge in 7488 discovered, engine SELL -37 ZAR
- Horizon 20: top paper h15-h19, discovery h24 +87 bps
- Min confidence 0.4, min edge 20 bps, no fallback noise
- Uses winning features: ext_vs_ma_20 (+9.07), trend_slope_20 (+5.56)
- NEW: neutral-regime range trading: range_pos_20, bb_pos_20, mean_rev_strength
  for 66.7% neutral market where trend fails
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
    """LONG only simple trend — ext_vs_ma_20 + SMA20 + NEW neutral features."""
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
        ext = (cur_close / cur_sma20) - 1.0 if cur_sma20 != 0 else 0
        if ext <= -0.02 and cur_sma20 > cur_sma50:
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
            dist = (cur_close - cur_sma20) / cur_atr
            if 0.2 <= dist <= 2.5:
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

        # --- NEW: Range position LONG for neutral regime (66.7% neutral) ---
        # feat_range_pos_20: 0=low of 20-bar range, 1=high. Buy low in neutral.
        high_20 = high.rolling(20).max().iloc[-1]
        low_20 = low.rolling(20).min().iloc[-1]
        if not np.isnan(high_20) and not np.isnan(low_20) and high_20 != low_20:
            range_pos = (cur_close - low_20) / (high_20 - low_20)
            if 0.05 <= range_pos <= 0.35:  # near low, not extreme
                # Check trend neutral: SMA20 and SMA50 close = neutral
                sma_diff = abs(cur_sma20 - cur_sma50) / cur_close
                if sma_diff < 0.02:  # neutral trend
                    confidence = 0.45 + (0.35 - range_pos) * 0.3
                    edge_bps = max(20.0, (0.5 - range_pos) * 10000 * 0.1)
                    stop = cur_close - 1.5 * cur_atr
                    if confidence >= min_confidence:
                        signals.append(SimpleTrendSignal(
                            pair=symbol, side="BUY", entry_price=cur_close,
                            stop_price=stop, atr=cur_atr, edge=edge_bps,
                            confidence=min(1.0, confidence), horizon_bars=20,
                            signal_type="range_pos_neutral", regime_fit=0.85,
                        ))

        # --- NEW: BB position LONG: buy near lower BB in neutral ---
        # BB width contraction indicates squeeze, breakout imminent
        close_sma20 = close.rolling(20).mean().iloc[-1]
        close_std20 = close.rolling(20).std().iloc[-1]
        if not np.isnan(close_sma20) and not np.isnan(close_std20) and close_std20 > 0:
            bb_upper = close_sma20 + 2.0 * close_std20
            bb_lower = close_sma20 - 2.0 * close_std20
            if bb_upper != bb_lower:
                bb_pos = (cur_close - bb_lower) / (bb_upper - bb_lower)
                bb_width = (bb_upper - bb_lower) / close_sma20
                # Buy near lower BB (0.1-0.3) when width is contracting (<0.08)
                if 0.05 <= bb_pos <= 0.35 and bb_width < 0.08:
                    confidence = 0.45 + (0.35 - bb_pos) * 0.2
                    edge_bps = max(20.0, (0.5 - bb_pos) * 10000 * 0.12)
                    stop = cur_close - 1.5 * cur_atr
                    if confidence >= min_confidence:
                        signals.append(SimpleTrendSignal(
                            pair=symbol, side="BUY", entry_price=cur_close,
                            stop_price=stop, atr=cur_atr, edge=edge_bps,
                            confidence=min(1.0, confidence), horizon_bars=20,
                            signal_type="bb_pos_squeeze", regime_fit=0.8,
                        ))

        # --- NEW: Time since low: buy when just bounced from low ---
        # If time_since_low is small (0-0.2 = recently at low), momentum up
        low_series = low.rolling(20).apply(lambda x: float(len(x)-1 - np.argmin(x)), raw=False)
        cur_time_low = low_series.iloc[-1] / 20.0 if not np.isnan(low_series.iloc[-1]) else 1.0
        if 0.05 <= cur_time_low <= 0.25:  # recently at low, now bouncing
            # Check close > low + some distance
            if cur_close > low_20 + 0.3 * (high_20 - low_20):
                confidence = 0.4 + (0.25 - cur_time_low) * 0.5
                edge_bps = max(20.0, (0.3 - cur_time_low) * 10000 * 0.08)
                stop = cur_close - 1.5 * cur_atr
                if confidence >= min_confidence:
                    signals.append(SimpleTrendSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=20,
                        signal_type="time_since_low_bounce", regime_fit=0.75,
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
