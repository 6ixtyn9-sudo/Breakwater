#!/usr/bin/env python3
"""Are we ready to trade VALR spot live, under the exit policy in force now?

Read-only. Promotes nothing, writes nothing, trades nothing.

This exists because "ready" is two different questions that get answered as
one, and they fail in different ways:

  EARNED   evidence that accrues by waiting - closed trades, shadow days,
           expectancy, profit factor, drawdown. Time fixes these.
  BUILT    mechanisms that no amount of waiting produces - a live executor
           for the book, a canary that has actually placed an order, a
           promotion registry row. Time fixes none of these.

A system can look ready on the first list while being unable to place a
single order, so both are printed and the verdict needs both.

The evidence half is deliberately narrow:

  * VALR spot only (kind == SPOT). The `native` lane pools VALR spot with
    Hyperliquid perps; a VALR question is not answered by Hyperliquid fills.
  * Current exit policy only. The ledger holds hundreds of closes from the
    retired +2R target. The gate wants >= 10 trades over >= 14 days, which
    those old closes already satisfy - so counting them would let a slice go
    live on the strength of mechanics that were removed.
  * One close per signal, inherited from promotion_evidence: the 28x LINKZAR
    artifact is not evidence.

Usage:
    PYTHONPATH=src python3 scripts/live_readiness.py
    PYTHONPATH=src python3 scripts/live_readiness.py --all-policies
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater.paper_trade import exit_policy_id  # noqa: E402
from breakwater.promotion_evidence import (  # noqa: E402
    ResearchEvidence,
    build_evidence,
    dedupe_by_signal,
    evaluate,
    filter_by_exit_policy,
    filter_by_kind,
    load_research_evidence,
    read_ledger,
    real_closes,
    summarise,
)

DATA = ROOT / "localdata"
LEDGER = DATA / "research" / "paper_trade_log.csv"

# Mirrors of promotion.PromotionGate's shadow-stage thresholds. Only used to
# print "x / y"; the actual verdict always comes from running the real gate,
# so a drift here misreports progress but can never wave anything through.
SHADOW_TRADES_REQUIRED = 10
SHADOW_DAYS_REQUIRED = 14
MIN_SLICE_TRADES = int(os.getenv("BREAKWATER_PROMOTION_MIN_SLICE_TRADES", "5"))


def _seed() -> float:
    try:
        return float(os.getenv("BREAKWATER_PAPER_EQUITY_SEED", "2000"))
    except ValueError:
        return 2000.0


def _bar(done: int, needed: int) -> str:
    return f"{done} / {needed}" + ("  OK" if done >= needed else f"  (need {needed - done} more)")


def built_blockers() -> list[tuple[str, bool, str]]:
    """Mechanisms that waiting does not produce. (name, ready, detail)."""
    registry = {}
    registry_path = DATA / "promotion_registry.json"
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text()).get("strategies") or {}
        except (OSError, json.JSONDecodeError):
            registry = {}
    live_capped = sum(
        1 for row in registry.values() if row.get("lifecycle") == "live_capped"
    )

    engine_src = (ROOT / "src" / "breakwater" / "engine.py").read_text()
    book_executor = 'payload.get("slice_id") != "big-wave"' not in engine_src

    risk_state = {}
    risk_path = DATA / "risk_state.json"
    if risk_path.exists():
        try:
            risk_state = json.loads(risk_path.read_text())
        except (OSError, json.JSONDecodeError):
            risk_state = {}
    pnl_events = len(risk_state.get("realized_pnl_events") or [])

    canary_marker = DATA / ".valr_spot_canary.json"

    return [
        (
            "live executor reaches the book",
            book_executor,
            "engine.operational_pass filters to slice_id=='big-wave'; the "
            "monitored book has no live path"
            if not book_executor
            else "book slices are reachable by the live executor",
        ),
        (
            "order path proven by canary",
            canary_marker.exists(),
            "TradeExecutor.execute has never run against the real VALR API"
            if not canary_marker.exists()
            else f"canary receipt at {canary_marker.name}",
        ),
        (
            "realized-P&L loss limits wired",
            True,
            f"reconciliation active; {pnl_events} realized event(s) booked so far"
            + (" (unexercised until something closes live)" if not pnl_events else ""),
        ),
        (
            "a strategy is live_capped",
            live_capped > 0,
            f"promotion registry holds {len(registry)} strategies, "
            f"{live_capped} live_capped",
        ),
        (
            "global live arm",
            os.getenv("BREAKWATER_MODE", "readonly") == "live",
            f"BREAKWATER_MODE={os.getenv('BREAKWATER_MODE', 'readonly')}, "
            f"BREAKWATER_LIVE_ACK={'set' if os.getenv('BREAKWATER_LIVE_ACK', 'off') != 'off' else 'off'}",
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all-policies",
        action="store_true",
        help="do not filter to the current exit policy (shows the mixed ledger)",
    )
    parser.add_argument("--kind", default="SPOT", help="SPOT (VALR) or PERP")
    parser.add_argument("--seed", type=float, default=None)
    args = parser.parse_args(argv)

    seed = args.seed if args.seed is not None else _seed()
    policy = None if args.all_policies else exit_policy_id()
    out: list[str] = []

    def add(line: str = "") -> None:
        out.append(line)

    add(f"# Live readiness — VALR {args.kind.lower()}, exit policy `{exit_policy_id()}`")
    add()
    add("> Read-only. Nothing here promotes, arms or trades.")
    add()

    rows = read_ledger(LEDGER)
    everything = real_closes(rows)
    in_kind = filter_by_kind(everything, args.kind)
    scoped = filter_by_exit_policy(in_kind, policy)
    counted = dedupe_by_signal(scoped)
    card = summarise(counted, seed_zar=seed)

    # ---- 1. earned evidence -------------------------------------------------
    add("## 1. Evidence earned under the current policy")
    add()
    unstamped = sum(1 for row in in_kind if not str(row.get("exit_policy") or ""))
    add(f"- Ledger real closes (all policies, all kinds): **{len(everything)}**")
    add(f"- ...of kind {args.kind.upper()}: **{len(in_kind)}** ({unstamped} predate the policy stamp)")
    add(f"- ...under `{policy or 'any policy'}`: **{len(scoped)}** -> **{len(counted)}** after one-close-per-signal")
    add()
    add(f"- Shadow trades: **{_bar(card.trades, SHADOW_TRADES_REQUIRED)}**")
    add(f"- Shadow days:   **{_bar(card.shadow_days, SHADOW_DAYS_REQUIRED)}**")
    if card.trades:
        add(
            f"- Expectancy: **{card.expectancy_zar:+.4f} ZAR/trade** | "
            f"net {card.net_zar:+.2f} | win {card.win_rate:.1%} | "
            f"PF {card.profit_factor:.2f} | maxDD {card.max_drawdown:.1%}"
        )
        add(f"- Window: {card.first_close} -> {card.last_close}")
    else:
        add(
            "- No qualifying closes yet. This is the correct reading, not a bug: "
            "the policy changed on 2026-09-29 and evidence starts from zero."
        )
    add()

    # ---- 2. per-slice gate verdicts ----------------------------------------
    add("## 2. Gate verdict per slice (real gate, not a mirror)")
    add()
    research = load_research_evidence(DATA)
    by_slice: dict[str, list[dict]] = {}
    for row in counted:
        by_slice.setdefault(str(row.get("slice_id") or ""), []).append(row)
    ranked = sorted(
        by_slice.items(), key=lambda kv: len(kv[1]), reverse=True
    )
    eligible = [(s, r) for s, r in ranked if len(r) >= MIN_SLICE_TRADES]
    if not eligible:
        add(
            f"_No slice has {MIN_SLICE_TRADES}+ closes under this policy yet "
            f"({len(ranked)} slice(s) have any)._"
        )
    for slice_id, slice_rows in eligible:
        slice_card = summarise(slice_rows, seed_zar=seed)
        evidence = build_evidence(
            strategy_id=slice_id,
            card=slice_card,
            research=research.get(slice_id, ResearchEvidence()),
        )
        decision = evaluate(evidence, live_armed=False)
        add(
            f"- `{slice_id}` — {slice_card.trades} closes, "
            f"{slice_card.expectancy_zar:+.3f} ZAR/trade, PF {slice_card.profit_factor:.2f} "
            f"→ **{decision.lifecycle.value}**"
        )
        for reason in decision.reasons:
            add(f"    - blocked: {reason}")
    add()

    # ---- 3. built mechanisms ------------------------------------------------
    add("## 3. Mechanisms (not earned by waiting)")
    add()
    blockers = built_blockers()
    for name, ready, detail in blockers:
        add(f"- {'READY  ' if ready else 'MISSING'} | **{name}** — {detail}")
    add()

    # ---- 4. verdict ---------------------------------------------------------
    missing = [name for name, ready, _ in blockers if not ready]
    evidence_short = (
        card.trades < SHADOW_TRADES_REQUIRED or card.shadow_days < SHADOW_DAYS_REQUIRED
    )
    add("## 4. Verdict")
    add()
    if missing or evidence_short:
        add("**NOT READY.**")
        add()
        if evidence_short:
            add(
                f"- Evidence: {card.trades}/{SHADOW_TRADES_REQUIRED} trades, "
                f"{card.shadow_days}/{SHADOW_DAYS_REQUIRED} days under `{exit_policy_id()}`."
            )
        for name in missing:
            add(f"- Missing mechanism: {name}")
    else:
        add("**Evidence and mechanisms both clear.** Arming is still a human decision.")
    add()

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
