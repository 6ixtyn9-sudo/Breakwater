"""Breakwater Multi-Engine Discovery.

Multiple specialized engines, each producing signals based on a different
methodology. A meta-ranker selects the top 20.

Engines:
  1. Factor/Statistical (existing pipeline in validation.py)
  2. Momentum/Trend (momentum.py)
  3. Mean Reversion (mean_reversion.py)
  4. Cross-Asset Lead/Lag (lead_lag.py)
  5-8. TODO: Funding Rate, Liquidation, On-Chain, Sentiment
"""

from breakwater.engines.momentum import MomentumSignal, scan_momentum
from breakwater.engines.mean_reversion import MeanReversionSignal, scan_mean_reversion
from breakwater.engines.lead_lag import LeadLagSignal, scan_lead_lag, scan_pairs_divergence
from breakwater.engines.ranker import RankedSignal, rank_signals

__all__ = [
    "MomentumSignal",
    "MeanReversionSignal",
    "LeadLagSignal",
    "RankedSignal",
    "scan_momentum",
    "scan_mean_reversion",
    "scan_lead_lag",
    "scan_pairs_divergence",
    "rank_signals",
]
