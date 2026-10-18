#!/usr/bin/env python3
"""Seed ``slice_memory.csv`` from the realised paper trade log.

Slice memory (``research_lifecycle.sync_book``) only learns about a slice when
it rotates out *after* the feature shipped. Everything that rotated out
before -- including the 32 slices dropped on 2026-10-18 and the W38/W39
earners -- would otherwise return as strangers. This script writes one memory
entry per ``(slice_id, kind)`` that has at least one realised paper close,
with the same attribution rule ``reconcile_paper_stats_from_log`` uses, so
the numbers agree with the book's own paper_* columns.

Fields the log cannot tell us (times admitted/dropped, drop reason) are left
blank or marked ``backfilled_from_trade_log``. Entries already in memory are
left alone; this never overwrites what ``sync_book`` has recorded.

Usage: PYTHONPATH=src python3 scripts/backfill_slice_memory.py [--data-dir localdata]
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breakwater.research_lifecycle import (  # noqa: E402
    MEMORY_HEADERS,
    _write_memory,
    read_memory,
)

IGNORED_EXITS = {"regime", "not_book", "no_price", "adverse"}


def totals_from_log(log_path: Path) -> dict[tuple[str, str], dict]:
    totals: dict[tuple[str, str], dict] = {}
    if not log_path.exists():
        return totals
    with log_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("outcome") or "") not in {"win", "loss"}:
                continue
            if str(row.get("exit_reason") or "") in IGNORED_EXITS:
                continue
            sid = str(row.get("slice_id") or "")
            if not sid:
                continue
            key = (sid, str(row.get("kind") or "").strip().upper())
            bucket = totals.setdefault(key, {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0, "first": "", "last": ""})
            bucket["trades"] += 1
            try:
                pnl = float(row.get("pnl_zar") or 0.0)
            except (TypeError, ValueError):
                pnl = 0.0
            bucket["pnl"] += pnl
            if str(row.get("pnl_outcome") or row.get("outcome")) == "win" or pnl > 0:
                bucket["wins"] += 1
            else:
                bucket["losses"] += 1
            closed = str(row.get("closed_at") or "")
            if closed and (not bucket["first"] or closed < bucket["first"]):
                bucket["first"] = closed
            if closed > bucket["last"]:
                bucket["last"] = closed
    return totals


def backfill(research_dir: Path, *, now: datetime | None = None) -> tuple[int, int]:
    now = now or datetime.now(timezone.utc)
    memory_path = research_dir / "slice_memory.csv"
    memory = read_memory(memory_path)
    added = 0
    for key, stats in sorted(totals_from_log(research_dir / "paper_trade_log.csv").items()):
        if key in memory:
            continue
        entry = {h: "" for h in MEMORY_HEADERS}
        entry["slice_id"], entry["kind"] = key
        entry["first_validated_at"] = stats["first"]
        entry["last_dropped_at"] = stats["last"]
        entry["last_drop_reason"] = "backfilled_from_trade_log"
        entry["last_status"] = ""
        entry["paper_trades"] = str(stats["trades"])
        entry["paper_wins"] = str(stats["wins"])
        entry["paper_losses"] = str(stats["losses"])
        entry["paper_pnl_zar"] = f"{stats['pnl']:.4f}"
        memory[key] = entry
        added += 1
    _write_memory(memory_path, memory)
    return added, len(memory)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="localdata")
    args = parser.parse_args()
    research_dir = Path(args.data_dir) / "research"
    added, total = backfill(research_dir)
    print(f"slice memory: added {added} entries from the trade log; {total} total at {research_dir / 'slice_memory.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
