#!/usr/bin/env python3
"""Union two versions of an append-only weekly CSV when a state push races.

Why
---
The positioning tape (``localdata/positioning/<week>.csv``) and the paper
skip log (``localdata/research/paper_skip_log/<week>.csv``) are append-only:
every hourly paper job adds one hour of rows and never rewrites earlier
ones. ``commit_state.sh`` resolves a push race by ``git reset --hard
origin/main`` and restoring the role's own copy of each owned file. When the
hourly jobs overlap (a job pinned to the checkout it was dispatched with,
finishing after the next job already pushed), that restore replaces the
other job's hour with this job's hour. Measured on committed state at the
2026-W43 -> W44 rotation: W44 alternated {00:00} -> {01:00} -> {00:00,02:00}
-> {01:00,02:00} across four pushes; hour 00:00 was lost for good and the
previous week's ``.gz`` flip-flopped between two different contents.

What
----
Row union. Rows from ``--origin`` come first in their original order, then
rows from ``--mine`` that are not already present. Identity is the tuple of
``--key`` columns when given and present in both headers, otherwise the whole
row. The header is taken from ``--origin`` (``--mine`` if origin is missing);
rows from the other file are re-mapped by column name so a header drift does
not shift values. Either input and the output may be gzipped — decided by the
``.gz`` suffix. Output is written atomically to ``--out``.

Stdlib only, no breakwater import: this runs inside the persist step and must
not fail because of an unrelated import error.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import os
import sys
from pathlib import Path

csv.field_size_limit(10**8)


def _open_text(path: Path, mode: str, packed: bool | None = None):
    if packed is None:
        packed = path.suffix == ".gz"
    if packed:
        return gzip.open(path, mode + "t", encoding="utf-8", newline="")
    return path.open(mode, encoding="utf-8", newline="")


def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with _open_text(path, "r") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        rows = [dict(r) for r in reader]
    return header, rows


def _identity(row: dict[str, str], header: list[str], key: list[str]) -> tuple:
    if key:
        return tuple(str(row.get(k, "") or "") for k in key)
    return tuple(str(row.get(h, "") or "") for h in header)


def merge_rows(
    origin_header: list[str],
    origin_rows: list[dict[str, str]],
    mine_header: list[str],
    mine_rows: list[dict[str, str]],
    key: list[str] | None = None,
) -> tuple[list[str], list[dict[str, str]]]:
    header = origin_header or mine_header
    if not header:
        return [], []
    use_key = [k for k in (key or []) if k in header]
    if key and (len(use_key) != len(key) or any(k not in mine_header for k in key if mine_header)):
        # Key not fully present on both sides: fall back to whole-row identity.
        use_key = []
    seen: set[tuple] = set()
    out: list[dict[str, str]] = []
    for row in origin_rows:
        ident = _identity(row, header, use_key)
        if ident in seen:
            continue
        seen.add(ident)
        out.append({h: row.get(h, "") for h in header})
    for row in mine_rows:
        mapped = {h: row.get(h, "") for h in header}
        ident = _identity(mapped, header, use_key)
        if ident in seen:
            continue
        seen.add(ident)
        out.append(mapped)
    return header, out


def _write_atomic(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with _open_text(tmp, "w", packed=path.suffix == ".gz") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--origin", required=True, type=Path, help="origin/main copy (may be absent)"
    )
    parser.add_argument("--mine", required=True, type=Path, help="this role's copy (may be absent)")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--key",
        default="",
        help="comma-separated identity columns; whole row when empty or not present on both sides",
    )
    args = parser.parse_args(argv)

    key = [k.strip() for k in args.key.split(",") if k.strip()]
    origin_header, origin_rows = _read(args.origin)
    mine_header, mine_rows = _read(args.mine)
    if not origin_header and not mine_header:
        print("merge_append_log_on_conflict: both inputs missing or empty", file=sys.stderr)
        return 1
    header, rows = merge_rows(origin_header, origin_rows, mine_header, mine_rows, key)
    _write_atomic(args.out, header, rows)
    print(
        f"merge_append_log_on_conflict: origin={len(origin_rows)} mine={len(mine_rows)} "
        f"merged={len(rows)} -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
