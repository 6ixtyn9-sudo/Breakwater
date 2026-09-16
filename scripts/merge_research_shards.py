#!/usr/bin/env python3
"""Merge sharded research outputs into canonical files.

Run after parallel research shards complete. Combines:
  - discovered_slices_shard*.csv → discovered_slices.csv
  - validated_slices_shard*.csv → validated_slices.csv
  - asset_edges_shard*.csv → asset_edges.csv

Then runs sync_book() to promote validated slices to the monitored book.
"""

from __future__ import annotations

import csv
import glob
import os
import sys
from pathlib import Path

DATA_DIR = Path(os.getenv("BREAKWATER_DATA_DIR", "localdata"))
RESEARCH_DIR = DATA_DIR / "research"


def merge_csvs(pattern: str, output: Path) -> int:
    """Merge all files matching pattern into output. Returns total rows."""
    files = sorted(glob.glob(str(RESEARCH_DIR / pattern)))
    if not files:
        print(f"  No files matching {pattern}")
        return 0

    all_rows: list[dict] = []
    fieldnames: list[str] = []

    for fpath in files:
        with open(fpath, newline="") as f:
            reader = csv.DictReader(f)
            if not fieldnames and reader.fieldnames:
                fieldnames = list(reader.fieldnames)
            for row in reader:
                all_rows.append(row)

    if not fieldnames:
        print(f"  No data in {pattern}")
        return 0

    # Deduplicate by slice_id (keep last occurrence = most recent shard)
    seen: dict[str, dict] = {}
    for row in all_rows:
        sid = row.get("slice_id", "")
        seen[sid] = row

    deduped = list(seen.values())

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(f"  {pattern}: {len(files)} files, {len(all_rows)} raw rows → {len(deduped)} deduped → {output.name}")
    return len(deduped)


def main() -> None:
    print("Merging research shards...")

    merge_csvs("discovered_slices_shard*.csv", RESEARCH_DIR / "discovered_slices.csv")
    merge_csvs("validated_slices_shard*.csv", RESEARCH_DIR / "validated_slices.csv")
    merge_csvs("asset_edges_shard*.csv", RESEARCH_DIR / "asset_edges.csv")

    # Run sync_book to promote validated slices
    print("\nRunning sync_book...")
    sys.path.insert(0, "src")
    from breakwater.research_lifecycle import sync_book

    book_path = RESEARCH_DIR / "monitored_slices.csv"
    validated_path = RESEARCH_DIR / "validated_slices.csv"

    summary = sync_book(
        validated_path=validated_path,
        book_path=book_path,
    )
    print(f"sync_book result: {summary}")

    # Clean up shard files
    for pattern in ("discovered_slices_shard*.csv", "validated_slices_shard*.csv", "asset_edges_shard*.csv"):
        for fpath in glob.glob(str(RESEARCH_DIR / pattern)):
            os.remove(fpath)
            print(f"  Cleaned up {os.path.basename(fpath)}")

    print("\nDone. Canonical files ready for paper cycle.")


if __name__ == "__main__":
    main()
