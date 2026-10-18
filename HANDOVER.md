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

## Session 5 (2026-10-15) — research scores alpha, not beta

### The problem

Paper equity was +301 ZAR lifetime but negative over 7 days, both lanes
frozen, deep audit 0/74,880 passes, zero armable shorts, native bear-regime
entries −63.8 ZAR. The common cause was in research, not execution:

- Discovery scored each `feature:state` on the **raw** forward trade return.
  In a trending universe every LONG state has a positive mean because the
  *market* went up, so Bonferroni flagged market beta as edge.
- Chronological walk-forward on raw returns then made that beta look
  temporally stable (bull folds pass, bull folds pass, bull folds pass).
- `side_train` compared raw LONG vs raw SHORT training means, so SHORT could
  never win the direction gate while the unconditional mean was positive.
  That is why the short inventory was empty.
- Long-only beta then paid the bill in bear regimes.

### What changed

`discovery.prepare_pooled` now attaches an equal-weight, leave-one-out
cross-sectional benchmark per bar and benchmark-relative returns
(`fwd_trade_net_long_resid`, `fwd_trade_net_short_resid`). The benchmark is
**the same trade rule on the peers** (`fwd_trade_bench_{long,short}`: same
side, same stop, same cost), *not* buy-and-hold of the peers. The first cut
of this session used buy-and-hold and it manufactured +52 bps / t=37 of
"alpha" for longs in a uniform crash with zero cross-sectional information,
because a 1.5-ATR stop beats buy-and-hold in every crash. Trade-vs-same-trade
cancels the stop mechanics; `tests/test_alpha_vs_beta.py::
test_stop_truncation_does_not_manufacture_alpha_in_crash` pins it. The raw
buy-and-hold benchmark survives only as the diagnostic `fwd_ret_market`.
Validation and the deep audit residualize their own (calibrated-stop,
trailing) series the same way via `discovery.loo_cross_sectional_mean`.

- **Discovery**: `t_stat`/`p_value`/`mean_ret_costadj` stay raw (what you
  would earn). New `alpha_t_stat`/`alpha_p_value`/`mean_resid_costadj`
  carry the alpha evidence. `bonferroni_pass` now needs alpha significance
  AND `mean_resid > 0` AND raw `mean > 0`.
- **Validation**: direction (`side_train`), fold passes, recency, breadth,
  symbol-level p-value and per-asset edges are judged on residual returns.
  `mean_positive` stays on raw returns — relative outperformance that loses
  money outright is not tradeable. `regime_confounded` is now computed on
  residual returns and is a **hard gate** (`regime_gate_ok`): if the alpha
  disappears in the hostile regime it was beta in a costume. Unproven
  (too few hostile rows) still passes. New regime-stratified columns:
  `regime_{bull,neutral,bear}_{n,mean_ret,mean_resid}`.
- **Deep audit**: preliminary pass additionally needs recent and weighted
  residual means > 0; new columns `*_mean_resid`, `residualized`.
- Universes with < 2 peers at a bar get benchmark 0 (residual == raw), so
  single-symbol groups behave exactly as before.

### Knobs

- `BREAKWATER_DISCOVERY_RESIDUALIZE` (default 1) — raw scoring if 0.
- `BREAKWATER_DISCOVERY_MARKET_MIN_PEERS` (default 2).
- `BREAKWATER_VALIDATION_RESIDUAL` (default 1).
- `BREAKWATER_VALIDATION_REGIME_GATE` (default 1).

### Expect on the next research cycle

Fewer validated slices (most of the 51 native monitored slices are ≤ 81 bps
raw edge against a 70 bps ZAR-spot round trip and will not carry alpha), and
SHORT candidates appearing for the first time. That is the intended result:
the book should shrink to things that beat the universe, and the short
inventory should stop being structurally empty. `tests/test_alpha_vs_beta.py`
pins the behaviour on synthetic beta-only and alpha universes.

### First real run (2026-10-16, run 38827908376)

Discovery+validation finished in < 1 h and committed. The deep audit ran
into its 330-min limit: the LOO benchmark grouped on an object array of
tz-aware Timestamps (~142 ms × 74,880 candidates ≈ 3 h). Fixed by
factorizing the int64 view + `np.bincount` (now ~3–10 ms/call).

Book turnover was large, not small: 69 → 89 validated, kept 9 / dropped 60 /
added 80, all PERP, **3 SHORT rows for the first time** (`feat_adx_14:0:SHORT`
h15/h20/h24). The new set is dominated by `state 0 LONG` on momentum-type
features (`feat_ret_1/3`, `feat_intraday_mom`, `feat_session_mom`,
`feat_close_position`, `feat_vwap_*`, `feat_cci_20`) — i.e. cross-sectional
short-term reversal at 12–24 h, a coherent and well-documented crypto effect
rather than a grab-bag. Median residual edge 7 bps vs 9 bps perp round trip
(the residual cancels cost, so raw `mean_ret_costadj` is the money number).

Bug found in that output: `feat_hour_utc`, `feat_asia_vol`, `feat_asia_range`
validated with `mean_resid_ret` ≈ 1e-19. Time-of-day states are identical
across the cross-section, so LOO residuals cancel exactly and `> 0.0` let
floating-point noise pass 3/5 folds; two `feat_rsi_divergence:2:LONG` rows
validated with *negative* overall alpha. Production runs with
`REQUIRE_BONFERRONI=0`, so discovery's alpha-significance test was bypassed
and validation had no alpha floor. Added `alpha_positive` gate (`MIN_ALPHA`,
env `BREAKWATER_VALIDATION_MIN_ALPHA_BPS`, default = float guard) applied to
the whole-sample residual and to each fold. Default floor is deliberately ~0;
raise it once there is a paper-trade read on the reversal cluster.

### Ledger rotation (same session)

`localdata/research/paper_trade_log.csv` was 54 MB in git and growing
~1 MB/day toward GitHub's 100 MB blob limit, which would have broken
`commit_state.sh` for the paper role. 99.85% of it was skip/guard rows
(349,759 skipped vs 536 closes); nothing reads those for a decision — every
consumer filters to `win`/`loss` first. `append_log` now routes skipped rows
to `paper_skip_log/YYYY-Www.csv` (ISO week); on week rollover older weeks are
gzipped in place (~12x). The open week stays plain CSV deliberately: git
delta-compresses appended text, a gzip that changes hourly would store a
fresh blob per commit. `rotate_skips_out_of_log` runs at the top of every
paper cycle: a one-time 3 s split of the legacy ledger on the runner (so the
PR did not have to touch the hourly-updated file), then a no-op read of a
~200 KB file. Lossless and idempotent; realised PnL unchanged.
`iter_paper_log(include_skips=True)` gives the full decision journal.
Old 54 MB blobs remain in git *history*, which is fine — the limit is per
pushed blob, not per repo.

### Second real run (2026-10-17) and the carry-forward leak

Research refresh completed in 4h42 (deep audit 4h02, no timeout); ledger
rotation landed (0.19 MB ledger, weekly gz sidecars). Validated: 73, all
LONG, `alpha_positive` column live. Yesterday's three `feat_adx_14:0:SHORT`
rows did not re-validate.

Digest said "book slices absent from pools: 30". Cause: `sync_book`'s
`_carry_eligible` looked up the slice's current raw `mean_ret_costadj` and
carried it if above the keep floor — it never read `validated`. So the
alpha/regime gates rejected a slice and the lifecycle kept it anyway on its
raw (beta) edge: 31 of 53 book rows were research-rejected, 26 still
`monitored`, 61 paper trades for −25.8 ZAR. Fixed: a slice present in this
run's output that is neither `validated` nor a concentrated candidate is not
carried (nor paper-protected). Slices absent from the run (another lane's
cycle) keep legacy behaviour. Replay on committed state drops exactly those
31. New summary key `research_rejected_dropped`.

**The SHORT finding worth building on.** The strongest residual alpha in the
whole run is SHORT: `feat_vol_regime:0:SHORT` h15/h20/h24 at +24..+31 bps
benchmark-relative, 4/5 folds, failing *only* `mean_net<=0` (raw −31..−45
bps because the sample's market drift is positive). That is the mirror image
of the original bug: `mean_positive` on raw returns is itself a beta gate —
it admits longs in bull samples and rejects shorts in them. An outright
short of a cross-sectional signal is beta-dependent by construction. The
residual evidence says the signal is real in both directions; the engine
that captures it without beta is long state-2 / short state-0 on perps
(market-neutral, 9 bps). That is the "more engines" candidate with actual
evidence behind it; everything else so far is directional beta exposure.

### Market-neutral spread evidence (same day, research-only)

Scoped rather than built. `src/breakwater/spread_research.py` now runs on
PERP shards inside the research pass and writes
`localdata/research/spread_slices.csv`: for each feature × horizon × pairing
(long state 2 / short state 0, and the reverse) the per-bar dollar-neutral
spread `0.5 * (mean long-leg net + mean short-leg net)`, both legs on the
same stop-aware 9 bps trade model, ≥3 names per leg per bar. Stats are
non-overlap `t`, 5 purged folds, drawdown, and `market_corr` against the
universe return — the last one is the important check: in a crash the
spread goes positive because stops truncate the long leg, and it shows up
as `market_corr ≈ −0.9`. The `qualifies` flag feeds **no gate**. Workflow
merges the shard files; `commit_state.sh` commits the merged file; daily
print section 8 prints the top three. Go/no-go gates (3 consecutive
qualifying runs, ≥ +15 bps gross, both legs with residual alpha, breadth ≥ 4,
`|market_corr| ≤ 0.3`) and the engine shape (pair-position with joint exit,
funding fetch as prerequisite) are in `docs/market_neutral_engine.md`.
The first real read arrives with the next research run.

### Third run (2026-10-17 10:21Z, 19 min) — where the P&L actually came from

Run 39024592537 on `d4253a4`: 19 minutes end to end (the 4h42 before it was
the deep audit; research alone is ~20–35 min). 1672 slices, 128 validated,
**all PERP LONG, zero SPOT**. Book 72 → 49 rows after the carry-forward fix
(41 unique slices, all in the pool). Spread file: 528 rows, 0 qualifying;
best is `feat_vol_regime:L2S0:h20` +36.9 bps but carried by the long leg
(+71 vs +2.7), `market_corr` 0.34, and the whole L2S0 family has a
*negative* last-20% mean — a "do not build" read, not a near miss.
`n_nonoverlap` caps at ~28 for h20/h24 with 1000 candles; set the repo
variable `BREAKWATER_PERP_CANDLE_COUNT=2000` if the spread read at those
horizons is to mean anything (fetch supports up to 5000; ~doubles shard time).

The decisive number is the P&L split by whether a slice is in the current
book:

| week | in current book | dropped/rejected |
|---|---|---|
| W38 | 0 trades | 258 trades, +278.63 |
| W39 | 1, +0.51 | 105, +246.80 |
| W40 | 14, +1.13 | 48, −62.04 |
| W41 | 22, −53.96 | 55, −19.96 |
| W42 | 5, −15.99 | 33, −34.56 |

The lifetime +299 ZAR is `feat_close_pos_ma:1:LONG:h24` on **LINKZAR**:
28 trades, +269.8 of the slice's +283. Research now scores that slice
`alpha<=0`, folds 00001. It was a LINK rally, not an edge. The current
41-slice book has 42 closes and −68.8 ZAR of history. Nothing in the
system has yet demonstrated repeatable alpha; the paper equity curve is
one asset's beta followed by cost bleed.

Also fixed here: under sharding no `research_done` row ever reached the
committed `status.csv` (each shard wrote its own, never uploaded), so the
daily print's §8 had no "Latest research" line. `scripts/research_summary.py`
now rebuilds the row from the merged files inside `commit_state.sh research`
(idempotent per merged file set; shard-only facts are marked "not
propagated").

### Slice memory (2026-10-18) — rotation is fine, amnesia is not

Overnight run (00:10Z, 4h32 with deep audit): validated 128 → 53 (first
three SHORTs ever, `feat_adx_14:0:SHORT`, +2..+13 bps), regime_confounded
536 → 732, book 49 → 19 rows: 32 of 41 slices dropped, 28 of them on
`regime_confounded`, every surviving row at 0 paper trades. Operator's call:
slices may rotate, but a slice that comes back must be remembered.

`sync_book` now keeps `localdata/research/slice_memory.csv` (per
`(slice_id, kind)`: first/last validated, times admitted/dropped, last drop
reason, paper record and cooldown at the moment of dropping). A slice that
returns with no row in the book inherits that record instead of
`paper_trades=0`, and faces the same test a held slice faces: cooldown still
running → `cooldown`; ≥3 trades and negative → `decayed`. No staleness test
on return (it could not have signalled while out). Summary keys:
`remembered`, `remembered_cooldown`, `remembered_decayed`, `memory_rows`.
`scripts/backfill_slice_memory.py` seeded 151 entries from the trade log
(52 of them would return `decayed`); it never overwrites what `sync_book`
recorded.

Also fixed in the same change, because memory could not be counted without
it: a slice re-validated this run was both promoted (fresh row) **and**
carried (old row) — 49 rows for 41 slices on 10-17, and a `monitored` twin
that outlived a `decayed` verdict. Carry now skips slice_ids promoted this
run (`carry_skipped_promoted`).

Freeze otherwise holds: nothing else in research/validation/paper changed.

### Decision 2026-10-18 — seven-day observation window, then new inputs

Operator decision. **Freeze until 2026-10-25**: no changes to research,
validation, the book, or paper trading. Plumbing/observability fixes only
if something breaks. Judge the clean book against: in-book P&L (needs ~60
closes to mean anything), book turnover per run (`remembered` /
`carry_skipped_promoted` / rows == unique slices), claimed-vs-realised gap,
and whether any slice holds its place for three runs while green on paper.

**After 2026-10-25, regardless of the read, action the input problem.**
Every feature today is OHLCV on hourly bars. The next research cycle adds
positioning inputs from Hyperliquid: funding rate (history available via
`fundingHistory`, so it can be back-filled), open interest and basis/premium
(`metaAndAssetCtxs` is current-state only — no history; needs forward
collection), and order-book imbalance (`l2Book` snapshot, current-state only;
needs forward collection). Anything that needs forward collection should
start being snapshotted *during* the window so there is data to research on
day eight; that collector is read-only and is the one piece of new code the
freeze permits.

**Collector shipped (same PR):** `src/breakwater/positioning.py`, two CLI
commands, nothing else touched.

- `breakwater.py positioning-snapshot` — one `metaAndAssetCtxs` call plus one
  `l2Book` per active PERP coin in `localdata/universe.csv` (~178 coins, ~0.1 s
  apart, well under the venue's weight budget). Per coin: mark/oracle/mid,
  premium, hourly funding, open interest (+ USD notional), 24h volume, best
  bid/ask, spread bps, cumulative USD depth and imbalance
  `(bid−ask)/(bid+ask)` at 1/5/10 levels. Appends to
  `localdata/positioning/YYYY-Www.csv` (ISO week; older weeks gzipped like the
  skip log). Keyed by `snapshot_hour`: a second run in the same hour is a
  no-op with zero network calls, so it rides the 20–40 min paper cadence and
  yields one row per coin per hour. A failed book keeps the context row with
  `book_error` set; a 429/5xx retries three times honouring `Retry-After`.
- `breakwater.py positioning-backfill-funding --days N` — paginates
  `fundingHistory` into `localdata/positioning/funding_history.csv`
  (coin, time, funding_rate, premium), deduped and resuming from the newest
  stored point per coin. Run once by hand (`--days 90`), re-run any time.
- `scripts/commit_state.sh` paper role ships `localdata/positioning/*.csv{,.gz}`.
- Wiring is a `paper.yml` step after the shadow scan (the sandbox cannot
  edit workflows): `continue-on-error: true`, `PYTHONPATH=src python
  scripts/breakwater.py positioning-snapshot`. Until that step is added the
  code is inert.
- Budget: ~178 rows × ~250 bytes × 24 h ≈ 1 MB/week plain, ~100 KB gzipped.

### Still open (not done here)

- Cross-sectional *state* binning (rank the feature across symbols per bar
  instead of per-symbol expanding terciles) — needs engine-side state
  computation at trade time, so left as a follow-up.
- Venue routing: ZAR spot at 70 bps round trip needs ≥ 100 bps raw edge to
  be worth trading; USDC spot (20 bps) / perps (9 bps) do not.
- Features beyond OHLCV (funding, basis, OI, order-book imbalance).
