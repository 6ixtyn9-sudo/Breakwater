"""Tests for the research-side short audit and on-demand short inventory."""

from __future__ import annotations

from breakwater.engine import _short_research_audit


def _v(slice_id, side, mean, *, validated=True, fail_reasons=""):
    class Row:
        pass

    row = Row()
    row.slice_id = slice_id
    row.side = side
    row.mean_ret_costadj = mean
    row.validated = validated
    row.fail_reasons = fail_reasons
    return row


def test_short_audit_reports_gap(tmp_path, monkeypatch):
    monkeypatch.setenv("BREAKWATER_MIN_NET_EDGE", "0.004")
    validated = [
        _v("a:LONG", "LONG", 0.006, validated=True),
        _v("b:SHORT", "SHORT", 0.006, validated=True),
        _v("c:SHORT", "SHORT", 0.002, validated=False, fail_reasons="breadth_ok"),
        _v("d:SHORT", "SHORT", 0.005, validated=False, fail_reasons="temporal_pass"),
    ]
    discovered = [
        _v("x:SHORT", "SHORT", 0.006),
        _v("y:SHORT", "SHORT", 0.004),
    ]
    audit = _short_research_audit(validated, discovered)
    assert audit["shorts_discovered"] == 2
    assert audit["shorts_validated"] == 3
    assert audit["shorts_passing"] == 1
    assert audit["shorts_eligible"] == 2
    assert audit["best_short_edge_bps"] == 60.0
    # best overall is the passing 60b short, so it has no fail reason
    assert audit["best_short_fail_reasons"] == ""
    # the best non-passing short is d (50b, temporal_pass), which explains the gap
    assert audit["best_failing_short_edge_bps"] == 50.0
    assert audit["best_failing_short_fail_reasons"] == "temporal_pass"
