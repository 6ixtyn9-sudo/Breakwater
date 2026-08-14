# Breakwater — Handover

Date: 2026-08-14

Single source of truth. Update this file in place. Do not create drifting
reports or extra planning documents unless explicitly asked. Where this file
lags the code, trust the code and correct this file.

## Current posture

- Mode: `readonly` on GitHub Actions; `shadow` paper trading via `paper.yml`.
- Live execution: spot path code-complete but gated (no `live_capped`
  strategy, live gates off). Perp execution is impossible at the venue:
  VALR Perps trading routes authenticate by web session only and return
  HTTP 401 code -93 to API keys (`perps_api: unavailable` in every
  guardian run; the system auto-reports when this changes).
- Cadence (cron-job.org, dispatch-only workflows): guardian every 30 min,
  paper hourly, research daily at 02:30 UTC.
- Book: built only from walk-forward-validated, regime-confounded-free
  slices; paper trades are simulations committed to the repo.

## Architecture map

```text
universe.py      full VALR spot + Perps ingestion, volume-ranked, 7-day freshness
perpdata.py      Hyperliquid public candles (the venue's own market data)
features.py      descriptive price-state features + forward MAE in ATR
discovery.py     expanding-window state bins, Bonferroni-controlled slices
validation.py    chronological walk-forward folds + hostile-regime check
research_lifecycle.py  monitored book: decay, cooldowns, provenance
monitor.py       per-slice signals, side-aware regime gate, calibrated stops
paper_trade.py   simulated fills: knife guard, winner capture, exits, audit
risk.py          env-supplied mandate, perp sizing under venue minimums
engine.py        guardian / shadow / research / health orchestration
```

## Lessons audit (predecessor handover -> Breakwater status)

Inherited and verified:

- Falling-knife entry guard: skip adverse entries beyond
  min(1.0 ATR, 2 percent) of the signal close. NOTE: paper fills at the
  reference price by construction, so this guard's teeth are on the LIVE
  path (`plan_order` rejects a 1 percent chase vs the executable price).
- Winner-capture premium: min(0.25 ATR, 1 percent) in the trade's direction.
- Fail-open visibility: every skip journaled with its reason
  (adverse / no_price / regime / not_book).
- MAE-calibrated per-slice stops: 90th percentile, clamped [1.5, 3.5] ATR.
- Side-aware regime gate: no longs in a death-cross bear, no shorts in a
  bull, fail-open otherwise.
- Regime-stratified validation: hostile-regime rows must not oppose
  the slice's side; confounded slices are recorded and excluded.
- Book-only paper trading: unvalidated fallback signals are research-only.
- Immortal-trade guard: positions close at entry after 24 missing bars.
- Stale-data refusal: universe re-ingested after 7 days.
- Provenance honesty: every book row records `validated_walk_forward`.
- Serialized state commits: all workflows share `breakwater-state`.
- Research/paper separation: separate workflows.
- Book wipe protection: `sync_book` preserves kinds with no fresh
  validation and never wipes on an empty validated file; research halts
  instead of writing empty artifacts.
- Green != live: `shadow_scan_done` commits paper counts
  (closed/open/skipped) to status.csv; `breakwater.py health` gives a
  one-glance heartbeat of universe freshness, book composition and paper
  positions with no network calls.

Deliberate deviations (recorded honestly):

- The predecessor system forbade leverage entirely; Breakwater's per-position leverage cap
  (default 3x) is operator-mandated and bounded by VALR's isolated-margin
  model (worst loss per position = allocated margin).
- The predecessor system was an equities lab with RTH sessions and corporate actions;
  crypto is 24/7, so no DST/RTH windows, no adjustment gates, no
  corporate-action quarantine apply here.
- The predecessor system's yfinance/Tiingo/Alpaca warehouse stack is replaced by VALR +
  Hyperliquid public feeds.

Known placeholders and seams (do not tune without evidence):

- SPOT_FEE_BPS 20 / PERP_FEE_BPS 26 are first-pass simulations; they must
  be calibrated from realized paper fills before any live step.
- Per-slice hold-horizon: the book carries `horizon_bars` but the paper
  time-stop is the global 48 bars. Per-slice horizon calibration is
  deferred (research-side feature).
- `xyz:` builder pairs are skipped (no Hyperliquid coin mapping).
- Big-wave fallback signals exist only for an empty book and never paper-trade.
- The promotion registry (live_capped) is vestigial from v0.1; live
  execution also requires the two live gates and a clean guardian.

## Operational runbook

Watch commands (after any run):

```bash
cd Breakwater
git pull --ff-only origin main
tail -3 localdata/status.csv
tail -3 localdata/research/paper_trade_log.csv
cat localdata/research/paper_positions.json
PYTHONPATH=src python scripts/breakwater.py health
```

Workflow dispatch and secret updates are documented in README.md.
Updates ship as signed git bundles; never hand-edit committed state files.

## Process rules for future agents

- Verify current code on main before claiming anything is broken or
  missing; tag evidence with its as-of time.
- No silent fallbacks, no silent drops: every guard decision is journaled
  with a reason.
- Fail closed: empty data, partial mandate, malformed artifacts halt the
  run instead of degrading quietly.
- A green workflow is not proof of work: the committed status detail and
  `health` are the evidence.
- If a gate is ever relaxed, update the provenance labels tied to it in
  the same commit.
- Every shipped shell filter or query is executed against a realistic
  synthetic payload before it leaves the sandbox.
- Small patches, in-place documentation, no placeholder files.
