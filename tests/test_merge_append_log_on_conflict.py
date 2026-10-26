"""Unit tests for scripts/merge_append_log_on_conflict.py (row union)."""

from __future__ import annotations

import csv
import gzip
import importlib.util
import io
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "merge_append_log_on_conflict.py"


def _load():
    spec = importlib.util.spec_from_file_location("merge_append_log_on_conflict", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _rows(text: str) -> tuple[list[str], list[dict]]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader.fieldnames or []), [dict(r) for r in reader]


HEADER = "snapshot_at,snapshot_hour,coin,funding_hourly\n"


def test_union_keeps_both_hours_and_dedupes_on_key():
    mod = _load()
    origin = _rows(
        HEADER + "2026-10-26T01:08Z,2026-10-26T01:00Z,BTC,1\n"
        "2026-10-26T01:08Z,2026-10-26T01:00Z,ETH,2\n"
    )
    mine = _rows(
        HEADER + "2026-10-26T00:05Z,2026-10-26T00:00Z,BTC,0\n"
        "2026-10-26T01:40Z,2026-10-26T01:00Z,BTC,9\n"
    )  # same key, later capture
    header, rows = mod.merge_rows(*origin, *mine, key=["snapshot_hour", "coin"])
    assert header == ["snapshot_at", "snapshot_hour", "coin", "funding_hourly"]
    keys = [(r["snapshot_hour"], r["coin"]) for r in rows]
    assert keys == [
        ("2026-10-26T01:00Z", "BTC"),
        ("2026-10-26T01:00Z", "ETH"),
        ("2026-10-26T00:00Z", "BTC"),
    ]
    # Origin wins on a key collision; mine's duplicate is not appended.
    assert rows[0]["funding_hourly"] == "1"


def test_union_falls_back_to_whole_row_without_key():
    mod = _load()
    origin = _rows("closed_at,outcome\n2026-10-26T00:09Z,skipped\n")
    mine = _rows("closed_at,outcome\n2026-10-26T00:09Z,skipped\n2026-10-26T01:09Z,skipped\n")
    _, rows = mod.merge_rows(*origin, *mine, key=[])
    assert [r["closed_at"] for r in rows] == ["2026-10-26T00:09Z", "2026-10-26T01:09Z"]


def test_cli_handles_gzip_in_and_out(tmp_path):
    origin = tmp_path / "w.csv"
    origin.write_text(HEADER + "a,2026-10-25T22:00Z,BTC,1\n")
    mine = tmp_path / "w.csv.gz"
    with gzip.open(mine, "wt", newline="") as handle:
        handle.write(HEADER + "b,2026-10-25T21:00Z,BTC,0\n")
    out = tmp_path / "out.csv.gz"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--origin",
            str(origin),
            "--mine",
            str(mine),
            "--out",
            str(out),
            "--key",
            "snapshot_hour,coin",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    with gzip.open(out, "rt", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["snapshot_hour"] for r in rows] == ["2026-10-25T22:00Z", "2026-10-25T21:00Z"]


def test_cli_missing_origin_copies_mine(tmp_path):
    mine = tmp_path / "w.csv"
    mine.write_text(HEADER + "a,2026-10-26T00:00Z,BTC,1\n")
    out = tmp_path / "out.csv"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--origin",
            str(tmp_path / "absent.csv"),
            "--mine",
            str(mine),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.read_text() == mine.read_text()
