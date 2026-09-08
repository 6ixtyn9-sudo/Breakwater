#!/usr/bin/env python3
"""Shadow bootstrap score of the CURRENT monitored book.

Read-only instrumentation. It promotes nothing, blocks nothing, freezes
nothing and writes no book, no paper state and no position. It produces a
table and nothing else.

Why this exists
---------------
Production research scores a (feature, state, side, horizon) cell with a naive
t-test, ``mean / (std / sqrt(n))``, over pooled bars. Those bars are
overlapping forward windows sampled every bar across cross-correlated symbols,
so ``n`` massively overstates the independent information: a 1,000-hour window
holds roughly 20 independent 48-hour blocks, not 14,711.

The deep-history audit already contains the honest estimator (a 48h block
bootstrap). Run over 5,000 candles it passed 0 of 3,744 native candidates with
a best p of 0.3854, while production validated 779 of 3,744 at p=0.0000. This
script asks the narrow, decision-relevant question the audit does not:

    for the slices we are actually trading today, what does the honest
    estimator say?

It is not a gate. Do not wire it into promotion until the table has been read
and argued over. A negative answer here is a fact about the estimator, the
universe and the window - it is NOT proof that no edge exists, and it must
never be used on its own to retire a lane.

Usage
-----
    PYTHONPATH=src python scripts/book_audit.py --lane native
    PYTHONPATH=src python scripts/book_audit.py --lane hip3
    PYTHONPATH=src python scripts/book_audit.py --lane all --candles 2000

Output
------
    localdata/audit/book_bootstrap.csv   one row per book slice
    localdata/audit/book_summary.json    counts + the survivors
    stdout                               the same table
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "localdata"
sys.path.insert(0, str(ROOT / "src"))

from breakwater.deep_research_audit import (  # noqa: E402
    FEATURE_COLUMNS,
    _evaluate,
    _fetch_group,
    _groups,
)
from breakwater.discovery import prepare_pooled  # noqa: E402

NATIVE_BOOK = DATA / "research" / "monitored_slices.csv"
HIP3_BOOK = DATA / "hip3" / "research" / "monitored_slices.csv"
OUT_DIR = DATA / "audit"

HEADERS = [
    "lane",
    "group",
    "slice_id",
    "feature",
    "state",
    "side",
    "horizon_bars",
    "book_status",
    "book_edge_bps",
    "book_n",
    "book_p_value",
    "paper_trades",
    "paper_pnl_zar",
    "audit_n",
    "symbols_used",
    "weighted_mean_bps",
    "recent_1000_mean_bps",
    "weighted_effective_n",
    "block_bootstrap_p",
    "positive_symbol_fraction",
    "cluster_count",
    "positive_cluster_fraction",
    "survives_p20",
]


@dataclass(frozen=True)
class _BookSlice:
    """Exactly the attributes ``_evaluate`` and stop calibration consume."""

    feature: str
    state: int
    side: str
    horizon_bars: int
    kind: str
    slice_id: str


def _parse_slice_id(slice_id: str):
    """Split a book slice id into (lane, group, feature, state, side, horizon).

    Native:  feat_ext_vs_ma_50:0:LONG:h24
    HIP-3:   hip3_xyz_equity_c0:feat_ext_vs_ma_50:0:LONG:h24
    """
    raw = str(slice_id or "").strip()
    if raw.startswith("hip3_"):
        lane = "hip3"
        rest = raw[len("hip3_") :]
        group, _, tail = rest.partition(":")
    else:
        lane = "native"
        group = "native_crypto_c0"
        tail = raw
    parts = tail.split(":")
    # feature:state:side:hN  - a slice in an unknown shape is skipped, not guessed.
    if len(parts) != 4:
        return None
    feature, state_text, side, horizon_text = parts
    if not feature.startswith("feat_"):
        return None
    try:
        state = int(state_text)
        horizon = int(str(horizon_text).lstrip("hH"))
    except (TypeError, ValueError):
        return None
    return lane, group, feature, state, str(side).upper(), horizon


def _read_book(path: Path):
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bps(value: float) -> float:
    return round(value * 10_000.0, 4)


def run_book_audit(*, lane: str, max_pairs: int, candle_count: int) -> dict:
    if lane not in {"native", "hip3", "all"}:
        raise ValueError("book audit lane must be native, hip3, or all")

    books = []
    if lane in {"native", "all"}:
        books.extend(("native", row) for row in _read_book(NATIVE_BOOK))
    if lane in {"hip3", "all"}:
        books.extend(("hip3", row) for row in _read_book(HIP3_BOOK))

    wanted: dict[tuple[str, str], list[tuple[dict, _BookSlice]]] = {}
    skipped: list[tuple[str, str]] = []
    for book_lane, row in books:
        slice_id = str(row.get("slice_id") or "")
        parsed = _parse_slice_id(slice_id)
        if parsed is None:
            skipped.append((slice_id, "unparseable_slice_id"))
            continue
        parsed_lane, group, feature, state, side, horizon = parsed
        if parsed_lane != book_lane:
            skipped.append((slice_id, f"lane_mismatch:{parsed_lane}"))
            continue
        if feature not in FEATURE_COLUMNS:
            skipped.append((slice_id, f"unknown_feature:{feature}"))
            continue
        candidate = _BookSlice(
            feature=feature,
            state=state,
            side=side,
            horizon_bars=horizon,
            kind="PERP",
            slice_id=slice_id,
        )
        wanted.setdefault((book_lane, group), []).append((row, candidate))

    groups = {f"{g.lane}:{g.name}": g for g in _groups(lane, max_pairs=max_pairs, data_dir=DATA)}
    sleep_seconds = float(os.getenv("BREAKWATER_CANDLE_PAGE_SLEEP_SECONDS", "0.05"))
    rows: list[dict] = []
    fetch_errors: dict[str, str] = {}
    groups_used = []

    for (book_lane, group_name), entries in sorted(wanted.items()):
        group = groups.get(f"{book_lane}:{group_name}")
        if group is None:
            for row, _ in entries:
                skipped.append((str(row.get("slice_id")), f"no_audit_group:{group_name}"))
            continue
        pooled, errors = _fetch_group(group, candle_count=candle_count, sleep_seconds=sleep_seconds)
        fetch_errors.update(errors)
        if pooled.empty:
            for row, _ in entries:
                skipped.append((str(row.get("slice_id")), "no_candles"))
            continue
        groups_used.append(f"{book_lane}:{group_name}")
        # prepare_pooled is the expensive step; do it once per distinct horizon.
        prepared_by_horizon: dict[int, object] = {}
        for row, candidate in entries:
            horizon = candidate.horizon_bars
            if horizon not in prepared_by_horizon:
                prepared_by_horizon[horizon] = prepare_pooled(
                    pooled, FEATURE_COLUMNS, group.cost_bps, horizon_bars=horizon
                )
            result = _evaluate(
                prepared_by_horizon[horizon], candidate, lane=book_lane, group=group_name
            )
            bootstrap_p = _num(result.get("block_bootstrap_p"), 1.0)
            rows.append(
                {
                    "lane": book_lane,
                    "group": group_name,
                    "slice_id": candidate.slice_id,
                    "feature": candidate.feature,
                    "state": candidate.state,
                    "side": candidate.side,
                    "horizon_bars": horizon,
                    "book_status": row.get("status") or "",
                    "book_edge_bps": _bps(_num(row.get("mean_ret_costadj"))),
                    "book_n": int(_num(row.get("n"))),
                    "book_p_value": round(_num(row.get("p_value")), 6),
                    "paper_trades": int(_num(row.get("paper_trades"))),
                    "paper_pnl_zar": round(_num(row.get("paper_pnl_zar")), 2),
                    "audit_n": int(_num(result.get("n"))),
                    "symbols_used": int(_num(result.get("symbols_used"))),
                    "weighted_mean_bps": _bps(_num(result.get("weighted_5000_mean"))),
                    "recent_1000_mean_bps": _bps(_num(result.get("recent_1000_mean"))),
                    "weighted_effective_n": round(_num(result.get("weighted_effective_n")), 1),
                    "block_bootstrap_p": round(bootstrap_p, 6),
                    "positive_symbol_fraction": round(
                        _num(result.get("positive_symbol_fraction")), 4
                    ),
                    "cluster_count": int(_num(result.get("cluster_count"))),
                    "positive_cluster_fraction": round(
                        _num(result.get("positive_cluster_fraction")), 4
                    ),
                    "survives_p20": bool(bootstrap_p <= 0.20),
                }
            )

    rows.sort(key=lambda r: (r["lane"], r["block_bootstrap_p"], -r["weighted_mean_bps"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "book_bootstrap.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    survivors = [r for r in rows if r["survives_p20"]]
    scored = len(rows)
    summary = {
        "lane": lane,
        "candles_requested": candle_count,
        "max_pairs": max_pairs,
        "book_rows_scored": scored,
        "book_rows_skipped": len(skipped),
        "skipped_sample": skipped[:10],
        "groups_used": groups_used,
        "fetch_error_count": len(fetch_errors),
        "fetch_errors": dict(list(fetch_errors.items())[:10]),
        "promotion_enabled": False,
        "is_gate": False,
        "survivors_p20": len(survivors),
        "survivor_slice_ids": [r["slice_id"] for r in survivors],
        "median_block_bootstrap_p": (
            round(float(np.median([r["block_bootstrap_p"] for r in rows])), 6) if rows else None
        ),
        "best_block_bootstrap_p": (round(min(r["block_bootstrap_p"] for r in rows), 6) if rows else None),
        "output": str(OUT_DIR / "book_bootstrap.csv"),
    }
    (OUT_DIR / "book_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def _print_table(summary: dict) -> None:
    path = OUT_DIR / "book_bootstrap.csv"
    if not path.exists():
        return
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    print()
    print(f"{'lane':7s} {'slice_id':52s} {'h':>3s} {'bookEdge':>9s} {'bookP':>7s} "
          f"{'audEdge':>8s} {'bootP':>7s} {'posSym':>7s} {'paperPnL':>9s}")
    print("-" * 118)
    for r in rows:
        flag = "  <-- survives" if r["survives_p20"] == "True" else ""
        print(
            f"{r['lane'][:7]:7s} {r['slice_id'][:52]:52s} {r['horizon_bars']:>3s} "
            f"{r['book_edge_bps']:>9s} {r['book_p_value'][:6]:>7s} "
            f"{r['weighted_mean_bps']:>8s} {r['block_bootstrap_p'][:6]:>7s} "
            f"{r['positive_symbol_fraction']:>7s} {r['paper_pnl_zar']:>9s}{flag}"
        )
    print("-" * 118)
    print(f"scored {summary['book_rows_scored']} | survivors at p<=0.20: "
          f"{summary['survivors_p20']} | best p: {summary['best_block_bootstrap_p']} | "
          f"median p: {summary['median_block_bootstrap_p']}")
    print()
    print("bookEdge = the production naive-t-test edge currently justifying the slice.")
    print("bootP    = the same slice under a 48h block bootstrap.")
    print("This is a table, not a gate. It changes nothing.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane", default="native", choices=["native", "hip3", "all"])
    parser.add_argument("--candles", type=int, default=2000,
                        help="hourly candles per symbol (default 2000)")
    parser.add_argument("--max-pairs", type=int, default=60)
    args = parser.parse_args()
    summary = run_book_audit(
        lane=args.lane, max_pairs=args.max_pairs, candle_count=args.candles
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    _print_table(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
