# Breakwater Handover / Runbook (2026-08-16)

Date: Sunday, 2026-08-16 (UTC)

This document is the canonical handover for future agents/operators:
- where Breakwater is today
- what was broken and fixed
- what “good” looks like next
- when (and how) to go live + add leverage
- operational guardrails to avoid over-tuning

---

## 0) Executive Summary (read this first)

Breakwater initially ran in a **mismatch state**: slices were discovered/validated using a fixed forward-return horizon (`horizon_bars`), but paper trading used stop/target/time-stop exits. This caused biased/low-quality evidence and early poor paper results.

As of 2026-08-16, Breakwater has been updated to:
1) **Align paper execution to slice horizon** (horizon exits) and automatically **migrate legacy open positions** to include `horizon_bars` and `regime`.
2) **Reduce biased evidence** from strict regime gating via **evidence-aware regime blocking** using `hostile_unproven`.
3) Track and act on **truth after fees** via `pnl_outcome` (while keeping legacy `outcome`).

Primary goal for the week: **hands-off paper trading** across sessions, gather clean evidence, avoid frequent code changes.

---

## 1) Current Operating Mode

- Exchange mode: `readonly` (no live orders)
- Trading mode: paper/shadow (“paper positions” + “paper trade log”)
- We are awaiting VALR support response (API/perps/auth questions).

---

## 2) System Map (where things live)

### 2.1 Core research/decision pipeline (conceptual)
1) Bars pulled for pooled universe
2) Feature computation
3) Discovery (`discovery.py`): find candidate slices, with Bonferroni correction
4) Validation (`validation.py`): walk-forward + hostile regime audit
5) Book build/promote -> `monitored_slices.csv`
6) Monitor (`monitor.py`) emits signals from the book
7) Paper trade (`paper_trade.py`) executes signals and logs outcomes
8) Feedback loop updates slice lifecycle/book metrics

### 2.2 Files of record (operator should know these)

**Book / strategy config**
- `localdata/research/monitored_slices.csv`
  - includes: `slice_id`, `kind`, `feature`, `state`, `side`, `horizon_bars`, `stop_atr_mult`, `hostile_unproven`, plus performance counters

**Paper trading state**
- `localdata/research/paper_positions.json`
  - open paper positions (must remain consistent with paper log)
  - should include: `horizon_bars`, `regime`, `bars_held`

**Paper trade audit**
- `localdata/research/paper_trade_log.csv`
  - authoritative event log for closed and skipped paper actions
  - includes: `exit_reason`, `bars_held`, `pnl_zar`, `outcome`, `pnl_outcome`, `regime`

**Operational status / heartbeat**
- `localdata/status.csv`
  - guardian snapshots, mode, and “paper cycle summary” counters

---

## 3) What was broken originally (root causes)

### 3.1 Horizon mismatch (biggest issue)
- Research measured expectancy at a fixed horizon (`horizon_bars`)
- Paper execution exited via stop/target/time-stop, often holding far longer
- This invalidated evidence and created misleading results

### 3.2 Biased evidence from strict regime gate
- Book is currently heavily SHORT skewed
- If shorts are blocked in bull, evidence is filtered to bear/neutral pockets
- This is not necessarily “safer”; it can be *more biased* and slow learning

### 3.3 Win-rate label wasn’t “truth”
- `outcome=win` could still have negative `pnl_zar` after fees
- Lifecycle feedback/cooldown was previously based on `outcome` (direction), not realized PnL

---

## 4) Fixes implemented (must remain true)

### 4.1 Horizon alignment + migration (paper)
In `src/breakwater/paper_trade.py`:
- Positions carry `horizon_bars`
- Exit at bar close when `bars_held >= horizon_bars` with `exit_reason=horizon`
- Stop remains an intrabar safety boundary
- Legacy open positions are auto-migrated each run:
  - missing/0 `horizon_bars` backfilled from `monitored_slices.csv`
  - missing `regime` filled from `monitor.regime_of(frame)` or `unknown`

**Expected evidence signature:**
- most closes show `exit_reason=horizon`
- `bars_held` equals `horizon_bars` (often 6)

### 4.2 Evidence-aware regime blocking + strict override
In `src/breakwater/monitor.py`:
- `regime_blocks(side, regime, hostile_unproven)`:
  - if strict mode enabled → always block in hostile regime
  - otherwise → block only if `hostile_unproven=True`
- strict override env var:
  - `BREAKWATER_REGIME_GATE_STRICT=1`

In `src/breakwater/paper_trade.py`:
- paper regime gating must pass `signal.hostile_unproven` into `regime_blocks(...)`
- otherwise paper would re-block trades even if monitor allowed them

### 4.3 Two outcome metrics + truth-based feedback
In `src/breakwater/paper_trade.py`:
- `outcome` = legacy directional label
- `pnl_outcome` = truth after fees (`win` if `pnl_zar > 0` else `loss`)
- lifecycle feedback + cooldown uses `pnl_outcome`

**Expected signature:**
- you may see `outcome=win` but `pnl_outcome=loss` on tiny moves/fees
- that’s correct; it prevents false reinforcement

---

## 5) Operator Controls / Environment Variables

### 5.1 Regime gating
- `BREAKWATER_REGIME_GATE_STRICT=1`
  - restore “always block hostile regime” behavior

### 5.2 Paper limits (if present in your paper file)
- `BREAKWATER_PAPER_TIME_STOP_BARS`
- `BREAKWATER_PAPER_MAX_POSITIONS`
- `BREAKWATER_PAPER_MAX_POSITIONS_PER_KIND`

### 5.3 Trailing feature (legacy; typically off)
- `BREAKWATER_TRAIL_ENABLE`
- `BREAKWATER_TRAIL_ACTIVATE_R`
- `BREAKWATER_TRAIL_DISTANCE_R`
- `BREAKWATER_TRAIL_IGNORE_TIME_STOP`

---

## 6) What we want to see this week (positive signs)

### 6.1 Process integrity (first priority)
- positions have `horizon_bars` + `regime`
- closes primarily via `exit_reason=horizon`
- `bars_held` ≈ `horizon_bars`
- low incidence of `stale_data` forced closes
- no duplicated signal IDs / same-bar re-entries

### 6.2 Evidence quality (avoid biased sampling)
- regime-blocked skips should reduce materially (unless strict mode enabled)
- trades occur across sessions (Asia/EU/US), not only in one quiet window

### 6.3 Profitability (truth metric)
- net realized `sum(pnl_zar)` positive over a meaningful sample
- `pnl_outcome` win-rate and mean PnL/trade stable or improving
- not dominated by one symbol/pair

---

## 7) Go-live conditions (before real money)

Do not go live because “one night was green”.

Minimum conservative gate:
- >= 100 closed horizon trades (non-skipped)
- net realized PnL (`sum(pnl_zar)`) > 0 over that set
- profit factor > 1 (preferably > 1.2)
- no single pair contributes > ~40% of total pnl
- stable ops for multiple days without intervention

Rollout plan:
1) micro-live SPOT only (no leverage), tiny notional
2) observe live slippage/fees for ~1 week
3) scale notional slowly

---

## 8) Leverage conditions (before PERP leverage)

Leverage introduces liquidation/margin failure modes.

Require:
- stable perps API integration (VALR response pending)
- proven stop logic and position sizing with live fills
- positive after-fees expectancy specifically on perps sample
- circuit breaker / kill switch validated

Ramp:
- start at minimal leverage; increase slowly only after stable weeks

---

## 9) Daily operator routine (restraint / anti-overfit)

- Freeze code during Mon–Fri unless an operational bug is confirmed.
- Review on a schedule (e.g., 2x/day). No “constant tweaking”.
- Keep a change log with hypotheses and expected metric improvements.
- If tempted to tweak: write it down and wait for review window.

---

## 10) Notes for future agents (what not to break)
- Do not remove `horizon_bars` from positions.
- Do not revert paper exits back to time-stop/target as the default (it invalidates evidence).
- Do not let paper gating re-block monitor (paper must use `signal.hostile_unproven`).
- Keep both metrics (`outcome` and `pnl_outcome`); use truth for feedback.

---

End.
