# Breakwater Handover

## Critical Context

**Breakwater will never be green with one engine.** The current system uses a single statistical/factor-based discovery pipeline that pattern-matches on historical price features. It fails because:
- Patterns get arbitraged away in reflexive crypto markets
- The system has NO SHORT edges for native crypto
- LONG edges fail validation in bear markets (last fold always negative)
- It's curve-fitting, not understanding why assets move

**The fix: multi-engine architecture.** Multiple specialized engines, each producing signals based on a different methodology. A meta-ranker selects the top 20. This is how professional quant funds work.

## Current System Status (2026-09-15)

| Metric | Value |
|--------|-------|
| Native PERP P&L | -2.05 ZAR (28 trades, 14W/14L) |
| HIP-3 P&L | +1.64 ZAR (37 trades, 26W/11L) |
| Combined P&L | -0.41 ZAR |
| Market Regime | Bear (56.67% bear breadth, 5 consecutive bear bars) |
| Native Book | Restored 5-fold validated slices (from old proven run) |
| Fresh Research | 0 validated (bear killed last fold for all LONG candidates) |
| Code | FOLD_COUNT=5, NaN fix active, timeout=60min |

## What Happened

### Timeline
1. System was at +31 ZAR with 36 proven slices (5-fold validation, all LONG)
2. We made code changes that broke the system:
   - FOLD_COUNT: 5→3 (let marginal slices through, lost ~31 ZAR)
   - BREADTH_MIN_SYMBOLS: 10→6 (less strict)
   - BREADTH_MIN_POSITIVE_FRACTION: 0.55→0.50 (less strict)
   - Trailing validation OFF by default
3. The NaN fix was correct but caused book turnover — old proven slices replaced by new unproven ones
4. We restored the old code defaults (FOLD_COUNT=5, etc.) and the old book
5. Fresh 5-fold research ran but validated 0 slices — bear market killed the last fold for all LONG candidates

### Key Bugs Fixed
| Commit | Fix |
|--------|-----|
| `3f910900` | NaN contamination: `valid = np.isfinite(val_values)` (was `net_values`) |
| `dd8629e` | Trailing validation OFF by default |
| `3d35b77` | STRICT_PASS_FLOOR scales with FOLD_COUNT |
| `839916d` | Empty counterfactual log handled |
| `ea766e0` | MIN_GREEN_ASSETS 3→2 (HIP-3 book fix) |
| `983dac0` | Restored FOLD_COUNT=5, BREADTH=10, BREADTH_FRAC=0.55 |

### YAML Overrides (unchanged, match old proven run)
```yaml
BREAKWATER_VALIDATION_REQUIRE_BONFERRONI: "0"
BREAKWATER_VALIDATION_RELAXED_MIN_PASSES: "2"
BREAKWATER_BREADTH_MIN_SYMBOLS: "6"
BREAKWATER_BREADTH_MIN_POSITIVE_FRACTION: "0.40"
```

## Multi-Engine Architecture

### Why Multiple Engines
One engine = one point of failure. If the statistical engine can't find edges in a bear market, the system sits idle. Multiple engines ensure there's always something trading.

### Engine Roadmap

#### Phase 1: Price-Only Engines (can build now)

**Engine 1: Factor/Statistical (current pipeline)**
- Keep as-is with restored 5-fold validation
- Status: working but produces 0 validated slices in bear market

**Engine 2: Momentum/Trend Following**
- Don't predict, react. If an asset has been trending for N bars, enter in that direction.
- Features: SMA crossovers (50/200), breakout above N-bar high, ADX for trend strength
- Works in trending markets, gets chopped in ranging (use regime detector to enable/disable)
- Status: TO BUILD

**Engine 3: Mean Reversion**
- Assets that deviate far from their mean tend to revert.
- Features: RSI extremes (<30 oversold, >70 overbought), Bollinger band bounces, z-score of price vs 20-SMA
- Works in ranging markets, gets destroyed in trends (use regime detector to enable/disable)
- Status: TO BUILD

**Engine 4: Cross-Asset Lead/Lag**
- BTC often leads, alts follow with a lag. That lag is tradeable.
- Method: Granger causality or transfer entropy between BTC and each alt. Measure lag in bars. When BTC moves, enter alts that historically follow.
- Also: pairs trading — if two assets are normally correlated and diverge, trade the convergence.
- Status: TO BUILD

#### Phase 2: Crypto-Native Engines (need new data)

**Engine 5: Funding Rate**
- When perpetual funding rate is extreme (>0.1%), it's a crowded trade. Short perp + long spot collects funding and profits on reversion.
- Data needed: VALR/Hyperliquid funding rate API
- Edge: structural, not statistical — based on market mechanics

**Engine 6: Liquidation Cascade**
- When mass liquidations happen, price overshoots. Buy the cascade, sell the bounce.
- Data needed: Coinglass or similar liquidation feed
- Edge: structural — forced selling creates predictable price dislocations

**Engine 7: On-Chain Flow**
- Whale deposits to exchange = about to sell. Withdrawals = about to hold.
- Data needed: Glassnode, CryptoQuant, or direct blockchain node
- Edge: information advantage — you see whale moves before they hit the order book

**Engine 8: Sentiment/Social**
- Social media volume, Fear & Greed index, Reddit/CT mentions
- Contrarian: extreme fear = buy, extreme greed = sell
- Data needed: LunarCrush, Santiment, or similar

### Meta-Ranker Design
Each engine returns signals with:
- `expected_edge`: estimated edge per bar (bps)
- `confidence`: how confident the engine is (0-1)
- `regime_fit`: how well the signal fits the current regime (0-1)
- `data_freshness`: how recent the supporting data is (0-1)

Meta-ranker formula: `score = expected_edge × confidence × regime_fit × data_freshness`

Top 20 signals by score are selected for paper/live trading.

### Regime-Conditional Activation
Not all engines should run in all regimes:
- **Trending**: momentum ON, mean reversion OFF
- **Ranging**: momentum OFF, mean reversion ON
- **Bear**: funding rate ON (short crowded longs), on-chain ON (whale deposits = sell signal)
- **Bull**: all engines ON

## Open Items

### Critical
- [ ] Build Engine 2 (Momentum/Trend)
- [ ] Build Engine 3 (Mean Reversion)
- [ ] Build Engine 4 (Cross-Asset Lead/Lag)
- [ ] Build Meta-Ranker to combine engines

### Important
- [ ] Source funding rate data for Engine 5
- [ ] Fix Guardian cron cadence (currently every 30 min, should be 60 min)
- [ ] Add SHORT edges for native crypto (either via engines or new features)

### Nice to Have
- [ ] On-chain data integration (Engine 7)
- [ ] Sentiment data integration (Engine 8)
- [ ] Liquidation data integration (Engine 6)

## Architecture Notes

### Current Pipeline
```
Discovery → Validation → Book Sync → Paper Trading
   ↓            ↓            ↓            ↓
Features    Walk-forward   Monitored    Signals
candidates  fold check     slices       → Positions
```

### Proposed Pipeline
```
Engine 1 (Factor)     ─┐
Engine 2 (Momentum)   ─┤
Engine 3 (Mean Rev)   ─┤→ Meta-Ranker → Top 20 → Paper Trading
Engine 4 (Cross-Asset)─┤
Engine 5 (Funding)    ─┘
```

### Key Files
- `src/breakwater/validation.py` — Walk-forward validation (current)
- `src/breakwater/paper_trade.py` — Paper trading engine
- `src/breakwater/monitor.py` — Book monitoring and signal generation
- `src/breakwater/regime_tracker.py` — Regime detection and gating
- `src/breakwater/research_lifecycle.py` — Book sync and promotion
- `.github/workflows/research.yml` — Native research CI
- `.github/workflows/hip3-research.yml` — HIP-3 research CI
- `.github/workflows/paper.yml` — Paper trading CI (hourly, 60min timeout)

### Environment Variables
See `.github/workflows/paper.yml` for full list. Key ones:
- `BREAKWATER_MODE`: shadow (paper) or live
- `BREAKWATER_GREEN_GATE`: 1 (on)
- `BREAKWATER_PAPER_MAX_BOOK_SLICES`: 20
- `BREAKWATER_PAPER_SESSIONS`: eu,us
- `BREAKWATER_TRAIL_ENABLE`: 1 (trailing stops on)
