"""Print the honest paper scorecard and its promotion verdict.

Read-only by default. ``--write-registry`` records the verdict for each slice
evaluated; LIVE_CAPPED is only reachable when ``--live-armed`` is passed *and*
``BREAKWATER_LIVE_ACK`` matches the acknowledgement string, because the gate
itself refuses to promote without the global arm.

Usage:
    PYTHONPATH=src python3 scripts/promotion_evidence.py
    PYTHONPATH=src python3 scripts/promotion_evidence.py --lane native
    PYTHONPATH=src python3 scripts/promotion_evidence.py --slice feat_close_pos_ma:1:LONG:h24
    PYTHONPATH=src python3 scripts/promotion_evidence.py --write-registry
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater.config import LIVE_ACKNOWLEDGEMENT  # noqa: E402
from breakwater.models import Lifecycle  # noqa: E402
from breakwater.promotion import PromotionRegistry  # noqa: E402
from breakwater.promotion_evidence import (  # noqa: E402
    ResearchEvidence,
    build_evidence,
    load_research_evidence,
    dedupe_by_signal,
    drops_for_lane,
    evaluate,
    read_ledger,
    real_closes,
    summarise,
    summary_lines,
)

DATA = ROOT / "localdata"
LEDGER = DATA / "research" / "paper_trade_log.csv"
REGISTRY = DATA / "promotion_registry.json"
# Minimum closes before a slice gets its own registry row: below this the gate
# verdict is noise wearing a schema.
MIN_SLICE_TRADES = int(os.getenv("BREAKWATER_PROMOTION_MIN_SLICE_TRADES", "5"))
RESEARCH_EMPTY = ResearchEvidence()


def _seed() -> float:
    try:
        return float(os.getenv("BREAKWATER_PAPER_EQUITY_SEED", "2000"))
    except ValueError:
        return 2000.0


def _live_armed(requested: bool) -> bool:
    if not requested:
        return False
    return os.getenv("BREAKWATER_LIVE_ACK", "off") == LIVE_ACKNOWLEDGEMENT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=["native", "hip3"], default=None)
    parser.add_argument("--slice", dest="slice_id", default=None)
    parser.add_argument("--seed", type=float, default=None)
    parser.add_argument("--write-registry", action="store_true")
    parser.add_argument(
        "--live-armed",
        action="store_true",
        help="allow the gate to return live_capped (also requires BREAKWATER_LIVE_ACK)",
    )
    args = parser.parse_args(argv)

    seed = args.seed if args.seed is not None else _seed()
    research = load_research_evidence(DATA)
    rows = read_ledger(LEDGER)
    if not rows:
        print(f"no ledger at {LEDGER}; nothing to score")
        return 1

    # Two populations, kept distinct on purpose: the gate population the lane
    # verdict reads (ACTUAL_EXITS) and every real fill in the ledger. The
    # difference between them is printed rather than silently dropped.
    gate_rows = drops_for_lane(real_closes(rows), args.lane)
    every_fill = drops_for_lane(
        [r for r in rows if str(r.get("outcome") or "") in {"win", "loss"}], args.lane
    )
    if args.slice_id:
        gate_rows = [r for r in gate_rows if str(r.get("slice_id")) == args.slice_id]
        every_fill = [r for r in every_fill if str(r.get("slice_id")) == args.slice_id]
    counted = dedupe_by_signal(gate_rows)

    print("# Breakwater promotion evidence")
    print()
    print(
        "Ledger rows: {rows} | real closes in the gate population: {n} | "
        "all real fills: {all}".format(rows=len(rows), n=len(gate_rows), all=len(every_fill))
    )
    print(
        "Basis: one close per signal_id (a signal is one decision; duplicate "
        "closes of the same signal_id are the artifact, not the evidence)."
    )
    print()

    for line in summary_lines(
        label="ALL LANES" if not args.lane else f"LANE {args.lane}",
        lane=args.lane,
        raw_closes=gate_rows,
        all_fills=every_fill,
        seed_zar=seed,
    ):
        print(line)
    print()

    # Per-slice scorecards, so a slice can be judged on its own record rather
    # than on the lane's.
    by_slice: dict[str, list[dict]] = {}
    for row in counted:
        by_slice.setdefault(str(row.get("slice_id") or ""), []).append(row)
    ranked = sorted(
        by_slice.items(), key=lambda item: -summarise(item[1], seed_zar=seed).net_zar
    )

    print("Per-slice scorecards (ranked by net ZAR, one close per signal):")
    decisions: list[tuple[str, object, object]] = []
    for slice_id, closes in ranked:
        card = summarise(closes, seed_zar=seed)
        evidence = build_evidence(
            strategy_id=f"paper:{slice_id}", card=card, research=research.get(slice_id)
        )
        decision = evaluate(evidence, live_armed=_live_armed(args.live_armed))
        decisions.append((slice_id, evidence, decision))
        flag = "" if card.trades >= MIN_SLICE_TRADES else "  (below min closes)"
        print(
            f"  {slice_id:44s} n={card.trades:3d} net={card.net_zar:+9.2f} "
            f"pf={card.profit_factor:5.2f} dd={card.max_drawdown * 100:5.2f}% "
            f"-> {decision.lifecycle.value}{flag}"
        )
        if decision.reasons:
            for reason in decision.reasons:
                print(f"      - {reason}")

    if ranked:
        print()
        print("Gate field mapping for the top slice (auditable, not assumed):")
        top = decisions[0][1]
        for field, (source, value) in (research.get(ranked[0][0]) or RESEARCH_EMPTY).mapped_fields.items():
            if source.startswith("paper"):
                continue
            shown = getattr(top, field, value)
            print(f"  {field:22s} = {shown}  <- {source}")
        print(
            "  reconciliation_passes / protection_passes are live-canary counters; "
            "paper leaves them at 0 by design."
        )
    print()
    verdicts = Counter(decision.lifecycle.value for _, _, decision in decisions)
    print("Verdicts: " + ", ".join(f"{k}={v}" for k, v in sorted(verdicts.items())))
    print(
        "Live arm: "
        + ("ARMED" if _live_armed(args.live_armed) else "not armed (live_capped unreachable)")
    )

    if args.write_registry:
        registry = PromotionRegistry(REGISTRY)
        written = 0
        for slice_id, evidence, decision in decisions:
            if evidence.shadow_trades < MIN_SLICE_TRADES:
                continue
            registry.update(decision, evidence)
            written += 1
        print(f"Registry rows written: {written} -> {REGISTRY}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
