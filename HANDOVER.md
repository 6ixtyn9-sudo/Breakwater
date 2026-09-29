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

## Session 2 (2026-09-16)

### Bugs Fixed
| Commit | Fix |
|--------|-----|
| `f3883e2` | Engine session gate removed, thresholds lowered to 0.001, fallback_sma added |
| `8bbd390` | 10 new feature families (volume, RSI, structure, momentum, session) + temporal_pass relaxation |
| `9b53867` | carry-forward uses current research edge, not stale promotion value |
| Manual | BREAKWATER_MIN_NET_EDGE 0.004→0.002 |
| Manual | BREAKWATER_PAPER_SESSIONS removed (all sessions enabled) |

### Status (2026-09-16)
- Native: -15.87 ZAR (54 trades) — was trading 9 zombie slices with decayed edges
- HIP-3: +8.64 ZAR (44 trades) — carrying, PARA equity shorts strong
- Engine: -1.03 ZAR (3 trades) — just started firing
- Combined: -8.26 ZAR (101 trades)
- Fresh research: 157 validated (floor was blocking at 0.004, now 0.002)
- Features: 26 total (16 old + 10 new)
- Engines: all 4 built and running (simple_trend, momentum, mean_reversion, lead_lag)

### Root Causes Found
1. **Engine 0 signals**: session gate in `_run_engines()` blocked engines during Asia hours
2. **Zombie slices**: `sync_book._carry_eligible()` used stale promotion-time edge values
3. **0 validated slices**: promotion floor too high (0.004) for available edges (0.29% max)
4. **Homogeneous features**: all 16 were price-extension variants, added 10 different types

### Key Lesson
**Research must run daily.** Zombie slices happen when research goes stale — edges decay but the book keeps the old positive values. The carry-forward fix helps but regular research is the real solution.

### Updated Open Items
- [ ] Monitor first research run with all fixes
- [ ] Judge engine quality after 50+ trades
- [ ] Fix stop exits (-22.42 ZAR, biggest drain)
- [ ] Build Meta-Ranker
- [ ] Investigate regime_shift churning (-4.08 ZAR, 26 trades)

## Session 3 (2026-09-29) — exit policy: no_target_trail_1r

### What changed and why

The fixed +2R profit target is **retired by default**. The prospective
counterfactual ledger (`localdata/research/paper_counterfactuals.json`,
tracked bar-by-bar, never retrofitted) measured five shadow exit policies
against the live one over 303 comparisons. **All five beat it:**

| policy | shadow P&L | delta vs actual |
|---|---|---|
| `no_target_trail_1r` | +192.50 | **+145.94** ← adopted |
| `target_3r_trail_1r` | +126.00 | +89.27 |
| `target_4r_trail_1r` | +105.66 | +68.93 |
| `target_2r_trail_1r` | +94.40 | +61.75 |
| `no_target_trail_2r` | +113.85 | +28.90 |

The 2R target capped the right tail while the MAE stop let the left tail run
the full distance. Lifetime that shape produced **56 `stop` exits with zero
wins, -214.05 ZAR**, against +561.30 over 65 targets.

### The bug underneath it (this is the important part)

The counterfactual did not beat the live engine only on policy — it beat it
because **the live trailing stop had never once armed for a real book slice.**

`_mark_position_bar` persisted `peak_price` / `trough_price` *inside* the
trailing branch. For a book position (`horizon_bars > 0`) that branch required
`r_gate_on`; `r_gate_on` required `prev_mfe_r >= 1R`; `prev_mfe_r` was computed
from `peak_price` — which only that same branch ever wrote. A closed loop:
peak stayed pinned at the entry price forever, so the gate never opened.

Evidence on committed state before the fix:
- all 7 open positions had `peak_price == trough_price == entry_price`, one of them 21 bars old;
- **126 of the 244 closes held >= 10 bars logged `mfe_r == 0.000000` exactly**;
- the lifetime ledger holds **one** `trail_stop` against 56 `stop`s.

It was not just the trail. `mfe_r`/`mae_r` in the trade log derive from the same
state, so **every excursion diagnostic only ever saw the final bar** — and the
MAE-calibrated per-slice stop distance is the 90th percentile of that
understated adverse excursion. Stops have been sized off one bar of damage
instead of each trade's worst point. Expect stop distances to widen as honest
MAE data accumulates; that is the fix working, not a regression.

Two smaller defects fixed alongside:
- `TRAIL_ENABLE=0` did not disable trailing for r-gated positions (the flag was
  bypassed by `or r_gate_on`). It is now a true master switch.
- The "exit on the same bar the trail ratchets" re-check was dead code — it set
  `exit_price` inside a branch that then returned `None` unconditionally, and its
  comment claimed the opposite. Removed. Ratchet-at-bar-end is both what the
  engine actually did and what the counterfactual does, so live and shadow now
  run identical mechanics rather than similar ones.

### New knobs

| var | default | meaning |
|---|---|---|
| `BREAKWATER_PAPER_TARGET_ENABLE` | `0` | `1` restores the +2R target exit |
| `BREAKWATER_PAPER_MAX_BARS` | `120` | hard age cap; matches the counterfactual's cap |
| `BREAKWATER_PAPER_SLICE_GAP_RESPECT_R_GATE` | `1` | don't gap-close a position that banked +1R |

`paper.yml` does **not** pin these, so the code defaults above are what runs —
the new policy is live on the next paper cycle with no workflow change. The
trade-off is that reverting currently needs a code change. To make revert a
repo-variable flip instead, paste this into the `env:` block of
`.github/workflows/paper.yml` next to the `BREAKWATER_TRAIL_*` lines (this
edit needs `workflows` scope, which the automation token does not have):

```yaml
          BREAKWATER_PAPER_TARGET_ENABLE: ${{ vars.BREAKWATER_PAPER_TARGET_ENABLE || '0' }}
          BREAKWATER_PAPER_MAX_BARS: ${{ vars.BREAKWATER_PAPER_MAX_BARS || '120' }}
          BREAKWATER_PAPER_SLICE_GAP_RESPECT_R_GATE: ${{ vars.BREAKWATER_PAPER_SLICE_GAP_RESPECT_R_GATE || '1' }}
```

Guardian runs its shadow scan on code defaults and pins none of the trailing
knobs, so it already follows the new policy either way.

`TARGET_R_MULTIPLE` is retained: the through-target **entry** guard still uses
it, and refusing to chase a move that already ran +2R stands on its own.

The slice-gap change is the one judgement call not directly measured: no shadow
policy modelled a `slice_gap` exit, and with the target gone that 12-bar timer
would have become the winner cap the counterfactual just priced out.

### How this gets judged

`target_2r_trail_1r` stays in `paper_counterfactual.POLICIES`, so the retired
policy keeps being measured against the new default — the same comparison now
runs in the opposite direction. If `target_2r_trail_1r` starts printing a
positive `delta_vs_actual_zar` over a comparable sample, the change was wrong.

Caveats to hold: the +145.94 is 303 comparisons in a mostly bull/neutral window;
the shadows model neither funding nor slippage nor intrabar path; and the 7
currently-open positions carry corrupted peak state that rebuilds from the next
bar onward, so their first trail will arm later than it should.

### Updated Open Items
- [ ] Watch `delta_vs_actual_zar` for `target_2r_trail_1r` — that is now the control
- [ ] Re-check per-slice stop distances once honest MAE data accumulates (they were calibrated on one-bar excursions)
- [ ] ~~Fix stop exits (biggest drain)~~ — addressed here; verify on the next 50 closes
- [ ] Build Meta-Ranker
- [ ] Investigate regime_shift churning
- [ ] No `cron:` in any workflow — the hourly cadence comes from an external trigger
- [ ] HIP-3 Discovery last ran 2026-08-23

## Session 4 (2026-09-29) — evidence scoping for the new exit policy

Decision: **gather evidence under `no_target_trail_1r` before going live**,
target venue **VALR spot**.

### The trap this closes

The promotion gate wants `shadow_trades >= 10` over `shadow_days >= 14`. The
paper ledger already holds 382 closes that satisfy both — all of them
produced by the retired +2R target, by an engine whose trailing stop never
armed and whose MAE/MFE diagnostics only saw the final bar. Left alone,
`scripts/promotion_evidence.py --write-registry --live-armed` could have
promoted a slice to `LIVE_CAPPED` **today**, on the strength of mechanics
that no longer exist.

That is the most expensive kind of number in the system: true, and about
something else.

### What changed

Every paper trade is now stamped with the exit policy that governed it.

- `paper_trade.exit_policy_id()` derives the stamp from the live knobs
  (`notarget_trail1r`, `target2r_trail1r`, `target2r_notrail`, ...) rather
  than hard-coding it, so flipping `TARGET_ENABLE` back changes the stamp by
  itself and two policies' trades can never pool into one evidence set.
- Stamped on the position at **entry**; carried onto every close row
  (normal, `stale_data`, `slice_gap`) via a new `exit_policy` log column.
- Legacy rows migrate blank and are **excluded**, not charitably assumed.
  Verified on the real 29 MB / 189,065-row ledger: 1.6 s one-time rewrite,
  no row loss, idempotent.
- `promotion_evidence.filter_by_exit_policy` / `filter_by_kind` do the
  scoping. `kind` matters because `native` is a venue-separation label that
  pools VALR spot with Hyperliquid perps — a VALR question is not answered
  by Hyperliquid fills.

**This was time-critical.** Every hour of unstamped trading would have been
evidence we could not attribute to a policy.

### `scripts/live_readiness.py`

One command answers "can we go live on VALR spot yet", splitting the two
questions that usually get answered as one:

- **EARNED** — closes, shadow days, expectancy, PF, drawdown. Accrues by waiting.
- **BUILT** — live executor, canary, registry row, global arm. Waiting produces none of these.

Per-slice verdicts come from running the *real* `PromotionGate`, not a
restatement of its thresholds, so the report cannot drift into being more
generous than the gate.

Current output: **0 / 10 trades, 0 / 14 days** under `notarget_trail1r`, and
four missing mechanisms. Zero is the correct reading, not a bug.

### What is still BUILT-missing (in the order it should be done)

1. **Live executor that reaches the book.** `engine.operational_pass` filters
   to `slice_id == "big-wave"`; the monitored book has no live path at all.
2. **Canary.** `TradeExecutor.execute` has never run against the real VALR
   API. First contact should be a minimum-size place-and-cancel, not a
   signal-driven entry.
3. **Registry row.** Needs 1 and 2 plus the evidence.
4. **Global arm.** `BREAKWATER_MODE=live` + `BREAKWATER_LIVE_ACK`. Human, last.

### Watch while the evidence accrues

- `delta_vs_actual_zar` for `target_2r_trail_1r` — the retired policy is now
  the control; if it turns positive over a comparable sample, the change was wrong.
- Per-slice stop distances, which were calibrated on one-bar excursions and
  should widen as honest MAE data arrives.
- Both lanes are frozen red, so entries are throttled to green islands —
  evidence will accrue slower than the raw signal count suggests.

### VALR order-path canary (`scripts/valr_canary.py`)

`TradeExecutor.execute` had never run against the real VALR API. Signing,
the `/v2/orders/limit` body shape, order-id parsing, the `_completed`
polling loop, the status vocabulary, `active_order`, `cancel_order` — all
believed-correct, none known-correct. Without a canary the first test of
that code is a signal-driven entry whose timing we did not choose.

**Two orders, neither able to fill.**

1. `fok_kill` — a **FOK** limit BUY at ~50% below the best bid. It cannot
   cross the spread, so it cannot fill; fill-or-kill means it cannot rest
   either. Exercises placement, id parsing, the real `_completed` loop
   (called directly, not reimplemented) and terminal-status parsing.
2. `rest_confirm_cancel` — a **post-only GTC** BUY at the same deep price.
   Post-only makes VALR reject it outright rather than let it take
   liquidity. It rests, is confirmed via `active_order` (the same call that
   verifies a protective stop went live), then cancelled in a `finally`.

Plus a `no_residual` sweep of `open_orders()` filtered to the `bw-canary`
tag, so it recognises only its own litter. An unreadable order book raises
rather than reporting a confident empty list.

`build_plan` refuses on: unlisted pair, non-SPOT, inactive, non-ZAR quote,
crossed/one-sided book, tick rounding the price to zero, minimum size above
the 30 ZAR notional cap, and — re-checked after tick rounding — any price at
or above the best bid.

**Dry run is the default** and touches no write endpoint; the test fake
raises if it does. Arming needs `--arm` *and*
`BREAKWATER_CANARY_ACK=I_ACCEPT_BREAKWATER_CANARY_ORDERS`, and deliberately
**not** `BREAKWATER_MODE=live`: making the only way to test the plumbing be
to arm the strategy is backwards. Different decisions, different keys.

Still unproven after a green canary, and the receipt says so rather than
implying coverage: a real fill (`averagePrice`, `totalExecutedQuantity`),
`place_spot_stop_limit` (needs base currency, so needs a fill), and the
`place_market` emergency close.

Receipt at `localdata/valr_spot_canary.json`, added to `commit_state.sh` so
it survives the ephemeral runner. `live_readiness.py` requires `armed AND
ok` — a dry-run receipt does not count as proof.

**Naming:** `breakwater.order_canary` is this. `breakwater.canary` is the
pre-existing capped *risk mandate* preset. "How much may we lose" vs "does
placing an order work at all" — independent gates, both required.
