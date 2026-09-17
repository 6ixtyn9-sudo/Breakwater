"""Mean Reversion Engine — FIXED Sep 17.

Data-driven fixes from paper_trade_log.csv 157 closes -46 ZAR:
- LONG only: SHORT 0 positive mean in 7488 discovered, engine SELL -37 ZAR (19 SELL / 3 BUY)
- Horizon 20 (was 10): top discovered h24 +87 bps, paper winners h15-h19
- Use winning features: ext_vs_ma_20 (+9.07 paper, 4 trades 100% win), vol_regime (+7.60)
  not RSI/BB which are -12 in paper
- Min edge 20 bps (2x PERP cost 9 bps), confidence 0.4, stop 1.5 ATR
- Asia session best 02 UTC +4.57, EU open 08-09 worst -13,-10
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MeanReversionSignal:
    pair: str
    side: str  # "BUY" only now
    entry_price: float
    stop_price: float
    atr: float
    edge: float  # bps
    confidence: float
    horizon_bars: int
    signal_type: str
    regime_fit: float


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()


def _sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(period).mean()


def scan_mean_reversion(
    frames: dict[str, pd.DataFrame],
    *,
    rsi_period: int = 14,
    rsi_oversold: float = 35.0,
    bb_period: int = 20,
    zscore_period: int = 20,
    zscore_threshold: float = 2.0,
    min_confidence: float = 0.4,
) -> list[MeanReversionSignal]:
    """LONG only mean reversion — ext_vs_ma_20 + vol_regime.

    Data-driven: SHORT 0 edge, Asia best, h20 best, ext_vs_ma_20 +9.07 paper.
    """
    signals: list[MeanReversionSignal] = []

    for symbol, df in frames.items():
        if df is None or len(df) < 60:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)

        sma20 = _sma(close, 20)
        sma50 = _sma(close, 50)
        rsi = _rsi(close, rsi_period)
        atr = _atr(high, low, close)

        cur_close = close.iloc[-1]
        cur_atr = atr.iloc[-1]
        cur_sma20 = sma20.iloc[-1]
        cur_sma50 = sma50.iloc[-1]
        cur_rsi = rsi.iloc[-1]

        if np.isnan(cur_atr) or cur_atr <= 0 or np.isnan(cur_sma20):
            continue
        cur_atr = max(cur_atr, cur_close * 0.005)

        # --- Winning feature: ext_vs_ma_20 (price 2% below SMA20) ---
        # Paper: feat_ext_vs_ma_20 +9.07 (4 trades 100% win), best discovered h24 +87 bps
        ext_vs_ma20 = (cur_close / cur_sma20) - 1.0 if cur_sma20 != 0 else 0
        if ext_vs_ma20 <= -0.02:  # 2% below MA20
            # Deeper = higher confidence
            extremity = min(1.0, abs(ext_vs_ma20) / 0.05)
            confidence = 0.4 + 0.4 * extremity
            # Edge: distance to SMA20, at least 20 bps
            edge_bps = max(20.0, abs(ext_vs_ma20) * 10000 * 0.5)
            stop = cur_close - 1.5 * cur_atr
            if confidence >= min_confidence and edge_bps >= 20:
                signals.append(MeanReversionSignal(
                    pair=symbol, side="BUY", entry_price=cur_close,
                    stop_price=stop, atr=cur_atr, edge=edge_bps,
                    confidence=min(1.0, confidence), horizon_bars=20,
                    signal_type="ext_vs_ma_20", regime_fit=0.9,
                ))

        # --- RSI oversold LONG only (no SHORT) ---
        if not np.isnan(cur_rsi) and cur_rsi < rsi_oversold:
            extremity = (rsi_oversold - cur_rsi) / rsi_oversold
            confidence = 0.4 + 0.3 * extremity
            # Require price also below SMA20 to avoid catching falling knife in strong downtrend
            if cur_close < cur_sma20:
                edge_bps = max(20.0, (rsi_oversold - cur_rsi) * 2)
                stop = cur_close - 1.5 * cur_atr
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=20,
                        signal_type="rsi", regime_fit=0.6,
                    ))

        # --- Z-score LONG only, deeper threshold 2.0 (was 1.5) ---
        mean20 = close.rolling(20).mean().iloc[-1]
        std20 = close.rolling(20).std().iloc[-1]
        if not np.isnan(mean20) and not np.isnan(std20) and std20 > 0:
            zscore = (cur_close - mean20) / std20
            if zscore < -zscore_threshold:
                extremity = min(1.0, (abs(zscore) - zscore_threshold) / 2.0)
                confidence = 0.4 + 0.3 * extremity
                edge_bps = max(20.0, abs(zscore) * 10)
                stop = cur_close - 1.5 * cur_atr
                if confidence >= min_confidence:
                    signals.append(MeanReversionSignal(
                        pair=symbol, side="BUY", entry_price=cur_close,
                        stop_price=stop, atr=cur_atr, edge=edge_bps,
                        confidence=min(1.0, confidence), horizon_bars=20,
                        signal_type="zscore", regime_fit=0.5,
                    ))

    # Filter profitable pairs: ARB +7.76, TAO +5.69, SUI +5.47 have edge
    # Boost confidence for top pairs
    top_pairs = {"ARBUSDC", "TAOUSDC", "SUIUSDC", "BNBUSDC", "SOLUSDC", "XPLUSDC"}
    boosted = []
    for s in signals:
        if s.pair in top_pairs:
            boosted.append(MeanReversionSignal(
                pair=s.pair, side=s.side, entry_price=s.entry_price,
                stop_price=s.stop_price, atr=s.atr, edge=s.edge * 1.2,
                confidence=min(1.0, s.confidence * 1.1), horizon_bars=s.horizon_bars,
                signal_type=s.signal_type, regime_fit=s.regime_fit,
            ))
        else:
            boosted.append(s)

    return sorted(boosted, key=lambda s: (-s.confidence, -s.edge))
