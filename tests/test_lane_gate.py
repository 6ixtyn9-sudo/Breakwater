"""Tests for the green-account lane/slice gate."""

from __future__ import annotations

import csv
from pathlib import Path

from breakwater.lane_gate import (
    GreenGate,
    compute_green_gate,
    filter_green_book_rows,
)


def _write_log(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "slice_id", "pair", "outcome", "exit_reason", "pnl_zar", "closed_at",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _row(slice_id, pnl, *, outcome="win", reason="target"):
    return {
        "slice_id": slice_id,
        "pair": "BTCUSDC",
        "outcome": outcome,
        "exit_reason": reason,
        "pnl_zar": str(pnl),
        "closed_at": "2026-08-30T12:00:00Z",
    }


def test_native_green_hip3_frozen(tmp_path):
    log = tmp_path / "paper_trade_log.csv"
    rows = [_row(f"native:{i}", 1.0) for i in range(15)] + [
        _row("hip3_xyz:feat_a", -2.0, outcome="loss", reason="stop")
        for _ in range(12)
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert gate.enabled is True
    assert gate.native_green is True
    assert gate.hip3_green is False
    # Native has enough evidence and is green; HIP-3 has reached the minimum
    # and still prints negative, so it is proven red and frozen.
    assert gate.frozen_lanes == {"hip3"}
    assert gate.warmup_lanes == set()
    assert gate.green("native_x") is True
    assert gate.green("hip3_xyz:feat_a") is False
    assert gate.should_exit("hip3_xyz:feat_a") is True
    assert gate.should_exit("native_x") is False


def test_green_island_survives_red_lane(tmp_path):
    log = tmp_path / "paper_trade_log.csv"
    green_slice = "hip3_xyz:good"
    red_slice = "hip3_xyz:red"
    rows = [
        _row(f"native:{i}", 1.0) for i in range(15)
    ] + [
        _row(green_slice, 2.0, reason="target"),
        _row(green_slice, 1.5, reason="trail_stop"),
        _row(green_slice, 1.0, reason="target"),
    ] + [
        _row(red_slice, -5.0, outcome="loss", reason="stop")
        for _ in range(7)
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    # Native is green; HIP-3 has 10 closes total but is red overall.
    assert gate.native_green is True
    assert gate.hip3_green is False
    assert "hip3" in gate.frozen_lanes
    # The single proven-positive HIP-3 slice is kept alive.
    assert gate.green(green_slice) is True
    assert green_slice in gate.green_islands
    # Negative and untested HIP-3 slices are frozen.
    assert gate.green(red_slice) is False
    assert gate.green("hip3_xyz:untested") is False


def test_cold_start_lane_is_warmup_not_frozen(tmp_path):
    """A fresh-slate lane has no evidence, so it must be allowed to trade
    rather than dead-locked. Only lanes that reach LANE_MIN_CLOSED and still
    print negative P&L are frozen (proven red)."""
    log = tmp_path / "paper_trade_log.csv"
    _write_log(log, [])
    gate = compute_green_gate(log)
    assert gate.enabled is True
    assert gate.native_green is False
    assert gate.hip3_green is False
    assert gate.frozen_lanes == set()
    assert gate.warmup_lanes == {"native", "hip3"}
    assert gate.green("native:any") is True
    assert gate.green("hip3_any:any") is True
    assert gate.should_exit("native:any") is False
    summary = gate.summary
    assert summary["warmup_lanes"] == ["hip3", "native"]
    assert summary["native"]["warmup"] is True
    assert summary["hip3"]["warmup"] is True


def test_cold_start_lane_allows_untested_slices(tmp_path):
    """A warm-up lane may keep trading untested slices so it can accumulate
    the closes the gate needs for a real verdict."""
    log = tmp_path / "paper_trade_log.csv"
    rows = [
        _row("native:a", 1.0, reason="target"),
        _row("native:a", 1.0, reason="target"),
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    # 2 closes < LANE_MIN_CLOSED (10): native is warm-up, not frozen.
    assert gate.native_green is False
    assert "native" in gate.warmup_lanes
    assert "native" not in gate.frozen_lanes
    # The slice has only 2 closes (< SLICE_MIN_CLOSED), so it is untested and
    # allowed to keep earning noise.
    assert gate.green("native:a") is True
    assert gate.should_exit("native:a") is False


def test_cold_start_proven_negative_slice_is_blocked(tmp_path):
    """Cold-start awareness must not let a proven-negative slice trade forever:
    once a slice reaches SLICE_MIN_CLOSED and is negative it is blocked, even
    while its lane is still warm-up."""
    log = tmp_path / "paper_trade_log.csv"
    rows = [
        _row("native:bad", -1.0, outcome="loss", reason="stop"),
        _row("native:bad", -1.0, outcome="loss", reason="stop"),
        _row("native:bad", -1.0, outcome="loss", reason="stop"),
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert "native" in gate.warmup_lanes
    assert "native:bad" in gate.blocked_slices
    assert gate.green("native:bad") is False
    assert gate.should_exit("native:bad") is True


def test_single_loss_does_not_freeze_green_lane_slice(tmp_path):
    # Red-team regression: one unlucky stop must NOT kill a slice, or the
    # paper engine starves itself into no-action.
    log = tmp_path / "paper_trade_log.csv"
    rows = [_row(f"native:{i}", 1.0) for i in range(15)] + [
        _row("native:one_loss", -2.0, outcome="loss", reason="stop"),
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert gate.green("native:one_loss") is True
    assert gate.should_exit("native:one_loss") is False
    assert "native:one_loss" not in gate.blocked_slices


def test_negative_slice_in_green_lane_is_blocked(tmp_path):
    log = tmp_path / "paper_trade_log.csv"
    rows = [_row(f"native:{i}", 1.0) for i in range(25)] + [
        _row("native:bad", -1.0, outcome="loss", reason="stop"),
        _row("native:bad", -1.0, outcome="loss", reason="stop"),
        _row("native:bad", -1.0, outcome="loss", reason="stop"),
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert gate.native_green is True
    assert "native:bad" in gate.blocked_slices
    assert gate.green("native:bad") is False
    assert gate.green("native:new") is True  # untested slice in a green lane is allowed


def test_filter_green_book_rows(tmp_path):
    log = tmp_path / "paper_trade_log.csv"
    rows = [
        {"slice_id": "native:good", "status": "monitored"},
        {"slice_id": "native:blocked", "status": "monitored"},
    ]
    _write_log(log, [_row(f"native:{i}", 1.0) for i in range(25)] + [
        _row("native:blocked", -1.0, outcome="loss", reason="stop"),
        _row("native:blocked", -1.0, outcome="loss", reason="stop"),
        _row("native:blocked", -1.0, outcome="loss", reason="stop"),
    ])
    gate = compute_green_gate(log)
    allowed, blocked = filter_green_book_rows(rows, gate)
    assert [r["slice_id"] for r in allowed] == ["native:good"]
    assert [r["slice_id"] for r in blocked] == ["native:blocked"]
    assert isinstance(gate, GreenGate)
