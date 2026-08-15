# Breakwater — Handover

Date: 2026-08-15

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
- Cadence (cronjobs.com, dispatch-only workflows): guardian every 30 min,
  paper hourly, research daily at 02:30 UTC.
  - NOTE: the repo workflows are `workflow_dispatch` only. Scheduling is external.
- Runtime knobs (current GitHub Actions settings):
  - Research horizon bars: `BREAKWATER_RESEARCH_HORIZON_BARS="6"` (research.yml).
  - Paper time-stop bars: `BREAKWATER_PAPER_TIME_STOP_BARS="12"` (paper.yml).
  - Trailing stop is wired in paper.yml but OFF by default:
    `BREAKWATER_TRAIL_ENABLE="0"` plus `*_ACTIVATE_R="1.0"`,
    `*_DISTANCE_R="1.0"`, `*_IGNORE_TIME_STOP="0"`.
- Book: built only from walk-forward-validated, regime-confounded-free
  slices; paper trades are simulations committed to the repo.
- VALR Perps API status (as of 2026-08-15): /simple-futures/symbol-info is public, but authenticated /simple-futures/* routes 
  (positions/settings/address/order/tp-sl) return HTTP 401 with code -93 when signed with API keys. Support ticket [RM3PGP-R30W3] is 
  escalated; do not build execution on /simple-futures until VALR confirms API-key support.

## Architecture map
```text
universe.py      full VALR spot + Perps ingestion, volume-ranked, 7-day freshness
perpdata.py      Hyperliquid public candles (the venue's own market data)
features.py      descriptive price-state features + forward MAE in ATR
discovery.py     expanding-window state bins, Bonferroni-controlled slices
validation.py    chronological walk-forward folds + hostile-regime check
research_lifecycle.py  monitored book: decay, cooldowns, provenance
monitor.py       per-slice signals, side-aware regime gate, calibrated stops
paper_trade.py   simulated fills: knife guard, winner capture, exits, audit (+ optional trailing)
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

## Decisions
- 2026-08-14, paper concurrency raised (operator call): paper exists to
  accumulate evidence, not to respect capital scarcity, so it now holds
  up to three positions per kind (SPOT, PERP; six total). New entries are
  selected by validated-edge strength (top |edge| first), one position
  per pair, so slots go to the best evidence rather than iteration order.
  The live-account mandate remains one position, unchanged. Recorded
  caveat for the evidence review: simultaneous paper positions resolve in
  the same market windows, so per-slice round-trip counts are correlated
  observations, not independent ones — the review must weigh that before
  treating accumulated counts as proof.
- 2026-08-15, knobs shipped (operator call): research horizon and paper
  time-stop are now controlled by env vars (defaults preserve prior behavior),
  and GitHub Actions sets horizon=6 and time_stop=12 to improve research/execution
  alignment and learning speed.

## Incidents
- 2026-08-14, legacy log header hid audit columns: paper_trade_log.csv was
  created before exit_reason/entry_guard/regime existed, so its header
  names 13 columns while every row written since carries 16. The audit
  values are in the raw file but invisible to any csv.DictReader, which
  silently drops the extras — a quiet audit gap. Fix: append_log now
  migrates the header once (rewrites with the current 16-column header,
  padding legacy rows) before appending; idempotent and data-preserving.
- 2026-08-14, cross-kind signal contamination: monitor_book tested every
  book slice against every frame regardless of market, so spot slices
  emitted fake signals on perp pairs (kind SPOT, pair BTCUSDC) while the
  real perp slices could not be distinguished. Fixed by scoping frames by
  kind (frames_by_kind), plus regime-blocked matches are now reported and
  journaled instead of silently dropped (visibility, per doctrine).
  Paper additionally holds one slot per kind (SPOT + PERP) so perp
  evidence accumulates; the live mandate (one position) is untouched.
- 2026-08-14, state-commit push race (paper run #2 failed): the guardian and
  paper cron jobs both dispatch at 14:00:00 UTC. Two workflow_dispatch
  events created in the same instant can both pass the concurrency-group
  check, so their commit_state pushes collided; the paper run's pull
  --rebase conflicted on localdata/status.csv and the run failed, losing
  one hourly paper state update (self-healing, but red). Fix: commit_state.sh
  now resolves state conflicts deterministically — status.csv unions
  origin's rows with ours (append-only log, deduplicated), all other state
  files take ours (later writer) — then pushes, verified against a
  simulated origin. Prevention: cron schedules staggered so no two
  workflows dispatch in the same minute (paper :15, research 02:45;
  guardian stays :00/:30).
- 2026-08-14, stale-universe mask: the committed universe.csv predated the
  perp-volume feature, so it ranked the perp universe alphabetically
  (0GUSDC first) instead of by venue volume. The 7-day freshness gate did
  not catch it because the file was recent. Every research run since had
  therefore been studying the alphabetically-first perps rather than the
  most liquid ones. Fix: is_legacy_universe() sentinel — any snapshot
  whose perp rows all carry zero volume is re-ingested regardless of age.
- 2026-08-14, dropped fix commit: an update of two commits was installed
  by cherry-picking only the bundle tip; the fix beneath it never reached
  main and the cron kept running without it. Caught from the operator's
  terminal output. Fix: scripts/install_bundle.sh cherry-picks the full
  range origin/main..bundle-head, and the installer is executed against a
  simulated origin before shipping.
- 2026-08-14, hostile-evidence blind spot: the regime-confound check
  passed slices whose hostile regime was never observed (fewer than 20
  hostile rows), silently. Such slices are now labelled hostile_unproven
  in validation, carried into the book, and counted in research summaries
  and the health digest.
- 2026-08-15, GitHub web-edit syntax breakage: browser copy/paste introduced
  indentation/syntax errors that halted `research`. Fix was full-file replacement
  plus reliance on CI compile gates. Operator note: prefer full-file replaces
  for web edits; avoid placeholder lines.
- 2026-08-15, VALR “simple-futures” private API unauthorized via API keys: /simple-futures/symbol-info works unauthenticated, but 
  private /simple-futures/* endpoints return HTTP 401 {"code": -93, "message": "Unauthorized"} when using a valid API key (View + 
  Trade). VALR support acknowledged and escalated (ticket [RM3PGP-R30W3]). Operational rule: do not spam these endpoints; re-test only 
  occasionally (e.g., once per day) and wait for VALR response before further integration work. Next polite status ping window: 2026-08- 
  20 to 2026-08-21 if no update.

## Known placeholders

Known placeholders and seams (do not tune without evidence):
- SPOT_FEE_BPS 20 / PERP_FEE_BPS 26 are first-pass simulations; they must
  be calibrated from realized paper fills before any live step.
- Per-slice hold-horizon: the book carries `horizon_bars` but the paper
  time-stop is still global (not per-slice). It is now controlled by
  `BREAKWATER_PAPER_TIME_STOP_BARS` (default 48). GitHub Actions currently
  sets it to 12. Per-slice horizon calibration is deferred (research-side feature).
- Trailing stop: supported in paper behind env flags (see Current posture),
  OFF by default; enable only with an evidence plan.
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

Operator note:
- `scripts/commit_state.sh` always pulls/pushes `origin main`. Running a workflow
  from a branch will still attempt to write state back to main unless you avoid
  calling commit_state.sh.

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
