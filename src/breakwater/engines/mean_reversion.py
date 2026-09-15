"""Mean Reversion Engine.

Assets that deviate far from their mean tend to revert. Buys oversold,
sells overbought.

Signals:
  - RSI extremes (<35 oversold, >65 overbought — tighter bands for crypto)
  - Bollinger Band bounces (price touches lower/upper band)
  - Z-score of price vs SMA (standard deviations from mean)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MeanReversionSignal:
    pair: str
    side: str  # "BUY" or "SELL"
    entry_price: float
    stop_price: float
    atr: float
    edge: float  # expected edge per bar (bps)
    confidence: float  # 0-1
    horizon_bars: int
    signal_type: str  # "rsi", "bollinger", "zscore"
    regime_fit: float  # 0-1


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range."""
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()


def _bollinger_bands(close: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Bollinger Bands: middle, upper, lower."""
    middle = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return middle, upper, lower


def _zscore(close: pd.Series, period: int = 20) -> pd.Series:
    """Z-score of price vs rolling mean."""
    mean = close.rolling(period).mean()
    std = close.rolling(period).std()
    return (close - mean) / std.replace(0, np.nan)


def scan_mean_reversion(
    frames: dict[str, pd.DataFrame],
    *,
    rsi_period: int = 14,
    rsi_oversold: float = 35.0,
    rsi_overbought: float = 65.0,
    bb_period: int = 20,
    bb_std: float = 1.8,
    zscore_period: int = 20,
    zscore_threshold: float = 1.5,
    min_confidence: float = 0.2,
) -> list[MeanReversionSignal]:
    """Scan all pairs for mean reversion signals.

    Lowered thresholds for real market conditions:
    - RSI: 35/65 (crypto oscillates in tighter bands than equities)
    - Bollinger: 1.8 std (closer bands = more touches)
    - Z-score: 1.5 (more frequent signals)
    """
    signals: list[MeanReversionSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < max(rsi_period, bb_period, zscore_period) + 14:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        rsi = _rsi(close, rsi_period)
        atr = _atr(high, low, close)
        bb_mid, bb_upper, bb_lower = _bollinger_bands(close, bb_period, bb_std)
        zs = _zscore(close, zscore_period)

        cur_close = close.iloc[-1]
        cur_rsi = rsi.iloc[-1]
        cur_atr = atr.iloc[-1]
        cur_bb_upper = bb_upper.iloc[-1]
        cur_bb_lower = bb_lower.iloc[-1]
        cur_bb_mid = bb_mid.iloc[-1]
        cur_zscore = zs.iloc[-1]

        if np.isnan(cur_atr) or cur_atr <= 0:
            continue

        # --- RSI signals ---
        if not np.isnan(cur_rsi):
            if cur_rsi < rsi_oversold:
                extremity = (rsi_oversold - cur_rsi) / rsi_oversold
                confidence = 0.3 + 0.35 * extremity
                stop = cur_close - 2.0 * cur_atr
                target = cur_bb_mid if not np.isnan(cur_bb_mid) else cur_close * 1.01
                edge_bps = max(1.0, (target - cur_close) / cur_close * 10000 * 0.3)
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=10,
                        signal_type="rsi", regime_fit=0.4,
                    ))

            elif cur_rsi > rsi_overbought:
                extremity = (cur_rsi - rsi_overbought) / (100 - rsi_overbought)
                confidence = 0.3 + 0.35 * extremity
                stop = cur_close + 2.0 * cur_atr
                target = cur_bb_mid if not np.isnan(cur_bb_mid) else cur_close * 0.99
                edge_bps = max(1.0, (cur_close - target) / cur_close * 10000 * 0.3)
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="SELL", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=10,
                        signal_type="rsi", regime_fit=0.4,
                    ))

        # --- Bollinger Band signals ---
        if not np.isnan(cur_bb_lower) and not np.isnan(cur_bb_upper):
            if cur_close <= cur_bb_lower:
                deviation = (cur_bb_lower - cur_close) / cur_atr if cur_atr > 0 else 0
                confidence = 0.3 + min(0.3, deviation * 0.15)
                stop = cur_close - 2.0 * cur_atr
                edge_bps = max(1.0, (cur_bb_mid - cur_close) / cur_close * 10000 * 0.3)
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=10,
                        signal_type="bollinger", regime_fit=0.4,
                    ))

            elif cur_close >= cur_bb_upper:
                deviation = (cur_close - cur_bb_upper) / cur_atr if cur_atr > 0 else 0
                confidence = 0.3 + min(0.3, deviation * 0.15)
                stop = cur_close + 2.0 * cur_atr
                edge_bps = max(1.0, (cur_close - cur_bb_mid) / cur_close * 10000 * 0.3)
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="SELL", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=10,
                        signal_type="bollinger", regime_fit=0.4,
                    ))

        # --- Z-score signals ---
        if not np.isnan(cur_zscore):
            if cur_zscore < -zscore_threshold:
                extremity = min(1.0, (abs(cur_zscore) - zscore_threshold) / zscore_threshold)
                confidence = 0.3 + 0.3 * extremity
                stop = cur_close - 2.0 * cur_atr
                edge_bps = max(1.0, abs(cur_zscore) * 8)
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=10,
                        signal_type="zscore", regime_fit=0.4,
                    ))

            elif cur_zscore > zscore_threshold:
                extremity = min(1.0, (cur_zscore - zscore_threshold) / zscore_threshold)
                confidence = 0.3 + 0.3 * extremity
                stop = cur_close + 2.0 * cur_atr
                edge_bps = max(1.0, abs(cur_zscore) * 8)
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="SELL", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=10,
                        signal_type="zscore", regime_fit=0.4,
                    ))

    return sorted(signals, key=lambda s: -s.confidence)
