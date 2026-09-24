# Spot venue remediation

Four changes, in the order they were asked for. Nothing here is armed: the
canary mechanism exists but live mode is still blocked, deliberately.

## 1. Re-entry accounting

**What was wrong.** The paper ledger counted a signal as many times as it
closed. On the 2026-09-24 ledger: 251 counted closes from 208 distinct
signal_ids, and the 43 duplicate closes carried **+387.65 ZAR of the +474.64
lifetime P&L**. The worst case was LINKZAR
`feat_close_pos_ma:1:LONG:h24`, whose signal `0be56cd44780fb6e` closed **28
times over three days** — every close entered at 160.39, every close an exact
+2R target at 166.003650, every close "held" for one bar — while the market was
already trading ~3.5% above that entry. Deduplicated to one close per signal
the spot lane is **+13.50 ZAR, not +398.78**.

**What changed** (`src/breakwater/paper_trade.py`):

- `ONE_ENTRY_PER_SIGNAL` (env `BREAKWATER_PAPER_ONE_ENTRY_PER_SIGNAL`, default on):
  a signal_id that is open, or that has already closed a position, cannot open
  another. Guard rows are **not** entries — a signal refused by the
  falling-knife or regime guard stays eligible, so a guard that fires once
  cannot silently retire the signal.
- `THROUGH_TARGET_GUARD` (env `BREAKWATER_PAPER_THROUGH_TARGET_GUARD`, default
  on): the exact mirror of the inherited falling-knife guard. If the latest
  price has already reached the +2R target, the trade is over — filling at the
  signal close would book a profit the market never offered.
- Both refusals are journaled (`exit_reason` `reentry` / `through_target`,
  `entry_guard` `reentry_blocked` / `through_target_blocked`) and counted in the
  cycle summary, so a guard that cannot see a price never pretends it blocked
  anything.

History is **not** rewritten: the ledger and the book keep their bytes. The
guards only bind from now on.

## 2. Venue cost re-basis

**What was wrong.** Cost is a property of the pair; the book treated it as a
property of the kind. `feat_close_pos_ma:1:LONG:h24` sat in the book as a
**PERP** row with a 21 bps edge, while all 37 of its paper closes were **SPOT**
fills on VALR ZAR pairs at a real **70 bps** round trip. The mean capture never
covered the fee.

Three separate leaks, all closed:

1. **Promotion floor** (`research_lifecycle._cost_bps`): a pooled SPOT slice can
   fire on ZAR pairs, so its floor follows the dearest venue it can reach —
   70 bps, giving a **140 bps** bar at `BREAKWATER_MIN_NET_EDGE_COST_MULT=2`
   instead of the old 40 bps crypto basis.
2. **Monitor gate** (`monitor.venue_cost_floor`): on every candidate pair, a
   SPOT row's edge must clear that pair's own round trip with headroom
   (`BREAKWATER_VENUE_COST_MULT`, default 2). ZAR → 140 bps, USDC/USDT → 40 bps.
   The perp book is untouched: its cost is uniform at 9 bps and is already
   governed by the research floor.
3. **Attribution** (`research_lifecycle.reconcile_paper_stats_from_log`): book
   paper stats are keyed by `(slice_id, kind)`, not `slice_id`. The PERP row had
   inherited all 37 SPOT fills and their +283.35 ZAR — which is what made it a
   "green island" propping up a frozen lane.

Fiat-quoted spot is also no longer excluded from the research pool
(`engine.py`): it is researched at its true 70 bps cost instead. Excluding a
venue from research never excluded it from fills; it only hid the cost.

## 3. The honest record

`scripts/promotion_evidence.py` (`src/breakwater/promotion_evidence.py`) prints
a scorecard from the committed ledger:

```
PYTHONPATH=src python3 scripts/promotion_evidence.py
PYTHONPATH=src python3 scripts/promotion_evidence.py --lane native
```

It reports **both** numbers — one close per signal, and the raw ledger figure —
plus every population delta by name (e.g. fills outside `lane_gate.ACTUAL_EXITS`),
so the scorecard can be reconciled against the daily print instead of replacing
it. It then evaluates the promotion gate per slice.

Current state (2026-09-24 ledger):

| | |
|---|---|
| Counted closes, one per signal | 208 over 9 days (2026-09-15 → 09-24) |
| Net | **+86.99 ZAR** (raw ledger: +474.64) |
| Win rate | 51.9% |
| Profit factor | 1.35 |
| Max drawdown | 3.65% of peak equity |
| Mean net R | +0.146 |
| Verdicts | 74 × `research_only`, 2 × `shadow_candidate` |

The two `shadow_candidate` slices (`feat_ext_strength:2:LONG:h15`,
`feat_close_pos_ma:1:LONG:h24`) are blocked on one thing only: **fewer than 14
shadow days**. They have 12 and 10 counted closes, positive expectancy,
PF > 1.2 and ~1% drawdown. That is the clock the operator wanted to start.

## 4. The capped canary

`src/breakwater/canary.py` holds the preset as executable code
(`CANARY_MANDATE`), validated through the same schema production uses:

| field | value |
|---|---|
| initial_equity_zar | 500.00 |
| absolute_equity_floor_zar | 450.00 |
| max_total_loss_zar | 50.00 |
| max_drawdown_fraction | 0.10 |
| daily / seven-day loss limit | 15.00 / 30.00 |
| max_aggregate_open_risk_zar | 10.00 |
| max_position_notional_zar | 100.00 |
| risk_per_trade_zar | 5.00 |
| max_positions | 1 |
| max_effective_leverage / perp_leverage_cap | 1 / 1 |

**The aggregate risk leash is wired.** `engine.guardian()` used to pass
`aggregate_open_risk_zar=Decimal(0)`, which reads as "nothing at risk" and meant
the policy's limit could never fire. It is now measured from the live book —
the distance from each position to its own resting stop
(`account.aggregate_open_stop_risk_zar`) — and anything unmeasurable (a stop
price or FX rate that will not resolve) is reported as **unknown** and fails
closed (`RiskManager.check_account(..., aggregate_open_risk_unknown=True)`).

### Arming is a deliberate, two-key act

Nothing below happens automatically, and the promotion gate refuses
`LIVE_CAPPED` without all of it:

1. Wait for the shadow clock. `scripts/promotion_evidence.py` must show the
   slice at `shadow_validated` or better — currently blocked at
   `shadow_candidate` on the 14-day rule.
2. Record the evidence:
   `PYTHONPATH=src python3 scripts/promotion_evidence.py --write-registry`
   (harmless without arming: rows land at `research_only` / `shadow_*`).
3. `reconciliation_passes` and `protection_passes` are counted by a live
   canary run; paper cannot manufacture them, which is why they sit at 0.
4. Only then set `BREAKWATER_MANDATE_JSON` to the canary preset,
   `BREAKWATER_MODE=live` and `BREAKWATER_LIVE_ACK=I_ACCEPT_BREAKWATER_LIVE_RISK`.

`startup_assertions()` raises `GuardianHalt` until a `live_capped` row exists,
credentials are present and the mandate is configured — so the last step cannot
be done by accident.

## 5. VALR Perps retired (venue choke)

**What was wrong.** `guardian()` raised `GuardianHalt` whenever perp state was
unverifiable **in live mode**. VALR Perps answers HTTP 401 on every
authenticated `/simple-futures` call with a valid, correctly-scoped key —
`scripts/perps_canary.py` exists to prove it, and it used to end with "will
detect automatically when this changes". That choke is at the venue and will
not clear, so the halt made **live mode impossible to start**, spot included,
permanently and silently.

The halt existed so live trading would not run blind on perp exposure. That
concern does not reach here: the executor refuses VALR futures unconditionally
(`PerpetualActivationBlocked`), so the system cannot open a VALR perp position
to be blind to. Hyperliquid remains the authoritative perp venue with its own
read-only position state.

**What changed** (`engine.py`):

- `VALR_PERPS_RETIRED` (env `BREAKWATER_VALR_PERPS_RETIRED`, default **on**).
  Retired → a 401 is an expected state: `perps_api: "retired"`, the error text
  kept for evidence, no halt.
- `BREAKWATER_VALR_PERPS_RETIRED=0` restores the previous halt **exactly**.
  The retirement is a named switch, not a deleted check.
- If the venue ever answers, the data is still used — equity, exposure and
  `perps_api: "available"` — so the retirement cannot hide real positions.
- Residual risk, stated in the code: a position opened by hand in the VALR web
  app would not be visible on this path. That is what the switch is for.
- The daily print now reads `VALR perps: **retired** (venue choke, not used;
  Hyperliquid is the perp venue)` with the last probe one line down, instead of
  reporting a permanent failure as if it were a transient one.
