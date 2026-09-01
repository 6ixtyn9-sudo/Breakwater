# Second-opinion review brief: green gate + per-asset research

This file exists so an independent reviewer who cannot see the original
conversation can review the work from the repo alone. Read this, then the code
it points to, then answer the **Open questions** at the bottom. The repo is on
branch `arena/01a052f8-breakwater`.

- Review commit: `3770647` ("feat: green gate + per-asset research for native/hip-3 long/short")
- Test + lint state at commit time: 271 passed, `ruff check .` clean.
- Warning: the commit also carries earlier, entangled work (short-inventory,
  regime-tracker, HIP-3 class-breadth, daily print/report). That extra scope was
  an explicit user decision; it is not the focus of this review. Judge the two
  mission items below, not the bundled extras.

## Mission (what was supposed to be built)

Two high-ROI items:
1. **Green gate** — per-slice loser eviction. Only let money keep flowing where
   it has printed green. (Prior weekend replay claimed +7.11 improvement.)
2. **Per-asset research** — pooled validation proves a *market-state* edge, but
   the monitor previously traded every matching pair. New: per-symbol verdicts
   so the monitor skips only assets research proved do not carry the edge.

Both must apply to **native AND HIP-3**, and to **LONG AND SHORT**.

## 1. Green gate

Files: `src/breakwater/lane_gate.py`, `src/breakwater/paper_trade.py`,
`src/breakwater/engine.py`.

### Semantics (implemented)

- Lane is green iff `closed >= BREAKWATER_GREEN_LANE_MIN_CLOSED` (default 10)
  **and** lane P&L > 0. Native and HIP-3 judged separately.
- Non-green lane is **frozen**: no new entries from it; open positions in it are
  defensively exited (`should_exit` returns true).
- **Green islands**: inside a frozen lane, a slice with `>= 3` closed trades and
  positive P&L keeps trading (so a red lane can keep its one working slice).
- Inside a green lane, a slice is blocked only once it has `>= 3` closed trades
  and net P&L <= 0. 0–2 closes is untested → allowed.
- Exits that count as "real" are `ACTUAL_EXITS = {stop, trail_stop, target,
  horizon, rotated, time_stop, regime_shift, lane_gate}`. Guard/skip rows are
  excluded.
- `filter_green_book_rows` splits book rows into allowed + blocked; engine calls
  it on the native book and on the HIP-3 book (engine lines ~709, ~744).
- Paper cycle consumes it via `green_gate` arg (`paper_trade.py`) — `green()`
  gates new entries, `should_exit()` forces defensive exits.
- `BREAKWATER_GREEN_GATE=1` default; explicit in `.github/workflows/paper.yml`.

### Data inputs

Paper trade log `localdata/research/paper_trade_log.csv`. Green gate state is
recomputed each shadow scan (no persistent gate file). It reports
`green_gate` (summary) in paper result + status detail.

## 2. Per-asset research

Files: `src/breakwater/validation.py` (AssetEdge), `src/breakwater/monitor.py`,
`src/breakwater/engine.py`, `src/breakwater/hip3_research.py`,
`src/breakwater/config.py`.

### Semantics (implemented)

- `validate_slices()` already computes stop-aware net returns and walk-forward
  fold boundaries. It now also, when passed `asset_edges=`, calls
  `_compute_asset_edges_for_slice()` for **every candidate** (both sides, all
  horizons). So per-asset rows fall out of the existing validation pass — no
  separate expensive loop.
- Per asset inside a slice:
  - `n` = count of finite net rows for that asset in-state.
  - `mean_net` = mean of those net returns.
  - `folds_with_rows` = folds containing `>= PER_ASSET_FOLD_MIN_ROWS` (3) rows
    for that asset.
  - `folds_positive` = those folds whose asset row mean > 0.
  - `fold_positive_fraction` = `folds_positive / folds_with_rows` (0 if no folds).
- Verdict:
  - `n < PER_ASSET_MIN_ROWS` (20) → **untested** (`insufficient_rows`), allowed.
  - `mean_net > 0 AND fold_positive_fraction >= 0.60` (or `folds_with_rows == 0`)
    → **green**.
  - otherwise → **blocked** (`not_green_per_asset`).
- **Important asymmetry / design intent:** only proven-not-green assets are
  blocked. Untested assets are allowed so action is never zeroed.
- `AssetEdge` fields include folds_positive, folds_with_rows, fold_positive_fraction,
  asset_status, reason. CSV write/read roundtrip via `write_asset_edges` /
  `read_asset_edges`.
- Lookup key = `(slice_id, asset.upper())`, so HIP-3 symbols like `XYZ:AMD`
  resolve against uppercase monitor pairs.

### Flow

- Native: `engine.research_pass()` writes `localdata/research/asset_edges.csv`.
- HIP-3: `run_hip3_research()` writes `localdata/hip3/research/asset_edges.csv`.
- `engine.shadow_scan()` builds lookups for both, passes them into `monitor_book`
  for native and HIP-3, and reports `per_asset_gate` (row counts + a
  green/blocked/untested breakdown per lane) in paper result + status detail.
- `monitor.monitor_book(..., asset_edge_lookup=...)`: if `(slice_id, pair.upper())`
  resolves to `blocked`, the signal is skipped with `guard=asset_not_green`.
  `green`/`untested` → allowed. A lookup key that is absent (not in the file)
  is also allowed.
- **Fail-closed on missing evidence:** `read_asset_edges` no longer returns `[]`
  when `asset_edges.csv` is missing — it raises `RuntimeError` so a paper cycle
  cannot silently trade without the per-asset gate. A bad schema also raises.
  An existing-but-empty file is still allowed (research ran, zero per-asset
  verdicts), which keeps the "untested is allowed" intent intact.
- `scripts/commit_state.sh` persists both `asset_edges.csv` files.
- Workflows `research.yml` + `hip3-research.yml` export
  `BREAKWATER_PER_ASSET_MIN_ROWS` (20), `...MIN_FOLD_POSITIVE_FRACTION` (0.60),
  `...FOLD_MIN_ROWS` (3).

## Tests

- `tests/test_lane_gate.py` (5): native-green/hip3-frozen, green island survives
  red lane, single loss does not freeze green slice, negative slice in green lane
  blocked, `filter_green_book_rows`.
- `tests/test_per_asset_edges.py` (8): unit verdicts (green/blocked/untested),
  public `validate_slices` LONG+SHORT emission, monitor blocks only proven
  not-green, untested allowed, green allowed, HIP-3 upper lookup, CSV roundtrip,
  canonical env-name guard.

## Open questions — please answer these directly

1. **Green gate thresholds.** Are lane-min-closed=10, slice-min-closed=3,
   island-min-closed=3, and "positive P&L" the right calibrations? The +7.11
   weekend replay is not visible here — is the gate credible from these defaults
   alone, or is it liable to freeze the whole book (especially HIP-3 with few
   closed trades)?
2. **Green-island exception.** In a frozen lane, any slice with >=3 closes and
   positive P&L keeps trading. Is that a principled exception or an escape hatch
   that lets a red lane keep most of its volume?
3. **Per-asset `n` floor / fold rule.** MIN_ROWS=20 and FOLD_MIN_ROWS=3. On real
   data, many `(slice, asset)` pairs will be `untested` and therefore allowed —
   this could mean the per-asset gate does little filtering in practice. Is that
   acceptable, or should `untested` be treated differently?
4. **Fold alignment.** Fold boundaries are computed on the *pooled* (sorted)
   rows, not per asset. Assets unevenly distributed across time may have most of
   their rows in 1–2 folds, so `folds_with_rows` can be tiny. Does that make the
   per-asset verdict trustworthy?
5. **Verdict logic edge cases.** An asset with `mean_net > 0` but
   `folds_with_rows == 0` is marked `green`. Is that a bug (no fold evidence) or
   an acceptable "allow" bias given the untested-asymmetry philosophy? An asset
   with a small positive mean but 1/5 positive folds is `blocked` — is that the
   intended strength/flexibility trade-off?
6. **Interaction of the two gates.** Green gate is trade-log based (paper
   history); per-asset is research based (out-of-fold). Do they conflict or
   double-penalize? E.g. a slice with a losing paper history but strong fresh
   per-asset research: which should win?
7. **Native/HIP-3 parity.** Anything in the per-asset or green-gate path that
   behaves differently for HIP-3 than native (symbol casing, `slice_id` prefix,
   sparse HIP-3 logs, `asset_edges.csv` not present yet)?
8. **Operational risk.** The code is validated on synthetic frames. What is the
   highest-risk thing that could go wrong on the *first real* Actions research →
   asset_edges.csv → shadow-scan cycle? (Schema mismatch, missing file
   behaviour, key casing, gate default action when data is absent.)
9. **Anything that should NOT be merged.** If you had authority over the merge,
   what (if anything) would you block on before this goes to main?

## Repro

```bash
cd /home/user/Breakwater
PYTHONPATH=src:/home/user/Breakwater/scripts python -m pytest tests/test_lane_gate.py tests/test_per_asset_edges.py -q
PYTHONPATH=src:/home/user/Breakwater/scripts python -m pytest -q          # full suite
python -m ruff check .
```
