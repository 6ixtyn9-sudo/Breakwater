"""Read-only readout of the shadow exit policies.

The paper engine mirrors every real open position into five shadow exit
policies (see src/breakwater/paper_counterfactual.py). Those shadows never
create orders, so reading them costs nothing. Nothing in the digest reports
their results today: the only place the counterfactual log surfaces in
daily_print.py is as a row count labelled "ghost rows" in section 7.

Two questions this answers, in order:

1. Is the mirror trustworthy? target_2r_trail_1r is the control policy: it
   is meant to reproduce the real exit, so any disagreement with the actual
   trade is a measurement error, not a result. This classifies each
   disagreement by cause and reports how many comparisons survive.

2. On the surviving comparisons only, does a wider target or a wider trail
   beat the control? A ranking computed over all rows is contaminated by
   whatever broke the control; the clean subset is the honest number.

Run: python3 scripts/trail_report.py
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "localdata"
LOG = DATA / "research" / "paper_counterfactual_log.csv"
CONTROL = "target_2r_trail_1r"

# Exits the shadow cannot produce: the gate liquidating a frozen lane, prices
# that went stale, and rotation to a better slice. These are real-world
# interventions on the actual trade, not differences in exit policy.
UNMIRRORABLE = {"lane_gate", "stale_data", "rotated"}


def dec(value, default=Decimal(0)) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default
    return number if number.is_finite() else default


def horizon_bars(slice_id: str) -> int:
    match = re.search(r":h(\d+)$", slice_id or "")
    return int(match.group(1)) if match else 0


def main() -> int:
    if not LOG.exists():
        print(f"missing {LOG}")
        return 1
    rows = list(csv.DictReader(LOG.open(newline="")))
    if not rows:
        print("counterfactual log is empty")
        return 1

    # ---- 1. classify every control disagreement by cause -------------------
    control = [r for r in rows if r["policy"] == CONTROL]
    causes: Counter[str] = Counter()
    clean: set[str] = set()
    for row in control:
        delta = dec(row.get("delta_vs_actual_zar"))
        same_reason = row.get("exit_reason") == row.get("actual_exit_reason")
        if abs(delta) <= Decimal("0.01") and same_reason:
            causes["agree (usable)"] += 1
            clean.add(row["signal_id"])
            continue
        actual = (row.get("actual_exit_reason") or "").strip()
        if actual in UNMIRRORABLE:
            causes[f"unmirrorable actual exit: {actual}"] += 1
        elif dec(row.get("bars_held")) > horizon_bars(row.get("slice_id", "")) > 0:
            causes["held past horizon (r_gate extension)"] += 1
        elif abs(delta) > Decimal("0.01") and same_reason:
            causes["same exit reason, different price"] += 1
        else:
            causes["unexplained"] += 1

    print(
        f"counterfactual log: {len(rows)} completed shadow exits, "
        f"{len({r['signal_id'] for r in rows})} mirrored positions"
    )
    print(f"\n1. CONTROL INTEGRITY ({len(control)} control comparisons)")
    for cause, count in causes.most_common():
        print(f"   {count:>3}  {cause}")
    print(f"   -> usable comparisons: {len(clean)}/{len(control)}")

    # ---- 2. policy ranking, all rows vs clean subset ----------------------
    def rank(subset: list[dict], title: str) -> None:
        print(f"\n2. {title} (n={len(subset)} mirrored positions)")
        base: Decimal | None = None
        for policy in sorted({r["policy"] for r in subset}):
            sub = [r for r in subset if r["policy"] == policy]
            pnl = sum(dec(r["pnl_zar"]) for r in sub)
            wins = sum(1 for r in sub if dec(r["pnl_zar"]) > 0)
            gb = (sum(dec(r.get("peak_giveback_r")) for r in sub) / len(sub)) if sub else 0
            if policy == CONTROL:
                base = pnl
            print(
                f"   {policy:<20} n={len(sub):>3}  pnl={pnl:>+8.2f}  "
                f"win%={100 * wins / max(len(sub), 1):>5.1f}  giveback={gb:>+5.2f}R"
            )
        if base is not None:
            print("   vs control:")
            for policy in sorted({r["policy"] for r in subset}):
                if policy == CONTROL:
                    continue
                sub = [r for r in subset if r["policy"] == policy]
                pnl = sum(dec(r["pnl_zar"]) for r in sub)
                print(
                    f"   {policy:<20} {pnl - base:>+8.2f} ZAR "
                    f"({(pnl - base) / max(len(sub), 1):>+6.2f} per trade)"
                )

    rank(rows, "all comparisons (contaminated by control failures)")
    if clean:
        rank([r for r in rows if r["signal_id"] in clean], "clean comparisons only")
    else:
        print("\n   no clean comparisons: the mirror cannot support a decision yet")

    # ---- 3. the concentrated slice ---------------------------------------
    by_slice: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    counts: Counter[str] = Counter()
    for row in rows:
        sid = row["slice_id"]
        counts[sid] += 1
        by_slice[sid][row["policy"]] += dec(row["pnl_zar"])
    top = [s for s, _ in counts.most_common(3)]
    print("\n3. busiest slices (this is where the book is concentrated)")
    for sid in top:
        row = by_slice[sid]
        best = max(row.items(), key=lambda kv: kv[1])
        ctrl = row.get(CONTROL, Decimal(0))
        print(
            f"   {sid:<42} rows={counts[sid]:>3}  control={ctrl:>+7.2f}  "
            f"best={best[0]}={best[1]:+7.2f} ({best[1] - ctrl:+.2f})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
