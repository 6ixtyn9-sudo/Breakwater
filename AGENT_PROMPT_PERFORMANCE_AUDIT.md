# Audit: Paper Trading Performance — Why Is Everything Red?

## Context

The system has been running paper trading since Sep 14. The results are ugly:

```
TOTAL: -32.19 ZAR | 131 trades
  HIP-3:    +6.11 ZAR | 36W/17L (68% WR) | 53 trades  ← ONLY green lane
  Native:  -22.69 ZAR | 28W/38L (42% WR) | 66 trades
  Engine:  -15.61 ZAR |  5W/7L  (42% WR) | 12 trades
```

HIP-3 is carrying the system. Native and engines are bleeding.

## Detailed Breakdown

### Native Lane: Where the Money Dies

**By regime × side:**
```
  bull  BUY:  -11.04 ZAR ( 7 trades)  ← buying at tops
neutral  BUY:  -11.02 ZAR (24 trades)  ← overtrading in chop
neutral SELL:   -6.21 ZAR (17 trades)
   bear  BUY:   +2.51 ZAR (42 trades)  ← actually profitable
   bear SELL:   +4.34 ZAR (18 trades)
   bull  SELL:   +4.84 ZAR (11 trades)
```

**By exit reason:**
```
        stop: -25.89 ZAR ( 9 trades)  ← biggest single drain
regime_shift:  -9.59 ZAR (36 trades)  ← chopped by regime flips
     horizon:  -0.69 ZAR ( 8 trades)
  trail_stop:  +1.02 ZAR ( 1 trade)
   slice_gap:  +2.31 ZAR (54 trades)  ← lots of churn, breakeven
      target: +16.26 ZAR (11 trades)  ← when it hits, it hits
```

**By side:**
```
  BUY: -19.54 ZAR (73 trades)  ← LONG bias is killing it
 SELL:  +2.96 ZAR (46 trades)
```

**Key observations:**
1. BUY side is -19.54 ZAR. Longs are a net negative. The book is heavily LONG-biased.
2. Neutral regime (41 trades, -17.23 ZAR) is the worst regime. Overtrading in chop.
3. `regime_shift` exit (36 trades, -9.59 ZAR) — positions are getting regime-chopped. Opening and then the regime flips.
4. `stop` exit (9 trades, -25.89 ZAR) — few stops but massive damage per stop. Avg -2.88 ZAR per stop hit.
5. Bear regime is actually GREEN (+6.85 ZAR combined BUY+SELL).

### Engine Lane: Mean Reversion is Dead

```
mean_reversion: -14.29 ZAR (2W/4L, 33% WR)
      momentum:  -1.32 ZAR (3W/3L, 50% WR)
```

mean_reversion is the worst engine. Only 6 trades but -14.29 ZAR. Two of those trades likely had oversized risk (the pre-fix 2x ATR stops). Recent fixes (hostile_unproven, stop tightening, BUY penalty in bear) should help but haven't been tested yet.

### Risk Distribution

```
risk_fraction: min=0.003 median=0.025 max=0.060 mean=0.030
>3% risk: 61 trades (47% of all trades!)
>5% risk: 20 trades
```

Almost half the trades risk more than 3% of the book. 20 trades risk 5-6%. This is too aggressive for a R2000 book — one bad stop can lose R100+.

### Validated Slices: 7,488 slices, ALL LONG, ALL h1-h24

The validated slice pool has 7,488 entries across 26 feature families. **Every single one is LONG (BUY).** There are a few SHORT entries at higher horizons. This means:
- The book is structurally LONG-biased
- In a bear or neutral regime, most slices are fighting the trend
- SHORT edges are almost non-existent in the validated pool

### HIP-3: Why Is It Green?

HIP-3 has 68% WR across 53 trades. It's the only lane making money. Why?
- Different signal source (pair equity correlation)
- Shorter holding periods
- Less regime-chopped
- Or just lucky on a small sample

## What I Need You to Audit

### P0: Why are native longs bleeding?

The system has a massive LONG bias (73 BUY vs 46 SELL). BUY in bull is -11.04, BUY in neutral is -11.02. Only BUY in bear is green. **The system is buying at tops and in choppy markets.**

Specific questions:
1. Is the regime gate actually blocking BUY in neutral? It shows -11.02 ZAR on 24 trades, so it seems like it's not.
2. Why is `regime_shift` exit -9.59 ZAR? Are positions opening right before a regime flip? Is there a lag issue?
3. Why are stops -25.89 ZAR on only 9 trades? That's -2.88 per stop. Is the stop distance still too wide?
4. The book is 7,488 validated slices, ALL LONG. Should SHORT edges be weighted higher to balance the book?

### P1: Risk management

47% of trades risk >3%. The 3% cap is supposed to be enforced. Why are trades getting through with 5-6% risk?

### P2: Engine viability

Should engines be disabled entirely until more data? mean_reversion is -14.29 on 6 trades. momentum is -1.32 on 6 trades. Is 12 trades enough to judge, or should we wait for 50+?

### P3: Feature homogeneity

26 feature families, all based on the same underlying data (returns, RSI, ATR, volume, moving averages). Should we add fundamentally different features (funding rate, order book depth, cross-pair correlation, on-chain metrics)?

## Files to Review

- `src/breakwater/paper_trade.py` — main paper trading loop
- `src/breakwater/regime_tracker.py` — regime detection, gate, defensive_exit
- `src/breakwater/ranker.py` — signal ranking and dedup
- `src/breakwater/engine.py` — engine signal generation
- `src/breakwater/engines/momentum.py` — momentum engine
- `src/breakwater/engines/mean_reversion.py` — mean reversion engine
- `src/breakwater/features.py` — feature computation
- `src/breakwater/research_lifecycle.py` — research pipeline
- `src/breakwater/validation.py` — temporal validation
- `localdata/research/paper_trade_log.csv` — all paper trades
- `localdata/research/validated_slices.csv` — 7,488 validated slices

## Constraints

- All fixes go to `main` branch
- R2000 book, need R10/week to be meaningful
- No workflow YAML changes (user handles those)
- Don't disable engines entirely — improve them
- Be ruthless, be precise, fix everything
