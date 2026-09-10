"""Tests for the read-only section 2b claimed-vs-realised verdict.

The section lives in scripts/daily_print.py. Its statistics are tested on
synthetic fixtures: empty / all-skipped logs must not raise or divide by
zero, the t-statistic math is checked on a known two-row sample, and a book
slice missing from the validated pool must render "unknown" instead of being
silently averaged away.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import daily_print as dp  # noqa: E402


def _close(slice_id, pnl, notional=200.0, exit_reason="horizon", outcome=None):
    return {
        "slice_id": slice_id,
        "pair": "TESTUSDC",
        "outcome": outcome or ("win" if pnl > 0 else "loss"),
        "exit_reason": exit_reason,
        "pnl_zar": f"{pnl:.4f}",
        "notional_zar": f"{notional:.2f}",
        "closed_at": "2026-09-10T00:00:00+00:00",
    }


def _skip(slice_id="feat_x:0:LONG:h1", reason="session"):
    return {
        "slice_id": slice_id,
        "pair": "TESTUSDC",
        "outcome": "skipped",
        "exit_reason": reason,
        "pnl_zar": "0",
        "notional_zar": "0",
        "closed_at": "2026-09-10T00:00:00+00:00",
    }


def _book(ids):
    return [{"slice_id": sid, "status": "monitored"} for sid in ids]


def _validated(edge_by_id):
    return [
        {"slice_id": sid, "validated": "True", "mean_ret_costadj": f"{edge:.6f}"}
        for sid, edge in edge_by_id.items()
    ]


def _section(rows, native_ids, hip3_ids, native_edges=None, hip3_edges=None):
    return dp._claimed_vs_realised_section(
        rows,
        _book(native_ids),
        _book(hip3_ids),
        _validated(native_edges or {}),
        _validated(hip3_edges or {}),
    )


NATIVE_ID = "feat_edge:0:LONG:h1"
HIP3_ID = "hip3_grp:feat_edge:0:LONG:h1"


def test_empty_log_prints_insufficient_sample_no_exception():
    text = _section([], [NATIVE_ID], [], {NATIVE_ID: 0.004}, {})
    assert "## 2b. Claimed vs realised" in text
    assert "INSUFFICIENT SAMPLE" in text
    assert "0 real closes" in text
    # No t-statistic is allowed while the sample is too small.
    assert "t =" not in text
    assert "net of fees" in text
    assert "feeds no gate" in text


def test_all_skipped_log_no_division_by_zero():
    rows = [_skip(reason="session") for _ in range(800)]
    text = _section(rows, [NATIVE_ID], [], {NATIVE_ID: 0.004}, {})
    assert "800 decision rows; 0 real closes" in text
    assert "INSUFFICIENT SAMPLE" in text
    assert "t =" not in text


def test_stale_data_row_is_not_a_real_close():
    # Section 2b reuses lane_gate's real-close definition, which (unlike the
    # ledger view in section 2) does not count stale_data exits.
    rows = [_close(NATIVE_ID, -5.0, exit_reason="stale_data")]
    assert dp._real_close_rows(rows) == []
    text = _section(rows, [NATIVE_ID], [], {NATIVE_ID: 0.004}, {})
    assert "0 real closes" in text


def test_two_row_fixture_known_mean_sd_and_t_to_two_decimal_places():
    # Two closes of -2 and -10 ZAR on 200 ZAR notional; claimed edge is 1% =
    # 2.00 ZAR/trade. mean=-6, sample sd=sqrt(32)=5.6569, SE=sd/sqrt(2)=4.00,
    # gap=-8.00, t=-2.00 exactly.
    rows = [_close(NATIVE_ID, -2.0), _close(NATIVE_ID, -10.0)]
    stats = dp._close_stats(rows)
    assert stats["n"] == 2
    assert stats["mean"] == pytest.approx(-6.0)
    assert stats["sd"] == pytest.approx(5.656854, abs=1e-6)
    assert stats["se"] == pytest.approx(4.0)
    t = dp._gap_t(stats["mean"], stats["se"], 2.0)
    assert f"{t:+.2f}" == "-2.00"
    assert dp._verdict(t, stats["mean"], 2.0) == "FALLS SHORT"
    # The rendered section still suppresses the t for n < 30.
    text = _section(rows, [NATIVE_ID], [], {NATIVE_ID: 0.01}, {})
    assert "INSUFFICIENT SAMPLE" in text
    assert "t =" not in text


def test_verdict_word_mapping():
    assert dp._verdict(-2.5, -3.0, 1.0) == "FALLS SHORT"
    assert dp._verdict(2.5, 3.0, 1.0) == "EXCEEDS"
    assert dp._verdict(0.1, 0.1, 0.0) == "NOT ESTABLISHED"
    # t >= 2 while realised is not actually above claimed stays unestablished.
    assert dp._verdict(2.5, 0.5, 1.0) == "NOT ESTABLISHED"


def test_book_slice_absent_from_validated_reports_unknown():
    ghost = "feat_ghost:0:LONG:h1"
    text = _section([], [ghost], [], {}, {})
    assert "unknown" in text
    assert "0/1 book slices present in the validated pools" in text
    assert f"absent: `{ghost}`" in text
    # No claimed ZAR figure is invented, and no t appears.
    assert "ZAR/trade" not in text
    assert "t =" not in text


def test_partial_match_denominator_is_visible():
    ghost = "feat_ghost:0:LONG:h1"
    rows = [_close(NATIVE_ID, -2.0), _close(NATIVE_ID, -10.0)]
    text = _section(rows, [NATIVE_ID, ghost], [], {NATIVE_ID: 0.01}, {})
    # Median computed over the one matched slice, with both denominators shown
    # and the absent slice named rather than silently dropped.
    assert "over 1 book slices present in the validated pools" in text
    assert "absent from pools: 1" in text
    assert f"absent: `{ghost}`" in text


def test_per_lane_split_small_lane_is_insufficient():
    rows = []
    # 35 native closes (alternating -3/-7 -> mean -5) and 24 hip3 closes.
    for i in range(35):
        rows.append(_close(NATIVE_ID, -3.0 if i % 2 == 0 else -7.0))
    for i in range(24):
        rows.append(_close(HIP3_ID, -3.0 if i % 2 == 0 else -7.0))
    text = _section(
        rows,
        [NATIVE_ID],
        [HIP3_ID],
        {NATIVE_ID: 0.005},
        {HIP3_ID: 0.001},
    )
    native_line = next(line for line in text.splitlines() if line.startswith("- native:"))
    hip3_line = next(line for line in text.splitlines() if line.startswith("- hip3:"))
    assert "realised 35 closes" in native_line
    assert "FALLS SHORT" in native_line
    assert "realised 24 closes" in hip3_line
    assert "INSUFFICIENT SAMPLE" in hip3_line
    # Pooled line has the full sample and prints a t; hip3's lane does not.
    assert "Realised (59 real closes" in text
    assert "t =" in text
    assert "t " not in hip3_line


def _write_minimal_state(base: Path):
    research = base / "research"
    hip3 = base / "hip3" / "research"
    research.mkdir(parents=True)
    hip3.mkdir(parents=True)

    log_header = [
        "closed_at",
        "pair",
        "kind",
        "slice_id",
        "side",
        "entry_price",
        "exit_price",
        "stop_price",
        "notional_zar",
        "pnl_zar",
        "outcome",
        "bars_held",
        "exit_reason",
        "entry_guard",
        "regime",
        "pnl_outcome",
    ]
    with (research / "paper_trade_log.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(log_header)
        w.writerow([""] * 9 + ["0", "skipped", "0", "session", "session_blocked", "bear", ""])

    book_header = "slice_id,status,mean_ret_costadj\n"
    # A monitored slice with no validated row: the unknown path end to end.
    (research / "monitored_slices.csv").write_text(
        book_header + "feat_unknown:0:LONG:h1,monitored,\n"
    )
    (research / "validated_slices.csv").write_text("slice_id,validated,mean_ret_costadj\n")
    (hip3 / "monitored_slices.csv").write_text(book_header)
    (hip3 / "validated_slices.csv").write_text("slice_id,validated,mean_ret_costadj\n")

    # One open BUY: entry 100, stop 90, notional 1000 -> 100.00 ZAR stop-risk.
    (research / "paper_positions.json").write_text(
        json.dumps(
            [
                {
                    "slice_id": NATIVE_ID,
                    "pair": "TESTUSDC",
                    "side": "BUY",
                    "entry_price": "100",
                    "stop_price": "90",
                    "notional_zar": "1000",
                    "bars_held": "3",
                    "peak_price": "101",
                }
            ]
        )
    )

    detail = {
        "paper": {
            "aggregate_risk_cap_zar": "100.0",
            "aggregate_open_risk_zar": "12.5",
            "aggregate_risk_utilization": "0.125",
            "aggregate_risk_status": "ok",
            "aggregate_risk_remaining_zar": "87.5",
            "aggregate_risk_cap_skips": 0,
            "aggregate_risk_unknown_skips": 0,
            "book_stats": {},
            "positions_without_new_bars": 0,
            "replayed_bars": 0,
            "invalid_positions_quarantined": 0,
        }
    }
    with (base / "status.csv").open("w", newline="") as h:
        w = csv.writer(h)
        w.writerow(["timestamp_utc", "stage", "mode", "detail"])
        w.writerow(["2026-09-10T00:00:00+00:00", "shadow_scan_done", "shadow", json.dumps(detail)])


def test_full_report_renders_section_2b_and_unwired_leash(tmp_path, monkeypatch):
    data = tmp_path / "localdata"
    _write_minimal_state(data)
    monkeypatch.setattr(dp, "DATA", data)
    text = dp._report_text()

    assert "## 2b. Claimed vs realised" in text
    assert "unknown" in text
    assert "INSUFFICIENT SAMPLE" in text

    # Part B: the leash is unmistakably unwired, numbers stay visible.
    assert "NOT WIRED FOR LIVE TRADING" in text
    assert "100.00 ZAR" in text
    assert "Paper shadow ledger (gates paper entries only, nothing live)" in text
    assert "12.50 / 100.00 ZAR | 12.5% | ok" in text
    # The old bare line that implied enforcement is gone.
    assert "- Aggregate: **12.50 / 100.00 ZAR" not in text
