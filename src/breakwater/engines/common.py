"""Shared signal type for all engines."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Signal:
    """A trade signal from any engine."""

    symbol: str
    side: str  # "BUY" or "SELL"
    engine: str  # which engine produced this
    horizon_bars: int
    expected_edge: float  # estimated edge per bar (fraction, e.g. 0.005 = 50 bps)
    confidence: float  # 0-1, how confident the engine is
    regime_fit: float  # 0-1, how well signal fits current regime
    stop_atr_mult: float = 2.0
    reason: str = ""

    @property
    def score(self) -> float:
        """Combined score for ranking."""
        return self.expected_edge * self.confidence * self.regime_fit
