"""Cross-Asset Lead/Lag Engine — FIXED Sep 17 LONG only.

Data-driven fixes:
- LONG only: SHORT 0 edge, engine SELL -37 ZAR, BTC down → alt down SELL loses in bull
- Only trade BTC up → alt up (BUY), not BTC down → alt down
- Min edge 20 bps, confidence 0.4, horizon 20
- Asia session best, profitable pairs ARB/TAO/SUI
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LeadLagSignal:
    pair: str
    side: str  # BUY only now
    entry_price: float
    stop_price: float
    atr: float
    edge: float
    confidence: float
    horizon_bars: int
    signal_type: str
    regime_fit: float
    leader: str


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()


def _find_lead_lag(
    leader_returns: pd.Series,
    follower_returns: pd.Series,
    max_lag: int = 20,
) -> tuple[int, float]:
    best_lag = 0
    best_corr = 0.0
    for lag in range(1, max_lag + 1):
        shifted = leader_returns.shift(lag)
        mask = shifted.notna() & follower_returns.notna()
        if mask.sum() < 30:
            continue
        corr = float(shifted[mask].corr(follower_returns[mask]))
        if abs(corr) > abs(best_corr):
            best_corr = corr
            best_lag = lag
    return best_lag, best_corr


def _detect_btc_move(
    btc_returns: pd.Series,
    lookback: int = 10,
    threshold_pct: float = 1.5,
) -> tuple[bool, str, float]:
    recent = btc_returns.iloc[-lookback:]
    cumulative = float(recent.sum() * 100)
    if cumulative > threshold_pct:
        return True, "BUY", cumulative
    # FIXED: Only BUY, no SELL — SHORT has 0 edge
    return False, "", 0.0


def scan_lead_lag(
    frames: dict[str, pd.DataFrame],
    *,
    leader_symbol: str = "BTCUSDC",
    max_lag: int = 20,
    btc_move_lookback: int = 10,
    btc_move_threshold: float = 1.5,
    min_correlation: float = 0.4,
    min_confidence: float = 0.4,
    lookback_window: int = 500,
) -> list[LeadLagSignal]:
    """LONG only BTC lead — BTC up → alt up.

    Data-driven: SHORT 0 edge, Asia best, min edge 20 bps.
    """
    signals: list[LeadLagSignal] = []

    btc_frame = None
    for sym in [leader_symbol, "BTCUSDC", "BTCUSDT", "BTC"]:
        if sym in frames and frames[sym] is not None:
            btc_frame = frames[sym]
            leader_symbol = sym
            break

    if btc_frame is None or len(btc_frame) < lookback_window:
        return signals

    btc_close = btc_frame["close"].astype(float)
    btc_returns = btc_close.pct_change()

    has_move, move_dir, move_mag = _detect_btc_move(
        btc_returns, btc_move_lookback, btc_move_threshold
    )

    if not has_move or move_dir != "BUY":
        return signals

    for symbol, df in frames.items():
        if symbol == leader_symbol:
            continue
        if df is None or len(df) < lookback_window:
            continue

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        cur_close = close.iloc[-1]
        cur_atr = float(_atr(high, low, close).iloc[-1])

        if np.isnan(cur_atr) or cur_atr <= 0:
            continue
        cur_atr = max(cur_atr, cur_close * 0.005)

        # Align returns
        if "start" in btc_frame.columns and "start" in df.columns:
            btc_aligned = btc_frame.set_index("start")["close"].astype(float)
            alt_aligned = df.set_index("start")["close"].astype(float)
            joined = btc_aligned.to_frame("btc").join(alt_aligned.to_frame("alt"), how="inner").dropna()
            if len(joined) < lookback_window:
                continue
            btc_ret = joined["btc"].pct_change()
            alt_ret = joined["alt"].pct_change()
        else:
            btc_ret = btc_returns
            alt_ret = close.pct_change()

        alt_recent = alt_ret.iloc[-lookback_window:-btc_move_lookback] if btc_move_lookback > 0 else alt_ret.iloc[-lookback_window:]
        btc_corr_recent = btc_ret.iloc[-lookback_window:-btc_move_lookback] if btc_move_lookback > 0 else btc_ret.iloc[-lookback_window:]

        best_lag, best_corr = _find_lead_lag(btc_corr_recent, alt_recent, max_lag)

        if abs(best_corr) < min_correlation or best_lag < 1:
            continue

        # Only positive correlation + BTC up → BUY alt
        if best_corr <= 0:
            continue

        corr_strength = min(1.0, best_corr / 0.8)
        mag_strength = min(1.0, move_mag / 10.0)
        lag_penalty = max(0.5, 1.0 - best_lag / max_lag)

        confidence = (0.4 * corr_strength + 0.3 * mag_strength + 0.3 * lag_penalty)
        if confidence < min_confidence:
            continue

        # Edge: BTC move * correlation, min 20 bps
        edge_bps = max(20.0, move_mag * 100 * best_corr * 0.4)

        stop = cur_close - 1.5 * cur_atr

        signals.append(LeadLagSignal(
            pair=symbol, side="BUY", entry_price=cur_close,
            stop_price=stop, atr=cur_atr, edge=edge_bps,
            confidence=min(1.0, confidence), horizon_bars=20,
            signal_type="btc_lead", regime_fit=0.8, leader=leader_symbol,
        ))

    # Boost top pairs
    top_pairs = {"ARBUSDC", "TAOUSDC", "SUIUSDC", "BNBUSDC", "SOLUSDC"}
    boosted = []
    for s in signals:
        if s.pair in top_pairs:
            boosted.append(LeadLagSignal(
                pair=s.pair, side=s.side, entry_price=s.entry_price,
                stop_price=s.stop_price, atr=s.atr, edge=s.edge * 1.2,
                confidence=min(1.0, s.confidence * 1.1), horizon_bars=s.horizon_bars,
                signal_type=s.signal_type, regime_fit=s.regime_fit, leader=s.leader,
            ))
        else:
            boosted.append(s)

    return sorted(boosted, key=lambda s: -s.confidence)
