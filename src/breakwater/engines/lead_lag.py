"""Cross-Asset Lead/Lag Engine.

BTC often leads, alts follow with a lag. That lag is tradeable.

Method:
  - Compute rolling correlation between BTC and each alt
  - Measure the lag (in bars) at which correlation is highest
  - When BTC makes a significant move, enter alts that historically follow
  - Also: pairs trading — when two correlated assets diverge, trade convergence

This is structural alpha — based on how information propagates through
the crypto market, not on statistical patterns.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LeadLagSignal:
    pair: str
    side: str  # "BUY" or "SELL"
    entry_price: float
    stop_price: float
    atr: float
    edge: float  # expected edge per bar (bps)
    confidence: float  # 0-1
    horizon_bars: int
    signal_type: str  # "btc_lead" or "pairs_divergence"
    regime_fit: float  # 0-1
    leader: str  # which asset is leading


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range."""
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
    """Find the lag (in bars) at which correlation is highest.

    Returns (best_lag, correlation_at_best_lag).
    Positive lag means leader moves first.
    """
    best_lag = 0
    best_corr = 0.0

    for lag in range(1, max_lag + 1):
        shifted = leader_returns.shift(lag)
        # Drop NaN for correlation
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
    lookback: int = 5,
    threshold_pct: float = 3.0,
) -> tuple[bool, str, float]:
    """Detect if BTC made a significant move recently.

    Returns (has_move, direction, magnitude_pct).
    """
    recent = btc_returns.iloc[-lookback:]
    cumulative = float(recent.sum() * 100)

    if cumulative > threshold_pct:
        return True, "BUY", cumulative
    elif cumulative < -threshold_pct:
        return True, "SELL", abs(cumulative)
    return False, "", 0.0


def scan_lead_lag(
    frames: dict[str, pd.DataFrame],
    *,
    leader_symbol: str = "BTCUSDC",
    max_lag: int = 20,
    btc_move_lookback: int = 10,
    btc_move_threshold: float = 1.5,
    min_correlation: float = 0.3,
    min_confidence: float = 0.3,
    lookback_window: int = 500,
) -> list[LeadLagSignal]:
    """Scan all pairs for lead/lag signals based on BTC moves.

    Args:
        frames: dict of symbol -> DataFrame with columns [open, high, low, close].
        leader_symbol: the leading asset (usually BTC).
        max_lag: maximum lag to check (bars).
        btc_move_lookback: bars to look back for BTC move.
        btc_move_threshold: minimum % move to trigger.
        min_correlation: minimum correlation to consider a lead/lag relationship.
        min_confidence: minimum confidence to emit a signal.
        lookback_window: bars to use for lead/lag estimation.

    Returns:
        List of LeadLagSignal, sorted by confidence descending.
    """
    signals: list[LeadLagSignal] = []

    # Find BTC frame
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
    btc_recent = btc_returns.iloc[-lookback_window:]

    # Check if BTC made a significant move
    has_move, move_dir, move_mag = _detect_btc_move(
        btc_returns, btc_move_lookback, btc_move_threshold
    )

    if not has_move:
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
        # ATR floor: prevent tiny ATR from causing max leverage in low-vol periods
        cur_atr = max(cur_atr, cur_close * 0.005)

        # Timestamp-align returns to avoid positional mismatch when frames
        # have different start times or counts.
        btc_starts = btc_frame["start"] if "start" in btc_frame.columns else btc_frame.index
        alt_starts = df["start"] if "start" in df.index or "start" in df.columns else df.index
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

        # Align returns to lookback window, excluding recent trigger move
        # to avoid correlation contamination from the move itself.
        alt_recent = alt_ret.iloc[-lookback_window:-btc_move_lookback] if btc_move_lookback > 0 else alt_ret.iloc[-lookback_window:]
        btc_corr_recent = btc_ret.iloc[-lookback_window:-btc_move_lookback] if btc_move_lookback > 0 else btc_ret.iloc[-lookback_window:]

        # Find lead/lag relationship
        best_lag, best_corr = _find_lead_lag(btc_corr_recent, alt_recent, max_lag)

        if abs(best_corr) < min_correlation or best_lag < 1:
            continue

        # BTC moved, alt should follow (with the lag)
        # If correlation is positive: BTC up → alt up (BUY), BTC down → alt down (SELL)
        # If correlation is negative: BTC up → alt down (SELL), BTC down → alt up (BUY)
        if best_corr > 0:
            alt_side = move_dir
        else:
            alt_side = "SELL" if move_dir == "BUY" else "BUY"

        # Confidence based on correlation strength and move magnitude
        corr_strength = min(1.0, abs(best_corr) / 0.8)
        mag_strength = min(1.0, move_mag / 10.0)
        lag_penalty = max(0.5, 1.0 - best_lag / max_lag)  # shorter lag = higher confidence

        confidence = (0.4 * corr_strength + 0.3 * mag_strength + 0.3 * lag_penalty)

        # Edge: expected move magnitude * fraction that's still ahead
        # The BTC move already happened; the alt hasn't moved yet
        bars_since_move = btc_move_lookback
        if best_lag > bars_since_move:
            # Alt hasn't moved yet — full edge
            edge_fraction = 1.0
        else:
            # Alt may have partially moved — reduced edge
            edge_fraction = max(0.1, (best_lag - bars_since_move + best_lag) / best_lag)

        edge_bps = max(1.0, move_mag * 100 * edge_fraction * 0.3)

        stop_distance = 2.0 * cur_atr
        if alt_side == "BUY":
            stop = cur_close - stop_distance
        else:
            stop = cur_close + stop_distance

        if confidence >= min_confidence:
            signals.append(LeadLagSignal(
                pair=symbol,
                side=alt_side,
                entry_price=cur_close,
                stop_price=stop,
                atr=cur_atr,
                edge=edge_bps,
                confidence=min(1.0, confidence),
                horizon_bars=best_lag,
                signal_type="btc_lead",
                regime_fit=0.7,  # works in all regimes
                leader=leader_symbol,
            ))

    return sorted(signals, key=lambda s: -s.confidence)


def scan_pairs_divergence(
    frames: dict[str, pd.DataFrame],
    *,
    correlation_window: int = 100,
    divergence_threshold: float = 2.0,
    min_correlation: float = 0.6,
    min_confidence: float = 0.3,
) -> list[LeadLagSignal]:
    """Find pairs that are normally correlated but have diverged.

    When two correlated assets diverge beyond normal, trade the convergence.
    This is a pairs trading / statistical arbitrage approach.
    """
    signals: list[LeadLagSignal] = []

    symbols = [s for s, df in frames.items() if df is not None and len(df) > correlation_window + 50]
    if len(symbols) < 2:
        return signals

    # Precompute returns for all symbols
    returns = {}
    closes = {}
    atrs = {}
    for sym in symbols:
        df = frames[sym]
        close = df["close"].astype(float)
        returns[sym] = close.pct_change()
        closes[sym] = close
        atrs[sym] = float(_atr(df["high"].astype(float), df["low"].astype(float), close).iloc[-1])

    # Check all pairs
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            sym_a, sym_b = symbols[i], symbols[j]

            ret_a = returns[sym_a].iloc[-correlation_window:]
            ret_b = returns[sym_b].iloc[-correlation_window:]

            mask = ret_a.notna() & ret_b.notna()
            if mask.sum() < 50:
                continue

            corr = float(ret_a[mask].corr(ret_b[mask]))
            if abs(corr) < min_correlation:
                continue

            # Compute z-score of spread
            close_a = closes[sym_a]
            close_b = closes[sym_b]

            # Normalize prices to compare
            norm_a = close_a / close_a.iloc[-correlation_window]
            norm_b = close_b / close_b.iloc[-correlation_window]
            spread = norm_a - norm_b
            spread_mean = spread.iloc[-correlation_window:].mean()
            spread_std = spread.iloc[-correlation_window:].std()

            if spread_std <= 0:
                continue

            zscore = float((spread.iloc[-1] - spread_mean) / spread_std)

            if abs(zscore) < divergence_threshold:
                continue

            # Z-score > threshold: A is expensive relative to B
            # Trade: sell A, buy B (convergence)
            # But we emit as individual signals per pair
            cur_atr_a = atrs[sym_a]
            cur_atr_b = atrs[sym_b]

            if cur_atr_a <= 0 or cur_atr_b <= 0:
                continue

            extremity = min(1.0, (abs(zscore) - divergence_threshold) / divergence_threshold)
            confidence = 0.4 + 0.3 * extremity + 0.2 * min(1.0, abs(corr) / 0.8)

            edge_bps = max(1.0, abs(zscore) * 15)  # ~15 bps per z-score unit

            # Signal for sym_a: if zscore > 0, A is expensive → SELL A
            # Signal for sym_b: if zscore > 0, B is cheap → BUY B
            if zscore > 0:
                signals.append(LeadLagSignal(
                    pair=sym_a,
                    side="SELL",
                    entry_price=float(closes[sym_a].iloc[-1]),
                    stop_price=float(closes[sym_a].iloc[-1]) + 2.0 * cur_atr_a,
                    atr=cur_atr_a,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=20,
                    signal_type="pairs_divergence",
                    regime_fit=0.5,
                    leader=sym_b,
                ))
                signals.append(LeadLagSignal(
                    pair=sym_b,
                    side="BUY",
                    entry_price=float(closes[sym_b].iloc[-1]),
                    stop_price=float(closes[sym_b].iloc[-1]) - 2.0 * cur_atr_b,
                    atr=cur_atr_b,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=20,
                    signal_type="pairs_divergence",
                    regime_fit=0.5,
                    leader=sym_a,
                ))
            else:
                signals.append(LeadLagSignal(
                    pair=sym_a,
                    side="BUY",
                    entry_price=float(closes[sym_a].iloc[-1]),
                    stop_price=float(closes[sym_a].iloc[-1]) - 2.0 * cur_atr_a,
                    atr=cur_atr_a,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=20,
                    signal_type="pairs_divergence",
                    regime_fit=0.5,
                    leader=sym_b,
                ))
                signals.append(LeadLagSignal(
                    pair=sym_b,
                    side="SELL",
                    entry_price=float(closes[sym_b].iloc[-1]),
                    stop_price=float(closes[sym_b].iloc[-1]) + 2.0 * cur_atr_b,
                    atr=cur_atr_b,
                    edge=edge_bps,
                    confidence=min(1.0, confidence),
                    horizon_bars=20,
                    signal_type="pairs_divergence",
                    regime_fit=0.5,
                    leader=sym_a,
                ))

    return sorted(signals, key=lambda s: -s.confidence)
