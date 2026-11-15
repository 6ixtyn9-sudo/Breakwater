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
    # With SHORT_USE_PROVISIONAL=True, both validated and unvalidated SHORT
    # rows from the validated file are included (LONG is still filtered out).
    assert len(candidates) == 2
    validated_ids = {c.slice_id for c in candidates if c.validated}
    assert validated_ids == {"feat:SHORT"}


def test_armable_requires_evidence_gates_not_env_flag(tmp_path, monkeypatch):
    candidate = si.ShortCandidate(
        slice_id="feat:SHORT", kind="PERP", feature="feat", state=2,
        side="SHORT", mean_ret_costadj=0.006, edge_bps=60.0, n=500,
        breadth_symbols=8, p_value=0.01, validated=True, provisional=False,
        regime_confounded=False, hostile_unproven=False, fail_reasons="",
        horizon_bars=12, stop_atr_mult=3.5, source="validated",
    )
    # Promotion is evidence-gated, not env-gated: all research bars pass and a
    # confirmed bear is present => armable with no env flag.
    assert si._armable(candidate, confirmed_bear=True) == (True, "ok")
    assert si._armable(candidate, confirmed_bear=False) == (False, "not_confirmed_bear")
    # Unvalidated candidates are now armable as provisional (with risk haircut)
    # when SHORT_USE_PROVISIONAL is True (the default).
    unvalidated = si.ShortCandidate(**{**candidate.__dict__, "validated": False})
    assert si._armable(unvalidated, confirmed_bear=True) == (True, "ok")
    # The safety switch still exists for an operator who explicitly disables it,
    # but it is NOT the default blocker.
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


def test_observe_candidates_computes_features_once_per_frame(monkeypatch):
    """Features, regime and ATR depend on the frame, not the candidate.

    Before the cache, ~600 eligible candidates x 15 frames recomputed the full
    feature set ~9,000 times per paper cycle (45-100 min; the 90-min timeouts
    of 2026-11-06 -> 11-10). Outputs must be identical with the cache.
    """
    import numpy as np
    import pandas as pd

    import breakwater.features as features

    rng = np.random.default_rng(3)
    frames = {}
    for pair in ("BTCUSDC", "ETHUSDC", "SOLUSDC"):
        n = 300
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
        frames[pair] = pd.DataFrame(
            {
                "start": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
                "open": close,
                "high": close * 1.004,
                "low": close * 0.996,
                "close": close,
                "volume": rng.uniform(100, 1000, n),
                "symbol": pair,
            }
        )
    base = dict(
        kind="PERP", side="SHORT", mean_ret_costadj=0.006, edge_bps=60.0, n=500,
        breadth_symbols=8, p_value=0.01, validated=True, provisional=False,
        regime_confounded=False, hostile_unproven=False, fail_reasons="",
        horizon_bars=12, stop_atr_mult=3.5, source="validated",
    )
    candidates = [
        si.ShortCandidate(slice_id=f"{feat}:{state}:SHORT", feature=feat, state=state, **base)
        for feat in ("feat_ret_1", "feat_rsi_14", "feat_ret_20", "feat_atr_percent")
        for state in (0, 1, 2)
    ]
    now = datetime(2026, 1, 13, 12, tzinfo=timezone.utc)

    calls = []
    real = features.compute_price_features

    def counting(frame):
        calls.append(str(frame["symbol"].iloc[0]))
        return real(frame)

    monkeypatch.setattr(features, "compute_price_features", counting)

    cached = si._observe_candidates(
        candidates, {"PERP": frames}, server_time=now, confirmed_bear=True
    )
    assert sorted(calls) == sorted(frames)  # exactly once per frame

    # Same observations as the uncached per-candidate computation.
    reference = []
    for candidate in candidates:
        reference.extend(
            si._observe_candidates(
                [candidate], {"PERP": frames}, server_time=now, confirmed_bear=True
            )
        )
    assert [o.__dict__ for o in cached] == [o.__dict__ for o in reference]
    assert cached  # at least one state matched, so the comparison is not vacuous
