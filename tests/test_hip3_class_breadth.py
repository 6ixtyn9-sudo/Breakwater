"""Tests for HIP-3 market-class breadth fallback."""

from __future__ import annotations

from breakwater.hip3_research import (
    _apply_hip3_class_breadth,
    _hip3_parse_fingerprint,
)
from breakwater.validation import ValidatedSlice


def _group_row(slice_id, *, fail_reasons="breadth_ok", validated=False):
    return ValidatedSlice(
        slice_id=slice_id,
        kind="PERP",
        feature="feat_atr_norm_ext",
        state=1,
        side="SHORT",
        folds=5,
        walk_forward_pass_pattern="11111",
        walk_forward_pass_count=5,
        fold_mean_rets="0.001,0.001,0.001,0.001,0.001",
        fold_sizes="10,10,10,10,10",
        n=160,
        mean_ret_costadj=0.005,
        p_value=0.0001,
        validated=validated,
        required_passes=3,
        latest_fold_passes=True,
        temporal_pass=True,
        direction_ok=True,
        breadth_ok=False,
        breadth_symbols_used=1,
        breadth_positive_fraction=1.0,
        recency_ok=True,
        mean_positive=True,
        side_train="SHORT",
        fail_reasons=fail_reasons,
        horizon_bars=24,
        stop_atr_mult=3.5,
        hostile_n=0,
        hostile_mean_ret=0.0,
        regime_confounded=False,
        hostile_unproven=False,
    )


def test_parse_fingerprint():
    group, feature, state, side, horizon = _hip3_parse_fingerprint(
        "hip3_xyz_equity_c0:feat_atr_norm_ext:1:SHORT:h24"
    )
    assert group == "xyz_equity_c0"
    assert feature == "feat_atr_norm_ext"
    assert state == 1
    assert side == "SHORT"
    assert horizon == 24
    assert _hip3_parse_fingerprint("feat:1:SHORT") is None


def test_class_breadth_upgrades_only_breadth_failure():
    group_to_class = {"xyz_equity_c0": "equity"}
    # Class-level evidence passes all gates and has 18 symbols.
    class_row = _group_row("fake:1:SHORT", fail_reasons="")
    # Snapshot needs breadth_ok True and validated True on the class row.
    class_row = class_row.__class__(
        **{
            **class_row.__dict__,
            "slice_id": "feat_atr_norm_ext:1:SHORT",
            "breadth_ok": True,
            "breadth_symbols_used": 18,
            "validated": True,
        }
    )
    row = _group_row("hip3_xyz_equity_c0:feat_atr_norm_ext:1:SHORT:h24")
    precomputed = {("feat_atr_norm_ext", 1, "SHORT", 24): class_row}
    out = _apply_hip3_class_breadth(
        [row],
        frames_by_class={},
        group_to_class=group_to_class,
        effective_cost=30.0,
        horizons=[24],
        precomputed_rows=precomputed,
    )
    assert len(out) == 1
    assert out[0].validated is True
    assert out[0].breadth_ok is True
    assert out[0].breadth_scope == "class"
    assert out[0].breadth_class_symbols == 18
    assert out[0].fail_reasons == ""


def test_class_breadth_does_not_upgrade_other_failures():
    group_to_class = {"xyz_equity_c0": "equity"}
    class_row = _group_row("feat_atr_norm_ext:1:SHORT", fail_reasons="")
    class_row = class_row.__class__(
        **{**class_row.__dict__, "breadth_ok": True, "breadth_symbols_used": 18, "validated": True}
    )
    # Row fails breadth AND recency - must stay invalid.
    row = _group_row("hip3_xyz_equity_c0:feat_atr_norm_ext:1:SHORT:h24", fail_reasons="breadth_ok,recency_ok")
    precomputed = {("feat_atr_norm_ext", 1, "SHORT", 24): class_row}
    out = _apply_hip3_class_breadth(
        [row],
        frames_by_class={},
        group_to_class=group_to_class,
        effective_cost=30.0,
        horizons=[24],
        precomputed_rows=precomputed,
    )
    assert out[0].validated is False
    assert out[0].breadth_scope == "symbol"


def test_class_breadth_disabled_returns_unchanged(monkeypatch):
    monkeypatch.setenv("BREAKWATER_HIP3_CLASS_BREADTH", "0")
    row = _group_row("hip3_xyz_equity_c0:feat_atr_norm_ext:1:SHORT:h24")
    out = _apply_hip3_class_breadth(
        [row],
        frames_by_class={},
        group_to_class={"xyz_equity_c0": "equity"},
        effective_cost=30.0,
        horizons=[24],
        precomputed_rows={},
    )
    assert out[0] is row
