#!/usr/bin/env python3
"""Merge two versions of monitored_slices.csv when a state push races.

Why
---
``monitored_slices.csv`` has two writers. The research job decides the
*composition* (which slices are in the book, their edge fields, status on
admission). The paper job updates *per-slice paper columns* (trade counts,
P&L, cooldown, last signal bar) every hour. ``commit_state.sh`` resolves a
push race by ``git reset --hard origin/main`` and then restoring the role's
own copy of every owned file — so when the hourly paper job started before
research pushed and finished after, it restored a stale book over the fresh
one. Measured on committed state: 2026-10-16 (51→53 reverted after 4 min)
and 2026-10-21 (31→52 reverted after 8.6 min — an entire research cycle
discarded).

What
----
Column-wise merge. Rows and every non-paper column come from the
``--composition`` file. For slices present in both, the paper-owned columns
are taken from ``--paper-fields``; a cooldown recorded there also carries its
status. Slices only in ``--paper-fields`` are dropped (composition decides
membership). Output is written atomically to ``--out``.

Stdlib only, no breakwater import: this runs inside the persist step and must
not fail because of an unrelated import error.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

PAPER_FIELDS = (
    "paper_trades",
    "paper_wins",
    "paper_losses",
    "paper_pnl_zar",
    "last_signal_bar",
    "cooldown_until",
)
COOLDOWN = "cooldown"


def _read(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _key(row: dict) -> tuple[str, str]:
    return (str(row.get("slice_id") or ""), str(row.get("kind") or "").strip().upper())


def merge_rows(composition: list[dict], paper: list[dict]) -> tuple[list[dict], int]:
    """Return (merged rows, number of rows that took paper fields)."""
    by_key = {_key(row): row for row in paper}
    merged: list[dict] = []
    applied = 0
    for row in composition:
        out = dict(row)
        prior = by_key.get(_key(row))
        if prior is not None:
            for field in PAPER_FIELDS:
                if field in prior:
                    out[field] = prior[field]
            if str(prior.get("status") or "") == COOLDOWN and str(prior.get("cooldown_until") or ""):
                out["status"] = COOLDOWN
            applied += 1
        merged.append(out)
    return merged, applied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--composition", required=True, type=Path)
    parser.add_argument("--paper-fields", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    headers, composition = _read(args.composition)
    _, paper = _read(args.paper_fields)
    if not headers:
        print("merge_book_on_conflict: composition file has no header", file=sys.stderr)
        return 1
    merged, applied = merge_rows(composition, paper)

    tmp = args.out.with_name(args.out.name + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged)
    os.replace(tmp, args.out)
    print(
        f"merge_book_on_conflict: {len(merged)} rows from composition, "
        f"paper fields applied to {applied}, "
        f"{len(paper) - applied} stale rows not carried"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
