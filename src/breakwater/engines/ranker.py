"""Meta-Ranker: Combines signals from all engines and selects the top N.

Each engine produces signals with confidence, edge, and regime_fit.
The meta-ranker scores them and picks the best across all engines.

score = expected_edge × confidence × regime_fit × data_freshness

This naturally diversifies across strategies — if momentum fails in a bear,
mean reversion and lead-lag engines compensate.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

import pandas as pd


class Signal(Protocol):
    """Protocol that all engine signals must satisfy."""
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


@dataclass(frozen=True)
class RankedSignal:
    """A signal with its meta-rank score."""
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
    engine: str  # which engine produced it
    score: float  # meta-rank score


def _data_freshness(signal: Signal) -> float:
    """Estimate how fresh/relevant the signal's data is.

    Shorter horizon = fresher. Longer horizon = more time for regime to change.
    """
    h = max(1, signal.horizon_bars)
    # 1 bar = 1.0 freshness, 50 bars = 0.5 freshness
    return max(0.1, 1.0 / (1.0 + h / 50.0))


def rank_signals(
    engine_signals: dict[str, list[Signal]],
    *,
    max_signals: int = 20,
    regime: str = "unknown",
) -> list[RankedSignal]:
    """Rank signals from all engines and return the top N.

    Args:
        engine_signals: dict of engine_name -> list of signals.
        max_signals: maximum number of signals to return.
        regime: current market regime (adjusts regime_fit).

    Returns:
        Top N RankedSignals sorted by score descending.
    """
    all_ranked: list[RankedSignal] = []

    for engine_name, signals in engine_signals.items():
        for sig in signals:
            # Adjust regime_fit based on current regime
            adjusted_regime_fit = sig.regime_fit
            if regime == "bear" and sig.side == "BUY":
                # Penalize longs in bear (but don't zero — engine may have reason)
                adjusted_regime_fit *= 0.5
            elif regime == "bull" and sig.side == "SELL":
                # Penalize shorts in bull
                adjusted_regime_fit *= 0.5

            freshness = _data_freshness(sig)
            score = sig.edge * sig.confidence * adjusted_regime_fit * freshness

            all_ranked.append(RankedSignal(
                pair=sig.pair,
                side=sig.side,
                entry_price=sig.entry_price,
                stop_price=sig.stop_price,
                atr=sig.atr,
                edge=sig.edge,
                confidence=sig.confidence,
                horizon_bars=sig.horizon_bars,
                signal_type=sig.signal_type,
                regime_fit=adjusted_regime_fit,
                engine=engine_name,
                score=score,
            ))

    # Sort by score descending, deduplicate by pair+side
    all_ranked.sort(key=lambda s: -s.score)

    seen: set[tuple[str, str]] = set()
    result: list[RankedSignal] = []
    for sig in all_ranked:
        key = (sig.pair, sig.side)
        if key in seen:
            continue
        seen.add(key)
        result.append(sig)
        if len(result) >= max_signals:
            break

    return result
