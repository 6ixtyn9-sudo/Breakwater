"""Engine 2: Momentum / Trend Following.

Don't predict, react. If an asset has been trending for N bars, enter in
that direction. Uses SMA crossovers, breakout above N-bar high/low, and
ADX for trend strength.

Works in trending markets. Gets chopped in ranging markets — the regime
detector should gate this engine ON only when regime is trending.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from breakwater.engines.common import Signal

# --- Configurable parameters (env-backed at call site) ---
SMA_FAST = 20
SMA_SLOW = 50
ADX_PERIOD = 14
ADX_THRESHOLD = 25  # ADX > 25 = trending
BREAKOUT_LOOKBACK = 20  # N-bar high/low breakout
HORIZON_BARS = 12  # default holding period


def _adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average Directional Index — measures trend strength."""
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    # When +DM > -DM, keep +DM, zero -DM, and vice versa
    cond = plus_dm > minus_dm
    plus_dm = plus_dm.where(cond, 0)
    minus_dm = minus_dm.where(~cond, 0)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(period).mean()
    return adx


def generate(
    df: pd.DataFrame,
    *,
    symbol: str = "",
    regime: str = "neutral",
    min_adx: float = ADX_THRESHOLD,
    horizon_bars: int = HORIZON_BARS,
) -> list[Signal]:
    """Generate momentum signals for one symbol.

    Args:
        df: OHLCV DataFrame with columns [open, high, low, close, volume].
            Must be sorted by time ascending.
        symbol: asset name for the signal
        regime: current market regime (bull/bear/neutral)
        min_adx: minimum ADX to consider the market trending
        horizon_bars: holding period in bars

    Returns:
        List of 0 or 1 Signal (momentum gives at most one signal per symbol)
    """
    if len(df) < SMA_SLOW + ADX_PERIOD:
        return []

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)

    # Trend strength
    adx = _adx(high, low, close, ADX_PERIOD)
    current_adx = float(adx.iloc[-1]) if not np.isnan(adx.iloc[-1]) else 0
    if current_adx < min_adx:
        return []  # not trending, skip

    # SMA crossover
    sma_fast = close.rolling(SMA_FAST).mean()
    sma_slow = close.rolling(SMA_SLOW).mean()
    fast_above = float(sma_fast.iloc[-1]) > float(sma_slow.iloc[-1])
    fast_crossed_up = (
        float(sma_fast.iloc[-1]) > float(sma_slow.iloc[-1])
        and float(sma_fast.iloc[-2]) <= float(sma_slow.iloc[-2])
    )

    # Breakout
    recent_high = float(high.iloc[-BREAKOUT_LOOKBACK:].max())
    recent_low = float(low.iloc[-BREAKOUT_LOOKBACK:].min())
    current_price = float(close.iloc[-1])
    breakout_up = current_price >= recent_high
    breakout_down = current_price <= recent_low

    # Direction: breakout takes priority, then SMA crossover
    if breakout_up:
        side = "BUY"
    elif breakout_down:
        side = "SELL"
    elif fast_above:
        side = "BUY"
    else:
        side = "SELL"

    # Confidence: stronger ADX = more confident, breakout = higher confidence
    adx_conf = min(1.0, (current_adx - min_adx) / 30)  # scale 25-55 → 0-1
    breakout_bonus = 0.2 if (breakout_up or breakout_down) else 0
    crossover_bonus = 0.2 if fast_crossed_up else 0
    confidence = min(1.0, 0.4 + adx_conf * 0.4 + breakout_bonus + crossover_bonus)

    # Regime fit: momentum works in trending regimes
    regime_fit = 1.0 if regime in ("bull", "bear") else 0.5

    # Expected edge: ADX/10000 as a rough proxy (ADX 30 → 30 bps)
    expected_edge = current_adx / 10000

    return [
        Signal(
            symbol=symbol,
            side=side,
            engine="momentum",
            horizon_bars=horizon_bars,
            expected_edge=expected_edge,
            confidence=confidence,
            regime_fit=regime_fit,
            reason=f"adx={current_adx:.0f} sma_cross={fast_crossed_up} breakout={'up' if breakout_up else 'down' if breakout_down else 'no'}",
        )
    ]
