"""Tests for the intraday short-observation inventory."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from breakwater import short_inventory as si


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _validated(rows: list[dict]) -> list[dict]:
    return rows


def test_filters_validated_short_rows(tmp_path):
    validated = tmp_path / "validated_slices.csv"
    discovered = tmp_path / "discovered_slices.csv"
    _write_csv(discovered, [{"slice_id": "dummy"}])
    _write_csv(
        validated,
        [
            {
                "slice_id": "feat:SHORT", "kind": "PERP", "feature": "feat",
                "state": "2", "side": "SHORT", "mean_ret_costadj": "0.006",
                "n": "500", "breadth_symbols_used": "8", "validated": "True",
                "regime_confounded": "False", "hostile_unproven": "False",
                "horizon_bars": "12", "stop_atr_mult": "3.5",
            },
            {
                "slice_id": "feat:SHORT:unval", "kind": "PERP", "feature": "feat",
                "state": "2", "side": "SHORT", "mean_ret_costadj": "0.006",
                "n": "500", "breadth_symbols_used": "8", "validated": "False",
                "regime_confounded": "False", "hostile_unproven": "False",
                "horizon_bars": "12", "stop_atr_mult": "3.5",
            },
            {
                "slice_id": "feat:LONG", "kind": "PERP", "feature": "feat",
                "state": "2", "side": "LONG", "mean_ret_costadj": "0.006",
                "n": "500", "breadth_symbols_used": "8", "validated": "True",
                "regime_confounded": "False", "hostile_unproven": "False",
                "horizon_bars": "12", "stop_atr_mult": "3.5",
            },
        ],
    )
    candidates = si._short_candidates(validated, discovered)
    assert len(candidates) == 1
    assert candidates[0].slice_id == "feat:SHORT"
    assert candidates[0].validated is True


def test_armable_requires_validate_bear_and_env(tmp_path, monkeypatch):
    candidate = si.ShortCandidate(
        slice_id="feat:SHORT", kind="PERP", feature="feat", state=2,
        side="SHORT", mean_ret_costadj=0.006, edge_bps=60.0, n=500,
        breadth_symbols=8, p_value=0.01, validated=True, provisional=False,
        regime_confounded=False, hostile_unproven=False, fail_reasons="",
        horizon_bars=12, stop_atr_mult=3.5, source="validated",
    )
    monkeypatch.setattr(si, "SHORT_PROMOTE_ENABLED", True)
    assert si._armable(candidate, confirmed_bear=True) == (True, "ok")
    assert si._armable(candidate, confirmed_bear=False) == (False, "not_confirmed_bear")
    assert si._armable(si.ShortCandidate(**{**candidate.__dict__, "validated": False}), confirmed_bear=True) == (
        False, "not_validated"
    )
    monkeypatch.setattr(si, "SHORT_PROMOTE_ENABLED", False)
    assert si._armable(candidate, confirmed_bear=True) == (False, "promote_env_off")


def test_compute_inventory_empty_frames(tmp_path):
    validated = tmp_path / "validated_slices.csv"
    discovered = tmp_path / "discovered_slices.csv"
    _write_csv(validated, [])
    _write_csv(discovered, [])
    payload = si.compute_short_inventory(
        validated_path=validated,
        discovered_path=discovered,
        frames_by_kind={},
        server_time=datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc),
        confirmed_bear=True,
    )
    assert payload["enabled"] is True
    assert payload["candidates"] == 0
    assert payload["armable"] == 0
