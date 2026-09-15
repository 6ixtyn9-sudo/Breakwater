"""Engine 3: Mean Reversion.

Assets that deviate far from their mean tend to revert. Uses RSI extremes,
Bollinger band bounces, and z-score of price vs moving average.

Works in ranging markets. Gets destroyed in trends — the regime detector
should gate this engine ON only when regime is ranging/neutral.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from breakwater.engines.common import Signal

# --- Configurable parameters ---
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
BB_PERIOD = 20
BB_STD = 2.0
ZSCORE_PERIOD = 20
ZSCORE_THRESHOLD = 2.0  # z-score > 2 = extended
HORIZON_BARS = 8  # shorter horizon for mean reversion


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _bollinger(close: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Bollinger Bands: (upper, middle, lower)."""
    middle = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper, middle, lower


def _zscore(close: pd.Series, period: int = 20) -> pd.Series:
    """Z-score of price vs rolling mean."""
    mean = close.rolling(period).mean()
    std = close.rolling(period).std()
    return (close - mean) / std.replace(0, np.nan)


def generate(
    df: pd.DataFrame,
    *,
    symbol: str = "",
    regime: str = "neutral",
    horizon_bars: int = HORIZON_BARS,
) -> list[Signal]:
    """Generate mean-reversion signals for one symbol.

    Args:
        df: OHLCV DataFrame with columns [open, high, low, close, volume].
            Must be sorted by time ascending.
        symbol: asset name for the signal
        regime: current market regime (bull/bear/neutral)

    Returns:
        List of 0 or 1 Signal
    """
    if len(df) < max(RSI_PERIOD, BB_PERIOD, ZSCORE_PERIOD) + 5:
        return []

    close = df["close"].astype(float)

    # RSI
    rsi = _rsi(close, RSI_PERIOD)
    current_rsi = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = _bollinger(close, BB_PERIOD, BB_STD)
    price = float(close.iloc[-1])
    bb_up = float(bb_upper.iloc[-1]) if not np.isnan(bb_upper.iloc[-1]) else price
    bb_low = float(bb_lower.iloc[-1]) if not np.isnan(bb_lower.iloc[-1]) else price

    # Z-score
    zs = _zscore(close, ZSCORE_PERIOD)
    current_z = float(zs.iloc[-1]) if not np.isnan(zs.iloc[-1]) else 0

    # Signal logic: need at least 2 of 3 indicators agreeing
    oversold_signals = 0
    overbought_signals = 0

    if current_rsi < RSI_OVERSOLD:
        oversold_signals += 1
    if price <= bb_low:
        oversold_signals += 1
    if current_z < -ZSCORE_THRESHOLD:
        oversold_signals += 1

    if current_rsi > RSI_OVERBOUGHT:
        overbought_signals += 1
    if price >= bb_up:
        overbought_signals += 1
    if current_z > ZSCORE_THRESHOLD:
        overbought_signals += 1

    if oversold_signals >= 2:
        side = "BUY"  # oversold, expect reversion up
        signals_count = oversold_signals
    elif overbought_signals >= 2:
        side = "SELL"  # overbought, expect reversion down
        signals_count = overbought_signals
    else:
        return []  # no signal

    # Confidence: more indicators agreeing = higher confidence
    confidence = 0.3 + signals_count * 0.2  # 2 signals → 0.7, 3 → 0.9

    # Regime fit: mean reversion works in ranging/neutral, not in trends
    regime_fit = 1.0 if regime == "neutral" else 0.3

    # Expected edge: based on how far extended the price is
    extension = abs(current_z)
    expected_edge = min(0.01, extension * 0.002)  # z=2 → 40 bps, z=3 → 60 bps, cap 100 bps

    return [
        Signal(
            symbol=symbol,
            side=side,
            engine="mean_reversion",
            horizon_bars=horizon_bars,
            expected_edge=expected_edge,
            confidence=confidence,
            regime_fit=regime_fit,
            reason=f"rsi={current_rsi:.0f} z={current_z:.2f} bb={'low' if price <= bb_low else 'high' if price >= bb_up else 'mid'}",
        )
    ]
