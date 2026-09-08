"""Tests for the green-account lane/slice gate."""

from __future__ import annotations

import csv
from pathlib import Path

from breakwater.lane_gate import (
    ACTUAL_EXITS,
    GreenGate,
    compute_green_gate,
    filter_green_book_rows,
    lane_tradability,
)


def _write_log(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "slice_id",
        "pair",
        "outcome",
        "exit_reason",
        "pnl_zar",
        "closed_at",
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
        _row("hip3_xyz:feat_a", -2.0, outcome="loss", reason="stop") for _ in range(12)
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
    # Forced liquidation is retired: a red lane blocks ENTRIES. It does not
    # dump open positions at the latest close any more.
    assert not hasattr(gate, "should_exit")


def test_green_island_survives_red_lane(tmp_path):
    log = tmp_path / "paper_trade_log.csv"
    green_slice = "hip3_xyz:good"
    red_slice = "hip3_xyz:red"
    rows = (
        [_row(f"native:{i}", 1.0) for i in range(15)]
        + [
            _row(green_slice, 2.0, reason="target"),
            _row(green_slice, 1.5, reason="trail_stop"),
            _row(green_slice, 1.0, reason="target"),
        ]
        + [_row(red_slice, -5.0, outcome="loss", reason="stop") for _ in range(7)]
    )
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
    # An untested slice is admitted on purpose: a frozen lane that admits only
    # islands can never test a new idea, so it can never rebuild its record.
    # It is an audition, not a verdict - see native_proven below.
    assert gate.green("hip3_xyz:untested") is True


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
    _write_log(
        log,
        [_row(f"native:{i}", 1.0) for i in range(25)]
        + [
            _row("native:blocked", -1.0, outcome="loss", reason="stop"),
            _row("native:blocked", -1.0, outcome="loss", reason="stop"),
            _row("native:blocked", -1.0, outcome="loss", reason="stop"),
        ],
    )
    gate = compute_green_gate(log)
    allowed, blocked = filter_green_book_rows(rows, gate)
    assert [r["slice_id"] for r in allowed] == ["native:good"]
    assert [r["slice_id"] for r in blocked] == ["native:blocked"]
    assert isinstance(gate, GreenGate)


def test_forced_liquidation_is_retired(tmp_path):
    """A red lane must NOT force-close open positions.

    Regression for the 02-08 Sep bleed: 32 of 72 closes (44%) were forced
    `lane_gate` exits, and the ghost control scored +4.56 ZAR/trade better on
    the 31 liquidated trades (+141.4 ZAR) while matching real exits to the cent
    on every natural exit. The gate blocks new money; it does not dump
    positions, which is what the stop, target and horizon are for.
    """
    log = tmp_path / "paper_trade_log.csv"
    rows = [_row(f"native:{i}", 1.0) for i in range(15)] + [
        _row("hip3_xyz:feat_a", -2.0, outcome="loss", reason="stop") for _ in range(12)
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert "hip3" in gate.frozen_lanes
    # Entry gating still bites hard...
    assert gate.green("hip3_xyz:feat_a") is False
    # ...but there is no exit mechanism left to call.
    assert not hasattr(gate, "should_exit")
    assert "lane_gate" in ACTUAL_EXITS  # historical rows stay countable


def test_lane_gate_historical_rows_stay_countable():
    """`lane_gate` must remain an actual exit.

    Dropping it would retroactively recount every lane's closes and silently
    rewrite the statistics the gate reads to make its next verdict.
    """
    assert "lane_gate" in ACTUAL_EXITS


def test_coma_lane_is_reported(tmp_path):
    """A frozen lane with no proven slice is the state to shout about.

    Audition slots mean a frozen lane is rarely unable to trade, so "zero
    tradable" is no longer the alarm. A lane trading only on slices that have
    never earned anything is the modern form of the same trap: activity without
    accumulated evidence. It must be reported loudly rather than sitting behind
    a green "operational" runner.
    """
    log = tmp_path / "paper_trade_log.csv"
    rows = [_row("native:a", -2.0, outcome="loss", reason="stop") for _ in range(12)]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert "native" in gate.frozen_lanes

    # Book full of slices, none of which is a green island -> coma.
    book = [f"native:s{i}" for i in range(20)]
    report = lane_tradability(gate, book, [])
    assert report["native_proven"] == 0  # nothing earned a record
    assert report["native_tradable"] == 20  # all 20 are auditions
    assert report["coma_lanes"] == ["native"]
    assert report["coma"] is True


def test_tradable_island_prevents_coma_but_is_counted(tmp_path):
    """One surviving green island is the difference between frozen and dead."""
    log = tmp_path / "paper_trade_log.csv"
    island = "native:island"
    rows = [_row("native:a", -2.0, outcome="loss", reason="stop") for _ in range(12)] + [
        _row(island, 3.0, reason="target") for _ in range(4)
    ]
    _write_log(log, rows)
    gate = compute_green_gate(log)
    assert "native" in gate.frozen_lanes

    book = ["native:a", "native:b", island]
    report = lane_tradability(gate, book, [])
    # Only the island is proven; native:a is blocked on its record and native:b
    # is admitted as an audition, so tradable and proven now differ.
    assert report["native_proven"] == 1
    assert report["native_tradable_slices"] == ["native:b", island]
    # Not coma yet - but this is the one-bad-trade-from-death state.
    assert report["coma_lanes"] == []
    assert report["coma"] is False


def test_no_coma_when_lane_is_not_frozen(tmp_path):
    """Warm-up and green lanes are never reported as coma, even if tiny."""
    log = tmp_path / "paper_trade_log.csv"
    _write_log(log, [_row("native:a", 1.0)])
    gate = compute_green_gate(log)
    assert "native" not in gate.frozen_lanes
    report = lane_tradability(gate, ["native:a"], ["hip3_:x"])
    assert report["native_tradable"] == 1
    assert report["coma"] is False


def test_lane_window_lets_a_recovered_lane_resume(tmp_path, monkeypatch):
    """A deep old hole must not freeze a lane forever (absorbing state)."""
    from breakwater import lane_gate

    rows = [_row("feat_a:0:LONG:h24", -20.0, outcome="loss", reason="stop")] * 6
    rows += [_row("feat_a:0:LONG:h24", 5.0) for _ in range(12)]
    log = tmp_path / "paper_trade_log.csv"
    _write_log(log, rows)

    monkeypatch.setattr(lane_gate, "LANE_WINDOW", 0)
    assert "native" in compute_green_gate(log).frozen_lanes

    monkeypatch.setattr(lane_gate, "LANE_WINDOW", 10)
    gate = compute_green_gate(log)
    assert "native" not in gate.frozen_lanes
    assert gate.native.pnl == 50.0
    assert gate.native.closed == 10


def test_coma_still_fires_when_only_probes_are_tradable(tmp_path):
    """The probe allowance must not silence the absorbing-state alarm."""
    rows = []
    for index in range(6):
        rows += [_row(f"feat_p{index}:0:LONG:h24", -5.0, outcome="loss", reason="stop")] * 2
    log = tmp_path / "paper_trade_log.csv"
    _write_log(log, rows)

    gate = compute_green_gate(log)
    assert "native" in gate.frozen_lanes
    ids = [f"feat_p{index}:0:LONG:h24" for index in range(6)]
    report = lane_tradability(gate, ids, [])
    assert report["native_tradable"] == 6
    assert report["coma_lanes"] == ["native"]


def test_gate_semantics_are_hardcoded_not_configurable():
    """The lane fix is behaviour, not a knob - nothing may make it optional again."""
    from breakwater import lane_gate

    assert lane_gate.LANE_WINDOW >= 10, "a frozen lane must be able to recover"
    assert lane_gate.PROBE_UNTESTED is True, "untested slices must be able to audition"
    source = Path(lane_gate.__file__).read_text()
    for forbidden in ("BREAKWATER_GREEN_LANE_WINDOW", "BREAKWATER_GREEN_PROBE_UNTESTED"):
        assert forbidden not in source, f"{forbidden} came back as a knob"
