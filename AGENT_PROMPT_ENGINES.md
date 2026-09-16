# Engine Signal Investigation — Why Zero?

Date: 2026-09-16
Auditor: Arena Agent

## Problem

The multi-engine system (simple_trend, momentum, mean_reversion, lead_lag) has produced **0 engine signals** across every paper run since it was built. The code is wired, thresholds have been lowered, the book filter is bypassed, the session gate is applied — but nothing comes out.

We need to find out why and fix it.

## What We Know

1. **Code is in place**: `engine.py` `_run_engines()` runs after `monitor_book()`, extends signals list
2. **Tests pass**: All 4 engines produce signals on synthetic data (6 simple_trend, 2 mean_reversion on test data)
3. **Thresholds lowered**: ADX 18, RSI 35/65, z-score 1.5, BTC move 1.5%, simple_trend fires on 0.3% moves
4. **Book filter bypassed**: `is_engine_signal = signal.slice_id.startswith("engine_")` — passes through
5. **Session gate applied**: `_paper_sessions()` and `_utc_session()` check in `_run_engines()`
6. **Edge converted**: `edge_fractional = r.edge / 10000.0` (bps to fractional)
7. **Still 0 in production**: Every paper run shows 0 `engine_*` entries in trade log

## Investigation Steps

### Step 1: Are the engines being called at all?

Check `engine.py` `_run_engines()`:
- Is `BREAKWATER_MULTI_ENGINE` env var set? (default "1" — should be on)
- Does the function return early at any check?
- Are there any `except` blocks swallowing errors?

### Step 2: Do the engines produce signals on real data?

The engines need:
- `engine_frames` dict with at least 60 bars per pair
- Real market data (not synthetic)

Check:
- Is `engine_frames` populated? (frames_by_kind has SPOT and PERP entries)
- Are there enough bars? (`len(frame) >= 60` check)
- Do the engines return empty lists? If so, why?

### Step 3: What specific thresholds are blocking?

For each engine, trace the signal generation:

**simple_trend** (most permissive — should always fire):
- Needs `abs(ret) > 0.003` (0.3% 3-bar return)
- Needs `abs(dist) > 0.005` (0.5% from SMA10)
- Needs `min_confidence = 0.15`
- **Should fire on virtually any market. If this doesn't fire, something is fundamentally wrong.**

**momentum**:
- Needs ADX > 18 (was 25)
- Needs SMA crossover OR breakout OR trend alignment
- **ADX might be below 18 in ranging market**

**mean_reversion**:
- Needs RSI < 35 or > 65 (was 30/70)
- Needs Bollinger band touch (1.8 std)
- Needs z-score > 1.5
- **RSI might be in 40-60 range in ranging market**

**lead_lag**:
- Needs BTC move > 1.5% in 10 bars (was 3% in 5)
- Needs correlation > 0.3
- **BTC might not have moved 1.5% recently**

### Step 4: Are signals being filtered after generation?

Check `_run_engines()` return path:
- After engines produce results, `rank_signals()` picks top N
- Then conversion to `SliceSignal` with `entry > 0, stop > 0, atr > 0` check
- Then returned to `shadow_scan()` which extends `signals`
- Then paper cycle processes them

Check paper cycle filtering:
- `pair_held` — is the pair already open?
- `skipped` — is the slice_id in `book_slice_ids`? (bypass for engine_)
- `session_blocked` — is the session allowed?
- `regime_blocked` — does regime gate block BUY in bear?
- `slot_full` — is the position cap reached?
- `aggregate_risk_cap` — is risk budget exhausted?

### Step 5: Check the status CSV

The `status.csv` has a `no_action_reason` and `no_action_funnel` when signals exist but nothing opened. But if signals=0, there's no funnel to report.

Check `status_detail["signals"]` count. If it's > 0 but no engine signals in log, the filtering is the issue. If it's 0, the engines aren't producing.

## Key Files to Read

1. `src/breakwater/engine.py` — `_run_engines()` method (lines ~1111-1220)
2. `src/breakwater/engines/simple_trend.py` — the "always-on" engine
3. `src/breakwater/engines/momentum.py` — ADX threshold, trend_align signal
4. `src/breakwater/engines/mean_reversion.py` — RSI/Bollinger/z-score thresholds
5. `src/breakwater/engines/lead_lag.py` — BTC move threshold, timestamp join
6. `src/breakwater/engines/ranker.py` — signal ranking and dedup
7. `src/breakwater/paper_trade.py` — signal filtering in `run_paper_cycle()`
8. `localdata/status.csv` — last run's signal count and funnel
9. `localdata/research/paper_trade_log.csv` — verify 0 `engine_*` entries

## What to Produce

1. **Root cause**: Why exactly are engine signals = 0? Trace the code path.
2. **Fix**: Code change to make engines fire on real data.
3. **Verification**: How to confirm the fix works (test case or log output).

## Important Context

- Market regime: confirmed bear, consecutive_bear high
- `BREAKWATER_PAPER_SESSIONS` may be set (check env in workflow YAML)
- The system runs on GitHub Actions, not locally
- Real market data is hourly candles from VALR (spot) and Hyperliquid (perp)
- The simple_trend engine was specifically designed to "always fire" — if it doesn't, the bug is in the plumbing, not the thresholds
