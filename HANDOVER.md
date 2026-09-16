# Breakwater Handover

## Critical Context

**Breakwater will never be green with one engine.** The current system uses a single statistical/factor-based discovery pipeline that pattern-matches on historical price features. It fails because:
- Patterns get arbitraged away in reflexive crypto markets
- The system has NO SHORT edges for native crypto
- LONG edges fail validation in bear markets (last fold always negative)
- It's curve-fitting, not understanding why assets move

**The fix: multi-engine architecture.** Multiple specialized engines, each producing signals based on a different methodology. A meta-ranker selects the top 20. This is how professional quant funds work.

## Current System Status (2026-09-16)

| Metric | Value |
|--------|-------|
| Native PERP P&L | -15.87 ZAR (54 trades, 23W/31L) 🔴 |
| HIP-3 P&L | +8.64 ZAR (44 trades, 33W/11L) 🟢 |
| Engine P&L | -1.03 ZAR (3 trades, 0W/3L) — just started |
| Combined P&L | -8.26 ZAR (101 trades) |
| Market Regime | Bear |
| Native Book | Purged zombies, waiting for fresh research |
| Fresh Research | 157 validated (floor lowered to 0.002, was blocking at 0.004) |
| HIP-3 Book | 18 fresh slices (PARA equity shorts 1-1.8% edges) |
| Engines | Firing! 3 trades (engine_mean_reversion:rsi) |
| Features | 26 total (16 old + 10 new: volume, RSI, structure, momentum, session) |

## What Happened

### Session 1 (2026-09-15)
1. System was at +31 ZAR with 36 proven slices (5-fold validation, all LONG)
2. We made code changes that broke the system:
   - FOLD_COUNT: 5→3 (let marginal slices through, lost ~31 ZAR)
   - BREADTH_MIN_SYMBOLS: 10→6 (less strict)
   - BREADTH_MIN_POSITIVE_FRACTION: 0.55→0.50 (less strict)
   - Trailing validation OFF by default
3. The NaN fix was correct but caused book turnover — old proven slices replaced by new unproven ones
4. We restored the old code defaults (FOLD_COUNT=5, etc.) and the old book
5. Fresh 5-fold research ran but validated 0 slices — bear market killed the last fold for all LONG candidates

### Session 2 (2026-09-16)
1. **Engine signals were 0** — session gate in `_run_engines()` blocked engines during Asia hours. Removed.
2. **Native lane was -15.87 ZAR** — trading 9 zombie slices with decayed edges (current research showed negative, book stored positive from promotion time)
3. **Research validated 0 slices** — 157 candidates found but all below 0.004 promotion floor. Lowered to 0.002.
4. **Carry-forward bug** — `sync_book._carry_eligible()` used stale promotion-time edge values. Fixed to use current research.
5. **10 new feature families** — volume, RSI, price structure, momentum persistence, session awareness (total: 26 features)
6. **Temporal pass relaxation** — edges with 4/5+ fold passes skip recency gate (was double-penalizing)

### Key Bugs Fixed
| Commit | Fix |
|--------|-----|
| `3f910900` | NaN contamination: `valid = np.isfinite(val_values)` (was `net_values`) |
| `dd8629e` | Trailing validation OFF by default |
| `3d35b77` | STRICT_PASS_FLOOR scales with FOLD_COUNT |
| `839916d` | Empty counterfactual log handled |
| `ea766e0` | MIN_GREEN_ASSETS 3→2 (HIP-3 book fix) |
| `983dac0` | Restored FOLD_COUNT=5, BREADTH=10, BREADTH_FRAC=0.55 |
| `f3883e2` | Engine session gate removed, thresholds lowered to 0.001, fallback_sma added |
| `8bbd390` | 10 new feature families + temporal_pass relaxation (4/5+ skips recency) |
| `9b53867` | carry-forward uses current research edge, not stale promotion value |
| Manual | BREAKWATER_MIN_NET_EDGE 0.004→0.002 |
| Manual | BREAKWATER_PAPER_SESSIONS removed (all sessions enabled) |

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

#### Phase 1: Price-Only Engines (BUILT AND RUNNING)

**Engine 1: Factor/Statistical (current pipeline)**
- Keep as-is with restored 5-fold validation
- Status: working, 157 validated with new features + relaxed temporal

**Engine 2: Momentum/Trend Following**
- Don't predict, react. If an asset has been trending for N bars, enter in that direction.
- Features: SMA crossovers (50/200), breakout above N-bar high, ADX for trend strength
- Works in trending markets, gets chopped in ranging (use regime detector to enable/disable)
- Status: BUILT — ADX threshold 18, trend_align + sma_cross + breakout signals

**Engine 3: Mean Reversion**
- Assets that deviate far from their mean tend to revert.
- Features: RSI extremes (<35 oversold, >65 overbought), Bollinger band bounces (1.8σ), z-score (1.5)
- Works in ranging markets, gets destroyed in trends (use regime detector to enable/disable)
- Status: BUILT — 3 paper trades so far (all small losses, too early to judge)

**Engine 4: Cross-Asset Lead/Lag**
- BTC often leads, alts follow with a lag. That lag is tradeable.
- Method: correlation-based lead-lag with BTC move threshold 1.5% in 10 bars
- Status: BUILT — waiting for BTC to make a move

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
- [ ] Monitor first research run with all fixes (26 features, 0.002 floor, carry-fix)
- [ ] Judge engine quality after 50+ trades
- [ ] Fix stop exits (-22.42 ZAR from 7 stop-outs — biggest drain)
- [ ] Build Meta-Ranker to combine engines
- [ ] Investigate regime_shift exit churning (-4.08 ZAR, 26 trades)

### Important
- [ ] Source funding rate data for Engine 5
- [ ] Add SHORT edges for native crypto (engines may handle this)
- [ ] Keep research running daily — zombie slices happen when research goes stale

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
- `src/breakwater/features.py` — 26 features (16 price-extension + 10 new: volume, RSI, structure, momentum, session)
- `src/breakwater/validation.py` — Walk-forward validation, temporal_pass relaxation
- `src/breakwater/paper_trade.py` — Paper trading engine, green gate bypass for engines
- `src/breakwater/monitor.py` — Book monitoring and signal generation
- `src/breakwater/regime_tracker.py` — Regime detection and gating
- `src/breakwater/research_lifecycle.py` — Book sync, promotion, carry-forward fix
- `src/breakwater/engine.py` — shadow_scan(), _run_engines() (session gate removed)
- `src/breakwater/engines/simple_trend.py` — fallback_sma, 0.1% thresholds
- `.github/workflows/research.yml` — Native research CI (360min timeout)
- `.github/workflows/hip3-research.yml` — HIP-3 research CI
- `.github/workflows/paper.yml` — Paper trading CI (hourly, 90min timeout)

### Environment Variables
See `.github/workflows/paper.yml` for full list. Key ones:
- `BREAKWATER_MODE`: shadow (paper) or live
- `BREAKWATER_GREEN_GATE`: 1 (on)
- `BREAKWATER_PAPER_MAX_BOOK_SLICES`: 20
- `BREAKWATER_PAPER_SESSIONS`: (not set = all sessions, was eu,us)
- `BREAKWATER_TRAIL_ENABLE`: 1 (trailing stops on)
- `BREAKWATER_MIN_NET_EDGE`: 0.002 (was 0.004, GitHub variable)
- `BREAKWATER_MULTI_ENGINE`: 1 (engines always-on)
