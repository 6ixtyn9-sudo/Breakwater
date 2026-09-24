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
    assert len(dp._ledger_close_rows(rows)) == 1
    text = _section(rows, [NATIVE_ID], [], {NATIVE_ID: 0.004}, {})
    assert "0 real closes" in text


def test_population_delta_prints_when_ledger_and_gate_counts_differ():
    # A stale_data exit is a real close for sections 2/3 but not for the gate
    # set section 2b uses. The asymmetry must be printed, never hidden, and
    # the sets must not be unified.
    rows = [
        _close(NATIVE_ID, -5.0, exit_reason="stale_data"),
        _close(HIP3_ID, -2.0, exit_reason="stale_data"),
    ]
    text = _section(rows, [NATIVE_ID], [HIP3_ID], {NATIVE_ID: 0.004}, {HIP3_ID: 0.001})
    assert "Population delta vs sections 2/3" in text
    assert "counts 2 closes; this section counts 0 under lane_gate" in text
    assert "2 extra in the ledger (native 1 | hip3 1" in text
    assert "stale_data=2" in text
    assert "not unified on purpose" in text


def test_no_population_delta_line_when_sets_agree():
    # horizon exits belong to both sets; with no stale_data rows the section
    # must not invent a disagreement.
    rows = [_close(NATIVE_ID, -2.0), _close(NATIVE_ID, -10.0)]
    text = _section(rows, [NATIVE_ID], [], {NATIVE_ID: 0.01}, {})
    assert "Population delta" not in text
    # And all-skipped logs agree at zero.
    skipped = _section([_skip() for _ in range(10)], [NATIVE_ID], [], {NATIVE_ID: 0.01}, {})
    assert "Population delta" not in skipped


def test_verdict_constants_are_pinned_to_policy_literals():
    # These two numbers are the only "knobs" in an advisory section and the
    # temptation during a bad fortnight is to move one so the verdict gets
    # quieter. A change here must be deliberate, reviewed and visible, like
    # the pinned gate constants in tests/test_lane_gate.py.
    assert dp.MIN_VERDICT_CLOSES == 30
    assert dp.VERDICT_T_THRESHOLD == 2.0
    # Boundaries at the pinned threshold.
    assert dp._verdict(-2.0, -1.0, 0.0) == "FALLS SHORT"
    assert dp._verdict(2.0, 1.0, 0.0) == "EXCEEDS"
    assert dp._verdict(-1.999, -1.0, 0.0) == "NOT ESTABLISHED"
    assert dp._verdict(1.999, 1.0, 0.0) == "NOT ESTABLISHED"


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


def test_resolve_shadow_scan_skips_unreadable_newest():
    # Rows written before the 64 000-char bound end mid-string. The resolver
    # must never salvage one (a salvaged dict can silently lose its trailing
    # paper block): it walks back to the newest scan that parses whole.
    whole = json.dumps({"signals": 3, "paper": {"closed": 7}}, sort_keys=True)
    rows = [
        {"timestamp_utc": "2026-09-23T00:00:00+00:00", "detail": whole},
        {"timestamp_utc": "2026-09-24T00:00:00+00:00", "detail": whole[:-2]},
    ]
    row, detail = dp._resolve_shadow_scan(rows)
    assert row is rows[0]
    assert detail == {"signals": 3, "paper": {"closed": 7}}


def test_resolve_shadow_scan_prefers_newest_whole_scan_and_none_when_all_unreadable():
    rows = [
        {
            "timestamp_utc": "2026-09-22T00:00:00+00:00",
            "detail": json.dumps({"signals": 1, "paper": {"closed": 1}}),
        },
        {"timestamp_utc": "2026-09-23T00:00:00+00:00", "detail": '{"signals": 3'},
        {
            "timestamp_utc": "2026-09-24T00:00:00+00:00",
            "detail": json.dumps({"signals": 2, "paper": {"closed": 2}}),
        },
    ]
    row, detail = dp._resolve_shadow_scan(rows)
    assert row is rows[2]
    assert detail == {"signals": 2, "paper": {"closed": 2}}
    # A whole row without a paper block is NOT usable: section 5 would render
    # it as fabricated zeros. Skip it, and report (None, {}) when it is all
    # the history there is.
    paperless = {
        "timestamp_utc": "2026-09-25T00:00:00+00:00",
        "detail": json.dumps({"signals": 5}),
    }
    row, detail = dp._resolve_shadow_scan(rows + [paperless])
    assert row is rows[2]
    assert detail == {"signals": 2, "paper": {"closed": 2}}
    assert dp._resolve_shadow_scan([paperless]) == (None, {})
    assert dp._resolve_shadow_scan([rows[1]]) == (None, {})
    assert dp._resolve_shadow_scan([]) == (None, {})


def test_report_reuses_whole_scan_for_sections_5_and_13(tmp_path, monkeypatch):
    data = tmp_path / "localdata"
    _write_minimal_state(data)
    whole = {
        "signals": 3,
        "errors": 0,
        "regime_blocked": 1,
        "lane_gate_blocked": 2,
        "pair_errors": [],
        "paper": {
            "aggregate_risk_cap_zar": "100.0",
            "aggregate_open_risk_zar": "12.5",
            "aggregate_risk_utilization": "0.125",
            "aggregate_risk_status": "ok",
            "aggregate_risk_remaining_zar": "87.5",
            "aggregate_risk_cap_skips": 0,
            "aggregate_risk_unknown_skips": 0,
            "book_stats": {},
            "closed": 7,
            "new_signals": 2,
            "skipped": 1,
            "slot_full": 0,
            "slice_full": 0,
            "pair_held": 0,
            "positions_without_new_bars": 0,
            "replayed_bars": 0,
            "invalid_positions_quarantined": 0,
        },
    }
    # A newer row cut mid-string, exactly as the old 4000-char cap left them.
    cut = json.dumps(whole | {"signals": 999})[:300]
    with (data / "status.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp_utc", "stage", "mode", "detail"])
        writer.writerow(
            ["2026-09-23T00:00:00+00:00", "shadow_scan_done", "shadow",
             json.dumps(whole, sort_keys=True)]
        )
        writer.writerow(["2026-09-24T00:00:00+00:00", "shadow_scan_done", "shadow", cut])
    monkeypatch.setattr(dp, "DATA", data)
    text = dp._report_text()

    # Sections 5 and 13 share the newest whole scan: real numbers, never the
    # fabricated zeros / Nones a salvaged half-row used to produce.
    assert "12.50 / 100.00 ZAR | 12.5% | ok" in text
    assert "0.00 / 0.00 ZAR" not in text
    assert "signals=3" in text and "signals=None" not in text and "signals=999" not in text
    assert "closed=7" in text and "new_signals=2" in text
    # The report names the scan it used and admits the newest is unreadable.
    assert "2026-09-24T00:00:00" in text and "unreadable" in text
    assert "Resolved scan 2026-09-23T00:00:00" in text


def test_report_never_prints_zeros_from_a_paperless_scan(tmp_path, monkeypatch):
    # A whole row without a usable paper block (or without the aggregate-leash
    # keys) must never render the fabricated '0.00 / 0.00 ZAR | 0.0% | None'
    # ledger line - whether it sits older or newer than a paper-bearing row.
    data = tmp_path / "localdata"
    _write_minimal_state(data)
    monkeypatch.setattr(dp, "DATA", data)
    good = {
        "signals": 3,
        "errors": 0,
        "paper": {
            "aggregate_risk_cap_zar": "100.0",
            "aggregate_open_risk_zar": "12.5",
            "aggregate_risk_utilization": "0.125",
            "aggregate_risk_status": "ok",
            "closed": 7,
            "new_signals": 2,
            "skipped": 1,
        },
    }
    paperless = {"signals": 9}
    old_style_paper = {"signals": 7, "paper": {"closed": 3}}

    def write(rows):
        with (data / "status.csv").open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["timestamp_utc", "stage", "mode", "detail"])
            for stamp, detail in rows:
                writer.writerow([stamp, "shadow_scan_done", "shadow", detail])

    # Paperless row older than the good row: the good row is resolved.
    write([
        ("2026-09-23T00:00:00+00:00", json.dumps(paperless)),
        ("2026-09-24T00:00:00+00:00", json.dumps(good, sort_keys=True)),
    ])
    text = dp._report_text()
    assert "12.50 / 100.00 ZAR | 12.5% | ok" in text
    assert "0.00 / 0.00 ZAR" not in text

    # Paperless row newer than the good row: still the good row, never zeros.
    write([
        ("2026-09-24T00:00:00+00:00", json.dumps(good, sort_keys=True)),
        ("2026-09-25T00:00:00+00:00", json.dumps(paperless)),
    ])
    text = dp._report_text()
    assert "12.50 / 100.00 ZAR | 12.5% | ok" in text
    assert "0.00 / 0.00 ZAR" not in text
    assert "signals=3" in text and "signals=None" not in text
    assert "closed=7" in text and "new_signals=2" in text

    # A resolved scan whose paper predates the aggregate-leash keys: the
    # explicit no-numbers line, never the zeros line.
    write([("2026-09-24T00:00:00+00:00", json.dumps(old_style_paper, sort_keys=True))])
    text = dp._report_text()
    assert "carries no aggregate-risk numbers" in text
    assert "0.00 / 0.00 ZAR" not in text


def test_report_picks_newest_rows_by_timestamp_not_file_position(tmp_path, monkeypatch):
    # status.csv is not chronological: workflow merges interleave rows, so a
    # stale guardian_ok row can sit last and a stale scan anywhere. The report
    # must pick rows by timestamp, never by file position.
    data = tmp_path / "localdata"
    _write_minimal_state(data)
    guardian_new = {
        "mode": "shadow",
        "equity_zar": "700.55",
        "high_water_zar": "701.00",
        "key_permissions": [],
        "risk_allowed": True,
        "risk_reasons": [],
    }
    guardian_stale = dict(guardian_new, equity_zar="557.83")
    scan_old = {
        "signals": 1,
        "paper": {
            "aggregate_risk_cap_zar": "100.0",
            "aggregate_open_risk_zar": "12.5",
            "aggregate_risk_utilization": "0.125",
            "aggregate_risk_status": "ok",
        },
    }
    scan_new = {
        "signals": 4,
        "paper": {
            "aggregate_risk_cap_zar": "200.0",
            "aggregate_open_risk_zar": "34.5",
            "aggregate_risk_utilization": "0.1725",
            "aggregate_risk_status": "tight",
        },
    }
    with (data / "status.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp_utc", "stage", "mode", "detail"])
        # Deliberately out of order: newest scan in the middle, stale
        # guardian row last.
        writer.writerow([
            "2026-09-24T09:00:00+00:00", "shadow_scan_done", "shadow",
            json.dumps(scan_old, sort_keys=True),
        ])
        writer.writerow([
            "2026-09-24T10:00:00+00:00", "guardian_ok", "shadow",
            json.dumps(guardian_new, sort_keys=True),
        ])
        writer.writerow([
            "2026-09-24T11:00:00+00:00", "shadow_scan_done", "shadow",
            json.dumps(scan_new, sort_keys=True),
        ])
        writer.writerow([
            "2026-09-13T09:00:00+00:00", "guardian_ok", "shadow",
            json.dumps(guardian_stale, sort_keys=True),
        ])
    monkeypatch.setattr(dp, "DATA", data)
    text = dp._report_text()

    # Newest guardian equity, never the stale row that happens to sit last.
    assert "700.55" in text
    assert "557.83" not in text
    # Newest scan's leash numbers, not the older scan's.
    assert "34.50 / 200.00 ZAR | 17.2% | tight" in text
    assert "12.50 / 100.00 ZAR | 12.5% | ok" not in text
    assert "Latest scan 2026-09-24T11:00:00" in text


def test_resolve_shadow_scan_orders_by_timestamp_not_file_position():
    # The usable scan with the newest timestamp sits in the middle of the
    # file; position must never be read as 'latest'.
    rows = [
        {
            "timestamp_utc": "2026-09-24T09:00:00+00:00",
            "detail": json.dumps({"signals": 1, "paper": {"closed": 1}}),
        },
        {
            "timestamp_utc": "2026-09-25T08:00:00+00:00",
            "detail": json.dumps({"signals": 3, "paper": {"closed": 3}}),
        },
        {
            "timestamp_utc": "2026-09-23T00:00:00+00:00",
            "detail": json.dumps({"signals": 2, "paper": {"closed": 2}}),
        },
    ]
    row, detail = dp._resolve_shadow_scan(rows)
    assert row is rows[1]
    assert detail == {"signals": 3, "paper": {"closed": 3}}


def test_report_prints_unreadable_line_for_unparseable_guardian_row(tmp_path, monkeypatch):
    # Salvage used to patch up cut rows and present the partial dict as the
    # live reading. A guardian_ok row that does not parse whole must instead
    # be named unreadable - never patched into an equity figure.
    data = tmp_path / "localdata"
    _write_minimal_state(data)
    with (data / "status.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp_utc", "stage", "mode", "detail"])
        writer.writerow([
            "2026-09-24T12:00:00+00:00",
            "guardian_ok",
            "shadow",
            '{"mode": "shadow", "equity_zar": "557.83", "high',  # cut mid-string
        ])
    monkeypatch.setattr(dp, "DATA", data)
    text = dp._report_text()
    assert "guardian_ok row 2026-09-24T12:00:00 is unreadable" in text
    assert "VALR equity" not in text
    assert "557.83" not in text
