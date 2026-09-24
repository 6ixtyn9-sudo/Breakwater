# Post-merge state — 2026-09-24

This file is the committed record of the follow-up `status.csv` / daily-print
fix, landed on `main` on 2026-09-24. The defects it describes are **fixed**.
The dated snapshot and its addendum below are kept as the historical record of
what was found and what changed.

## Snapshot — 2026-09-24 (before the fix)

`status.append_status` capped the `detail` column with `str(detail)[:4000]`.
Every `mode=shadow` scan is larger than that, and because payloads are written
with sorted keys, `green_gate.blocked_slices` (the biggest value) sits before
`paper` — so the cut always destroyed the paper block. Verified against the
real data:

- 161 of 504 rows in `localdata/status.csv` were cut mid-string and
  unparseable.
- The committed `localdata/daily/latest.md` printed
  `Paper shadow ledger: **0.00 / 0.00 ZAR | 0.0% | None**` and
  `signals=None … closed=None new_signals=None` — fabricated readings in the
  honest record.
- `scripts/simulate_evidence_capacity.py`, which skips unparseable rows, was
  fitting episode intensity on **1 scan out of 337**.

## Addendum — the follow-up fix

- `append_status` now bounds the detail at 64 000 chars and, if a payload ever
  exceeds that, drops the bulkiest keys while recording `_truncated` (dropped
  keys + original length) — so the column stays valid JSON that names its own
  loss instead of being cut mid-string.
- `daily_print` resolves the newest shadow scan that is actually readable,
  reuses it for sections 5 and 13, and prints which scan it used when the
  newest one is unreadable.
- Historic rows are untouched: the fix applies forward only. The committed
  `localdata/daily/latest.md` keeps its fabricated readings until the next
  state-commit run regenerates it with the fix in place — daily prints are
  never retro-edited.

Changed files: `src/breakwater/status.py`, `scripts/daily_print.py`,
`src/breakwater/engine.py`, `tests/test_status.py`,
`tests/test_daily_print_verdict.py`, this document.
