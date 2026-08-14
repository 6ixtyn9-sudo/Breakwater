import numpy as np
import pandas as pd

from breakwater.discovery import SliceStat, prepare_pooled
from breakwater.validation import (
    FOLD_COUNT,
    read_validated,
    validate_slices,
    write_validated,
)


def rising_frame(n=400):
    rng = np.random.default_rng(5)
    close = 100 + np.cumsum(np.full(n, 0.02)) + rng.normal(0, 0.05, n)
    return pd.DataFrame({
        "start": pd.date_range("2026-06-01", periods=n, freq="h", tz="UTC"),
        "symbol": "RISER",
        "open": close - 0.2,
        "high": close + 0.4,
        "low": close - 0.4,
        "close": close,
        "volume": rng.uniform(10, 50, n),
    })


def candidate(kind="SPOT", state=0, side="LONG"):
    return SliceStat(
        slice_id=f"close:{state}:{side}",
        kind=kind,
        feature="close",
        state=state,
        side=side,
        n=200,
        mean_ret_costadj=0.001 if side == "LONG" else -0.001,
        median_ret_costadj=0.001,
        hit_rate=0.6,
        t_stat=4.0,
        p_value=0.0001,
        bonferroni_pass=True,
        horizon_bars=1,
    )


def test_validated_slice_with_consistent_rising_returns():
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    assert rows
    assert rows[0].folds == FOLD_COUNT
    assert len(rows[0].walk_forward_pass_pattern) == FOLD_COUNT


def test_validation_requires_latest_fold_pass():
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="SHORT")])
    if rows:
        assert rows[0].validated is False


def test_validated_roundtrip_through_csv(tmp_path):
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    path = tmp_path / "validated.csv"
    write_validated(path, rows)
    loaded = read_validated(path)
    assert len(loaded) == len(rows)
    assert loaded[0].slice_id == rows[0].slice_id
    assert loaded[0].walk_forward_pass_pattern == rows[0].walk_forward_pass_pattern


def test_stop_atr_mult_is_calibrated_within_bounds():
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    assert "fwd_mae_atr_5" in prepared.columns
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    assert rows
    assert 1.5 <= rows[0].stop_atr_mult <= 3.5


def test_read_validated_tolerates_legacy_schema_without_hostile_columns(tmp_path):
    frame = rising_frame()
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    rows = validate_slices(prepared, [candidate(state=0, side="LONG")])
    path = tmp_path / "validated.csv"
    write_validated(path, rows)
    import csv

    stripped = {"hostile_n", "hostile_mean_ret", "regime_confounded"}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        legacy_headers = [name for name in reader.fieldnames if name not in stripped]
        legacy_rows = [
            {name: value for name, value in row.items() if name not in stripped}
            for row in reader
        ]
    legacy_path = tmp_path / "legacy.csv"
    with legacy_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=legacy_headers)
        writer.writeheader()
        writer.writerows(legacy_rows)
    loaded = read_validated(legacy_path)
    assert len(loaded) == len(rows)
    assert loaded[0].stop_atr_mult == rows[0].stop_atr_mult
    assert loaded[0].regime_confounded is False


def test_hostile_regime_check_flags_regime_confounds():
    from breakwater.validation import _hostile_regime_check

    hostile_n, hostile_mean, confounded = _hostile_regime_check(
        "LONG", np.full(30, -0.01)
    )
    assert hostile_n == 30
    assert hostile_mean < 0
    assert confounded is True

    _, _, ok_long = _hostile_regime_check("LONG", np.full(30, 0.01))
    assert ok_long is False

    _, _, short_confounded = _hostile_regime_check("SHORT", np.full(30, 0.01))
    assert short_confounded is True

    _, _, small = _hostile_regime_check("LONG", np.full(5, -0.01))
    assert small is False


def test_regime_series_labels_the_prior():
    from breakwater.validation import _regime_series

    rng = np.random.default_rng(3)
    close = 100 + np.cumsum(np.full(400, 0.3)) + rng.normal(0, 0.2, 400)
    frame = pd.DataFrame({
        "start": pd.date_range("2026-06-01", periods=400, freq="h", tz="UTC"),
        "close": close,
    })
    labels = _regime_series(frame)
    assert set(labels.dropna().unique()).issubset({"bull", "bear", "neutral", "unknown"})
    assert (labels == "bull").any()


def test_bull_only_edge_is_regime_confounded_and_not_validated():
    """The KLAC safeguard: an edge that only works in friendly regimes must
    not be promoted as a structural edge."""
    rng = np.random.default_rng(11)
    bars = 500
    drift = np.zeros(bars)
    drift[:300] = 0.4
    drift[300:] = -0.4
    close = 100 + np.cumsum(drift) + rng.normal(0, 0.2, bars)
    frame = pd.DataFrame({
        "start": pd.date_range("2026-05-01", periods=bars, freq="h", tz="UTC"),
        "symbol": "CONFOUND",
        "open": close - 0.2,
        "high": close + 0.4,
        "low": close - 0.4,
        "close": close,
        "volume": rng.uniform(10, 50, bars),
    })
    prepared = prepare_pooled(frame, ["close"], cost_bps=0.0, horizon_bars=1)
    long_candidates = [
        SliceStat(
            slice_id=f"close:{state}:LONG",
            kind="SPOT",
            feature="close",
            state=state,
            side="LONG",
            n=200,
            mean_ret_costadj=0.001,
            median_ret_costadj=0.001,
            hit_rate=0.6,
            t_stat=4.0,
            p_value=0.0001,
            bonferroni_pass=True,
            horizon_bars=1,
        )
        for state in (0, 1, 2)
    ]
    rows = validate_slices(prepared, long_candidates)
    confounded = [row for row in rows if row.regime_confounded]
    assert confounded, "expected at least one regime-confounded slice"
    for row in confounded:
        assert row.validated is False
        assert row.hostile_n >= 20
