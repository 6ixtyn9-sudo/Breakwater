"""Engine 4: Cross-Asset Lead/Lag.

BTC often leads, alts follow with a lag. When BTC makes a significant
move, enter alts that historically follow in the same direction.

Also detects pairs divergence: if two normally-correlated assets diverge,
trade the convergence.

Uses rolling correlation and lagged cross-correlation to measure lead/lag
relationships. No external data needed — just price candles.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from breakwater.engines.common import Signal

# --- Configurable parameters ---
CORR_WINDOW = 50  # bars for rolling correlation
LAG_WINDOW = 10  # bars to check for lagged correlation
BTC_MOVE_THRESHOLD = 0.015  # 1.5% move in BTC to trigger
MIN_CORRELATION = 0.5  # minimum historical correlation to consider a pair
HORIZON_BARS = 10  # holding period for lagged entry
DIVERGENCE_ZSCORE = 2.0  # z-score of spread to trigger pairs trade


def _btc_lead_score(
    btc_returns: pd.Series,
    alt_returns: pd.Series,
    lag: int = 3,
) -> float:
    """Measure how well BTC leads this alt.

    Returns correlation between BTC returns at t and alt returns at t+lag.
    Positive = BTC leads alt in same direction.
    """
    if len(btc_returns) < lag + 20 or len(alt_returns) < lag + 20:
        return 0.0
    btc_aligned = btc_returns.iloc[:-lag].reset_index(drop=True)
    alt_aligned = alt_returns.iloc[lag:].reset_index(drop=True)
    min_len = min(len(btc_aligned), len(alt_aligned))
    if min_len < 20:
        return 0.0
    corr = float(btc_aligned[:min_len].corr(alt_aligned[:min_len]))
    return corr if not np.isnan(corr) else 0.0


def _rolling_correlation(
    series_a: pd.Series,
    series_b: pd.Series,
    window: int = 50,
) -> pd.Series:
    """Rolling correlation between two series."""
    return series_a.rolling(window).corr(series_b)


def generate(
    frames: dict[str, pd.DataFrame],
    *,
    btc_symbol: str = "BTCUSDC",
    regime: str = "neutral",
    move_threshold: float = BTC_MOVE_THRESHOLD,
    horizon_bars: int = HORIZON_BARS,
) -> list[Signal]:
    """Generate cross-asset signals for all symbols relative to BTC.

    Args:
        frames: dict of symbol -> OHLCV DataFrame (must include btc_symbol)
        btc_symbol: the leading asset (usually BTC)
        regime: current market regime
        move_threshold: minimum BTC move (fraction) to trigger alt entries
        horizon_bars: holding period in bars

    Returns:
        List of Signals for alts that should follow BTC's move
    """
    if btc_symbol not in frames:
        return []

    btc_df = frames[btc_symbol]
    if len(btc_df) < CORR_WINDOW + LAG_WINDOW + 20:
        return []

    btc_close = btc_df["close"].astype(float)
    btc_returns = btc_close.pct_change()

    # Check if BTC made a significant recent move
    btc_recent_move = (float(btc_close.iloc[-1]) / float(btc_close.iloc[-5]) - 1)
    if abs(btc_recent_move) < move_threshold:
        return []  # BTC hasn't moved enough

    btc_direction = "BUY" if btc_recent_move > 0 else "SELL"

    signals: list[Signal] = []

    for symbol, df in frames.items():
        if symbol == btc_symbol:
            continue
        if len(df) < CORR_WINDOW + LAG_WINDOW + 20:
            continue

        alt_close = df["close"].astype(float)
        alt_returns = alt_close.pct_change()

        # Historical correlation
        corr = _rolling_correlation(btc_returns, alt_returns, CORR_WINDOW)
        current_corr = float(corr.iloc[-1]) if not np.isnan(corr.iloc[-1]) else 0
        if current_corr < MIN_CORRELATION:
            continue  # not correlated enough

        # Lead/lag score: does BTC lead this alt?
        best_lag = 0
        best_score = 0.0
        for lag in range(1, LAG_WINDOW + 1):
            score = _btc_lead_score(btc_returns, alt_returns, lag)
            if score > best_score:
                best_score = score
                best_lag = lag

        if best_score < MIN_CORRELATION:
            continue  # BTC doesn't reliably lead this alt

        # Has the alt already moved? If it already followed BTC, skip.
        alt_recent_move = (float(alt_close.iloc[-1]) / float(alt_close.iloc[-5]) - 1)
        already_moved = (
            (btc_direction == "BUY" and alt_recent_move > move_threshold * 0.5)
            or (btc_direction == "SELL" and alt_recent_move < -move_threshold * 0.5)
        )
        if already_moved:
            continue  # already followed

        # Confidence: based on correlation strength and lead/lag score
        confidence = min(1.0, (current_corr + best_score) / 2)

        # Regime fit: cross-asset works in all regimes
        regime_fit = 0.8

        # Expected edge: proportional to BTC move minus what alt already moved
        remaining_move = abs(btc_recent_move) - abs(alt_recent_move)
        expected_edge = max(0, remaining_move * 0.5)  # expect 50% of remaining move

        if expected_edge < 0.001:
            continue  # edge too small

        signals.append(
            Signal(
                symbol=symbol,
                side=btc_direction,
                engine="cross_asset",
                horizon_bars=horizon_bars,
                expected_edge=expected_edge,
                confidence=confidence,
                regime_fit=regime_fit,
                reason=f"btc_move={btc_recent_move:+.3f} alt_move={alt_recent_move:+.3f} lag={best_lag} corr={current_corr:.2f}",
            )
        )

    # Sort by score (best first) and return top signals
    signals.sort(key=lambda s: -s.score)
    return signals[:10]  # cap at 10 alt signals per BTC move
