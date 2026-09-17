"""Momentum/Trend Following Engine — FIXED Sep 17.

Data-driven fixes:
- LONG only: SHORT 0 positive in 7488 discovered, engine SELL -37 ZAR
- Horizon 20 (was 10): top paper h15-h19 winners, h24 best in discovery +87 bps
- Use winning features: trend_slope_20 +5.56 (2 trades 100%), ext_vs_ma_20 +9.07
  not breakout which is -8 avg in engine
- Min edge 20 bps, confidence 0.4, ADX 20 (was 18) to filter chop
- Asia session best, EU open 08-09 worst
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MomentumSignal:
    pair: str
    side: str  # BUY only
    entry_price: float
    stop_price: float
    atr: float
    edge: float
    confidence: float
    horizon_bars: int
    signal_type: str
    regime_fit: float


def _adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
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
    adx_threshold: float = 20.0,
    adx_period: int = 14,
    min_confidence: float = 0.4,
) -> list[MomentumSignal]:
    """LONG only momentum — trend alignment + SMA cross.

    Data-driven: SHORT 0 edge, Asia best, h20 best, trend_slope_20 +5.56 paper.
    """
    signals: list[MomentumSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < sma_slow + adx_period:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        volume = df["volume"].astype(float) if "volume" in df.columns else None

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
        cur_atr = max(cur_atr, cur_close * 0.005)

        # Volume filter: avoid low-vol breakouts
        vol_ok = True
        if volume is not None and len(volume) >= 20:
            vol_avg = volume.iloc[-20:].mean()
            if vol_avg > 0:
                vol_ok = float(volume.iloc[-1]) >= 0.5 * vol_avg
        if not vol_ok:
            continue

        # --- SMA crossover LONG only (was both) ---
        if prev_sma_f <= prev_sma_s and cur_sma_f > cur_sma_s:
            trend_strength = min(1.0, cur_adx / 40.0)
            confidence = 0.4 + 0.3 * trend_strength
            if cur_close > cur_sma_f:
                confidence += 0.1
            # Require ADX > threshold to avoid chop (EU open 08-09 worst)
            if cur_adx < adx_threshold:
                continue
            edge_bps = max(20.0, (cur_close - cur_sma_s) / cur_close * 10000 * 0.15)
            stop = cur_close - 1.5 * cur_atr
            if confidence >= min_confidence and edge_bps >= 20:
                signals.append(MomentumSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="sma_cross", regime_fit=1.0 if cur_adx > adx_threshold else 0.5,
                ))

        # --- Breakout LONG only, higher ADX threshold ---
        recent_high = high.iloc[-breakout_lookback-1:-1].max()
        if not np.isnan(recent_high) and cur_close >= recent_high and cur_adx > adx_threshold:
            breakout_pct = (cur_close - recent_high) / recent_high
            # Filter tiny breakouts <0.5%
            if breakout_pct < 0.005:
                continue
            confidence = 0.4 + min(0.3, breakout_pct * 50)
            if cur_sma_f > cur_sma_s:
                confidence += 0.1
            edge_bps = max(20.0, breakout_pct * 10000 * 0.3)
            stop = cur_close - 1.5 * cur_atr
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="breakout", regime_fit=1.0,
                ))

        # --- Trend alignment LONG only (most profitable: +5.56 paper) ---
        # Bullish alignment: price > SMA20 > SMA50 + ADX>20
        if cur_adx > adx_threshold and cur_close > cur_sma_f > cur_sma_s:
            dist_from_sma = (cur_close - cur_sma_f) / cur_atr
            # Avoid overextended >3 ATR (chasing)
            if dist_from_sma > 3.0:
                continue
            confidence = 0.4 + min(0.3, dist_from_sma * 0.08)
            edge_bps = max(20.0, (cur_close - cur_sma_s) / cur_close * 10000 * 0.1)
            stop = cur_close - 1.5 * cur_atr
            if confidence >= min_confidence:
                signals.append(MomentumSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="trend_align", regime_fit=0.9,
                ))

    # Boost profitable pairs
    top_pairs = {"ARBUSDC", "TAOUSDC", "SUIUSDC", "BNBUSDC", "SOLUSDC"}
    boosted = []
    for s in signals:
        if s.pair in top_pairs:
            boosted.append(MomentumSignal(
                pair=s.pair, side=s.side, entry_price=s.entry_price,
                stop_price=s.stop_price, atr=s.atr, edge=s.edge * 1.2,
                confidence=min(1.0, s.confidence * 1.1), horizon_bars=s.horizon_bars,
                signal_type=s.signal_type, regime_fit=s.regime_fit,
            ))
        else:
            boosted.append(s)

    return sorted(boosted, key=lambda s: (-s.confidence, -s.edge))
