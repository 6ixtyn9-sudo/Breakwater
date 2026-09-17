"""Meta-Ranker — FIXED Sep 17 data-driven.

Fixes:
- LONG only: SHORT 0 edge in 7488 discovered, SELL -37 ZAR
- Boost long horizon: discovery h24 +87 bps best, paper h15-h19 winners, old freshness penalized long
- Boost profitable pairs: ARB +7.76, TAO +5.69, SUI +5.47
- Min edge 20 bps, confidence 0.4 already filtered in engines, ranker double-checks
- Regime: penalize SELL in bull heavily (0.1x not 0.5x), BUY in bear 0.1x
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class Signal(Protocol):
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
    engine: str
    score: float


def _data_freshness(signal: Signal) -> float:
    """Data-driven: long horizon is BETTER (h24 +87 bps), not worse.

    Old formula: 1/(1+h/100) penalized long horizon, crowding out momentum.
    New: boost h15-24, neutral for h10-14, slight penalty only for h<5 or h>30.
    """
    h = max(1, signal.horizon_bars)
    if 15 <= h <= 24:
        return 1.2  # Boost winners
    if 10 <= h <= 14:
        return 1.0
    if 5 <= h <= 9:
        return 0.8
    return 0.6


def rank_signals(
    engine_signals: dict[str, list[Signal]],
    *,
    max_signals: int = 3,
    regime: str = "unknown",
) -> list[RankedSignal]:
    """Rank LONG only signals, boost profitable pairs and long horizon."""
    all_ranked: list[RankedSignal] = []

    # Profitable pairs from paper log
    top_pairs = {"ARBUSDC", "TAOUSDC", "SUIUSDC", "BNBUSDC", "SOLUSDC", "XPLUSDC", "UNIUSDC"}
    top_pairs_boost = 1.3

    for engine_name, signals in engine_signals.items():
        for sig in signals:
            # FIXED: LONG only
            if sig.side != "BUY":
                continue
            # Min edge 20 bps double-check
            if sig.edge < 20.0:
                continue
            if sig.confidence < 0.4:
                continue

            adjusted_regime_fit = sig.regime_fit
            if regime == "bear" and sig.side == "BUY":
                adjusted_regime_fit *= 0.1  # Was 0.5, now 0.1 — hard block BUY in bear
            elif regime == "bull" and sig.side == "SELL":
                adjusted_regime_fit *= 0.1  # Was 0.5, now 0.1

            # Pair boost
            pair_boost = top_pairs_boost if sig.pair in top_pairs else 1.0

            freshness = _data_freshness(sig)
            score = sig.edge * sig.confidence * adjusted_regime_fit * freshness * pair_boost

            all_ranked.append(RankedSignal(
                pair=sig.pair, side=sig.side, entry_price=sig.entry_price,
                stop_price=sig.stop_price, atr=sig.atr, edge=sig.edge,
                confidence=sig.confidence, horizon_bars=sig.horizon_bars,
                signal_type=sig.signal_type, regime_fit=adjusted_regime_fit,
                engine=engine_name, score=score,
            ))

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
