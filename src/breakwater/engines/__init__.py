"""Multi-engine signal generation for Breakwater.

Each engine specializes in one type of trading edge:
- engine_factor: Statistical/factor-based (current pipeline)
- engine_momentum: Trend following
- engine_mean_reversion: RSI/Bollinger/z-score reversion
- engine_cross_asset: BTC leads, alts follow

All engines implement the same interface:
    def generate(df: pd.DataFrame, ...) -> list[Signal]
"""
