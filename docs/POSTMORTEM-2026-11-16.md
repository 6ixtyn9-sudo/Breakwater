# Final-read post-mortem — 2026-11-16

The binding read time was **2026-11-16 00:00Z**. The last
`main` state available at that cutoff was commit
`1e8f43d95f085fb4895792b1d764502770a4e596` (2026-11-15 23:38Z); the next
scheduled research run began after the read and is excluded.

## Verdict

**FAIL; no second extension.** Criterion A was **1/3** qualifying global
positioning slices. Criterion B was **28/30 strict real closes, +23.68 ZAR**:
P&L sign was positive, but the required count was missed. Both criteria required
a pass.

The earlier status message that called B **31/30, +24.35 ZAR** a pass was
wrong: it counted three `slice_gap` rows that are not real closes under the
agreed `lane_gate._is_real_close` / `ACTUAL_EXITS` definition. The correction
below is the authoritative final read; the old exploratory number is not a
pass.

## A — persistence

The three completed research runs before the cutoff were:

| Run stamp (UTC) | State snapshot |
|---|---|
| 2026-11-13 00:29:39 | `b3cf26b` |
| 2026-11-14 00:25:22 | `c98f32b` |
| 2026-11-15 00:32:43 | `5bfc7ce` |

Only one global positioning `slice_id` appeared in all three snapshots:
`feat_funding_rate:2:SHORT:h24`. `slice_memory.csv` shows no drop after
2026-11-06 through the 11-15 run, so it was continuously held across these
three runs. No other global positioning ID survived all three. Result: **1 of
the 3 required slices**.

**Measurement correction:** the 10-31 handover note said `validated_at` was
carried unchanged while a slice remained in the book. Source and state show
that `sync_book` refreshes `validated_at` when a row is promoted again, even
when the ID already exists; `slice_memory` records that row as `held`. Therefore
timestamp equality alone is not a drop test. For this read, consecutive book
presence plus the memory drop history establishes the one qualifying slice.
Future reads should use explicit per-run membership / memory evidence rather
than infer continuity from the timestamp field alone.

## B — strict global positioning closes

Population: the six global positioning feature prefixes, excluding `@oi_`
cohort slices. A close counts only when `lane_gate._is_real_close(row)` is
true (`outcome` win/loss and `exit_reason` in `lane_gate.ACTUAL_EXITS`). The
ledger at the cutoff contained 31 positioning rows with win/loss outcomes,
for raw P&L of +24.35 ZAR. Three had `exit_reason=slice_gap`; that reason is
not in `ACTUAL_EXITS`. Removing those rows gives:

- **28 strict real closes**, 19 wins / 9 losses
- **+23.68 ZAR** net P&L
- By exit: 11 `trail_stop` / +31.73; 13 `horizon` / +4.83; 4 `stop` / −12.88
- The three excluded `slice_gap` rows total +0.66 ZAR (one on 11-01 and two
  on 11-05); they remain in the ledger but do not count toward this criterion.

The strict 11-09 checkpoint (`76f8446`) recomputes to 24 closes / +18.21 ZAR;
the 11-16 read is therefore **+4 strict closes / +5.47 ZAR** from that
checkpoint. The frozen 11-09 handover mark of 27 / +18.88 is preserved as the
historical reported mark; it included the same three non-`ACTUAL_EXITS` rows
and is not the strict comparator. This restatement does not change the
pre-registered threshold.

All four additional strict positioning closes occurred 11-10 through 11-13.
The last was `feat_oi_ret_div:2:SHORT:h24` on BTCUSDC, +4.34 ZAR at
2026-11-13 10:39Z. There were no further strict global positioning closes by
the final read. The result is a positive sample with **insufficient flow**,
not a count pass.

## Machinery and total paper P&L at the read

The runtime-only cache fix (#37) had been merged without changing signal,
entry, or exit decisions. The first seven post-merge hourly paper runs
(11-15 06:00–12:00Z) all succeeded; the first waited 23m26s in queue and ran
4m40s, while the next six completed in roughly 3–5 minutes. The throughput
repair improved cycle completion, but did not produce enough global
positioning closes to meet B.

At the final-read digest, the unchanged paper account showed equity
**2,392.83 ZAR**, **+392.83 ZAR** lifetime on 591 strict closes; +22.92 today,
+86.83 over 7 days, and +93.11 over 30 days. Native was +437.33 ZAR (545
closes); HIP-3 was −44.50 ZAR (46 closes), red/frozen. Realized versus claimed
edge remained **NOT ESTABLISHED** (t=0.53). The gate was NOT READY. Three
native paper positions were open with 13.99 ZAR stop-risk; HIP-3 had none. No
live orders were placed. These account-wide figures are context only and do
not override the positioning criteria.

A same-predicate reconstruction at the 11-09 checkpoint is 570 real closes /
+348.97 ZAR, versus 591 / +392.83 at the final read (**+21 closes / +43.86
ZAR** across the extension). The frozen handover marks are retained; this
strict reconstruction is shown so future comparisons can be apples-to-apples.

## Findings

1. **Persistence failed.** Only one global positioning ID stayed in the book
   over the last three research runs; the other IDs rotated or dropped.
2. **Trade flow failed the predeclared count.** The extension added four strict
   global positioning closes, all by 11-13, leaving the lane two short of 30.
   The positive +5.47 ZAR incremental result does not satisfy the count rule.
3. **The runtime defect was real, and its fix was isolated.** Scan completion
   improved, but faster scans did not create validated positioning flow at the
   existing 1,000-bar setting. This supports the pre-stated finding rather
   than another waiting period.
4. **The first B reading was a measurement error.** Raw `outcome` rows are not
   interchangeable with `_is_real_close`; three `slice_gap` rows inflated the
   count from 28 to 31. Future engine ledgers and reports must make the
   population explicit.
5. **The edge remains unproven.** Positive overall and positioning P&L are not
   enough to establish claimed alpha; the final-read realized-versus-claimed
   test was not significant. No live trading or promotion is justified.

## Parallel-engine work boundary

The approved failure plan remains in force: keep the existing hourly paper
engine unchanged as a non-promoting shadow/control; keep the guardian
read-only; place no live orders; do not mix the new lane into the baseline
book. The post-mortem is complete.

The evidence-backed candidate already scoped in
[`market_neutral_engine.md`](market_neutral_engine.md) is the market-neutral
spread engine. Its pre-paper evidence gate is **not met**: on the three runs
above spread research had 0, 0, then 1 qualifying spread; the 11-15
`feat_vwap_dist:L2S0:h12` candidate was +12.6 bps, below the predeclared +15
bps magnitude bar, and it did not qualify on three consecutive runs. Engine
engineering may proceed in an isolated namespace, but **no paper entries or
workflow activation** until that evidence gate passes.

The parallel lane's paper-stage acceptance criterion is predeclared as at
least **30 completed pair positions with net P&L ≥ 0**, after both legs' fees,
realized funding, and the documented slippage haircut. A pair is one unit for
this count, not two leg rows. State, book, positions, ledger, and status must
remain under `localdata/parallel_spread/`; no shared baseline files, promotion
registry, guardian inputs, or live executor. The existing hourly control is
not modified.

## Shadow-control status after the read (2026-11-19 18:39Z)

The latest digest still reports the baseline paper account in observation mode:
605 strict closes, lifetime **+382.03 ZAR**, −2.07 today, +31.01 over 7 days,
and +99.00 over 30 days. Native is +426.53 ZAR; HIP-3 is −44.50 and frozen.
The green gate is NOT READY; realized versus claimed remains NOT ESTABLISHED
(t=0.13). Seven native paper positions were open with 15.90 ZAR stop-risk;
HIP-3 remained frozen with no open positions. The latest scan had zero errors;
the last 24 scheduled-run records showed 23 successes and one run still in
progress. This later account movement does not reopen the 11-16 read or change
its verdict.
