"""Meta-Ranker: combines signals from all engines, selects top N.

Each engine produces signals with expected_edge, confidence, and regime_fit.
The meta-ranker scores them and picks the best ones for trading.
"""
from __future__ import annotations

from breakwater.engines.common import Signal


def rank_signals(
    signals: list[Signal],
    *,
    max_signals: int = 20,
    min_score: float = 0.001,
    max_per_symbol: int = 2,
    max_per_engine: int = 8,
) -> list[Signal]:
    """Rank and filter signals from all engines.

    Args:
        signals: combined signals from all engines
        max_signals: maximum number of signals to return
        min_score: minimum score threshold
        max_per_symbol: max signals per symbol (prevent concentration)
        max_per_engine: max signals per engine (ensure diversification)

    Returns:
        Top N signals sorted by score descending
    """
    # Filter by minimum score
    qualified = [s for s in signals if s.score >= min_score]

    # Sort by score descending
    qualified.sort(key=lambda s: -s.score)

    # Apply per-symbol and per-engine caps
    symbol_count: dict[str, int] = {}
    engine_count: dict[str, int] = {}
    selected: list[Signal] = []

    for signal in qualified:
        if len(selected) >= max_signals:
            break

        sym = symbol_count.get(signal.symbol, 0)
        eng = engine_count.get(signal.engine, 0)

        if sym >= max_per_symbol:
            continue
        if eng >= max_per_engine:
            continue

        selected.append(signal)
        symbol_count[signal.symbol] = sym + 1
        engine_count[signal.engine] = eng + 1

    return selected


def score_summary(signals: list[Signal]) -> dict:
    """Summary stats for a list of signals (for logging/debugging)."""
    if not signals:
        return {"total": 0}

    engines: dict[str, int] = {}
    for s in signals:
        engines[s.engine] = engines.get(s.engine, 0) + 1

    return {
        "total": len(signals),
        "engines": engines,
        "avg_score": sum(s.score for s in signals) / len(signals),
        "avg_confidence": sum(s.confidence for s in signals) / len(signals),
        "buys": sum(1 for s in signals if s.side == "BUY"),
        "sells": sum(1 for s in signals if s.side == "SELL"),
    }
